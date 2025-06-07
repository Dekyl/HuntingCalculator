from PyQt6.QtCore import QObject, pyqtSignal

from logic.api_connection import connect_api

class DataFetcher(QObject):
    finished = pyqtSignal(str, object) # Signal to emit when data fetching is complete or fails (type of data sent)

    def __init__(self, spot_name: str, loot_ids: list[str], elixir_ids: list[str], region: str, language: str):
        """
        Initialize the DataFetcher with the necessary parameters.
            :param spot_name: The name of the hunting spot to fetch data for.
            :param loot_ids: List of item IDs to fetch data for.
            :param elixir_ids: List of elixir IDs to fetch data for.
            :param region: The region for which to fetch data.
            :param language: The language for which to fetch data.
        """
        super().__init__()
        self.spot_name = spot_name
        self.loot_ids = loot_ids
        self.elixir_ids = elixir_ids
        self.region = region
        self.language = language

    def run(self):
        """
        Run the data fetching process.
        This method connects to the API and retrieves the data for the specified hunting spot.
        It emits a signal with the results or None if an error occurs.
        """
        data = connect_api(self.loot_ids, self.elixir_ids, self.region, self.language) # type: ignore
        if data:
            self.finished.emit(self.spot_name, data)
        else:
            self.finished.emit(self.spot_name, None)
