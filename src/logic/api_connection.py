import pycurl
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Event

from logic.logs import add_log
from logic.get_data_api_requests import (
    get_item_name, get_item_data, get_item_icon, get_sell_price, get_buy_price
)
from config.config import max_threads, item_icons_root

def make_api_requests_items(item_ids: list[str], region: str, language: str = "en-US") -> dict[str, tuple[str, int]] | None:
    """
    Make API requests to fetch item prices from the Black Desert Market API.
        :param item_ids: List of item IDs to fetch prices for.
        :type item_ids: list[str]
        :param region: The region for which to fetch the data (default is "eu").
        :type region: str
        :param language: The language for which to fetch the data (default is "en-US").
        :type language: str
        :return: A dictionary containing item prices, or None if the API request fails.
    """
    item_prices_ids: dict[str, tuple[str, int] | None] = {}
    for id in item_ids:
        item_prices_ids[id] = None # Initialize with None to handle cases where the item is not found
    lock_items = Lock()  # Lock to ensure thread-safe access to items

    add_log("Connecting to Black Desert Market API to get item prices...", "info")

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
        
        res_get_icon = get_item_icon(id, connection, f"{item_icons_root}{id}.png", cancel_event, 0)
        if cancel_event.is_set() or res_get_icon == -1:
            add_log(f"Failed to fetch icon for item ID {id}. Skipping...", "error")
            connection.close()
            return -1
        
        connection.close()  # Close the connection after fetching data
        # Ensure thread-safe access to the shared dictionary if the cancel event is not set
        if not cancel_event.is_set():
            with lock_items:
                item_prices_ids[id] = (item_name, int(sell_price)) # id, item_name, sell_price

        return 0  # Return 0 on success, -1 on failure

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(process_item, id): id for id in item_ids}
        for future in as_completed(futures):
            result = future.result()
            if result == -1:
                add_log("Cancelling remaining tasks...", "error")
                cancel_event.set() # Cancel remaining futures
                break

    item_prices_ids_final: dict[str, tuple[str, int]] = {}
    items_log = "Items: {\n"
    for id, value in item_prices_ids.items():
        if value is None:
            add_log(f"Failed to fetch data for item ID {id}. Returning...", "error")
            return None
        item_name, price = value
        items_log += f"\tItem {id} ({item_name}): Price {price:,}\n"
        item_prices_ids_final[id] = (item_name, price)
    items_log += "}"
    add_log(items_log, "debug")

    return item_prices_ids_final

def make_api_requests_elixirs(elixir_ids: list[str], region: str, language: str = "en-US") -> dict[str, tuple[str, int]] | None:
    """
    Make API requests to fetch costs of elixirs from the Black Desert Market API.
        :param elixir_ids: List of elixir IDs to fetch costs for.
        :type elixir_ids: list[str]
        :param region: The region for which to fetch the data (default is "eu").
        :type region: str
        :param language: The language for which to fetch the data (default is "en-US").
        :type language: str
        :return: A dictionary containing elixir costs, or None if the API request fails.
    """
    elixir_costs_ids: dict[str, tuple[str, int] | None] = {}
    for id in elixir_ids:
        elixir_costs_ids[id] = None # Initialize with None to handle cases where the elixir is not found
    lock_elixirs = Lock()  # Lock to ensure thread-safe access to elixirs

    add_log("Connecting to Black Desert Market API to get elixir costs...", "info")

    cancel_event = Event()
    def process_elixir(id: str) -> int:
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
        
        connection.close()  # Close the connection after fetching data
        if not cancel_event.is_set():
            with lock_elixirs:
                elixir_costs_ids[id] = (item_name, int(elixir_cost))

        return 0  # Return 0 on success, -1 on failure
    
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(process_elixir, id): id for id in elixir_ids}
        for future in as_completed(futures):
            result = future.result()
            if result == -1:
                add_log("Cancelling remaining tasks...", "error")
                cancel_event.set() # Cancel remaining futures
                break

    elixir_costs_ids_final: dict[str, tuple[str, int]] = {}
    elixirs_log = "Elixirs: {\n"
    for id, value in elixir_costs_ids.items():
        if value is None:
            add_log(f"Failed to fetch cost for elixir ID {id}. Returning...", "error")
            return None
        item_name, cost = value
        elixirs_log += f"\tElixir {id}: (Name: {item_name}, Cost {cost:,})\n"
        elixir_costs_ids_final[id] = (item_name, cost)
    elixirs_log += "}"
    add_log(elixirs_log, "debug")

    return elixir_costs_ids_final

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
    items_retrieved = make_api_requests_items(item_ids, region, language)
    if items_retrieved is None:
        add_log("Failed to retrieve data from the Black Desert Market API for items.", "error")
        return None
    elixirs_retrieved = make_api_requests_elixirs(elixir_ids, region, language)
    if elixirs_retrieved is None:
        add_log("Failed to retrieve cost and name from the Black Desert Market API for elixirs.", "error")
        return None

    return {
        "items": {k: v for k, v in items_retrieved.items()},
        "elixirs": {k: v for k, v in elixirs_retrieved.items()},
    }