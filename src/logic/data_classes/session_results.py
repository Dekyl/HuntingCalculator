from dataclasses import dataclass
from config.config import FlatDict, FlatDictStr

@dataclass
class SessionResultsData:
    """
    Data class to hold the results of a hunting session.
    This class is used to store the necessary information required to display the results of a session.
    """
    name_spot: str
    value_pack: bool
    market_tax: float
    extra_profit: bool
    data_input: FlatDictStr
    elixirs_cost: str
    auto_calculate_best_profit: bool
    lightstone_costs: FlatDict
    imperfect_lightstone_costs: FlatDict
    black_stone_cost: FlatDict