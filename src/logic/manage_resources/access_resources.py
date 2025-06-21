import json, os, sys
from typing import Any

from logic.logs import add_log
from config.config import res_abs_paths, saved_sessions_folder, settings_json

def check_field_exists(field: str, settings: dict[str, Any], file_name: str = settings_json) -> bool:
    """
    Check if a field exists in the settings dictionary.
    If the field does not exist, log an error message.
        :param field: The field to check for existence.
        :param settings: The settings dictionary to check in.
        :param file_name: The name of the settings file for logging purposes.
    """
    if field not in settings:
        add_log(f"Field '{field}' does not exist in {file_name}.", "error")
        return False
    return True

def update_confirm_dialog(enable: bool, confirm_action: str) -> bool:
    """
    Update the confirmation dialog settings in the configuration file.
        :param enable: True to enable the confirmation dialog, False to disable it.
        :param confirm_action: The action for which the confirmation dialog is enabled or disabled.
        :return: True if the update was successful, False if it failed.
    """
    try:
        with open(settings_json, 'r', encoding='utf-8') as file:
            settings: dict[str, Any] = json.load(file)
    except FileNotFoundError:
        add_log(f"Settings file not found: '{settings_json}'. Creating a new one.", "warning")
        settings = {}
    except json.JSONDecodeError:
        add_log(f"Error decoding JSON in settings file: '{settings_json}'. Resetting to default.", "error")
        settings = {}

    if confirm_action == "clean_sessions":
        if not check_field_exists("show_confirm_clean_message", settings, settings_json):
            settings["show_confirm_clean_message"] = False  # Default value
        elif settings["show_confirm_clean_message"] == enable:
            return True  # No change needed if the value is already set
        settings['show_confirm_clean_message'] = enable
    elif confirm_action == "exit":
        if not check_field_exists("show_confirm_exit_message", settings, settings_json):
            settings["show_confirm_exit_message"] = False  # Default value
        elif settings["show_confirm_exit_message"] == enable:
            return True  # No change needed if the value is already set
        settings['show_confirm_exit_message'] = enable

    try:
        with open(settings_json, 'w', encoding='utf-8') as file:
            json.dump(settings, file, indent=4)
        add_log(f"Confirmation dialog for {confirm_action} {'enabled' if enable else 'disabled'}.", "info")
    except Exception as e:
        add_log(f"Error saving settings: {e}", "error")
        return False

    return True

def get_show_confirm_clean() -> tuple[bool, bool]:
    """
    Get the setting for showing the confirmation dialog before cleaning sessions.
    This function reads the configuration file to determine whether to show
    the confirmation dialog when cleaning sessions.
        :return: A tuple containing:
            - True if the confirmation dialog should be shown, False otherwise.
            - False if there was an error checking the field.
    """
    try:
        with open(settings_json, 'r', encoding='utf-8') as file:
            settings = json.load(file)
            if not check_field_exists("show_confirm_clean_message", settings, settings_json):
                return (False, False)  # Return False if the field does not exist
            confirm_clean = settings['show_confirm_clean_message']
            return (True, confirm_clean)  # Return True if the field exists and the value is retrieved successfully
    except FileNotFoundError:
        add_log(f"Settings file not found: '{settings_json}'.", "error")
        return (False, False)
    except json.JSONDecodeError:
        add_log(f"Error decoding JSON in settings file: '{settings_json}'.", "error")
        return (False, False)
    
def get_show_confirm_exit() -> tuple[bool, bool]:
    """
    Get the setting for showing the confirmation dialog before exiting the application.
    This function reads the configuration file to determine whether to show
    the confirmation dialog when exiting the application.
        :return: True if the confirmation dialog should be shown, False otherwise.
    """
    try:
        with open(settings_json, 'r', encoding='utf-8') as file:
            settings = json.load(file)
            if not check_field_exists("show_confirm_exit_message", settings, settings_json):
                return (False, False)  # Return False if the field does not exist
            confirm_exit = settings['show_confirm_exit_message']
            return (True, confirm_exit)  # Return True if the field exists and the value is retrieved successfully
    except FileNotFoundError:
        add_log(f"Settings file not found: '{settings_json}'.", "error")
        return (False, False)
    except json.JSONDecodeError:
        add_log(f"Error decoding JSON in settings file: '{settings_json}'.", "error")
        return (False, False)
    
