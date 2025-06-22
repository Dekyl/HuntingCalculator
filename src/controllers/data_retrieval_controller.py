from typing import Callable, Optional
from PySide6.QtCore import QThread, QTimer, Slot, QObject

from gui.dialogs.dialogs_user import show_dialog_type
from logic.calculate_results_session import calculate_elixirs_cost_hour
from logic.logs import add_log
from logic.data_fetcher import DataFetcher
from logic.data_classes.new_session_data import NewSessionData
from logic.manage_resources.access_resources import (
    get_spot_loot,
    get_user_setting,
    get_data_value,
    get_spot_id_icon,
    get_no_market_items,
    get_match_elixirs
)
from logic.sql_items_data.sql_db_connection import check_cached_data, update_cached_data
from logic.sql_items_data.merge_fetched_data import merge_cached_fetched_data
from config.config import (
    market_tax,
    NestedDict,
    reduced_item_names
)

from PySide6.QtCore import QThread, QTimer
from typing import Callable, Optional

class DataRetrievalController(QObject): # Inherits from QObject to use signals and slots (otherwise it would not work)
    """
    Controller for managing data retrieval for hunting sessions.
    This class handles the retrieval of data for a specific hunting spot, manages the worker thread,
    and processes the fetched data to create a new session.
    It is designed as a singleton to ensure that only one instance exists throughout the application.
    """
    instance = None # Singleton instance

    def __init__(
        self,
        show_error_enable_ui: Callable[[str, str, str], None],
        set_ui_enabled: Callable[[bool], None],
        set_session_button_enabled: Callable[[bool], None],
        create_new_session_widget: Callable[[NewSessionData], None]
    ):
        """
        Initialize the DataRetrievalController with necessary parameters.
            :param show_error_enable_ui: Function to show error messages and enable UI.
            :param set_ui_enabled: Function to enable or disable the main UI components.
            :param set_session_button_enabled: Function to enable or disable the session button.
            :param create_new_session_widget: Function to create a new session widget.
            :param on_finished_callback: Optional callback function to execute when data retrieval is finished.
        """
        super().__init__()
        if DataRetrievalController.instance is not None:
            raise Exception("DataRetrievalController is a singleton!")
        DataRetrievalController.instance = self
        add_log("DataRetrievalController initialized.", "info")

        self.show_error_enable_ui = show_error_enable_ui
        self.set_ui_enabled = set_ui_enabled
        self.set_session_button_enabled = set_session_button_enabled
        self.create_new_session_widget = create_new_session_widget

    def start_data_retrieval(self, spot_name: str):
        """
        Start the data retrieval process for the selected hunting spot.
        This method initializes the data fetching process, fetches loot items,
        and sets up the worker thread to handle the data retrieval.
            :param spot_name: The name of the hunting spot for which data is to be fetched.
        """
        add_log(f"Session selected: {spot_name}, retrieving data", "info")
        loot_items = get_spot_loot(spot_name)
        if not loot_items:
            self.show_error_enable_ui(f"Error fetching loot for spot '{spot_name}'.", "Data error", "no_action")
            return

        # Collect required data
        region = get_user_setting("region")
        language = get_user_setting("language")
        extra_profit = get_user_setting("extra_profit")
        value_pack = get_user_setting("value_pack")
        elixirs = get_user_setting("elixirs")
        lightstones = get_data_value("lighstone_items")
        imperfect_lightstones = get_data_value("imperfect_lighstone_items")
        auto_profit = get_user_setting("auto_calculate_best_profit")

        # Validate all
        if not region:
            self.show_error_enable_ui("'Region' setting not found.", "Settings file error", "no_action"); return
        if not language:
            self.show_error_enable_ui("'Language' setting not found.", "Settings file error", "no_action"); return
        if extra_profit is None:
            self.show_error_enable_ui("'Extra profit' setting missing.", "Settings file error", "no_action"); return
        if value_pack is None:
            self.show_error_enable_ui("'Value pack' setting missing.", "Settings file error", "no_action"); return
        if elixirs is None:
            self.show_error_enable_ui("'Elixirs' setting missing.", "Settings file error", "no_action"); return
        if lightstones is None:
            self.show_error_enable_ui("'lighstone_items' missing.", "Data file error", "no_action"); return
        if imperfect_lightstones is None:
            self.show_error_enable_ui("'imperfect_lighstone_items' missing.", "Data file error", "no_action"); return
        if auto_profit is None:
            self.show_error_enable_ui("'Auto profit' setting missing.", "Settings file error", "no_action"); return
        
        self.new_session = NewSessionData(
            spot_name,
            value_pack,
            auto_profit,
            market_tax,
            extra_profit
        )
        self.do_update_cached_data = True # Flag to determine if cached data should be updated

        # Check if any data is outdated
        add_log("Checking for outdated data...", "info")
        outdated_loot_items, self.loot_items_cached = check_cached_data(loot_items)
        outdated_elixirs, self.elixirs_cached = check_cached_data(elixirs)
        outdated_lightstones, self.lightstones_cached = check_cached_data(lightstones)
        outdated_imperfect_lightstones, self.imperfect_lightstones_cached = check_cached_data(imperfect_lightstones)

        if not outdated_loot_items and not outdated_elixirs and not outdated_lightstones and not outdated_imperfect_lightstones:
            add_log("No outdated data found, proceeding with cached data.", "info")
            self.do_update_cached_data = False
            data_fetched: NestedDict = {
                "items": self.loot_items_cached,
                "elixirs": self.elixirs_cached,
                "lightstones": self.lightstones_cached,
                "imperfect_lightstones": self.imperfect_lightstones_cached
            }
            self.on_data_fetched(data_fetched)
            return

        # Setup worker and thread
        self.worker_thread = QThread()
        self.worker = DataFetcher(
            outdated_loot_items,
            outdated_elixirs,
            region,
            outdated_lightstones,
            outdated_imperfect_lightstones
        )

        self.worker.moveToThread(self.worker_thread) # Move the worker to the thread
        self.worker_thread.started.connect(self.worker.run) # Start the worker's run method in the thread
        self.worker.finished_retrieving_data.connect(self.cleanup_worker)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()

    @Slot(object)
    def cleanup_worker(self, data_fetched: Optional[NestedDict]):
        """ 
        Clean up the worker thread after data retrieval is complete.
            :param data_fetched: The data fetched from the API, or None if an error occurred.
        """
        self.worker_thread.quit()
        self.worker.deleteLater()
        self.on_data_fetched(data_fetched) # Call the callback method with the fetched data

    def on_data_fetched(self, data_fetched: Optional[NestedDict]):
        """
        Callback method to handle the data fetched from the worker thread.
            :param data_fetched: The data fetched from the API, or None if an error occurred.
        """
        self.set_ui_enabled(True)
        if data_fetched is None:
            add_log(f"Error retrieving data for spot '{self.new_session.name_spot}'", "error")
            self.set_session_button_enabled(False)
            show_dialog_type(
                "Error fetching data from API, disabling button for 80s.",
                "API timeout",
                "error",
                "no_action"
            )
            QTimer.singleShot(80000, lambda: self.set_session_button_enabled(True))
            return
        
        if self.do_update_cached_data:
            # Update cached data if necessary
            add_log("Updating cached data...", "info")
            update_cached_data(data_fetched)
            # Merge the fetched data with cached data
            add_log("Merging fetched data with cached data...", "info")
            # Merges cached data into fetched data "data_fetched" variable
            merge_cached_fetched_data(data_fetched, self.loot_items_cached, self.elixirs_cached, self.lightstones_cached, self.imperfect_lightstones_cached)

        spot_id_icon = get_spot_id_icon(self.new_session.name_spot)
        if not spot_id_icon:
            show_dialog_type(
                f"Icon for spot '{self.new_session.name_spot}' not found.",
                "JSON error",
                "error",
                "no_action"
            )
            return

        no_market_items = get_no_market_items(self.new_session.name_spot)

        for item_id, (item_name, price) in data_fetched["items"].items():
            if item_name in reduced_item_names:
                # Reduce item name if it exists in the reduced_item_names mapping
                data_fetched["items"][item_id] = (reduced_item_names[item_name], price)

        self.new_session.set_extra_data(
            spot_id_icon,
            no_market_items,
            data_fetched["items"],
            calculate_elixirs_cost_hour(data_fetched["elixirs"]),
            data_fetched["lightstones"],
            data_fetched["imperfect_lightstones"]
        )

        self.create_new_session_widget(self.new_session)

    def handle_get_match_elixirs(self, elixir_name_id: str) -> dict[str, str] | str | None:
        """
        Get the matching elixirs for the given elixir name or elixir ID.
            :param elixir_name_id: The name ID of the elixir to match.
            :return: A dictionary containing the matching elixirs or a message if no matches are found.
        """
        if not elixir_name_id:
            return None
        if elixir_name_id.isspace():
            return "No matches."
        
        matches = get_match_elixirs(elixir_name_id)
        return matches if matches else "No matches."

    @staticmethod
    def get_instance() -> "DataRetrievalController":
        """
        Get the singleton instance of DataRetrievalController.
            :return: The singleton instance of DataRetrievalController.
        """
        if DataRetrievalController.instance is None:
            raise Exception("DataRetrievalController is not initialized.")
        return DataRetrievalController.instance