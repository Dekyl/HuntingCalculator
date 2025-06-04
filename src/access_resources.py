import sys, os
import shutil

res_list = {
    'data.json': 'res/data.json',
    'matchlock.ico': 'res/matchlock.ico',
}

def get_resource(relative_path:str) -> str:
    """
    Get the absolute path to a resource file, handling both development and production environments.
    This function checks if the application is running as a PyInstaller executable
    and adjusts the path accordingly.
        :param relative_path: The relative path to the resource file.
        :return: The absolute path to the resource file.
    """
    # Use getattr to safely access _MEIPASS if it exists, otherwise use the current directory
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))

    return os.path.join(base_path, relative_path)

def prepare_resources():
    """
    Prepare the resources for the application by copying necessary files
    to the destination folder. This function ensures that all required
    resources are available in the expected directory structure.
    """
    dest_folder = './res'
    os.makedirs(dest_folder, exist_ok=True)

    for file_name, resource_path in res_list.items():
        dest_file = os.path.join(dest_folder, file_name)
        if not os.path.exists(dest_file): # If file does not exist, copy it from sys.MEIPASS folder created by PyInstaller
            src_file = get_resource(resource_path)
            shutil.copyfile(src_file, dest_file)
    