from typing import Callable, Optional

from logic.manage_excels import clean_sessions
from logic.manage_resources.access_resources import get_show_confirm_clean, update_confirm_dialog
from logic.logs import add_log
from gui.dialogs.dialogs_user import show_dialog_type, show_dialog_confirmation
from config.config import settings_json

def on_clean_sessions(get_current_page_name: Callable[[], Optional[str]], change_page: Callable[[str], None]):
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

def on_clean_sessions_clicked(get_current_page_name: Callable[[], Optional[str]], change_page: Callable[[str], None]):
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

    if show_confirm_clean:
        add_log("Showing confirmation dialog for cleaning sessions.", "info")
        enable_confirm_message = show_dialog_confirmation(
            "Are you sure you want to clean the sessions?", 
            lambda: on_clean_sessions(get_current_page_name, change_page), 
            "clean_sessions"
        )
        if not update_confirm_dialog(enable_confirm_message, "clean_sessions"):
            show_dialog_type(
                f"Error updating settings in file '{settings_json}'. Check if the file exists and is writable.", 
                "Settings file error", 
                "error", 
                "no_action"
            )
    else:
        on_clean_sessions(get_current_page_name, change_page)