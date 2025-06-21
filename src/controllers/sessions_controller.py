from typing import Callable, Optional, Any

from logic.results_session.calculate_results_session import calculate_results_session
from logic.data_classes.save_session_data import SaveSessionData
from logic.data_classes.session_results import SessionResultsData
from logic.manage_excels import clean_sessions, save_session
from logic.manage_resources.access_resources import (
    get_show_confirm_clean, 
    update_confirm_dialog, 
    sessions_root_folder_exists,
    delete_saved_session
)
from logic.logs import add_log
from gui.dialogs.dialogs_user import (
    show_dialog_type, 
    show_dialog_confirmation, 
    show_dialog_view_session
)
from config.config import settings_json, saved_sessions_folder

def on_clean_sessions_subctrler(get_current_page_name: Callable[[], Optional[str]], change_page: Callable[[str], None]):
    """
    Handle the clean sessions action.
    This method is called when the clean sessions button is clicked.
    It cleans the sessions and shows a message box with the result of the action.
        :param get_current_page_name: Function to get the current page name.
        :param change_page: Function to change the current page.
    """
    result = clean_sessions()
    if get_current_page_name() == "view_sessions":
        change_page("home")  # Change to home page after cleaning sessions

    messages = {
        1: (
            "Sessions have been successfully cleaned.",
            "Success",
            "info"
        ),
        0: (
            "No saved sessions found. Nothing to clean.",
            "No elements found to delete",
            "info"
        ),
        -1: (
            "Folder not found, created. No sessions were deleted.",
            "Folder not found, created",
            "warning"
        )
    }

    default_message = (
        "An error occurred while cleaning sessions.",
        "Error",
        "error"
    )

    message, log_note, level = messages.get(result, default_message) # Default case for unexpected result

    add_log(f"Clean sessions dialog selection -> {result} ({log_note})", level)
    show_dialog_type(
        message,
        "Clean results",
        level,
        "clean_sessions"
    )

def on_clean_session_subctrler(get_current_page_name: Callable[[], Optional[str]], change_page: Callable[[str], None]):
    """
    Handle the clean sessions button click event.
    This method is called when the clean sessions button is clicked.
        :param get_current_page_name: Function to get the current page name.
        :param change_page: Function to change the current page.
    """
    add_log("Clean sessions button clicked.", "info")
    (res, show_confirm_clean) = get_show_confirm_clean()

    if not res:
        add_log(f"Error retrieving data from '{settings_json}', check if the file exists and is writable", "error")
        show_dialog_type(
            f"Error retrieving data from '{settings_json}', check if the file exists and is writable.", 
            "Settings file error", 
            "error", 
            "no_action"
        )
        return
    
    if not show_confirm_clean:
        add_log("Cleaning sessions without confirmation dialog.", "info")
        on_clean_sessions_subctrler(get_current_page_name, change_page)
        return

    add_log("Showing confirmation dialog for cleaning sessions.", "info")
    clean_sessions, remember_user_choice = show_dialog_confirmation(
        "Are you sure you want to clean the sessions?", 
        "clean_sessions"
    )

    if clean_sessions:
        if remember_user_choice == show_confirm_clean:
            add_log("Exiting without changing confirmation message.", "info")
            on_clean_sessions_subctrler(get_current_page_name, change_page)
            return
        
        if not update_confirm_dialog(remember_user_choice, "clean_sessions"):
            show_dialog_type(
                f"Error updating settings in file '{settings_json}'. Check if the file exists and is writable.",
                "Settings file error",
                "error",
                "no_action"
            )
        on_clean_sessions_subctrler(get_current_page_name, change_page)
    else:
        add_log("User cancelled cleaning sessions", "info")
        return

def delete_session_subctrler(file_path: str, change_page: Callable[[str], None]):
    """
    Delete a session file.
        :param file_path: The path to the session file to delete.
        :param change_page: Function to change the current page after deletion.
    """
    res = delete_saved_session(file_path)
    change_page("home")  # Change to home page after deleting session
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

def show_select_session_subctrler(process_view_session: Callable[[str], None]):
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
    
    process_view_session(session_file_selected) # Call the view method to open the view session dialog

def save_session_subctrler(session_data: SaveSessionData) -> bool:
    """
    Save the results of a hunting session to an Excel file.
        :param session_data: An instance of SaveSessionData containing the session details.
        :return: True if successful, False if an error occurs.
    """
    return save_session(session_data)
    
def get_res_session_subctrler(session_results: SessionResultsData) -> dict[str, Any] | int:
    """
    Get the results of a hunting session.
        :param session_results: An instance of SessionResultsData containing the results of the session.
        :return: A dictionary containing the results of the session or -1 if an error occurs.
    """
    return calculate_results_session(session_results)