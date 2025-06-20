from PySide6.QtCore import QObject, Signal

from logic.api.api_connection import connect_api

class DataFetcher(QObject):
    """
    DataFetcher is a QObject that handles the fetching of data from an API.
    It retrieves data for specified loot and elixir IDs, region, and language.
    It emits a signal when the data fetching is complete or fails.
    """
    finished = Signal(object, object, object) # Signal to emit when data fetching is complete or fails (type of data sent)

    def __init__(self, loot_ids: list[str], elixir_ids: list[str], region: str, language: str, lightstones_ids: list[str], imperfect_lightstone_ids: list[str]):
        """
        Initialize the DataFetcher with the necessary parameters.
            :param loot_ids: List of item IDs to fetch data for.
            :param elixir_ids: List of elixir IDs to fetch data for.
            :param region: The region for which to fetch data.
            :param language: The language for which to fetch data.
            :param lightstones_ids: List of lightstone IDs.
            :param imperfect_lightstone_ids: List of imperfect lightstone IDs.
        """
        super().__init__()
        self.loot_ids = loot_ids
        self.elixir_ids = elixir_ids
        self.region = region
        self.language = language
        self.lightstones_ids = lightstones_ids
        self.imperfect_lightstone_ids = imperfect_lightstone_ids

    def run(self):
        """
        Run the data fetching process.
        This method connects to the API and retrieves the data for the specified hunting spot.
        It emits a signal with the results or None if an error occurs.
        """
        self.data_retrieved, self.lightstone_costs, self.imperfect_lightstone_costs = connect_api(self.loot_ids, self.elixir_ids, self.lightstones_ids, self.imperfect_lightstone_ids, self.region, self.language)
        
        if self.data_retrieved and self.lightstone_costs and self.imperfect_lightstone_costs:
            self.finished.emit(self.data_retrieved, self.lightstone_costs, self.imperfect_lightstone_costs)  # Emit the retrieved data and costs
        else:
            self.finished.emit(None, None, None)  # Emit None if data retrieval fails