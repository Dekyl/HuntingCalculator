from dataclasses import dataclass
from config.config import FlatDict
from typing import Optional

@dataclass
class NewSessionData:
    """
    Data class to hold information for a new hunting session.
    This class is used to store the necessary
    information required to create a new session widget in the application.
    """
    name_spot: str
    value_pack: bool
    auto_calculate_best_profit: bool
    market_tax: float
    extra_profit: bool
    spot_id_icon: str = ""
    no_market_items: Optional[list[str]] = None
    items: Optional[FlatDict] = None
    elixirs_cost: str = ""
    lightstone_costs: Optional[FlatDict] = None
    imperfect_lightstone_costs: Optional[FlatDict] = None

    def set_extra_data(
        self, 
        spot_id_icon: str, 
        no_market_items: list[str], 
        items: FlatDict, 
        elixirs_cost: str, 
        lightstone_costs: FlatDict, 
        imperfect_lightstone_costs: FlatDict
    ):
        """
        Set additional data for the new session.
            :param spot_id_icon: The ID of the icon associated with the hunting spot.
            :param no_market_items: A list of items that are not available on the market.
            :param items: A dictionary containing the prices of items for the hunting spot.
            :param elixirs_cost: The cost of elixirs for the hunting spot.
            :param lightstone_costs: A dictionary containing the costs of lightstones for the hunting spot.
            :param imperfect_lightstone_costs: The costs of the imperfect lightstones for the hunting spot.
        """
        self.spot_id_icon = spot_id_icon
        self.no_market_items = no_market_items
        self.items = items
        self.elixirs_cost = elixirs_cost
        self.lightstone_costs = lightstone_costs
        self.imperfect_lightstone_costs = imperfect_lightstone_costs
