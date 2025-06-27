import logging
from typing import Any, TypeAlias

# Global configuration settings for the application

max_threads = 10 # Maximum number of threads to use for concurrent requests
log_level = logging.INFO # Logging level for the application
threshold_delete_logs = 1024 * 1024  # 1 MB
user_settings_folder = 'settings' # Folder where user settings are stored
sql_db_folder = 'db' # Folder where the SQLite database files are stored
saved_sessions_folder = "Hunting Sessions"  # Folder where hunting sessions are saved
sql_file = f'{sql_db_folder}/cached_data.db' # Path to the SQLite database file for cached data

res_list = {
    'data': 'res/data.json',
    'matchlock_ico': 'res/icons/app_icons/matchlock.ico',
    'settings_ico': 'res/icons/app_icons/settings.ico',
    'new_session_ico': 'res/icons/app_icons/new_session.ico',
    'home_ico': 'res/icons/app_icons/home.ico',
    'clean_sessions_ico': 'res/icons/app_icons/clean_sessions.ico',
    'view_sessions_ico': 'res/icons/app_icons/view_sessions.ico',
    'exit_ico': 'res/icons/app_icons/exit_app.ico',
    'not_found_ico': 'res/icons/app_icons/not_found.ico',
    'artifacts': 'res/icons/no_market_items/artifacts.png',
    'cracked_horn': 'res/icons/no_market_items/cracked_horn.png',
    'cracked_tooth': 'res/icons/no_market_items/cracked_tooth.png',
    'damaged_hide': 'res/icons/no_market_items/damaged_hide.png',
    'intact_horn': 'res/icons/no_market_items/intact_horn.png',
    'intact_tooth': 'res/icons/no_market_items/intact_tooth.png',
    'sharp_horn': 'res/icons/no_market_items/sharp_horn.png',
    'sharp_tooth': 'res/icons/no_market_items/sharp_tooth.png',
    'supreme_hide': 'res/icons/no_market_items/supreme_hide.png',
    'usable_hide': 'res/icons/no_market_items/usable_hide.png',
    'wildspark': 'res/icons/no_market_items/wildspark.png',
    'home_background': 'res/icons/app_images/home_page_background.png',
    'delete_elixir': 'res/icons/app_images/delete_elixir.png',
    'down_arrow': 'res/icons/app_images/down_arrow.png',
    'up_arrow': 'res/icons/app_images/up_arrow.png',
    'left_arrow': 'res/icons/app_images/left_arrow.png',
    'right_arrow': 'res/icons/app_images/right_arrow.png',
    '56221': 'res/icons/no_market_items/breath_of_narcion.png',
    "7923": "res/icons/items/7923.png",
    "6020": "res/icons/items/6020.png",
    "6223": "res/icons/items/6223.png",
    "3544": "res/icons/items/3544.png",
    "3554": "res/icons/items/3554.png",
    "3564": "res/icons/items/3564.png",
    "7904": "res/icons/items/7904.png",
    "6204": "res/icons/items/6204.png",
    "6004": "res/icons/items/6004.png",
    "3540": "res/icons/items/3540.png",
    "3550": "res/icons/items/3550.png",
    "3560": "res/icons/items/3560.png",
    "7901": "res/icons/items/7901.png",
    "6201": "res/icons/items/6201.png",
    "3541": "res/icons/items/3541.png",
    "3551": "res/icons/items/3551.png",
    "3561": "res/icons/items/3561.png",
    "6001": "res/icons/items/6001.png",
    "3542": "res/icons/items/3542.png",
    "3552": "res/icons/items/3552.png",
    "3562": "res/icons/items/3562.png",
    "7913": "res/icons/items/7913.png",
    "6214": "res/icons/items/6214.png",
    "6014": "res/icons/items/6014.png",
    "3543": "res/icons/items/3543.png",
    "3553": "res/icons/items/3553.png",
    "3563": "res/icons/items/3563.png",
    "767969": "res/icons/items/767969.png",
    "767970": "res/icons/items/767970.png",
    "767971": "res/icons/items/767971.png",
    "767972": "res/icons/items/767972.png",
    "767973": "res/icons/items/767973.png",
    "6185": "res/icons/items/6185.png",
    "4999": "res/icons/items/4999.png",
    "5000": "res/icons/items/5000.png",
    "4987": "res/icons/items/4987.png",
    "4998": "res/icons/items/4998.png",
    "721003": "res/icons/items/721003.png",
    "766107": "res/icons/items/766107.png"
}

