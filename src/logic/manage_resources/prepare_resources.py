import sys, os, json
import shutil

from logic.logs import add_log
from config.config import res_list, item_icons_root, settings_json, default_settings, res_abs_paths
from logic.manage_resources.access_resources import get_app_resource

def check_all_fields_exist_data(target_file: str, meipass_src: str, label: str):
    """
    Check if all fields in the target JSON file exist, and if not, add them with default values
    from the source JSON file located in the MEIPASS directory.
        :param target_file: The path to the target JSON file
        :param meipass_src: The path to the source JSON file in the MEIPASS directory.
        :param label: A label for logging purposes, indicating which file is being checked.
        :return: True if all fields exist or were added successfully, False otherwise.
    """
    if not os.path.exists(meipass_src):
        return False

    updated = False
    try:
        with open(target_file, 'r', encoding='utf-8') as file:
            data = json.load(file)

        with open(meipass_src, 'r', encoding='utf-8') as src_data_file:
            default_fields = json.load(src_data_file)

        for field, val in default_fields.items():
            if field not in data:
                add_log(f"Adding missing field '{field}' to {label}", "warning")
                data[field] = val
                updated = True

        if updated:
            with open(target_file, 'w', encoding='utf-8') as outfile:
                json.dump(data, outfile, indent=4)
                add_log(f"Added missing fields to {label}", "warning")

    except Exception as e:
        add_log(f"Error checking fields in {label}: {e}", "error")
        return False
    
    return True

def check_all_fields_exist_settings() -> bool:
    """
    Check if all fields in the settings JSON file exist, and if not, add them with default values.
        :return: True if all fields exist or were added successfully, False otherwise.
    """
    f_name = os.path.basename(settings_json)
    missing_fields = False
    try:
        with open(settings_json, 'r', encoding='utf-8') as file:
            settings_data = json.load(file)

        for field, val in default_settings.items():
            if field not in settings_data:
                missing_fields = True
                add_log(f"Adding missing field '{field}' to '{f_name}'", "warning")
                settings_data[field] = val

        if missing_fields:
            with open(settings_json, 'w', encoding='utf-8') as outfile:
                json.dump(settings_data, outfile, indent=4)
                add_log(f"Added missing fields to '{f_name}'", "warning")

    except Exception as e:
        add_log(f"Error checking fields in '{f_name}': {e}", "error")
        return False

    return True

def reset_folder(folder_path: str):
    """
    Resets the specified folder by removing it if it exists and creating a new one.
    This is used to ensure that the folder is clean and does not contain old files
    that are no longer needed.
        :param folder_path: The path to the folder to reset.
    """
    if os.path.exists(folder_path):
        # If the elixir icons folder already exists, remove it so it does not contain old icons
        # This is necessary to avoid keeping old icons that are no longer used in current session
        shutil.rmtree(folder_path)
    os.makedirs(folder_path, exist_ok=True)

def startup_resources() -> bool:
    """
    Prepare the resources for the application by copying necessary files
    to the destination folder. This function ensures that all required
    resources are available in the expected directory structure.
        :return: True if resources are prepared successfully, False otherwise.
    """
    global res_abs_paths

    reset_folder(item_icons_root)  # Reset the item icons folder

    if not os.path.exists('./Hunting Sessions'):
        os.mkdir('Hunting Sessions')

    if not os.path.exists(settings_json): #  Check if the settings JSON file exists
        add_log(f"Settings file {settings_json} not found, creating a new one.", "info")
        try:
            with open(settings_json, 'w', encoding='utf-8') as settings_file:
                json.dump(default_settings, settings_file, indent=4)  # Create a default settings JSON file
        except Exception as e:
            add_log(f"Failed to create settings file: {e}", "error")
            return False
    elif not check_all_fields_exist_settings():
        add_log(f"Missing fields in {os.path.basename(settings_json)}, could not be restored.", "error")
        return False

    is_dev_mode = not hasattr(sys, '_MEIPASS') # Check if running in development mode
    for key, res_path in res_list.items():
        res_src = get_app_resource(res_path)
        res_abs_paths[key] = res_src

        if not os.path.exists(res_src):
            add_log(f"Resource {res_path} not found, exiting.", "error") if is_dev_mode else add_log(f"Resource {res_path} not found in MEIPASS, exiting.", "error")
            return False

    return True
    