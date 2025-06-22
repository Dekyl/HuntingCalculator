import sys, os, json

from logic.logs import add_log
from config.config import (
    res_list, 
    settings_json, 
    default_settings, 
    res_abs_paths, 
    saved_sessions_folder
)
from logic.manage_resources.access_resources import get_app_resource

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

def startup_resources() -> bool:
    """
    Prepare the resources for the application by copying necessary files
    to the destination folder. This function ensures that all required
    resources are available in the expected directory structure.
        :return: True if resources are prepared successfully, False otherwise.
    """
    global res_abs_paths

    if not os.path.exists(saved_sessions_folder):
        os.mkdir(saved_sessions_folder)

    if not os.path.exists('settings'):
        os.mkdir('settings')

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
    