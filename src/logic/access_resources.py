import json

from typing import Any

from logic.logs import add_log

def update_confirm_dialog(enable: bool, confirm_action: str):
    """
    Update the confirmation dialog settings in the configuration file.
        :param enable: True to enable the confirmation dialog, False to disable it.
        :param confirm_action: The action for which the confirmation dialog is enabled or disabled.
    """
    with open('./res/settings.json', 'r', encoding='utf-8') as file:
        settings = json.load(file)
        if confirm_action == "clean_results":
            settings['show_confirm_clean_message'] = enable
        elif confirm_action == "exit":
            settings['show_confirm_exit_message'] = enable

    with open('./res/settings.json', 'w', encoding='utf-8') as file:
        json.dump(settings, file, indent=4)

    add_log(f"Confirmation dialog for {confirm_action} {'enabled' if enable else 'disabled'}.", "info")

def get_show_confirm_clean() -> bool:
    """
    Get the setting for showing the confirmation dialog before cleaning results.
    This function reads the configuration file to determine whether to show
    the confirmation dialog when cleaning results.
        :return: True if the confirmation dialog should be shown, False otherwise.
    """
    with open('./res/settings.json', 'r', encoding='utf-8') as file:
        settings = json.load(file)
        return settings['show_confirm_clean_message']
    
def get_show_confirm_exit() -> bool:
    """
    Get the setting for showing the confirmation dialog before exiting the application.
    This function reads the configuration file to determine whether to show
    the confirmation dialog when exiting the application.
        :return: True if the confirmation dialog should be shown, False otherwise.
    """
    with open('./res/settings.json', 'r', encoding='utf-8') as file:
        settings = json.load(file)
        return settings['show_confirm_exit_message']
    
def get_spots_list() -> list[str]:
    """
    Get the list of hunting spots from the data file.
    This function reads the data file and returns a list of hunting spots.
        :return: A list of hunting spots.
    """
    with open('./res/data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data.get('spots', [])
    
def get_spot_icon(spot_name: str) -> str:
    """
    Get the icon ID for a specific hunting spot.
        :param spot_name: The name of the hunting spot.
        :return: The ID of the icon associated with the hunting spot, or an empty string if not found.
    """
    with open('./res/data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data.get('spots', {}).get(spot_name, {}).get('icon_id', '')
    
def get_spot_loot(spot_name: str) -> list[str]:
    """
    Get the loot data for a specific hunting spot.
        :param spot_name: The name of the hunting spot.
        :return: A tuple containing two lists:
            - The first list contains the IDs of the loot items.
            - The second list contains the IDs of items that are not available on the market.
    """
    common_items = get_common_items()

    with open('./res/data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        spot = data.get('spots', {}).get(spot_name, {})
        spot_items = spot.get('loot', [])
    
    if not spot_items:
        add_log(f"No loot found for spot: {spot_name}", "warning")
        return []
    return spot_items + common_items

def get_no_market_items(spot_name: str) -> list[str]:
    """
    Get the list of items that are not available on the market for a specific hunting spot.
        :param spot_name: The name of the hunting spot.
        :return: A list of item IDs that are not available on the market.
    """
    with open('./res/data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data.get('spots', {}).get(spot_name, {}).get('no_market_items', [])
    
def get_common_items() -> list[str]:
    """
    Get the common items data from the data file.
        :return: A list of common items IDs.
    """
    with open('./res/data.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        return data.get('common_items', [])
    
def get_user_setting(setting: str) -> Any:
    """
    Get a specific user setting from the settings file.
        :param setting: The name of the setting to retrieve.
        :return: The value of the specified setting, or an empty string if not found.
    """
    with open('./res/settings.json', 'r', encoding='utf-8') as file:
        settings = json.load(file)
        return settings.get(setting, None)
