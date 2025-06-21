import time, pycurl, json
from io import BytesIO
from threading import Event
from typing import cast

from logic.logs import add_log
from config.config import timeout_connection, max_attempts, backoff_time, timeout_retrieve

def get_price(item_data: str, cancel_event: Event, sell_or_buy: str) -> str:
    """
    Fetch price of an item from the provided data.
        :param item_data: The raw data string containing response information from API.
        :param cancel_event: An event to signal cancellation of the operation.
        :param sell_or_buy: A string indicating whether to fetch the 'sellCount' or 'buyCount'.
        :return: The price of the item as a string.
    """
    try:
        data = json.loads(item_data)
        availability = data["data"]["availability"]
        price = None

        for entry in availability:
            if cancel_event.is_set():
                return ""

            if entry[sell_or_buy] != 0:
                if price is None:
                    price = entry["onePrice"]
                break
            
            price = entry["onePrice"]

        return str(price) if price is not None else ""

    except (KeyError, json.JSONDecodeError) as e:
        add_log(f"Error parsing item data: {e}", "error")
        return ""
    
def get_sell_price(item_data: str, cancel_event: Event) -> str:
    """
    Fetch selling price of an item from the provided data.
        :param item_data: The raw data string containing response information from API.
        :param cancel_event: An event to signal cancellation of the operation.
        :return: The selling price of the item as a string.
    """
    return get_price(item_data, cancel_event, "sellCount")

def get_buy_price(item_data: str, cancel_event: Event) -> str:
    """
    Fetch buying price of an item from the provided data.
        :param item_data: The raw data string containing response information from API.
        :param cancel_event: An event to signal cancellation of the operation.
        :return: The buying price of the item as a string.
    """
    return get_price(item_data, cancel_event, "buyCount")

def perform_api_request(url: str, cancel_event: Event) -> tuple[BytesIO, int]:
    """
    Perform an API request using pycurl to fetch data from the specified URL.
        :param url: The URL to fetch data from.
        :param cancel_event: An event to signal cancellation of the operation.
        :return: A tuple containing a BytesIO object with the response data and the HTTP response code.
    """
    if cancel_event.is_set():
        return BytesIO(), 0

    buffer = BytesIO()
    response_code: int = 0

    c = pycurl.Curl()
    headers = ['accept: */*']
    c.setopt(c.HTTPHEADER, headers)                   # type: ignore
    c.setopt(c.CONNECTTIMEOUT, timeout_connection)    # type: ignore
    c.setopt(c.URL, url)                              # type: ignore
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

def get_item_data(id_item: str, cancel_event: Event, region: str = "eu", attempts: int = 0) -> str:
    """
    Connect to the Black Desert Market API to fetch item or elixir data.
        :param id_item: The ID of the item or elixir to fetch.
        :param region: The region for which to fetch the data (default is "eu").
        :param cancel_event: An event to signal cancellation of the operation.
        :param attempts: The number of attempts made to fetch the data (default is 0).
        :return: The raw data string containing response information from API, or an empty string if the request fails.
    """
    if cancel_event.is_set():
        return ""
    
    url = f"https://api.blackdesertmarket.com/item/{id_item}/0?region={region}"
    buffer, response_code = perform_api_request(url, cancel_event)

    if response_code == 200:
        return buffer.getvalue().decode("utf-8")
    elif response_code == 500:
        add_log(f"Server returned 500 for item {id_item} data. Attempt {attempts + 1}", "warning")
    else:
        add_log(f"Unexpected response code {response_code} for item {id_item} data", "warning")

    if attempts < max_attempts:
        time.sleep(backoff_time)  # backoff before retrying
        return get_item_data(id_item, cancel_event, region, attempts + 1)

    add_log(f"Max attempts reached for item {id_item} data", "error")
    return ""