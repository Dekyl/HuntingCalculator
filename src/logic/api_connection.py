import pycurl, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Event
from io import BytesIO

from logic.logs import add_log

timeout_connection = 5  # Timeout in seconds for the connection to the API
max_threads = 12 # Maximum number of threads to use for concurrent requests

def get_sell_price(item_data:str, cancel_event: Event) -> str:
    """
    Fetch selling price of an item from the provided data.
        :param item_data: The raw data string containing response information from API.
        :type item_data: str
        :param cancel_event: An event to signal cancellation of the operation.
        :type cancel_event: Event
        :return: The selling price of the item as a string.
        :rtype: str
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

        if item_data[index] != "0":
            return last_sell_val
        
        item_data = item_data[index:len(item_data)]
        index = 0

    return last_sell_val

def get_buy_price(elixir_data:str, cancel_event: Event) -> str:
    """
    Fetch buying price of an elixir from the provided data.
        :param elixir_data: The raw data string containing response information from API.
        :type elixir_data: str
        :param cancel_event: An event to signal cancellation of the operation.
        :type cancel_event: Event
        :return: The buying price of the elixir as a string.
        :rtype: str
    """
    elixir_data = elixir_data[0:elixir_data.find("history")]
    index = 0
    buy_price = "0"

    while index < len(elixir_data):
        if cancel_event.is_set():  # Check if the cancel event is set before proceeding
            return ""
        
        index = elixir_data.find("buyCount")

        if index == -1:
            break
        
        index += len("buyCount") + 2

        left_index_price = elixir_data.find("onePrice", index) + len("onePrice") + 2
        right_index_price = elixir_data.find("}", left_index_price)
        buy_price = elixir_data[left_index_price:right_index_price]

        if elixir_data[index] != "0":
            return buy_price
        
        elixir_data = elixir_data[index:len(elixir_data)]
        index = 0

    return buy_price

def get_item_icon(id_item: str, connection: pycurl.Curl, save_path: str, cancel_event: Event) -> int:
    """
    Fetch the icon of an item from the Black Desert Market API.
        :param id_item: The ID of the item to fetch the icon for.
        :type id_item: str
        :param connection: The pycurl connection object to use for the request.
        :param save_path: The path where the icon will be saved.
        :type save_path: str
        :type connection: pycurl.Curl
        :param cancel_event: An event to signal cancellation of the operation.
        :type cancel_event: Event
        :return: 0 on success, -1 on failure.
    """
    url_icon =  f"https://api.blackdesertmarket.com/item/{id_item}/icon"
    buffer = BytesIO()
    response_code = None

    connection.setopt(connection.URL, url_icon) # type: ignore
    connection.setopt(connection.WRITEDATA, buffer) # type: ignore

    start_time = time.time()
    while response_code != 200:
        if cancel_event.is_set():
            return -1
        
        try:
            connection.perform()
            response_code = connection.getinfo(pycurl.HTTP_CODE) # type: ignore
        except Exception as e:
            add_log(f"{e}", "error")
            add_log("Failed to connect to Black Desert Market API. Retrying...", "warning")

        if time.time() - start_time > timeout_connection:
            if not cancel_event.is_set():
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

def get_item_name(id_item: str, connection: pycurl.Curl, cancel_event: Event, region: str = "eu", language: str = "en-US") -> str:
    """
    Connect to the Black Desert Market API to fetch item or elixir name.
        :param id_item: The ID of the item or elixir to fetch.
        :type id_item: str
        :param connection: The pycurl connection object to use for the request.
        :type connection: pycurl.Curl
        :param region: The region for which to fetch the data (default is "eu").
        :type region: str
        :param language: The language for which to fetch the data (default is "en-US").
        :type language: str
        :param cancel_event: An event to signal cancellation of the operation.
        :type cancel_event: Event
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
                add_log("Connection timeout reached", "error")
            return ""
        
    response_data = buffer.getvalue().decode('utf-8')
    try:
        # Extract the "name" field from the response
        start_index = response_data.find('"name":"') + len('"name":"')
        end_index = response_data.find('"', start_index)
        item_name = response_data[start_index:end_index]
        return item_name
    except Exception as e:
        add_log(f"Error extracting item name: {e}", "error")
        return ""

