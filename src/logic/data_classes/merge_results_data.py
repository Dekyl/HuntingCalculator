from dataclasses import dataclass

from config.config import NestedDict, FlatDict

@dataclass
class MergeResultsData:
    data_fetched: NestedDict
    loot_items_cached: FlatDict
    elixirs_cached: FlatDict
    lightstones_cached: FlatDict
    imperfect_lightstones_cached: FlatDict
    black_stone_cost_cached: FlatDict
    loot_items_in_order: dict[str, str]