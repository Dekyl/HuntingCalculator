import time, os, pycurl
from io import BytesIO
from threading import Event

from logic.logs import add_log
from config.config import timeout_connection, max_attempts, reduced_item_names

def get_sell_price(item_data:str, cancel_event: Event) -> str:
    """
    Fetch selling price of an item from the provided data.
        :param item_data: The raw data string containing response information from API.
        :param cancel_event: An event to signal cancellation of the operation.
        :return: The selling price of the item as a string.
    """
    item_data = item_data[0:item_data.find("history")]
    index = 0
    last_sell_val = "0"

    while index < len(item_data):
        if cancel_event.is_set():  # Check if the cancel event is set before proceeding
            return ""
        
        # Takes index of first "sellCount", iterates through all "sellCount" in item_data until it finds the best match to gain maximum profit (selling higher price with no sellers)
        index = item_data.find("sellCount")
        if index == -1:
            return last_sell_val
        
        index += len("sellCount") + 2
        left_index_price = item_data.find("onePrice", index) + len("onePrice") + 2
        right_index_price = item_data.find("}", left_index_price)
        last_sell_val = item_data[left_index_price:right_index_price]

        if item_data[index] != "0": # Takes 1 char of the price to check if it is 0 (no leading zeros)
            return last_sell_val
        
        item_data = item_data[index:len(item_data)]
        index = 0

    return last_sell_val

def get_buy_price(item_data:str, cancel_event: Event) -> str:
    """
    Fetch buying price of an item from the provided data.
        :param item_data: The raw data string containing response information from API.
        :param cancel_event: An event to signal cancellation of the operation.
        :return: The buying price of the item as a string.
    """
    item_data = item_data[0:item_data.find("history")]
    index = 0
    buy_price = "0"

    while index < len(item_data):
        if cancel_event.is_set():  # Check if the cancel event is set before proceeding
            return ""
        
        index = item_data.find("sellCount")

        if index == -1:
            break
        
        index += len("sellCount") + 2

        left_index_price = item_data.find("onePrice", index) + len("onePrice") + 2
        right_index_price = item_data.find("}", left_index_price)
        buy_price = item_data[left_index_price:right_index_price]

        if item_data[index] != "0": # Takes 1 char of the price to check if it is 0 (no leading zeros)
            return buy_price
        
        item_data = item_data[index:len(item_data)]
        index = 0

    return buy_price

def get_item_icon(id_item: str, connection: pycurl.Curl, save_path: str, cancel_event: Event, attempts: int = 0) -> int:
    """
    Fetch the icon of an item from the Black Desert Market API.
        :param id_item: The ID of the item to fetch the icon for.
        :param connection: The pycurl connection object to use for the request.
        :param save_path: The path where the icon will be saved.
        :param cancel_event: An event to signal cancellation of the operation.
        :param attempts: The number of attempts made to fetch the icon (default is 0).
        :return: 0 on success, -1 on failure.
    """
    if os.path.exists(save_path):
        add_log(f"Icon for ID {id_item} already exists at {save_path}. Skipping download.", "info")
        return 0

    url_icon =  f"https://api.blackdesertmarket.com/item/{id_item}/icon"
    buffer = BytesIO()
    response_code = None

    connection.setopt(connection.URL, url_icon) # type: ignore
    connection.setopt(connection.WRITEDATA, buffer) # type: ignore

    start_time = time.time()
    while response_code != 200 and attempts < max_attempts:
        if cancel_event.is_set():
            return -1
        
        try:
            connection.perform()
            response_code = connection.getinfo(pycurl.HTTP_CODE) # type: ignore
        except Exception as e:
            add_log(f"{e}", "error")
            add_log("Failed to connect to Black Desert Market API. Retrying...", "warning")

        if time.time() - start_time > timeout_connection:
            if attempts < max_attempts:
                add_log(f"Connection timeout reached, retrying... (Attempt {attempts + 1}/{max_attempts})", "warning")
                attempts += 1
            else:
                add_log("Connection timeout reached", "error")
                return -1
    
    content_type = connection.getinfo(pycurl.CONTENT_TYPE) # type: ignore

    if response_code != 200 or not content_type.startswith("image/"): # type: ignore
        add_log(f"Unexpected response for icon {id_item}: HTTP {response_code}, Content-Type: {content_type}", "error")
        return -1
    
    # Save the icon as PNG
    try:
        buffer.seek(0)
        with open(save_path, "wb") as icon_file:
            icon_file.write(buffer.getvalue())
    except Exception as e:
        add_log(f"Error saving icon for ID {id_item}: {e}", "error")

    return 0  # Return 0 on success, -1 on failure

