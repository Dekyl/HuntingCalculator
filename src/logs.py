import logging, os

threshold_delete_logs = 1024 * 1024  # 1 MB

logger = logging.getLogger('logs_app')
logger.setLevel(logging.INFO)
log_types = { 'info': logger.info,
              'warning': logger.warning,
              'error': logger.error,
              'debug': logger.debug }

def setup_logs():
    """
    Setup the logging configuration for the application.
    This function initializes the logger with a specific format and level.
    """
    os.makedirs('logs', exist_ok=True) # Ensure the logs directory exists

    if os.path.exists('logs/logs.log'):
        file_size = os.path.getsize('logs/logs.log')
        if file_size > threshold_delete_logs:
            os.remove('logs/logs.log')

    if not logger.hasHandlers():
        handler = logging.FileHandler('./logs/logs.log', mode='a')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

def add_log(message: str, level: str = 'info'):
    """
    Add a log message with the specified level.
    
    :param message: The log message to be recorded.
    :param level: The logging level (default is 'info').
    """
    if level not in log_types:
        logger.warning(f"Unknown level: {level}. Using 'info' as default.")
    log_types.get(level, logger.info)(message)