def get_item_data(id_item: str, connection: pycurl.Curl, cancel_event: Event, region: str = "eu") -> str:
    """
    Connect to the Black Desert Market API to fetch item or elixir data.
        :param id_item: The ID of the item or elixir to fetch.
        :type id_item: str
        :param connection: The pycurl connection object to use for the request.
        :type connection: pycurl.Curl
        :param region: The region for which to fetch the data (default is "eu").
        :type region: str
        :param cancel_event: An event to signal cancellation of the operation.
        :type cancel_event: Event
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

def make_api_requests(item_ids: list[str], elixir_ids: list[str], region: str, language: str = "en-US") -> dict[str, list[tuple[str, int]]] | None:
    """
    Make API requests to fetch prices of items and elixirs from the Black Desert Market API.
        :param item_ids: List of item IDs to fetch prices for.
        :type item_ids: list[str]
        :param elixir_ids: List of elixir IDs to fetch prices for.
        :type elixir_ids: list[str]
        :param region: The region for which to fetch the data (default is "eu").
        :type region: str
        :param language: The language for which to fetch the data (default is "en-US").
        :type language: str
        :return: A dictionary containing two lists: prices of items and costs of elixirs, or None if the API request fails.
    """
    prices_ids: dict[str, tuple[str, int] | None] = {}
    for id in item_ids:
        prices_ids[id] = None # Initialize with None to handle cases where the item is not found
    elixir_costs_ids: dict[str, tuple[str, int] | None] = {}
    for id in elixir_ids:
        elixir_costs_ids[id] = None # Initialize with None to handle cases where the elixir is not found
    lock_items = Lock()  # Lock to ensure thread-safe access to items
    lock_elixirs = Lock()  # Lock to ensure thread-safe access to elixirs

    add_log("Connecting to Black Desert Market API to get prices...", "info")

    cancel_event = Event()
    def process_item(id: str) -> int:
        if cancel_event.is_set(): # Check if the cancel event is set before proceeding
            return -1
    
        connection = pycurl.Curl()
        headers: list[str] = ['accept: */*']
        connection.setopt(connection.HTTPHEADER, headers) # type: ignore
        connection.setopt(connection.CONNECTTIMEOUT, 1) # type: ignore

        item_name = get_item_name(id, connection, cancel_event, region, language)
        if cancel_event.is_set() or not item_name:
            add_log(f"Failed to fetch item name for ID {id}. Skipping...", "error")
            connection.close()
            return -1

        body_sell_price = get_item_data(id, connection, cancel_event, region)
        if cancel_event.is_set() or not body_sell_price:
            add_log(f"Failed to fetch data for item ID {id}. Skipping...", "error")
            connection.close()
            return -1

        sell_price = get_sell_price(body_sell_price, cancel_event)
        if cancel_event.is_set() or not sell_price:
            add_log(f"Failed to fetch sell price for item ID {id}. Skipping...", "error")
            connection.close()
            return -1
        
        res_get_icon = get_item_icon(id, connection, f"./res/icons/items/{id}.png", cancel_event)
        if cancel_event.is_set() or res_get_icon == -1:
            add_log(f"Failed to fetch icon for item ID {id}. Skipping...", "error")
            connection.close()
            return -1
        
        connection.close()  # Close the connection after fetching data
        # Ensure thread-safe access to the shared dictionary if the cancel event is not set
        if not cancel_event.is_set():
            with lock_items:
                prices_ids[id] = (item_name, int(sell_price))

        return 0  # Return 0 on success, -1 on failure

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(process_item, id): id for id in item_ids}
        for future in as_completed(futures):
            result = future.result()
            if result == -1:
                add_log("Cancelling remaining tasks...", "error")
                cancel_event.set() # Cancel remaining futures
                break

    if any(v is None for v in prices_ids.values()):
        return None
    prices = [v for v in prices_ids.values() if v is not None]

    items_log = "Items: {\n"
    for item_name, price in prices:
        items_log += f"\tItem Name {item_name}: Price {price:,}\n"
    items_log += "}"
    add_log(items_log, "debug")

    cancel_event = Event()
    def process_elixir(id: str) -> int:
        if cancel_event.is_set(): # Check if the cancel event is set before proceeding
            return -1
        
        connection = pycurl.Curl()
        headers: list[str] = ['accept: */*']
        connection.setopt(connection.HTTPHEADER, headers) # type: ignore
        connection.setopt(connection.CONNECTTIMEOUT, 1) # type: ignore

        elixir_name = get_item_name(id, connection, cancel_event, region, language)
        if cancel_event.is_set() or not elixir_name:
            add_log(f"Failed to fetch elixir name for ID {id}. Skipping...", "error")
            connection.close()
            return -1

        body_buy_price = get_item_data(id, connection, cancel_event, region)
        if cancel_event.is_set() or not body_buy_price:
            add_log(f"Failed to fetch data for elixir ID {id}. Skipping...", "error")
            connection.close()
            return -1

        elixir_cost = get_buy_price(body_buy_price, cancel_event)
        if cancel_event.is_set() or not elixir_cost:
            add_log(f"Failed to fetch buy price for elixir ID {id}. Skipping...", "error")
            connection.close()
            return -1
        
        res_get_icon = get_item_icon(id, connection, f"./res/icons/elixirs/{id}.png", cancel_event)
        if cancel_event.is_set() or res_get_icon == -1:
            add_log(f"Failed to fetch icon for elixir ID {id}. Skipping...", "error")
            connection.close()
            return -1
        
        connection.close()  # Close the connection after fetching data
        if not cancel_event.is_set():
            with lock_elixirs:
                elixir_costs_ids[id] = (elixir_name, int(elixir_cost))

        return 0  # Return 0 on success, -1 on failure

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(process_elixir, id): id for id in elixir_ids}
        for future in as_completed(futures):
            result = future.result()
            if result == -1:
                add_log("Cancelling remaining tasks...", "error")
                cancel_event.set() # Cancel remaining futures
                break

    if any(v is None for v in prices_ids.values()):
        return None
    elixir_costs = [v for v in elixir_costs_ids.values() if v is not None]

    elixirs_log = "Elixirs: {\n"
    for elixir_name, cost in elixir_costs:
        elixirs_log += f"\tElixir Name {elixir_name}: Cost {cost:,}\n"
    elixirs_log += "}"
    add_log(elixirs_log, "debug")

    return {"prices": prices, "elixir_costs": elixir_costs}

def connect_api(item_ids: list[str], elixir_ids: list[str], region: str = "eu", language: str = "en-US") -> dict[str, list[tuple[str, int]]] | None:
    """
    Search for the current prices of items and elixirs from the Black Desert Market API and save them in a JSON file.
        :param item_ids: List of item IDs to fetch prices for.
        :type item_ids: list[str]
        :param elixir_ids: List of elixir IDs to fetch prices for.
        :type elixirs_ids: list[str]
        :param region: The region for which to fetch the data (default is "eu").
        :type region: str
        :param language: The language for which to fetch the data (default is "en-US").
        :type language: str
        :return: A dictionary containing two dictionaries: prices of items and costs of elixirs, or None if the API request fails.
    """
    data_retrieved = make_api_requests(item_ids, elixir_ids, region, language)
    if not data_retrieved:
        add_log("Failed to update prices from the Black Desert Market API.", "error")
        return None
    return data_retrieved