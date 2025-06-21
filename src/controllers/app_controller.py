from PySide6.QtCore import QTimer

from typing import Any, Optional

from logic.logs import add_log
from logic.exchange_calculator import exchange_results
from logic.manage_resources.access_resources import (
    update_confirm_dialog, 
    get_show_confirm_exit, 
    get_data_value
)
from logic.data_classes.save_session_data import SaveSessionData
from logic.data_classes.session_results import SessionResultsData
from gui.dialogs.dialogs_user import show_dialog_confirmation, show_dialog_type
from config.config import settings_json
from interface.view_interface import ViewInterface
from controllers.sessions_controller import (
    on_clean_session_subctrler, 
    delete_session_subctrler, 
    show_select_session_subctrler,
    save_session_subctrler, 
    get_res_session_subctrler
)
from controllers.data_retrieval_controller import DataRetrievalController, get_match_elixirs_subctrler
from controllers.settings_controller import get_all_settings_data_subctrler, apply_user_settings_subctrler

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
        self.data_controller = None

    def change_page_controller(self, page_name: str):
        """
        Change the current page in the view.
            :param page_name: The name of the page to change to.
        """
        add_log(f"Changing page to {page_name}.", "info")
        self.view.change_page(page_name)

    def on_clean_sessions_button_controller(self):
        """
        Handle the clean sessions button click event.
            This method is called when the clean sessions button is clicked.
        """
        on_clean_session_subctrler(self.view.get_current_page_name, self.change_page_controller)
        
    def exit_application_controller(self):
        """
        Perform the actions required to exit the application.
        """
        add_log("Exiting application.", "info")
        self.view.close_window()

    def on_exit_button_controller(self):
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
                lambda: self.exit_application_controller(), 
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
            self.exit_application_controller()

    def get_spots_list_controller(self) -> list[str]:
        """
        Get the list of spots from the data file.
            :return: A list of spots.
        """
        return get_data_value('spots')

    def create_settings_widget_controller(self):
        """
        Call view method defined in ViewInterface to create the settings widget.
        """
        self.view.create_settings_widget()
       
    def select_new_session_controller(self, spot_name: str):
        """
        Handle the selection of a new hunting session.
            :param spot_name: The name of the hunting spot selected by the user.
        """
        self.view.set_ui_enabled(False) # Disable the UI while fetching data
        def start_controller():
            self.data_controller = DataRetrievalController( # Retrieve data for the selected spot after giving time to render the UI changes
                spot_name,
                self.show_error_enable_ui_controller,
                self.view.set_ui_enabled,
                self.view.set_session_button_enabled,
                self.view.create_new_session_widget,
                self.clear_data_controller
            )
            self.data_controller.start()

        QTimer.singleShot(0, start_controller)

    def clear_data_controller(self):
        """
        Clear the data controller instance.
        This method is called to reset the data controller when necessary.
        """
        add_log("Clearing data controller instance.", "info")
        self.data_controller = None

    def show_error_enable_ui_controller(self, message: str, title: str, action: str = "no_action"):
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

    def on_exchange_hides_controller(self, green_hides: str, blue_hides: str) -> Optional[tuple[int, int, int]]:
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

    def save_session_controller(self, session_data: SaveSessionData) -> bool:
        """
        Save the results of a hunting session to an Excel file.
            :param session_data: An instance of SaveSessionData containing the session details.
            :return: True if successful, False if an error occurs.
        """
        return save_session_subctrler(session_data)
    
    def get_session_results_controller(self, session_results: SessionResultsData) -> dict[str, Any] | int:
        """
        Get the results of a hunting session.
            :param session_results: An instance of SessionResultsData containing the results of the session.
            :return: A dictionary containing the results of the session or -1 if an error occurs.
        """
        return get_res_session_subctrler(session_results)
    
    def get_all_settings_data_controller(self) -> Optional[dict[str, Any]]:
        """
        Get the settings data from the setings file.
            :return: A dictionary containing the settings data or None if the settings file is not found or if any required keys are missing.
        """
        return get_all_settings_data_subctrler()
    
    def apply_user_settings_controller(self, new_settings: dict[str, tuple[str, Any]]) -> int:
        """
        Save the new settings to the settings file.
            :param new_settings: A dictionary containing the new settings to save.
        """
        return apply_user_settings_subctrler(new_settings)
    
    def get_match_elixirs_controller(self, elixir_name_id: str) -> dict[str, str] | str | None:
        """
        Get the matching elixirs for the given elixir name or elixir ID.
            :param elixir_name_id: The name ID of the elixir to match.
            :return: A dictionary containing the matching elixirs or a message if no matches are found.
        """
        return get_match_elixirs_subctrler(elixir_name_id)
    
    def delete_session_controller(self, file_path: str):
        """
        Delete a session file.
            :param file_path: The path to the session file to delete.
        """
        delete_session_subctrler(file_path, self.change_page_controller)  # Call the clean_sessions_controller method to delete the session file

    def show_dialog_select_session_controller(self):
        """
        Show a dialog to select a session.
        This method retrieves the list of saved sessions and displays them in a dialog.
        """
        show_select_session_subctrler(self.view.process_view_session)

    @staticmethod
    def get_instance() -> "AppController":
        """
        Get the singleton instance of AppController.
            :return: The singleton instance of AppController.
        """
        if AppController._instance is None:
            raise Exception("AppController instance not created. Call AppController first.")
        return AppController._instance