def get_spot_id_icon(spot_name: str) -> str:
    """
    Get the icon ID for a specific hunting spot.
        :param spot_name: The name of the hunting spot.
        :return: The ID of the icon associated with the hunting spot, or an empty string if not found.
    """
    try:
        with open(res_abs_paths['data'], 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get('spots', {}).get(spot_name, {}).get('spot_id_icon', '')
    except FileNotFoundError:
        add_log(f"Data file not found: '{res_abs_paths['data']}'.", "error")
        return ''
    except json.JSONDecodeError:
        add_log(f"Error decoding JSON in data file: '{res_abs_paths['data']}'.", "error")
        return ''
    
def get_spot_loot(spot_name: str) -> dict[str, str]:
    """
    Get the loot data for a specific hunting spot.
        :param spot_name: The name of the hunting spot.
        :return: A tuple containing two lists:
            - The first list contains the IDs of the loot items.
            - The second list contains the IDs of items that are not available on the market.
    """
    common_items = get_data_value('common_items')
    try:
        with open(res_abs_paths['data'], 'r', encoding='utf-8') as file:
            data = json.load(file)
            spot = data.get('spots', {}).get(spot_name, {})
            spot_items = spot.get('loot', {})
    except FileNotFoundError:
        add_log(f"Data file not found: '{res_abs_paths['data']}'.", "error")
        return {}
    except json.JSONDecodeError:
        add_log(f"Error decoding JSON in data file: '{res_abs_paths['data']}'.", "error")
        return {}

    if not spot_items:
        return {}
    return {**spot_items, **common_items}  # Merge spot items with common items

def get_no_market_items(spot_name: str) -> list[str]:
    """
    Get the list of items that are not available on the market for a specific hunting spot.
        :param spot_name: The name of the hunting spot.
        :return: A list of item IDs that are not available on the market.
    """
    try:
        with open(res_abs_paths['data'], 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get('spots', {}).get(spot_name, {}).get('no_market_items', [])
    except FileNotFoundError:
        add_log(f"Data file not found: '{res_abs_paths['data']}'.", "error")
        return []
    except json.JSONDecodeError:
        add_log(f"Error decoding JSON in data file: '{res_abs_paths['data']}'.", "error")
        return []
    
def get_user_setting(setting: str) -> Any:
    """
    Get a specific user setting from the settings file.
        :param setting: The name of the setting to retrieve.
        :return: The value of the specified setting, or an empty string if not found.
    """
    try:
        with open(settings_json, 'r', encoding='utf-8') as file:
            settings = json.load(file)
            return settings.get(setting, None)
    except FileNotFoundError:
        add_log(f"Settings file not found: '{settings_json}'.", "error")
        return None
    except json.JSONDecodeError:
        add_log(f"Error decoding JSON in settings file: '{settings_json}'.", "error")
        return None
    
def get_user_settings() -> dict[str, Any]:
    """
    Get all user settings from the settings file.
        :return: A dictionary containing all user settings.
    """
    try:
        with open(settings_json, 'r', encoding='utf-8') as file:
            settings = json.load(file)
            return settings
    except FileNotFoundError:
        add_log(f"Settings file not found: '{settings_json}'.", "error")
        return {}
    except json.JSONDecodeError:
        add_log(f"Error decoding JSON in settings file: '{settings_json}'.", "error")
        return {}
    
def apply_user_settings(new_settings: dict[str, tuple[str, Any]]) -> int:
    """
    Save the new user settings to the settings file.
        :param new_settings: A dictionary containing the new settings to save.
    """
    try:
        new_settings_to_save = {}
        for _, (id, val) in new_settings.items():
            new_settings_to_save[id] = val  # Convert tuple to a simple value

        with open(settings_json, 'w', encoding='utf-8') as file:
            json.dump(new_settings_to_save, file, indent=4)
        add_log("Settings saved successfully.", "info")
    except Exception as e:
        add_log(f"Error saving settings: {e}", "error")
        return -1  # Return -1 to indicate an error in saving settings
    return 0  # Return 0 to indicate success

def sessions_root_folder_exists() -> int:
    """
    Check if the root folder for hunting sessions exists.
        :return: -1 if the folder does not exist and was created, -2 if it is not a directory, 0 if it exists and is a directory.
    """
    if not os.path.exists(saved_sessions_folder):
        os.mkdir(saved_sessions_folder)
        add_log(f"Folder '{saved_sessions_folder}' not found, created.", "warning")
        return -1

    if not os.path.isdir(saved_sessions_folder):
        add_log(f"Folder '{saved_sessions_folder}' is not a folder, check it before trying again.", "error")
        return -2

    return 0  # Return 0 to indicate the folder exists or was created successfully

def get_match_elixirs(elixir_name_id: str) -> dict[str, str]:
    """
    Get a dictionary of elixir IDs and names that match the provided elixir name or ID.
        :param elixir_name_id: The name or ID of the elixir to match.
        :return: A dictionary where keys are elixir IDs and values are elixir names that match the provided name or ID.
    """
    try:
        with open(res_abs_paths['data'], 'r', encoding='utf-8') as file:
            elixirs_perfumes = json.load(file).get('elixir_perfume_names_ids', {})
    except FileNotFoundError:
        add_log(f"Data file not found: '{res_abs_paths['data']}'.", "error")
        return {}
    except json.JSONDecodeError:
        add_log(f"Error decoding JSON in data file: '{res_abs_paths['data']}'.", "error")
        return {}
    except Exception as e:
        add_log(f"Unexpected error while reading data file: {e}", "error")
        return {}
    
    matches: dict[str, str] = {}
    for elixir_id, elixir_name in elixirs_perfumes.items():
        if elixir_name_id in elixir_id[:len(elixir_name_id)] or elixir_name_id.lower() in elixir_name.lower():
            matches[elixir_id] = elixir_name

    return matches

def get_data_value(data_name: str) -> Any:
    """
    Get a specific value from the data file.
        :param data_name: The name of the data to retrieve.
        :return: The value of the specified data, or None if not found.
    """
    try:
        with open(res_abs_paths['data'], 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data.get(data_name, None)
    except FileNotFoundError:
        add_log(f"Data file not found: '{res_abs_paths['data']}'.", "error")
        return None
    except json.JSONDecodeError:
        add_log(f"Error decoding JSON in data file: '{res_abs_paths['data']}'.", "error")
        return None
    
def delete_saved_session(file_path: str) -> int:
    """
    Delete a specific session file.
        :param file_path: The path to the session file to delete.
        :return: 0 if the deletion was successful, -1 if the file does not exist, -2 if an error occurred.
    """
    try:
        if not os.path.exists(file_path):
            add_log(f"Session file '{file_path}' does not exist.", "error")
            return -1
        os.remove(file_path)
        add_log(f"Session file '{file_path}' deleted successfully.", "info")
        return 0
    except Exception as e:
        add_log(f"Error deleting session file '{file_path}': {e}", "error")
        return -2

def get_app_resource(relative_path: str) -> str:
    """
    Get the absolute path to a resource file in the application (MEIPASS if executable, current dir if developer).
        :param relative_path: The relative path to the resource file.
        :return: The absolute path to the resource file.
    """
    base_path = getattr(sys, '_MEIPASS', "") # sys._MEIPASS is set by PyInstaller when running as an executable
    return os.path.join(base_path, relative_path) if base_path else relative_path