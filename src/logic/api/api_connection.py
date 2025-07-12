from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock, Event

from logic.logs import add_log
from logic.api.get_data_api_requests import ApiRequest
from config.config import (
    max_threads, 
    NestedDict, 
    FlatDict
)

def connect_api(item_ids: dict[str, str], elixir_ids: dict[str, str], lightstone_ids: dict[str, str], imperfect_lightstone_ids: dict[str, str], black_stone_cost: dict[str, str], region: str = "eu") -> tuple[bool, NestedDict]:
    """
    Search for the current prices of items and elixirs from the Black Desert Market API and save them in a JSON file.
        :param item_ids: Dictionary of item IDs and their names to fetch prices for.
        :param elixir_ids: Dictionary of elixir IDs and their names to fetch costs for.
        :param lightstone_ids: Dictionary of lightstone IDs to fetch costs for.
        :param imperfect_lightstone_ids: Dictionary of imperfect lightstone IDs to fetch costs for.
        :param black_stone_cost: Dictionary of black stone costs IDs to fetch costs for.
        :param region: The region for which to fetch the data.
        :return: A tuple containing a boolean indicating half requests done, and a nested dictionary with the fetched data until the moment it failed (if did).
    """

    data_types: list[tuple[str, dict[str, str], str]] = [
        ("items", item_ids, "Items"),
        ("elixirs", elixir_ids, "Elixirs"),
        ("lightstones", lightstone_ids, "Lightstones"),
        ("imperfect_lightstones", imperfect_lightstone_ids, "Imp-Lightstones"),
        ("black_stone_cost", black_stone_cost, "Black-Stone-Cost"),
    ]

    results: NestedDict = {"items": {}, "elixirs": {}, "lightstones": {}, "imperfect_lightstones": {}, "black_stone_cost": {}} # Initialize results dictionary
    for key, ids, label in data_types:
        if not ids:
            add_log(f"No {label} to fetch. Skipping...", "info")
            results[key] = {}
            continue
        all_fetched, data_fetched = make_api_requests(ids, region, label)
        results[key] = data_fetched
        if not all_fetched:
            add_log(f"Failed to fetch all data for {label}.", "error")
            return (False, results)  # Return partial results if any request fails

    return (True, results)

def make_api_requests(ids: dict[str, str], region: str, item_type: str = "Items") -> tuple[bool, FlatDict]:
    """
    Make API requests to fetch prices from the Black Desert Market API.
        :param ids: Dictionary of IDs and their names to fetch prices for.
        :param region: The region for which to fetch the data.
        :param item_type: Type of items to fetch prices for (e.g., "Items", "Elixirs").
        :return: A tuple containing a boolean indicating if all requests were successful, and a flat dictionary with the fetched prices.
    """
    prices_ids: dict[str, int] = {id: -1 for id in ids} # Initialize with None to handle cases where the item is not found
    lock = Lock()  # Lock to ensure thread-safe access

    add_log(f"Connecting to Black Desert Market API to get '{item_type}' prices...", "info")

    cancel_event = Event()
    def process_item(id: str) -> int:
        """
        Process a single item ID to fetch its price from the API.
            :param id: The ID of the item to fetch.
            :return: 0 on success, -1 on failure.
        """
        add_log(f"Processing {item_type} ID {id}...", "debug")
        if cancel_event.is_set(): # Check if the cancel event is set before proceeding
            return -1
        
        api_request = ApiRequest(id, item_type, cancel_event, region)
        price = api_request.get_price() # Fetch the price using the ApiRequest class

        if not price: # Check if the cancel event is set or if the price is empty
            add_log(f"Failed to fetch price for {item_type} ID {id}. Skipping...", "warning")
            return -1
        if cancel_event.is_set():
            add_log(f"Cancellation event set while fetching {item_type} ID {id}. Stopping further processing...", "warning")
            return -1
            
        # Ensure thread-safe access to the shared dictionary if the cancel event is not set
        if not cancel_event.is_set():
            with lock:
                price_int = int(price) if price.isdigit() else -1 # Convert price to int, handle non-digit cases
                prices_ids[id] = price_int # id, sell_price
                add_log(f"Fetched {item_type} ID {id} with price {price_int:,}", "debug")

        return 0  # Return 0 on success, -1 on failure

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {executor.submit(process_item, id): id for id in ids}
        for future in as_completed(futures):
            result = future.result()
            if result == -1:
                add_log("Cancelling remaining tasks...", "warning")
                cancel_event.set() # Cancel remaining futures
                break

    prices_final: FlatDict = {}
    items_log = f"{item_type}: {{\n"
    for id, price in prices_ids.items():
        if price == -1: # If the price is -1, it means that an error occurred while fetching data for this ID
            add_log(f"Failed to fetch data for ID {id}. Returning...", "warning")
            return (False, prices_final)
        name = ids[id]
        prices_final[id] = (name, price) # id, (name, price)
        items_log += f"\tID {id} ({name}): Price {price:,}\n"
    items_log += "}"
    
    add_log(items_log, "debug")
    return (True, prices_final)