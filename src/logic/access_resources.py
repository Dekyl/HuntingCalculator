import json
from typing import Any

from logic.logs import add_log

def check_field_exists(field: str, settings: dict[str, Any], file_name: str) -> bool:
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
    with open('res/settings.json', 'r', encoding='utf-8') as file:
        settings = json.load(file)
        if confirm_action == "clean_sessions":
            if not check_field_exists("show_confirm_clean_message", settings, "settings.json"):
                return False
            settings['show_confirm_clean_message'] = enable
        elif confirm_action == "exit":
            if not check_field_exists("show_confirm_exit_message", settings, "settings.json"):
                return False
            settings['show_confirm_exit_message'] = enable

    with open('res/settings.json', 'w', encoding='utf-8') as file:
        json.dump(settings, file, indent=4)
    add_log(f"Confirmation dialog for {confirm_action} {'enabled' if enable else 'disabled'}.", "info")
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
    with open('res/settings.json', 'r', encoding='utf-8') as file:
        settings = json.load(file)
        if not check_field_exists("show_confirm_clean_message", settings, "settings.json"):
            return (False, False)  # Return False if the field does not exist
        confirm_clean = settings['show_confirm_clean_message']
        if confirm_clean:
            add_log("Showing confirmation dialog for cleaning sessions.", "info")
        return (True, confirm_clean)  # Return True if the field exists and the value is retrieved successfully
    
def get_show_confirm_exit() -> tuple[bool, bool]:
    """
    Get the setting for showing the confirmation dialog before exiting the application.
    This function reads the configuration file to determine whether to show
    the confirmation dialog when exiting the application.
        :return: True if the confirmation dialog should be shown, False otherwise.
    """
    with open('res/settings.json', 'r', encoding='utf-8') as file:
        settings = json.load(file)
        if not check_field_exists("show_confirm_exit_message", settings, "settings.json"):
            return (False, False)  # Return False if the field does not exist
        return (True, settings['show_confirm_exit_message'])
    
def get_spots_list() -> list[str]:
    """
    Get the list of hunting spots from the data file.
    This function reads the data file and returns a list of hunting spots.
        :return: A list of hunting spots.
    """
    with open('res/data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data.get('spots', [])
    
def get_spot_id_icon(spot_name: str) -> str:
    """
    Get the icon ID for a specific hunting spot.
        :param spot_name: The name of the hunting spot.
        :return: The ID of the icon associated with the hunting spot, or an empty string if not found.
    """
    with open('res/data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data.get('spots', {}).get(spot_name, {}).get('spot_id_icon', '')
    
def get_spot_loot(spot_name: str) -> list[str]:
    """
    Get the loot data for a specific hunting spot.
        :param spot_name: The name of the hunting spot.
        :return: A tuple containing two lists:
            - The first list contains the IDs of the loot items.
            - The second list contains the IDs of items that are not available on the market.
    """
    common_items = get_common_items()

    with open('res/data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        spot = data.get('spots', {}).get(spot_name, {})
        spot_items = spot.get('loot', [])
    
    if not spot_items:
        return []
    return spot_items + common_items

def get_no_market_items(spot_name: str) -> list[str]:
    """
    Get the list of items that are not available on the market for a specific hunting spot.
        :param spot_name: The name of the hunting spot.
        :return: A list of item IDs that are not available on the market.
    """
    with open('res/data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data.get('spots', {}).get(spot_name, {}).get('no_market_items', [])
    
def get_common_items() -> list[str]:
    """
    Get the common items data from the data file.
        :return: A list of common items IDs.
    """
    with open('res/data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data.get('common_items', [])
    
def get_user_setting(setting: str) -> Any:
    """
    Get a specific user setting from the settings file.
        :param setting: The name of the setting to retrieve.
        :return: The value of the specified setting, or an empty string if not found.
    """
    with open('res/settings.json', 'r', encoding='utf-8') as file:
        settings = json.load(file)
        return settings.get(setting, None)
    
def get_user_settings() -> dict[str, Any]:
    """
    Get all user settings from the settings file.
        :return: A dictionary containing all user settings.
    """
    with open('res/settings.json', 'r', encoding='utf-8') as file:
        settings = json.load(file)
        return settings
    
def save_user_settings(new_settings: dict[str, tuple[str, Any]]) -> int:
    """
    Save the new user settings to the settings file.
        :param new_settings: A dictionary containing the new settings to save.
    """
    try:
        new_settings_to_save = {}
        for _, (id, val) in new_settings.items():
            new_settings_to_save[id] = val  # Convert tuple to a simple value

        with open('res/settings.json', 'w', encoding='utf-8') as file:
            json.dump(new_settings_to_save, file, indent=4)
        add_log("Settings saved successfully.", "info")
    except Exception as e:
        add_log(f"Error saving settings: {e}", "error")
        return -1  # Return -1 to indicate an error in saving settings
    return 0  # Return 0 to indicate success
