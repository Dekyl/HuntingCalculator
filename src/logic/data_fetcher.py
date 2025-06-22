from PySide6.QtCore import QObject, Signal

from logic.api.api_connection import connect_api

class DataFetcher(QObject):
    """
    DataFetcher is a QObject that handles the fetching of data from an API.
    It retrieves data for specified loot and elixir IDs, region, and language.
    It emits a signal when the data fetching is complete or fails.
    """
    finished_retrieving_data = Signal(object) # Signal to emit when data fetching is complete or fails (type of data sent)

    def __init__(self, loot_items: dict[str, str], elixirs: dict[str, str], region: str, lightstones: dict[str, str], imperfect_lightstones: dict[str, str]):
        """
        Initialize the DataFetcher with the necessary parameters.
            :param loot_items: Dictionary of loot item IDs and their names.
            :param elixir: Dictionary of elixir IDs and their names.
            :param region: The region for which to fetch data.
            :param lightstones: Dictionary of lightstone IDs and their names.
            :param imperfect_lightstone: Dictionary of imperfect lightstone IDs and their names.
        """
        super().__init__()
        self.loot_items = loot_items
        self.elixirs = elixirs
        self.region = region
        self.lightstones = lightstones
        self.imperfect_lightstones = imperfect_lightstones

    def run(self):
        """
        Run the data fetching process.
        This method connects to the API and retrieves the data for the specified hunting spot.
        It emits a signal with the results or None if an error occurs.
        """
        self.data_retrieved = connect_api(self.loot_items, self.elixirs, self.lightstones, self.imperfect_lightstones, self.region)
        
        if self.data_retrieved:
            self.finished_retrieving_data.emit(self.data_retrieved)  # Emit the retrieved data and costs
        else:
            self.finished_retrieving_data.emit(None)  # Emit None if data retrieval fails