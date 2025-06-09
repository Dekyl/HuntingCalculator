import pycurl
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Event

from logic.logs import add_log
from logic.get_data_api_requests import get_item_name, get_item_data, get_item_icon, get_sell_price, get_buy_price

timeout_connection = 1  # Timeout in seconds for the connection to the API
max_threads = 12 # Maximum number of threads to use for concurrent requests

def make_api_requests(item_ids: list[str], elixir_ids: list[str], region: str, language: str = "en-US") -> dict[str, dict[str, tuple[str, int]]] | None:
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
        :return: A dictionary containing two dictionaries: prices of items and costs of elixirs, or None if the API request fails.
    """
    item_prices_ids: dict[str, tuple[str, int] | None] = {}
    for id in item_ids:
        item_prices_ids[id] = None # Initialize with None to handle cases where the item is not found
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

        item_name = get_item_name(id, connection, cancel_event, timeout_connection, region, language)
        if cancel_event.is_set() or not item_name:
            add_log(f"Failed to fetch item name for ID {id}. Skipping...", "error")
            connection.close()
            return -1

        body_sell_price = get_item_data(id, connection, cancel_event, timeout_connection, region)
        if cancel_event.is_set() or not body_sell_price:
            add_log(f"Failed to fetch data for item ID {id}. Skipping...", "error")
            connection.close()
            return -1

        sell_price = get_sell_price(body_sell_price, cancel_event)
        if cancel_event.is_set() or not sell_price:
            add_log(f"Failed to fetch sell price for item ID {id}. Skipping...", "error")
            connection.close()
            return -1
        
        res_get_icon = get_item_icon(id, connection, f"./res/icons/items/{id}.png", cancel_event, timeout_connection)
        if cancel_event.is_set() or res_get_icon == -1:
            add_log(f"Failed to fetch icon for item ID {id}. Skipping...", "error")
            connection.close()
            return -1
        
        connection.close()  # Close the connection after fetching data
        # Ensure thread-safe access to the shared dictionary if the cancel event is not set
        if not cancel_event.is_set():
            with lock_items:
                item_prices_ids[id] = (item_name, int(sell_price))

        return 0  # Return 0 on success, -1 on failure

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(process_item, id): id for id in item_ids}
        for future in as_completed(futures):
            result = future.result()
            if result == -1:
                add_log("Cancelling remaining tasks...", "error")
                cancel_event.set() # Cancel remaining futures
                break

    if any(v is None for v in item_prices_ids.values()):
        return None

    items_log = "Items: {\n"
    for id, value in item_prices_ids.items():
        if value is None:
            return None
        item_name, price = value
        items_log += f"\tItem {id} ({item_name}): Price {price:,}\n"
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

        elixir_name = get_item_name(id, connection, cancel_event, timeout_connection, region, language)
        if cancel_event.is_set() or not elixir_name:
            add_log(f"Failed to fetch elixir name for ID {id}. Skipping...", "error")
            connection.close()
            return -1

        body_buy_price = get_item_data(id, connection, cancel_event, timeout_connection, region)
        if cancel_event.is_set() or not body_buy_price:
            add_log(f"Failed to fetch data for elixir ID {id}. Skipping...", "error")
            connection.close()
            return -1

        elixir_cost = get_buy_price(body_buy_price, cancel_event)
        if cancel_event.is_set() or not elixir_cost:
            add_log(f"Failed to fetch buy price for elixir ID {id}. Skipping...", "error")
            connection.close()
            return -1
        
        res_get_icon = get_item_icon(id, connection, f"./res/icons/elixirs/{id}.png", cancel_event, timeout_connection)
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

    if any(v is None for v in elixir_costs_ids.values()):
        return None

    elixirs_log = "Elixirs: {\n"
    for id, value in elixir_costs_ids.items():
        if value is None:
            return None
        elixir_name, cost = value
        elixirs_log += f"\tElixir {id} ({elixir_name}): Cost {cost:,}\n"
    elixirs_log += "}"
    add_log(elixirs_log, "debug")

    return {
        "items": {k: v for k, v in item_prices_ids.items() if v is not None},
        "elixirs": {k: v for k, v in elixir_costs_ids.items() if v is not None},
    }

def connect_api(item_ids: list[str], elixir_ids: list[str], region: str = "eu", language: str = "en-US") -> dict[str, dict[str, tuple[str, int]]] | None:
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