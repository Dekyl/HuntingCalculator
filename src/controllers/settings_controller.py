from typing import Optional, Any

from logic.logs import add_log
from logic.manage_resources.access_resources import get_user_settings, apply_user_settings
from gui.dialogs.dialogs_user import show_dialog_type
from config.config import settings_json, default_settings

def get_all_settings_data_subctrler() -> Optional[dict[str, Any]]:
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

def apply_user_settings_subctrler(new_settings: dict[str, tuple[str, Any]]) -> int:
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