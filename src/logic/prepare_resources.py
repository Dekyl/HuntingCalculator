import sys, os, json
import shutil

from logic.logs import add_log
from config.config import res_list, json_files

def get_resource_MEIPASS(relative_path: str) -> str:
    """
    Get the absolute path of a resource file in the MEIPASS directory.
    This function is used to retrieve the path of a resource file when the application
    is packaged with PyInstaller and run as an executable.
        :param relative_path: The relative path of the resource file (e.g., 'res/settings.json').
    """
    base_path = getattr(sys, '_MEIPASS', "") # sys._MEIPASS is set by PyInstaller when running as an executable
    return os.path.join(base_path, relative_path) if base_path else relative_path

def check_all_fields_exist(target_file: str, meipass_src: str, label: str):
    """
    Check if all fields in the target JSON file exist, and if not, add them with default values
    from the source JSON file located in the MEIPASS directory.
        :param target_file: The path to the target JSON file (e.g., 'res/settings.json').
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

def reset_folder(folder_path: str):
    """
    Resets the specified folder by removing it if it exists and creating a new one.
    This is used to ensure that the folder is clean and does not contain old files
    that are no longer needed.
        :param folder_path: The path to the folder to reset (e.g., 'res/icons/items').
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
    reset_folder('res/icons/items')  # Reset the item icons folder
    reset_folder('res/icons/elixirs')  # Reset the elixir icons folder

    is_dev_mode = not hasattr(sys, '_MEIPASS')

    if not os.path.exists('./Hunting Sessions'):
        os.mkdir('Hunting Sessions')

    if is_dev_mode:
        add_log("Running in development mode — skipping resource checks.", "info")
        return True
    
    add_log("Running from executable — performing resource checks.", "info")

    for res_path in res_list:
        meipass_src = get_resource_MEIPASS(res_path)

        if os.path.exists(res_path):
            if res_path in json_files:
                if not check_all_fields_exist(res_path, meipass_src, json_files[res_path]):
                    add_log(f"Missing fields in {json_files[res_path]}, could not be restored.", "error")
                    return False
                continue # All fields were checked, if the resource exists, skip copying it
        
        if meipass_src: # If the resource exists in the MEIPASS, copy it to the destination path
            try:
                # Copy the resource from the MEIPASS to the destination path
                shutil.copyfile(meipass_src, res_path)
                add_log(f"Copied resource {res_path} from MEIPASS", "info")
            except Exception as e:
                add_log(f"Failed to copy resource {res_path} from MEIPASS: {e}", "error")
                return False
            continue

        add_log(f"Resource {res_path} not found in MEIPASS and not copied", "error")
        return False

    return True
    