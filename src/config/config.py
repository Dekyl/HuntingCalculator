import logging

# Global configuration settings for the application

max_threads = 12 # Maximum number of threads to use for concurrent requests
value_pack_multiplier = 0.315 # Value pack multiplier for the results calculation
extra_profit_multiplier = 0.05 # Extra profit multiplier for the results calculation
log_level = logging.DEBUG # Logging level for the application
threshold_delete_logs = 1024 * 1024  # 1 MB
home_background_path = 'res/icons/home_page_background.png'

res_list = [
    'res/data.json',
    'res/settings.json',
    'res/icons/matchlock.ico',
    'res/icons/settings.ico',
    'res/icons/new_session.ico',
    'res/icons/home.ico',
    'res/icons/clean_sessions.ico',
    'res/icons/view_sessions.ico',
    'res/icons/exit_app.ico',
    'res/icons/not_found.ico',
    'res/icons/artifacts.png',
    'res/icons/breath_of_narcion.png',
    'res/icons/cracked_horn.png',
    'res/icons/cracked_tooth.png',
    'res/icons/damaged_hide.png',
    'res/icons/intact_horn.png',
    'res/icons/intact_tooth.png',
    'res/icons/sharp_horn.png',
    'res/icons/sharp_tooth.png',
    'res/icons/supreme_hide.png',
    'res/icons/usable_hide.png',
    'res/icons/wildspark.png',
    'res/icons/home_page_background.png',
    'res/icons/delete_elixir.png',
]

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

max_attempts = 5 # Maximum number of attempts to fetch one data from the API
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