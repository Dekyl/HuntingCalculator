from typing import Callable, Optional

from PySide6.QtCore import QThread, QTimer, QObject

from gui.dialogs.dialogs_user import show_dialog_type
from logic.results_session.calculate_results_session import calculate_elixirs_cost_hour
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
from config.config import (
    market_tax,
    NestedDict
)

from PySide6.QtCore import QThread, QTimer
from typing import Callable, Optional

class DataRetrievalController(QObject):
    """
    Controller for managing the data retrieval process for hunting spots.
    This class handles the initialization of data fetching, validation of settings,
    and the creation of new session widgets based on the retrieved data.
    """

    def __init__(
        self,
        spot_name: str,
        show_error_enable_ui: Callable[[str, str, str], None],
        set_ui_enabled: Callable[[bool], None],
        set_session_button_enabled: Callable[[bool], None],
        create_new_session_widget: Callable[[NewSessionData], None],
        on_finished_callback: Callable[[], None]
    ):
        """
        Initialize the DataRetrievalController with necessary parameters.
            :param spot_name: The name of the hunting spot for which data is being retrieved.
            :param show_error_enable_ui: Function to show error messages and enable UI.
            :param set_ui_enabled: Function to enable or disable the main UI components.
            :param set_session_button_enabled: Function to enable or disable the session button.
            :param create_new_session_widget: Function to create a new session widget.
            :param on_finished_callback: Optional callback function to execute when data retrieval is finished.
        """
        super().__init__()
        self.spot_name = spot_name
        self.show_error_enable_ui = show_error_enable_ui
        self.set_ui_enabled = set_ui_enabled
        self.set_session_button_enabled = set_session_button_enabled
        self.create_new_session_widget = create_new_session_widget
        self.on_finished_callback = on_finished_callback

    def start(self):
        """
        Start the data retrieval process for the selected hunting spot.
        This method initializes the data fetching process, retrieves loot items,
        and sets up the worker thread to handle the data retrieval.
        """
        add_log(f"Session selected: {self.spot_name}, retrieving data", "info")
        loot_items = get_spot_loot(self.spot_name)
        if not loot_items:
            self.show_error_enable_ui(f"Error fetching loot for spot '{self.spot_name}'.", "Data error", "no_action")
            return

        # Collect required data
        region = get_user_setting("region")
        language = get_user_setting("language")
        extra_profit = get_user_setting("extra_profit")
        value_pack = get_user_setting("value_pack")
        elixirs = get_user_setting("elixirs")
        lightstones = get_data_value("lighstone_items")
        imperfect_lightstones = get_data_value("imperfect_lighstone_items")

        # Validate all
        if not region:
            self.show_error_enable_ui("Region setting not found.", "Settings file error", "no_action"); return
        if not language:
            self.show_error_enable_ui("Language setting not found.", "Settings file error", "no_action"); return
        if extra_profit is None:
            self.show_error_enable_ui("Extra profit setting missing.", "Settings file error", "no_action"); return
        if value_pack is None:
            self.show_error_enable_ui("Value pack setting missing.", "Settings file error", "no_action"); return
        if elixirs is None:
            self.show_error_enable_ui("Elixirs setting missing.", "Settings file error", "no_action"); return
        if lightstones is None:
            self.show_error_enable_ui("'lighstone_items' missing.", "Data file error", "no_action"); return
        if imperfect_lightstones is None:
            self.show_error_enable_ui("'imperfect_lighstone_items' missing.", "Data file error", "no_action"); return

        auto_profit = get_user_setting("auto_calculate_best_profit")

        self.new_session = NewSessionData(
            self.spot_name,
            value_pack,
            auto_profit,
            market_tax,
            extra_profit
        )

        # Setup worker and thread
        self.worker_thread = QThread()
        self.worker = DataFetcher(
            loot_items,
            elixirs,
            region,
            lightstones,
            imperfect_lightstones
        )

        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.handle_finished)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.finished.connect(self.cleanup_reference)

        self.worker_thread.start()

    def cleanup_reference(self):
        """
        Clean up references after the worker thread has finished.
        This method is called to ensure that the worker thread and its resources are properly cleaned up.
        """
        self.on_finished_callback()

    def handle_finished(self, data: NestedDict):
        """
        Handle the completion of the data retrieval process.
            :param data: The data retrieved from the worker thread, or None if an error occurred.
        """
        self.on_data_retrieved(self.new_session, data)

    def on_data_retrieved(self, new_session: NewSessionData, data_retrieved: Optional[NestedDict]):
        """
        Callback method to handle the data retrieved from the worker thread.
            :param new_session: The NewSessionData instance containing the session details.
            :param data_retrieved: The data retrieved from the API, or None if an error occurred.
        """
        self.set_ui_enabled(True)

        if data_retrieved is None:
            add_log(f"Error retrieving data for spot '{new_session.name_spot}'", "error")
            self.set_session_button_enabled(False)
            show_dialog_type(
                "Error fetching data from API, disabling button for 80s.",
                "API timeout",
                "error",
                "no_action"
            )
            QTimer.singleShot(80000, lambda: self.set_session_button_enabled(True))
            return

        spot_id_icon = get_spot_id_icon(new_session.name_spot)
        if not spot_id_icon:
            show_dialog_type(
                f"Icon for spot '{new_session.name_spot}' not found.",
                "JSON error",
                "error",
                "no_action"
            )
            return

        no_market_items = get_no_market_items(new_session.name_spot)

        new_session.set_extra_data(
            spot_id_icon,
            no_market_items,
            data_retrieved["items"],
            calculate_elixirs_cost_hour(data_retrieved["elixirs"]),
            data_retrieved["lightstones"],
            data_retrieved["imperfect_lightstones"]
        )

        self.create_new_session_widget(new_session)

def get_match_elixirs_subctrler(elixir_name_id: str) -> dict[str, str] | str | None:
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