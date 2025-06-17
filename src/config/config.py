import logging

# Global configuration settings for the application

max_threads = 12 # Maximum number of threads to use for concurrent requests
value_pack_multiplier = 0.315 # Value pack multiplier for the results calculation
extra_profit_multiplier = 0.05 # Extra profit multiplier for the results calculation
log_level = logging.DEBUG # Logging level for the application
threshold_delete_logs = 1024 * 1024  # 1 MB
home_background_path = 'res/icons/app_images/home_page_background.png'

res_list = {
    'data': 'res/data.json',
    'settings': 'res/settings.json',
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

item_icons_root = 'res/icons/items/'  # Root directory for item icons
no_market_items_root = 'res/icons/no_market_items/'  # Root directory for no market items icons

json_files = {
    'res/data.json': 'data.json',
    'res/settings.json': 'settings.json'
}

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
    "Master's Special Stuffed Shadow Lion Head": "M. St. Sp. Shadow Lion Head",
    "Stuffed Grass Rhino Head": "St. Grass Rhino Head",
    "Master's Stuffed Grass Rhino Head": "M. St. Grass Rhino Head",
    "Master's Special Stuffed Grass Rhino Head": "M. St. Sp. Grass Rhino Head",
    "Stuffed Vedure Doe Head": "St. Vedure Doe Head",
    "Master's Stuffed Vedure Doe Head": "M. St. Vedure Doe Head",
    "Master's Special Stuffed Vedure Doe Head": "M. St. Sp. Vedure Doe Head",
    "Stuffed Verdure Buck Head": "St. Verdure Buck Head",
    "Master's Stuffed Verdure Buck Head": "M. St. Verdure Buck Head",
    "Master's Special Stuffed Verdure Buck Head": "M. St. Sp. Verdure Buck Head",
    "Stuffed Shadow Wolf Head": "St. Shadow Wolf Head",
    "Master's Stuffed Shadow Wolf Head": "M. St. Shadow Wolf Head",
    "Master's Special Stuffed Shadow Wolf Head": "M. St. Sp. Shadow Wolf Head",
}

max_attempts = 2 # Maximum number of attempts to fetch one data from the API
timeout_connection = 1 # Timeout for the connection in seconds

settings_keys = [
    "region",
    "show_confirm_clean_message",
    "show_confirm_exit_message",
    "value_pack",
    "extra_profit",
    "language",
    "elixirs"
]

saved_sessions_folder = "Hunting Sessions"  # Folder where hunting sessions are saved