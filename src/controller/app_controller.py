from PySide6.QtCore import QThread, QTimer

from typing import Any

from logic.manage_excels import clean_sessions, save_session
from logic.logs import add_log
from logic.exchange_calculator import exchange_results
from logic.access_resources import (
    update_confirm_dialog, 
    get_show_confirm_clean, 
    get_show_confirm_exit, 
    get_spot_loot, 
    get_user_setting, 
    get_spot_id_icon, 
    get_no_market_items,
    get_user_settings,
    save_user_settings,
    get_data_value
)
from logic.calculate_results_session import calculate_elixirs_cost_hour, calculate_results_session
from logic.data_fetcher import DataFetcher
from interface.view_interface import ViewInterface

class AppController:
    """
    A controller class to manage the application logic and user interactions.
    This class is a singleton and should be accessed via the get_instance method.
    """
    _instance = None # Singleton instance

    def __init__(self, view: ViewInterface):
        """
        Initialize the AppController with the main window.
            :param view: The main window of the application, implementing ViewInterface.
        """
        if AppController._instance is not None:
            raise Exception("This class is a singleton!")
        AppController._instance = self
        add_log("AppController initialized.", "info")
        self.view = view

    def on_clean_sessions_clicked(self):
        """
        Handle the clean sessions action.
            This method is called when the clean sessions button is clicked.
            It cleans the sessions and shows a message box with the result of the action.
        """
        result = clean_sessions()
        if result == 1:
            add_log(f"Clean sessions dialog selection -> {result} (Success)", "info")
            self.view.show_dialog_results("Sessions have been successfully cleaned.", "clean_sessions", result)
        elif result == 0:
            add_log(f"Clean sessions dialog selection -> {result}  (No elements found to delete)", "info")
            self.view.show_dialog_results("No saved sessions found. Nothing to clean.", "clean_sessions", result)
        elif result == -1:
            add_log(f"Clean sessions dialog selection -> {result}  (Error)", "error")
            self.view.show_dialog_results("An error occurred while cleaning sessions.", "clean_sessions", result)

    def on_clean_sessions_button(self):
        """
        Handle the clean sessions button click event.
            This method is called when the clean sessions button is clicked.
        """
        add_log("Clean sessions button clicked.", "info")
        (res, show_confirm_clean) = get_show_confirm_clean()

        if not res:
            add_log("Error retrieving data from settings.json, check if the file exists and is writable", "error")
            self.view.show_dialog_error("Error retrieving data from settings.json, check if the file exists and is writable.")
            return

        if show_confirm_clean:
            add_log("Showing confirmation dialog for cleaning sessions.", "info")
            enable_confirm_message = self.view.show_dialog_confirmation("Are you sure you want to clean the sessions?", self.on_clean_sessions_clicked, "clean_sessios")
            if not update_confirm_dialog(enable_confirm_message, "clean_sessions"):
                self.view.show_dialog_error("Error updating settings in file 'settings.json'. Check if the file exists and is writable.")
        else:
            self.on_clean_sessions_clicked()
        
    def on_exit_button(self):
        """
        Handle the exit button click event.
        """
        add_log("Exit button clicked.", "info")
        res, show_confirm_exit = get_show_confirm_exit()

        if not res:
            add_log("Error retrieving data from settings.json, check if the file exists and is writable", "error")
            self.view.show_dialog_error("Error retrieving data from settings.json, check if the file exists and is writable.")
            return

        if show_confirm_exit:
            add_log("Showing confirmation dialog for exiting app.", "info")
            enable_confirm_message = self.view.show_dialog_confirmation("Are you sure you want to exit?", lambda: self.view.close_window(), "exit")
            if not update_confirm_dialog(enable_confirm_message, "exit"):
                self.view.show_dialog_error("Error updating settings in file 'settings.json'. Check if the file exists and is writable.")
        else:
            self.view.close_window()

    def get_spots_list(self) -> list[str]:
        """
        Get the list of spots from the data file.
            :return: A list of spots.
        """
        return get_data_value('spots')

    def create_settings_widget(self):
        """
        Call view method defined in ViewInterface to create the settings widget.
        """
        self.view.create_settings_widget()
       
    def select_new_session(self, spot_name: str):
        """
        Handle the selection of a new hunting session.
            :param spot_name: The name of the hunting spot selected by the user.
        """
        self.view.set_ui_enabled(False) # Disable the UI while fetching data
        QTimer.singleShot(0, lambda: self.start_data_retrieval(spot_name)) # Retrieve data for the selected spot after giving time to render the UI changes

    def show_error_and_enable_ui(self, message: str):
        """
        Show an error message and re-enable the UI.
            :param message: The error message to display.
        """
        add_log(message, "error")
        self.view.show_dialog_error(message)
        self.view.set_ui_enabled(True)

    def start_data_retrieval(self, spot_name: str):
        """
        Start the data retrieval process for the selected hunting spot.
            :param spot_name: The name of the hunting spot selected by the user.
        """
        add_log(f"Session selected: {spot_name}, retrieving data", "info")
        loot_ids = get_spot_loot(spot_name)

        if not loot_ids:
            self.show_error_and_enable_ui(f"Error fetching loot for spot '{spot_name}'.")
            return
        
        region = get_user_setting("region")
        if not region:
            self.show_error_and_enable_ui("Region setting not found, add it in settings section.")
            return
        
        language = get_user_setting("language")
        if not language:
            self.show_error_and_enable_ui("Language setting not found, add it in settings section.")
            return
        
        market_tax = get_data_value("market_tax")
        if market_tax is None:
            self.show_error_and_enable_ui("Missing data in 'data.json' file.")
            return
        
        extra_profit = get_user_setting("extra_profit")
        if extra_profit is None:
            self.show_error_and_enable_ui("Extra profit setting not found, add it in settings section.")
            return
        
        value_pack = get_user_setting("value_pack")
        if value_pack is None:
            self.show_error_and_enable_ui("Value pack usage or not was not found, add it in settings section.")
            return

        self.thread = QThread()
        self.worker = DataFetcher(
            loot_ids,
            get_user_setting("elixir_ids"),
            region,
            language
        )

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(lambda: self.on_data_retrieved(spot_name, value_pack, market_tax, extra_profit, self.worker.data_retrieved))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_data_retrieved(self, spot_name: str, value_pack: bool, market_tax: float, extra_profit: bool, data_retrieved: dict[str, dict[str, tuple[str, int]]] | None):
        """
        Handle the data retrieval from the API.
            :param spot_name: The name of the hunting spot.
            :param value_pack: Whether the value pack is used or not.
            :param market_tax: The market tax percentage.
            :param extra_profit: If extra profit is enabled or not.
            :param data_retrieved: The data retrieved from the API, or None if an error occurred.
        """
        self.view.set_ui_enabled(True) # Re-enable the UI
        if data_retrieved is None:
            add_log(f"Error retrieving data for spot '{spot_name}'", "error")
            self.view.set_session_button_enabled(False) # Disable the new session button
            self.view.show_dialog_error("Error fetching data from API, too many requests, disabling new session button for 75 seconds.")
            QTimer.singleShot(75000, lambda: self.view.set_session_button_enabled(True)) # Re-enable the button after 75 seconds
            return
        
        spot_id_icon = get_spot_id_icon(spot_name)
        if not spot_id_icon:
            add_log(f"No icon found for spot '{spot_name}'", "error")
            self.view.show_dialog_error(f"Error fetching spot '{spot_name}' icon from JSON file.")
            return
        
        no_market_items = get_no_market_items(spot_name)
        self.view.create_new_session_widget(
            spot_name,
            value_pack,
            market_tax,
            extra_profit,
            spot_id_icon,
            no_market_items,
            data_retrieved['items'],
            calculate_elixirs_cost_hour(data_retrieved['elixirs'])
        )

    def on_exchange_hides(self, green_hides: str, blue_hides: str):
        """
        Handle the exchange of hides when the button is clicked.
            :param green_hides: The number of green hides to exchange.
            :param blue_hides: The number of blue hides to exchange.
        """
        if len(green_hides) == 0 or len(blue_hides) == 0:
            return
        try:
            res_exchange = exchange_results(int(green_hides), int(blue_hides))
            self.view.update_exchange_hides_results(res_exchange)
        except:
            return
        
    def save_session(self, labels_input_text: list[str], data_input: list[str], labels_res: list[str], results_tot: int, results_tot_h: int, results_tax: int, results_tax_h: int) -> int:
        """
        Save the results of a hunting session to an Excel file.
            :param labels_input_text: List of labels for the input data.
            :param data_input: List of input data values.
            :param labels_res: List of labels for the results.
            :param results_tot: Total results.
            :param results_tot_h: Total results per hour.
            :param results_tax: Results after tax.
            :param results_tax_h: Results after tax per hour.
            :return: 0 if successful, -1 if an error occurs.
        """
        return save_session(labels_input_text, data_input, labels_res, results_tot, results_tot_h, results_tax, results_tax_h)
    
    def get_session_results(self, value_pack: bool, market_tax: float, extra_profit: bool, data_input: dict[str, tuple[str, str]], elixirs_cost: str) -> dict[str, Any]:
        """
        Get the results of a hunting session.
            :param value_pack: Whether the value pack is used or not.
            :param market_tax: The market tax percentage.
            :param extra_profit: The extra profit percentage applied or not to session results.
            :param data_input: A dictionary containing the input data for the session. (name: (price, amount))
            :param elixirs_cost: The cost of elixirs for the session.
            :return: A dictionary containing the results of the session or empty dictionary if settings.json is not found or input data is invalid.
        """
        return calculate_results_session(value_pack, market_tax, extra_profit, data_input, elixirs_cost)
    
    def get_all_settings_data(self) -> dict[str, Any]:
        """
        Get the settings data from the settings.json file.
            :return: A dictionary containing the settings data.
        """
        return get_user_settings()
    
    def save_user_settings(self, new_settings: dict[str, tuple[str, Any]]) -> int:
        """
        Save the new settings to the settings.json file.
            :param new_settings: A dictionary containing the new settings to save.
        """
        result = save_user_settings(new_settings)
        if result == 0:
            add_log("Settings saved successfully.", "info")
        elif result == -1:
            add_log("Error saving settings: settings.json file not found.", "error")
            self.view.show_dialog_error("Error saving user settings in 'settings.json' file.")
        else:
            add_log(f"Unexpected result when saving settings: {result}", "error")
            self.view.show_dialog_error("Unexpected error occurred while saving user settings in 'settings.json' file.")
            
        return result

    @staticmethod
    def get_instance() -> "AppController":
        """
        Get the singleton instance of AppController.
            :return: The singleton instance of AppController.
        """
        if AppController._instance is None:
            raise Exception("AppController instance not created. Call AppController first.")
        return AppController._instance