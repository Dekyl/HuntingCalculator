import time, pycurl, json
from io import BytesIO
from threading import Event
from typing import cast

from logic.logs import add_log
from config.config import timeout_connection, max_attempts, backoff_time, timeout_retrieve

class ApiRequest():
    def __init__(self, id_item: str, item_type: str, cancel_event: Event, region: str = "eu"):
        """
        Initialize the ApiRequest object with item ID, type, region, and cancellation event.
            :param id_item: The ID of the item or elixir to fetch.
            :param item_type: The type of item (e.g., "Items", "Elixirs").
            :param cancel_event: An event to signal cancellation of the operation.
            :param region: The region for which to fetch the data (default is "eu").
        """
        self.id_item = id_item
        self.item_type = item_type
        self.cancel_event = cancel_event
        self.region = region
        self.attempts = 0
        self.sell_or_buy = "sellCount" if item_type == "Items" else "buyCount"
        self.url = f"https://api.blackdesertmarket.com/item/{self.id_item}/0?region={self.region}"

    def get_price(self) -> str:
        """
        Fetch the price of the item or elixir from the Black Desert Market API.
            :return: The price as a string if available, or an empty string if not found or an error occurs.
        """

        item_data = self.get_item_data()
        if not item_data:
            add_log(f"Failed to retrieve data for item {self.id_item} after {self.attempts} attempts", "error")
            return ""
        try:
            data = json.loads(item_data)
            availability = data["data"]["availability"]
            price = None

            for entry in availability:
                if self.cancel_event.is_set():
                    return ""

                if entry[self.sell_or_buy] != 0:
                    if price is None:
                        price = entry["onePrice"]
                    break
                
                price = entry["onePrice"]

            return str(price) if price is not None else ""

        except (KeyError, json.JSONDecodeError) as e:
            add_log(f"Error parsing item data: {e}", "error")
            return ""
        
    def get_item_data(self) -> str:
        """
        Connect to the Black Desert Market API to fetch item or elixir data.
            :return: The raw data string containing response information from API, or an empty string if the request fails.
        """
        if self.cancel_event.is_set():
            return ""
        
        buffer, response_code = self.perform_api_request()

        if response_code == 200:
            return buffer.getvalue().decode("utf-8")
        elif response_code == 500:
            add_log(f"Server returned 500 for item {self.id_item} data. ({self.attempts + 1}/{max_attempts})", "warning")
        else:
            add_log(f"Unexpected response code {response_code} for item {self.id_item} data", "warning")

        if self.attempts < max_attempts:
            time.sleep(backoff_time)  # backoff before retrying
            self.attempts += 1
            return self.get_item_data()

        add_log(f"Max attempts reached ({max_attempts}) for item {self.id_item} data", "error")
        return ""

    def perform_api_request(self) -> tuple[BytesIO, int]:
        """
        Perform an API request using pycurl to fetch data from the specified URL.
            :return: A tuple containing a BytesIO object with the response data and the HTTP response code.
        """
        if self.cancel_event.is_set():
            return BytesIO(), 0

        buffer = BytesIO()
        response_code: int = 0

        c = pycurl.Curl()
        headers = ['accept: */*']
        c.setopt(c.HTTPHEADER, headers)                   # type: ignore
        c.setopt(c.CONNECTTIMEOUT, timeout_connection)    # type: ignore
        c.setopt(c.URL, self.url)                              # type: ignore
        c.setopt(c.WRITEDATA, buffer)                     # type: ignore
        c.setopt(c.TIMEOUT, timeout_retrieve)             # type: ignore

        try:
            c.perform()
            response_code = cast(int, c.getinfo(pycurl.HTTP_CODE))  # type: ignore
        except Exception as e:
            add_log(f"Pycurl exception: {e}", "error")
        finally:
            c.close()

        return buffer, response_code