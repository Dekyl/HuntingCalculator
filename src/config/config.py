import logging
from typing import Any, TypeAlias

# Global configuration settings for the application

max_threads = 12 # Maximum number of threads to use for concurrent requests
log_level = logging.INFO # Logging level for the application
threshold_delete_logs = 1024 * 1024  # 1 MB

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
    'breath_of_narcion': 'res/icons/no_market_items/breath_of_narcion.png',
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
    'right_arrow': 'res/icons/app_images/right_arrow.png'
}

res_abs_paths: dict[str, str] = {}

item_icons_root = 'res/icons/items/'  # Root directory for item icons
settings_json = 'res/settings.json'  # Path to the settings JSON file

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

max_attempts = 3 # Maximum number of attempts to fetch one data from the API
timeout_connection = 1 # Timeout in seconds to establish a connection to the API
timeout_retrieve = 5 # Timeout in seconds to retrieve data from the API
saved_sessions_folder = "Hunting Sessions"  # Folder where hunting sessions are saved
backoff_time = 0.5 # Time in seconds to wait before retrying a request

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