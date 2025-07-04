from PySide6.QtCore import QObject, Signal

from logic.api.api_connection import connect_api

class DataFetcher(QObject):
    """
    DataFetcher is a QObject that handles the fetching of data from an API.
    It fetches data for specified loot and elixir IDs, region, and language.
    It emits a signal when the data fetching is complete or half complete.
    """
    finished_retrieving_data = Signal(object) # Signal to emit when data fetching is complete or fails (type of data sent)

    def __init__(self, loot_items: dict[str, str], elixirs: dict[str, str], region: str, lightstones: dict[str, str], imperfect_lightstones: dict[str, str], black_stone_cost: dict[str, str]):
        """
        Initialize the DataFetcher with the necessary parameters.
            :param loot_items: Dictionary of loot item IDs and their names.
            :param elixir: Dictionary of elixir IDs and their names.
            :param region: The region for which to fetch data.
            :param lightstones: Dictionary of lightstone IDs and their names.
            :param imperfect_lightstone: Dictionary of imperfect lightstone IDs and their names.
            :param black_stone_cost: Dictionary of black stone costs with IDs and names.
        """
        super().__init__()
        self.loot_items = loot_items
        self.elixirs = elixirs
        self.region = region
        self.lightstones = lightstones
        self.imperfect_lightstones = imperfect_lightstones
        self.black_stone_cost = black_stone_cost

    def run(self):
        """
        Run the data fetching process.
        This method connects to the API and fetches the data for the specified hunting spot.
        It emits a signal with the results.
        """
        self.data_fetched = connect_api(self.loot_items, self.elixirs, self.lightstones, self.imperfect_lightstones, self.black_stone_cost, self.region)
        self.finished_retrieving_data.emit(self.data_fetched)  # Emit the fetched data and costs