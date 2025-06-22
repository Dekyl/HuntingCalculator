from config.config import NestedDict, FlatDict

def merge_cached_fetched_data(data_fetched: NestedDict, loot_items: FlatDict, elixirs: FlatDict, lightstones: FlatDict, imperfect_lightstones: FlatDict):
    """
    Merge the fetched data with the cached data.
        :param data_fetched: Nested dictionary containing fetched data from the API (we merge into this).
        :param loot_items: Flat dictionary of loot items with their IDs and names.
        :param elixirs: Flat dictionary of elixirs with their IDs and names.
        :param lightstones: Flat dictionary of lightstones with their IDs and names.
        :param imperfect_lightstones: Flat dictionary of imperfect lightstones with their IDs and names.
        :return: None. The function modifies the data_fetched dictionary in place.
    """
    data_fetched["items"] = {**data_fetched["items"], **loot_items}
    data_fetched["elixirs"] = {**data_fetched["elixirs"], **elixirs}
    data_fetched["lightstones"] = {**data_fetched["lightstones"], **lightstones}
    data_fetched["imperfect_lightstones"] = {**data_fetched["imperfect_lightstones"], **imperfect_lightstones}
