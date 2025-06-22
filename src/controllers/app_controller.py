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
from gui.dialogs.dialogs_user import (
    show_dialog_confirmation, 
    show_dialog_type, 
    show_dialog_confirm_delete_session
)
from config.config import settings_json
from interface.view_interface import ViewInterface
from controllers.sessions_controller import SessionController
from controllers.data_retrieval_controller import DataRetrievalController
from controllers.settings_controller import handle_get_all_settings_data, handle_apply_user_settings

class AppController:
    """
    A controller class to manage the application logic and user interactions.
    This class is a singleton and should be accessed via the get_instance method.
    """
    instance = None # Singleton instance

    def __init__(self, view: ViewInterface):
        """
        Initialize the AppController with the main window.
            :param view: The main window of the application, implementing ViewInterface.
        """
        if AppController.instance is not None:
            raise Exception("AppController is a singleton!")
        AppController.instance = self
        add_log("AppController initialized.", "info")
        
        self.view = view
        self.session_controller = SessionController(
            self.view.get_current_page_name, 
            self.change_page_controller, 
            self.view.process_view_session
        )  # Initialize the session controller
        self.data_controller = DataRetrievalController( # Initialize the data retrieval controller
            self.show_error_enable_ui_controller,
            self.view.set_ui_enabled,
            self.view.set_session_button_enabled,
            self.view.create_new_session_widget
        )

    def change_page_controller(self, page_name: str):
        """
        Change the current page in the view.
            :param page_name: The name of the page to change to.
        """
        add_log(f"Changing page to {page_name}.", "info")
        self.view.change_page(page_name)

    def clean_all_sessions_controller(self):
        """
        Handle the clean sessions button click event.
            This method is called when the clean sessions button is clicked.
        """
        self.session_controller.handle_delete_all_sessions()
        
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
        success, show_confirm_exit = get_show_confirm_exit()

        if not success:
            add_log(f"Error retrieving data from '{settings_json}', check if the file exists and is writable", "error")
            show_dialog_type(
                f"Error retrieving data from '{settings_json}', check if the file exists and is writable.", 
                "Settings file error", 
                "error", 
                "no_action"
            )
            self.exit_application_controller()
            return
        
        if not show_confirm_exit:
            add_log("Exiting app without confirmation dialog.", "info")
            self.exit_application_controller()
            return

        add_log("Showing confirmation dialog for exiting app.", "info")
        user_confirm_exit, remember_user_choice = show_dialog_confirmation(
                                                    "Are you sure you want to exit?",
                                                    "exit"
                                                )

        if user_confirm_exit:
            if remember_user_choice == show_confirm_exit:
                add_log("Exiting without changing confirmation message.", "info")
                self.exit_application_controller()
                return
            
            if not update_confirm_dialog(remember_user_choice, "exit"):
                show_dialog_type(
                    f"Error updating settings in file '{settings_json}'. Check if the file exists and is writable.",
                    "Settings file error",
                    "error",
                    "no_action"
                )
            self.exit_application_controller()
        else:
            add_log("User cancelled exiting app", "info")
            return

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
        QTimer.singleShot(0, lambda: self.data_controller.start_data_retrieval(spot_name)) # Start data retrieval after the UI is rendered

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
        return self.session_controller.handle_save_session(session_data)
    
    def get_session_results_controller(self, session_results: SessionResultsData) -> dict[str, Any] | int:
        """
        Get the results of a hunting session.
            :param session_results: An instance of SessionResultsData containing the results of the session.
            :return: A dictionary containing the results of the session or -1 if an error occurs.
        """
        return self.session_controller.handle_get_results_session(session_results)
    
    def get_all_settings_data_controller(self) -> Optional[dict[str, Any]]:
        """
        Get the settings data from the setings file.
            :return: A dictionary containing the settings data or None if the settings file is not found or if any required keys are missing.
        """
        return handle_get_all_settings_data()
    
    def apply_user_settings_controller(self, new_settings: dict[str, tuple[str, Any]]) -> int:
        """
        Save the new settings to the settings file.
            :param new_settings: A dictionary containing the new settings to save.
        """
        return handle_apply_user_settings(new_settings)
    
    def get_match_elixirs_controller(self, elixir_name_id: str) -> dict[str, str] | str | None:
        """
        Get the matching elixirs for the given elixir name or elixir ID.
            :param elixir_name_id: The name ID of the elixir to match.
            :return: A dictionary containing the matching elixirs or a message if no matches are found.
        """
        return self.data_controller.handle_get_match_elixirs(elixir_name_id)
    
    def delete_session_controller(self, file_path: str):
        """
        Delete a session file.
            :param file_path: The path to the session file to delete.
        """
        delete = show_dialog_confirm_delete_session(file_path)  # Show a confirmation dialog before deleting the session file

        if not delete:
            add_log(f"User cancelled deletion of session file '{file_path}'.", "info")
            return
        
        add_log(f"Deleting session file '{file_path}'.", "info")
        self.session_controller.handle_delete_session(file_path)  # Call the clean_sessions_controller method to delete the session file

    def show_dialog_select_session_controller(self):
        """
        Show a dialog to select a session.
        This method fetches the list of saved sessions and displays them in a dialog.
        """
        self.session_controller.handle_show_select_session()

    @staticmethod
    def get_instance() -> "AppController":
        """
        Get the singleton instance of AppController.
            :return: The singleton instance of AppController.
        """
        if AppController.instance is None:
            raise Exception("AppController instance not created. Call AppController first.")
        return AppController.instance