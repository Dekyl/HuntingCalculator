import logging, os
from threading import Lock
from config.config import log_level, threshold_delete_logs

class LoggerManager:
    """ 
    A singleton class for managing application logs.
    It initializes the logger, sets up the log file,
    and provides methods to add log messages at different levels.
    """
    _instance = None

    def __init__(self):
        """ 
        Initialize the Logger instance.
        This method sets up the logging configuration and ensures that
        only one instance of Logger can exist (singleton pattern).
        """
        if LoggerManager._instance is not None:
            raise Exception("Logger is a singleton!")
        LoggerManager._instance = self

        os.makedirs('logs', exist_ok=True) # Ensure the logs directory exists

        if os.path.exists('logs/logs.log'):
            file_size = os.path.getsize('logs/logs.log')
            if file_size > threshold_delete_logs:
                os.remove('logs/logs.log')

        self.logger = logging.getLogger('logs_app')
        self.logger.setLevel(log_level)  # Set the logging level

        if not self.logger.hasHandlers():
            handler = logging.FileHandler('./logs/logs.log', mode='a')
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        self.log_types = { 'info': self.logger.info,
                      'warning': self.logger.warning,
                      'error': self.logger.error,
                      'debug': self.logger.debug }
        
        self.lock = Lock()  # Create a lock for thread-safe logging

        self.register_log("Logger initialized. Begin registering logs", "info")

    def register_log(self, message: str, level: str = 'info'):
        """
        Add a log message with the specified level.
        
        :param message: The log message to be recorded.
        :param level: The logging level (default is 'info').
        """
        with self.lock:
            if level not in self.log_types:
                self.logger.warning(f"Unknown level: {level}. Using 'info' as default.")
            self.log_types.get(level, self.logger.info)(message)

    @staticmethod
    def get_instance() -> "LoggerManager":
        """
        Get the singleton instance of the Logger class.
        If the instance does not exist, it creates one.
        """
        if LoggerManager._instance is None:
            raise Exception("Logger instance not created. Call Logger first.")
        return LoggerManager._instance
    
def add_log(message: str, level: str = 'info'):
    """
    Add a log message using the LoggerManager singleton instance.
    
    :param message: The log message to be recorded.
    :param level: The logging level (default is 'info').
    """
    logger = LoggerManager.get_instance()
    logger.register_log(message, level)