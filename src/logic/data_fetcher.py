from PyQt6.QtCore import QObject, pyqtSignal

from logic.api_connection import connect_api

class DataFetcher(QObject):
    finished = pyqtSignal(str, object) # Signal to emit when data fetching is complete or fails (type of data sent)

    def __init__(self, spot_name: str, loot_ids: list[str], elixir_ids: list[str], region: str, language: str):
        super().__init__()
        self.spot_name = spot_name
        self.loot_ids = loot_ids
        self.elixir_ids = elixir_ids
        self.region = region
        self.language = language

    def run(self):
        data = connect_api(self.loot_ids, self.elixir_ids, self.region, self.language) # type: ignore
        if data:
            self.finished.emit(self.spot_name, data)
        else:
            self.finished.emit(self.spot_name, None)
