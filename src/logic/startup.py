from logic.logs import setup_logs, add_log
from logic.prepare_resources import startup_resources

def setup_all() -> bool:
    """
    Setup all necessary components for the application.
    This function is called at the start of the application to ensure
    that all resources and configurations are ready.
    It initializes logging, prepares resources, and loads the application.
        :return: True if setup is successful, False otherwise.
    """
    setup_logs()
    add_log("Starting APP - Setting up all components\n", "info")
    add_log("Preparing resources...", "info")
    if not startup_resources():
        add_log("Failed to prepare resources. Exiting application.", "error")
        return False
    add_log("Loading app...\n", "info")
    return True