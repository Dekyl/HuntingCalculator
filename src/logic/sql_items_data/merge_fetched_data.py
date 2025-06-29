from logic.data_classes.merge_results_data import MergeResultsData

def merge_cached_fetched_data(merge_results_data: MergeResultsData):
    """
    Merge the fetched data with the cached data.
        :param merge_results_data: An instance of MergeResultsData containing the fetched and cached data.
    """
    items_in_order = {}
    for item_id, _ in merge_results_data.loot_items_in_order.items():
        if item_id in merge_results_data.data_fetched["items"]:
            items_in_order[item_id] = merge_results_data.data_fetched["items"][item_id]
        else:
            items_in_order[item_id] = merge_results_data.loot_items_cached[item_id]

    merge_results_data.data_fetched["items"] = items_in_order
    merge_results_data.data_fetched["elixirs"] = {**merge_results_data.data_fetched["elixirs"], **merge_results_data.elixirs_cached}
    merge_results_data.data_fetched["lightstones"] = {**merge_results_data.data_fetched["lightstones"], **merge_results_data.lightstones_cached}
    merge_results_data.data_fetched["imperfect_lightstones"] = {**merge_results_data.data_fetched["imperfect_lightstones"], **merge_results_data.imperfect_lightstones_cached}
    merge_results_data.data_fetched["black_stone_buy"] = {**merge_results_data.data_fetched["black_stone_buy"], **merge_results_data.black_stone_buy_cached}
    merge_results_data.data_fetched["black_stone_sell"] = {**merge_results_data.data_fetched["black_stone_sell"], **merge_results_data.black_stone_sell_cached}