res_abs_paths: dict[str, str] = {}
settings_json = 'settings/settings.json'  # Path to the settings JSON file
default_settings: dict[str, Any] = {
    "region": "eu",
    "show_confirm_clean_message": True,
    "show_confirm_exit_message": True,
    "value_pack": False,
    "extra_profit": False,
    "auto_calculate_best_profit": False,
    "language": "en-US",
    "elixirs": {}
}
breath_of_narcion_id = "56221"  # ID of the Breath of Narcion item

max_attempts = 3 # Maximum number of attempts to fetch one data from the API
timeout_connection = 1 # Timeout in seconds to establish a connection to the API
timeout_fetch = 5 # Timeout in seconds to fetch data from the API
backoff_time = 0.5 # Time in seconds to wait before retrying a request
time_cached = 60 * 10  # Time in seconds for cache data (10 minutes)

scroll_bar_style = f"""
    QScrollBar:vertical {{ /* Vertical background scroll bar */
        background-color: rgb(50, 50, 50);
        width: 12px;
        margin: 25px 0 25px 0;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:vertical {{ /* Vertical thumb scroll bar */
        background-color: rgb(150, 150, 150);
        min-height: 20px;
        border-radius: 5px;
    }}
    
    QScrollBar:horizontal {{ /* Horizontal background scroll bar */
        background-color: rgb(50, 50, 50);
        height: 12px;
        margin: 0 25px 0 25px;
        border-radius: 5px;
    }}
    
    QScrollBar::handle:horizontal {{ /* Horizontal thumb scroll bar */
        background-color: rgb(150, 150, 150);
        min-width: 20px;
        border-radius: 5px;
    }}

    QScrollBar::sub-line:vertical:hover, 
    QScrollBar::add-line:vertical:hover, 
    QScrollBar::sub-line:horizontal:hover, 
    QScrollBar::add-line:horizontal:hover {{
        background: rgb(200, 200, 200);
    }}
"""

n_damaged_hide_exchange = 60
n_usable_hide_exchange = 50
n_magical_lightstone_exchange = 6 # Number of Magical Lightstones obtained via exchange
n_magical_lightstones_scroll = 35 # Number of Magical Lightstones needed to craft one scroll
n_remnants_of_mystic_beasts_exchange = 70 # Remnants of Mystic Beasts obtained via exchange with "Breath of Narcion/Omua"
n_supreme_hide_scroll = 10 # Number of Supreme Hides needed to craft one scroll
value_pack_multiplier = 0.315 # Value pack multiplier for the results calculation
extra_profit_multiplier = 0.05 # Extra profit multiplier for the results calculation
market_tax = 0.35 # Market tax percentage for the results calculation

NestedDict: TypeAlias = dict[str, dict[str, tuple[str, int]]]
FlatDict: TypeAlias = dict[str, tuple[str, int]]

reduced_item_names = {
    "Concentrated Magical Black Gem": "Conc. Mag. Black Gem",
    "Blessing of Mystic Beasts - All AP": "BMB: All AP",
    "Blessing of Mystic Beasts - Accuracy": "BMB: Accuracy",
    "Blessing of Mystic Beasts - Damage Reduction": "BMB: Damage Reduction",
    "Blessing of Mystic Beasts - Evasion": "BMB: Evasion",
    "Blessing of Mystic Beasts - Max HP": "BMB: Max HP",
    "Black Gem Fragment": "Black Gem Frag.",
    "Sharp Black Crystal Shard": "S. Black Crystal Shard",
    "Imperfect Lightstone of Flora": "Imp. Lightst. of Flora",
    "Stuffed Shadow Lion Head": "St. Shadow Lion Head",
    "Master's Stuffed Shadow Lion Head": "M. St. Shadow Lion Head",
    "Master's Special Stuffed Shadow Lion Head": "M. Sp. St. Shadow Lion Head",
    "Stuffed Grass Rhino Head": "St. Grass Rhino Head",
    "Master's Stuffed Grass Rhino Head": "M. St. Grass Rhino Head",
    "Master's Special Stuffed Grass Rhino Head": "M. Sp. St. Grass Rhino Head",
    "Stuffed Verdure Doe": "St. Verdure Doe",
    "Master's Stuffed Verdure Doe": "M. St. Verdure Doe",
    "Master's Special Stuffed Verdure Doe": "M. Sp. St. Verdure Doe",
    "Stuffed Verdure Buck": "St. Verdure Buck",
    "Master's Stuffed Verdure Buck": "M. St. Verdure Buck",
    "Master's Special Stuffed Verdure Buck": "M. Sp. St. Verdure Buck",
    "Stuffed Shadow Wolf Head": "St. Shadow Wolf Head",
    "Master's Stuffed Shadow Wolf Head": "M. St. Shadow Wolf Head",
    "Master's Special Stuffed Shadow Wolf Head": "M. Sp. St. Shadow Wolf Head"
}