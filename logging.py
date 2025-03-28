import configparser
from PyQt5 import QtWidgets

class LoggingSettings:
    def __init__(self, config_file, config, app):
        """
        Initialize Logging settings with config file and application instance.
        
        Args:
            config_file (str): Path to the config.ini file
            config (configparser.ConfigParser): ConfigParser instance
            app (CoreCyclerApp): Reference to the main application instance
        """
        self.config_file = config_file
        self.config = config
        self.app = app
        self.setup_logging_settings()
        self.load_logging_settings()