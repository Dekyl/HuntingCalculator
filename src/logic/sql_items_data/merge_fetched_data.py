from config.config import NestedDict, FlatDict

def merge_cached_fetched_data(data_fetched: NestedDict, loot_items: FlatDict, elixirs: FlatDict, lightstones: FlatDict, imperfect_lightstones: FlatDict, loot_items_in_order: dict[str, str]):
    """
    Merge the fetched data with the cached data.
        :param data_fetched: Nested dictionary containing fetched data from the API (we merge into this).
        :param loot_items: Flat dictionary of loot cached items with their IDs, names and prices.
        :param elixirs: Flat dictionary of cached elixirs with their IDs, names and prices.
        :param lightstones: Flat dictionary of cached lightstones with their IDs, names and prices.
        :param imperfect_lightstones: Flat dictionary of cached imperfect lightstones with their IDs, names and prices.
        :param loot_items_in_order: Dictionary of loot items in order with their IDs and names (needed to merge data in order).
        :return: None. The function modifies the data_fetched dictionary in place.
    """
    items_in_order = {}
    for item_id, _ in loot_items_in_order.items():
        if item_id in data_fetched["items"]:
            items_in_order[item_id] = data_fetched["items"][item_id]
        else:
            items_in_order[item_id] = loot_items[item_id]

    data_fetched["items"] = items_in_order
    data_fetched["elixirs"] = {**data_fetched["elixirs"], **elixirs}
    data_fetched["lightstones"] = {**data_fetched["lightstones"], **lightstones}
    data_fetched["imperfect_lightstones"] = {**data_fetched["imperfect_lightstones"], **imperfect_lightstones}
