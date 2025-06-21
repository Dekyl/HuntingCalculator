from PySide6.QtCore import QThread, QTimer

from typing import Any, Optional

from logic.manage_excels import save_session
from logic.logs import add_log
from logic.exchange_calculator import exchange_results
from logic.manage_resources.access_resources import (
    update_confirm_dialog, 
    get_show_confirm_exit, 
    get_spot_loot, 
    get_user_setting, 
    get_spot_id_icon, 
    get_no_market_items,
    get_user_settings,
    apply_user_settings,
    get_data_value,
    get_match_elixirs,
    sessions_root_folder_exists,
    delete_saved_session
)
from logic.data_classes.new_session_data import NewSessionData
from logic.data_classes.save_session_data import SaveSessionData
from logic.data_classes.session_results import SessionResultsData
from logic.results_session.calculate_results_session import calculate_elixirs_cost_hour, calculate_results_session
from logic.data_fetcher import DataFetcher
from gui.dialogs.dialogs_user import show_dialog_confirmation, show_dialog_type, show_dialog_view_session
from config.config import (
    default_settings, 
    settings_json, 
    res_abs_paths,
    market_tax, 
    saved_sessions_folder,
    NestedDict
)
from interface.view_interface import ViewInterface
from controllers.clean_sessions_controller import on_clean_sessions_clicked

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

    def change_page(self, page_name: str):
        """
        Change the current page in the view.
            :param page_name: The name of the page to change to.
        """
        add_log(f"Changing page to {page_name}.", "info")
        self.view.change_page(page_name)

    def on_clean_sessions_button(self):
        """
        Handle the clean sessions button click event.
            This method is called when the clean sessions button is clicked.
        """
        on_clean_sessions_clicked(self.view.get_current_page_name, self.change_page)
        
    def exit_application(self):
        """
        Perform the actions required to exit the application.
        """
        add_log("Exiting application.", "info")
        self.view.close_window()

    def on_exit_button(self):
        """
        Handle the exit button click event.
        """
        add_log("Exit button clicked.", "info")
        res, show_confirm_exit = get_show_confirm_exit()

        if not res:
            add_log(f"Error retrieving data from '{settings_json}', check if the file exists and is writable", "error")
            show_dialog_type(
                f"Error retrieving data from '{settings_json}', check if the file exists and is writable.", 
                "Settings file error", 
                "error", 
                "no_action"
            )
            return

        if show_confirm_exit:
            add_log("Showing confirmation dialog for exiting app.", "info")
            enable_confirm_message = show_dialog_confirmation(
                "Are you sure you want to exit?", 
                lambda: self.exit_application(), 
                "exit"
            )
            if not update_confirm_dialog(enable_confirm_message, "exit"):
                show_dialog_type(
                    f"Error updating settings in file '{settings_json}'. Check if the file exists and is writable.", 
                    "Settings file error", 
                    "error", 
                    "no_action"
                )
        else:
            add_log("Exiting app without confirmation dialog.", "info")
            self.exit_application()

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

    def show_error_and_enable_ui(self, message: str, title: str, action: str = "no_action"):
        """
        Show an error message and re-enable the UI.
            :param message: The error message to display.
            :param title: The title of the error dialog.
            :param action: The action that triggered the error, used to set the icon.
        """
        add_log(message, "error")
        show_dialog_type(
            message, 
            title, 
            "error", 
            action
        )
        self.view.set_ui_enabled(True)

    def start_data_retrieval(self, spot_name: str):
        """
        Start the data retrieval process for the selected hunting spot.
            :param spot_name: The name of the hunting spot selected by the user.
        """
        add_log(f"Session selected: {spot_name}, retrieving data", "info")
        loot_items = get_spot_loot(spot_name)

        if not loot_items:
            self.show_error_and_enable_ui(f"Error fetching loot for spot '{spot_name}'.", "Data error", "no_action")
            return
        
        region = get_user_setting("region")
        if not region:
            self.show_error_and_enable_ui("Region setting not found, add it in settings section.", "Settings file error", "no_action")
            return
        
        language = get_user_setting("language")
        if not language:
            self.show_error_and_enable_ui("Language setting not found, add it in settings section.", "Settings file error", "no_action")
            return
        
        extra_profit = get_user_setting("extra_profit")
        if extra_profit is None:
            self.show_error_and_enable_ui("Extra profit setting not found, add it in settings section.", "Settings file error", "no_action")
            return
        
        value_pack = get_user_setting("value_pack")
        if value_pack is None:
            self.show_error_and_enable_ui("Value pack usage or not was not found, add it in settings section.", "Settings file error", "no_action")
            return
        
        elixirs: dict[str, str] | None = get_user_setting("elixirs")
        if elixirs is None:
            self.show_error_and_enable_ui("Elixirs setting not found, add it in settings section.", "Settings file error", "no_action")
            return
        
        lightstones: dict[str, str] | None = get_data_value("lighstone_items")
        if lightstones is None:
            self.show_error_and_enable_ui(f"'lighstone_items' missing in '{res_abs_paths['data']}' file.", "Data file error", "no_action")
            return
        
        imperfect_lightstones: dict[str, str] | None = get_data_value("imperfect_lighstone_items")
        if imperfect_lightstones is None:
            self.show_error_and_enable_ui(f"'imperfect_lighstone_items' missing in '{res_abs_paths['data']}' file.", "Data file error", "no_action")
            return
        
        auto_calculate_best_profit = get_user_setting("auto_calculate_best_profit")
        
        new_session = NewSessionData(
            spot_name, 
            value_pack, 
            auto_calculate_best_profit, 
            market_tax, 
            extra_profit
        )
        
        self.thread = QThread()
        self.worker = DataFetcher(
            loot_items,
            elixirs,
            region,
            lightstones,
            imperfect_lightstones
        )

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(lambda: self.on_data_retrieved(new_session, self.worker.data_retrieved))
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_data_retrieved(self, new_session: NewSessionData, data_retrieved: Optional[NestedDict]):
        """
        Handle the data retrieval from the API.
            :param new_session: The NewSessionData object containing the session details.
            :param data_retrieved: The data retrieved from the API, or None if an error occurred.
            :param lightstone_costs: The costs of lightstones for the hunting spot, or None if an error occurred.
            :param imperfect_lightstone_cost: The costs of the imperfect lightstones for the hunting spot, or None if an error occurred.
        """
        self.view.set_ui_enabled(True) # Re-enable the UI
        if data_retrieved is None:
            add_log(f"Error retrieving data for spot '{new_session.name_spot}'", "error")
            self.view.set_session_button_enabled(False) # Disable the new session button
            show_dialog_type(
                "Error fetching data from API, too many requests, disabling new session button for 80 seconds.", 
                "API timeout", 
                "error", 
                "no_action"
            )
            QTimer.singleShot(80000, lambda: self.view.set_session_button_enabled(True)) # Re-enable the button after 80 seconds
            return
        
        spot_id_icon = get_spot_id_icon(new_session.name_spot)
        if not spot_id_icon:
            add_log(f"No icon found for spot '{new_session.name_spot}'", "error")
            show_dialog_type(
                f"Error fetching spot '{new_session.name_spot}' icon from JSON file.", 
                "JSON data error", 
                "error", 
                "no_action"
            )
            return
        
        no_market_items = get_no_market_items(new_session.name_spot)
        
        new_session.set_extra_data(spot_id_icon,
            no_market_items,
            data_retrieved['items'],
            calculate_elixirs_cost_hour(data_retrieved['elixirs']),
            data_retrieved['lightstones'], 
            data_retrieved['imperfect_lightstones']
        )

        self.view.create_new_session_widget(new_session)

    def on_exchange_hides(self, green_hides: str, blue_hides: str) -> Optional[tuple[int, int, int]]:
        """
        Handle the exchange of hides when the button is clicked.
            :param green_hides: The number of green hides to exchange.
            :param blue_hides: The number of blue hides to exchange.
            :return: A tuple containing the results of the exchange hides or None if an error occurs.
        """
        if len(green_hides) == 0 or len(blue_hides) == 0:
            return None
        try:
            return exchange_results(int(green_hides), int(blue_hides))
        except:
            return None

    def save_session(self, session_data: SaveSessionData) -> bool:
        """
        Save the results of a hunting session to an Excel file.
            :param session_data: An instance of SaveSessionData containing the session details.
            :return: True if successful, False if an error occurs.
        """
        return save_session(session_data)
    
    def get_session_results(self, session_results: SessionResultsData) -> dict[str, Any] | int:
        """
        Get the results of a hunting session.
            :param session_results: An instance of SessionResultsData containing the results of the session.
            :return: A dictionary containing the results of the session or -1 if an error occurs.
        """
        return calculate_results_session(session_results)
    
    def get_all_settings_data(self) -> Optional[dict[str, Any]]:
        """
        Get the settings data from the setings file.
            :return: A dictionary containing the settings data or None if the settings file is not found or if any required keys are missing.
        """
        all_settings = get_user_settings()
        if not all_settings:
            return None

        missing_keys = [key for key in default_settings if key not in all_settings]
        if missing_keys:
            return None

        return all_settings
    
    def apply_user_settings(self, new_settings: dict[str, tuple[str, Any]]) -> int:
        """
        Save the new settings to the settings file.
            :param new_settings: A dictionary containing the new settings to save.
        """
        result = apply_user_settings(new_settings)
        if result == 0:
            add_log("Settings saved successfully.", "info")
        elif result == -1:
            add_log(f"Error saving settings: '{settings_json}' file not found.", "error")
            show_dialog_type(
                f"Error saving user settings in '{settings_json}' file.", 
                "Save setting error", 
                "error", 
                "no_action"
            )
        else:
            add_log(f"Unexpected result when saving settings: {result}", "error")
            show_dialog_type(
                f"Unexpected error occurred while saving user settings in '{settings_json}' file.", 
                "Save setting error", 
                "error", 
                "no_action"
            )
            
        return result
    
    def get_match_elixirs(self, elixir_name_id: str) -> dict[str, str] | str | None:
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
    
    def delete_session(self, file_path: str):
        """
        Delete a session file.
            :param file_path: The path to the session file to delete.
        """
        res = delete_saved_session(file_path)
        self.change_page("home")  # Change to home page after deleting session
        if res == 0:
            add_log(f"Session file '{file_path}' deleted successfully.", "info")
            show_dialog_type(
                f"Session file deleted successfully.", 
                "Delete session", 
                "info", 
                "no_action"
            )
        elif res == -1:
            add_log(f"Session file '{file_path}' does not exist.", "warning")
            show_dialog_type(
                f"Session file '{file_path}' does not exist.", 
                "Delete session", 
                "warning", 
                "no_action"
            )
        elif res == -2:
            add_log(f"Error deleting session file '{file_path}'.", "error")
            show_dialog_type(
                f"Error deleting session file '{file_path}'.", 
                "Delete session", 
                "error", 
                "no_action"
            )

    def show_dialog_select_session(self):
        """
        Show a dialog to view existing hunting sessions.
            This function checks if the sessions root folder exists and then opens a dialog to view sessions.
            If the folder does not exist, it shows an error dialog.
        """
        res = sessions_root_folder_exists()
        if res == -1:  # Sessions folder did not exist, created it
            show_dialog_type(
                f"'{saved_sessions_folder}' was not found. It has been created.", 
                "Saved sessions folder", 
                "warning", 
                "no_action"
            )
            return
        elif res == -2:
            show_dialog_type(
                f"'{saved_sessions_folder}' is not a folder. Check it before trying again.", 
                "Saved sessions folder", 
                "warning", 
                "no_action"
            )
            return
        
        session_file_selected = show_dialog_view_session()
        if not session_file_selected:
            return # Empty string means no file was selected
        
        self.view.process_view_session(session_file_selected) # Call the view method to open the view session dialog

    @staticmethod
    def get_instance() -> "AppController":
        """
        Get the singleton instance of AppController.
            :return: The singleton instance of AppController.
        """
        if AppController._instance is None:
            raise Exception("AppController instance not created. Call AppController first.")
        return AppController._instance