from PySide6.QtCore import QObject, Signal

from logic.api_connection import connect_api

class DataFetcher(QObject):
    finished = Signal(object) # Signal to emit when data fetching is complete or fails (type of data sent)

    def __init__(self, loot_ids: list[str], elixir_ids: list[str], region: str, language: str):
        """
        Initialize the DataFetcher with the necessary parameters.
            :param loot_ids: List of item IDs to fetch data for.
            :param elixir_ids: List of elixir IDs to fetch data for.
            :param region: The region for which to fetch data.
            :param language: The language for which to fetch data.
        """
        super().__init__()
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
        self.data_retrieved = connect_api(self.loot_ids, self.elixir_ids, self.region, self.language) # type: ignore
        if self.data_retrieved:
            self.finished.emit(self.data_retrieved)
        else:
            self.finished.emit(None)
