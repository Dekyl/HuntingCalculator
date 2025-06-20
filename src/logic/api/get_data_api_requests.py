import time, os, pycurl, json
from io import BytesIO
from threading import Event
from typing import cast

from logic.logs import add_log
from config.config import timeout_connection, max_attempts, reduced_item_names, backoff_time, timeout_retrieve

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

def get_item_icon(id_item: str, save_path: str, cancel_event: Event, attempts: int = 0) -> int:
    """
    Fetch the icon of an item from the Black Desert Market API.
        :param id_item: The ID of the item to fetch the icon for.
        :param save_path: The path where the icon will be saved.
        :param cancel_event: An event to signal cancellation of the operation.
        :param attempts: The number of attempts made to fetch the icon (default is 0).
        :return: 0 on success, -1 on failure.
    """
    if os.path.exists(save_path):
        add_log(f"Icon for ID {id_item} already exists at {save_path}. Skipping download.", "info")
        return 0

    url_icon =  f"https://api.blackdesertmarket.com/item/{id_item}/icon"
    buffer, response_code = perform_api_request(url_icon, cancel_event)

    if response_code == 200:
        # Save the icon as PNG
        try:
            buffer.seek(0)
            with open(save_path, "wb") as icon_file:
                icon_file.write(buffer.getvalue())
        except Exception as e:
            add_log(f"Error saving icon for ID {id_item}: {e}", "error")
            return -1

        return 0  # Return 0 on success, -1 on failure
    elif response_code == 500:
        add_log(f"Server returned 500 for item {id_item} icon. Attempt {attempts + 1}", "warning")
    else:
        add_log(f"Unexpected response code {response_code} for item {id_item} icon", "warning")

    if attempts < max_attempts:
        time.sleep(backoff_time)  # backoff before retrying
        return get_item_icon(id_item, save_path, cancel_event, attempts + 1)

    add_log(f"Max attempts reached for item {id_item} icon", "error")
    return -1

def reduce_item_name_length(item_name: str) -> str:
    """
    Reduce the length of item names to fit in QLabel view.
        :param item_name: The name of the item to reduce.
    """
    if item_name in reduced_item_names:
        return reduced_item_names[item_name]
    return item_name


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

def get_item_name(id_item: str, cancel_event: Event, region: str = "eu", language: str = "en-US", attempts: int = 0) -> str:
    """
    Connect to the Black Desert Market API to fetch item or elixir name.
        :param id_item: The ID of the item or elixir to fetch.
        :param cancel_event: An event to signal cancellation of the operation.
        :param region: The region for which to fetch the name (default is "eu").
        :param language: The language for which to fetch the name (default is "en-US").
        :param attempts: The number of attempts made to fetch the name (default is 0).
        :return: The name of the item or elixir as a string, or an empty string if the request fails.
    """
    buffer, response_code = perform_api_request(f"https://api.blackdesertmarket.com/item/{id_item}?region={region}&language={language}", cancel_event)

    if response_code == 200:
        try:
            response_data = buffer.getvalue().decode("utf-8")
            if '"name":"' not in response_data:
                add_log(f"No 'name' field in response: {response_data}", "error")
                return ""
            start_index = response_data.find('"name":"') + len('"name":"')
            end_index = response_data.find('"', start_index)
            item_name = response_data[start_index:end_index]
            return reduce_item_name_length(item_name)
        except Exception as e:
            add_log(f"Error parsing response: {e}", "error")
            return ""
    elif response_code == 500:
        add_log(f"Server returned 500 for item {id_item} name. Attempt {attempts + 1}", "warning")
    else:
        add_log(f"Unexpected response code {response_code} for item {id_item} name", "warning")

    if attempts < max_attempts:
        time.sleep(backoff_time)  # backoff before retrying
        return get_item_name(id_item, cancel_event, region, language, attempts + 1)

    add_log(f"Max attempts reached for item {id_item} name", "error")
    return ""

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