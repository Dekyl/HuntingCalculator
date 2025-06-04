import os
from get_prices import search_prices
from get_results import load_data
from logs import setup_logs, add_log
from access_resources import prepare_resources

def setup_all() -> bool:
    """
    Setup all necessary components for the application.
    This function is called at the start of the application to ensure
    that all resources and configurations are ready.
    """
    setup_logs()

    add_log("Starting APP - Setting up all components\n", "info")
    add_log("Preparing resources...", "info")
    prepare_resources()
    add_log("Getting actual item prices...", "info")
    if not search_prices():
        add_log("Failed to get item prices.", "error")
        return False
    
    add_log("Loading data obtained in previous step...", "info")
    if not load_data():
        add_log("Failed to load data from JSON file.", "error")
        return False

    if os.path.exists('./Hunting Sessions') == False:
        os.mkdir('Hunting Sessions')
    
    add_log("Loading app...\n", "info")
    return True