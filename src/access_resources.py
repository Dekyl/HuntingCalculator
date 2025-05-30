import sys, os
import shutil

res_list = {
    'data.json': 'res/data.json',
    'matchlock.ico': 'res/matchlock.ico',
}

def get_resource(relative_path):
    try:
        # Temporal folder created by PyInstaller when running the .exe
        base_path = sys._MEIPASS
    except Exception:
        # Fallback to the current directory when running in development mode
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def prepare_resources():
    dest_folder = './res'
    os.makedirs(dest_folder, exist_ok=True)

    for file_name, resource_path in res_list.items():
        dest_file = os.path.join(dest_folder, file_name)
        if not os.path.exists(dest_file):
            src_file = get_resource(resource_path)
            shutil.copyfile(src_file, dest_file)
    