def reduce_item_name_length(item_name: str) -> str:
    """
    Reduce the length of item names to fit in QLabel view.
        :param item_name: The name of the item to reduce.
    """
    if item_name in reduced_item_names:
        return reduced_item_names[item_name]
    return item_name

def get_item_name(id_item: str, connection: pycurl.Curl, cancel_event: Event, region: str = "eu", language: str = "en-US", attempts: int = 0) -> str:
    """
    Connect to the Black Desert Market API to fetch item or elixir name.
        :param id_item: The ID of the item or elixir to fetch.
        :param connection: The pycurl connection object to use for the request.
        :param cancel_event: An event to signal cancellation of the operation.
        :param region: The region for which to fetch the name (default is "eu").
        :param language: The language for which to fetch the name (default is "en-US").
        :param attempts: The number of attempts made to fetch the name (default is 0).
        :return: The name of the item or elixir as a string, or an empty string if the request fails.
    """
    url_base = f"https://api.blackdesertmarket.com/item/{id_item}?region={region}&language={language}"
    buffer = BytesIO()
    response_code = None
    
    connection.setopt(connection.URL, url_base) # type: ignore
    connection.setopt(connection.WRITEDATA, buffer) # type: ignore

    start_time = time.time()
    while response_code != 200:
        if cancel_event.is_set():
            return ""
        
        try:
            connection.perform()
            response_code = connection.getinfo(pycurl.HTTP_CODE) # type: ignore
        except Exception as e:
            add_log(f"{e}", "error")
            add_log("Failed to connect to Black Desert Market API. Retrying...", "warning")

        if time.time() - start_time > timeout_connection:
            if not cancel_event.is_set():
                if attempts < max_attempts:
                    add_log(f"Connection timeout reached, retrying... (Attempt {attempts + 1}/{max_attempts})", "warning")
                    return get_item_name(id_item, connection, cancel_event, region, language, attempts + 1)
                else:
                    add_log("Connection timeout reached", "error")
                    return ""
        
    response_data = buffer.getvalue().decode('utf-8')
    try:
        # Extract the "name" field from the response
        start_index = response_data.find('"name":"') + len('"name":"')
        end_index = response_data.find('"', start_index)
        item_name = response_data[start_index:end_index]
        item_name = reduce_item_name_length(item_name)
        return item_name
    except Exception as e:
        add_log(f"Error extracting item name: {e}", "error")
        return ""

def get_item_data(id_item: str, connection: pycurl.Curl, cancel_event: Event, region: str = "eu") -> str:
    """
    Connect to the Black Desert Market API to fetch item or elixir data.
        :param id_item: The ID of the item or elixir to fetch.
        :param connection: The pycurl connection object to use for the request.
        :param region: The region for which to fetch the data (default is "eu").
        :param cancel_event: An event to signal cancellation of the operation.
        :return: The raw data string containing response information from API, or an empty string if the request fails.
    """
    url_base = f"https://api.blackdesertmarket.com/item/{id_item}/0?region={region}"
    buffer = BytesIO()
    response_code = None
    
    connection.setopt(connection.URL, url_base) # type: ignore
    connection.setopt(connection.WRITEDATA, buffer) # type: ignore

    start_time = time.time()
    while response_code != 200:
        if cancel_event.is_set():
            return ""
        
        try:
            connection.perform()
            response_code = connection.getinfo(pycurl.HTTP_CODE) # type: ignore
        except Exception as e:
            add_log(f"{e}", "error")
            add_log("Failed to connect to Black Desert Market API. Retrying...", "warning")

        if time.time() - start_time > timeout_connection:
            if not cancel_event.is_set():
                add_log("Connection timeout reached", "error")
            return ""

    return buffer.getvalue().decode('utf-8')