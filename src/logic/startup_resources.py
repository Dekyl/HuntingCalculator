import sys, os, json
import shutil

from logic.logs import add_log

res_list = [
    'res/data.json',
    'res/settings.json',
    'res/icons/matchlock.ico',
    'res/icons/settings.ico',
    'res/icons/new_session.ico',
    'res/icons/home.ico',
    'res/icons/clean_results.ico',
    'res/icons/view_results.ico',
    'res/icons/exit_app.ico'
]

def get_resource_MEIPASS(relative_path:str) -> str:
    """
    Get the absolute path to a resource from sys._MEYPASS folder.
    This function returns the absolute path to a resource located 
    in the sys._MEIPASS directory, which is set by PyInstaller
        :param relative_path: The relative path to the resource.
        :return: The absolute path to the resource.
    """
    if not hasattr(sys, '_MEIPASS'):
        # If not running as an executable, return empty path
        return ""

    base_path = getattr(sys, '_MEIPASS') # sys._MEIPASS is set by PyInstaller when running as an executable
    return os.path.join(base_path, relative_path)

def prepare_resources() -> bool:
    """
    Prepare the resources for the application by copying necessary files
    to the destination folder. This function ensures that all required
    resources are available in the expected directory structure.
        :return: True if resources are prepared successfully, False otherwise.
    """

    item_icons_folder = 'res/icons/items'
    if os.path.exists(item_icons_folder):
        # If the item icons folder already exists, remove it so it does not contain old icons
        # This is necessary to avoid keeping old icons that are no longer used in current session
        shutil.rmtree(item_icons_folder)
    os.makedirs(item_icons_folder, exist_ok=True)

    elixir_icons_folder = 'res/icons/elixirs'
    if os.path.exists(elixir_icons_folder):
        # If the elixir icons folder already exists, remove it so it does not contain old icons
        # This is necessary to avoid keeping old icons that are no longer used in current session
        shutil.rmtree(elixir_icons_folder)
    os.makedirs(elixir_icons_folder, exist_ok=True)

    for res_path in res_list:
        if os.path.exists(res_path):
            continue  # File already exists, no need to copy

        src_file = get_resource_MEIPASS(res_path)
        if src_file: # If the resource exists in the MEIPASS, copy it to the destination path
            try:
                # Copy the resource from the MEIPASS to the destination path
                shutil.copyfile(src_file, res_path)
                add_log(f"Copied resource {res_path} from MEIPASS", "info")
            except Exception as e:
                add_log(f"Failed to copy resource {res_path} from MEIPASS: {e}", "error")
                return False
            continue

        if res_path == 'res/settings.json':
            try:
                with open(res_path, 'w') as f:
                    json.dump({
                        "show_confirm_exit_message": True,
                        "show_confirm_clean_message": True,
                        "region": "eu",
                        "market_tax": 0.35,
                        "value_pack": 0.315,
                        "elixir_ids": [],
                        "language": "en-US"
                    }, f, indent=4)
                add_log(f"Created default settings.json", "info")
            except Exception as e:
                add_log(f"Failed to create {res_path}: {e}", "error")
                return False
            continue

        add_log(f"Resource {res_path} not found in MEIPASS and not copied", "error")
        return False

    if not os.path.exists('./Hunting Sessions'):
        os.mkdir('Hunting Sessions')
    return True
    