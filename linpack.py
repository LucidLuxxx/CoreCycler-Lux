import configparser
from PyQt5 import QtWidgets

class LinpackSettings:
    def __init__(self, config_file, config, app):
        """
        Initialize Linpack settings with config file and application instance.
        
        Args:
            config_file (str): Path to the config.ini file
            config (configparser.ConfigParser): ConfigParser instance
            app (CoreCyclerApp): Reference to the main application instance
        """
        self.config_file = config_file
        self.config = config
        self.app = app
        self.setup_linpack_settings()

    def setup_linpack_settings(self):
        """Set up all Linpack-related settings and connect signals."""
        if "Linpack" not in self.config:
            self.config["Linpack"] = {}

        self.setup_version_settings()
        self.setup_mode_settings()
        self.setup_memory_settings()  # New method for comboBox_7

    def setup_version_settings(self):
        """Set up comboBox_5 for the 'version' setting in [Linpack]."""
        self.version_map = {
            0: "2018",
            1: "2019",
            2: "2021",
            3: "2024"
        }
        
        if self.app.comboBox_5.count() == 0:
            for version in self.version_map.values():
                self.app.comboBox_5.addItem(version)
        
        current_version = self.config["Linpack"].get("memory", "2018")
        reverse_map = {v: k for k, v in self.version_map.items()}
        if current_version in reverse_map:
            self.app.comboBox_5.setCurrentIndex(reverse_map[current_version])
        else:
            self.app.comboBox_5.setCurrentIndex(0)
        
        self.app.comboBox_5.currentIndexChanged.connect(self.update_version)

    def setup_mode_settings(self):
        """Set up comboBox_6 for the 'mode' setting in [Linpack]."""
        self.mode_map = {
            0: "Medium",
            1: "Slowest",
            2: "Slow",
            3: "Fast",
            4: "Fastest"
        }
        
        if self.app.comboBox_6.count() == 0:
            for mode in self.mode_map.values():
                self.app.comboBox_6.addItem(mode)
        
        current_mode = self.config["Linpack"].get("mode", "Medium")
        reverse_map = {v: k for k, v in self.mode_map.items()}
        if current_mode in reverse_map:
            self.app.comboBox_6.setCurrentIndex(reverse_map[current_mode])
        else:
            self.app.comboBox_6.setCurrentIndex(0)
        
        self.app.comboBox_6.currentIndexChanged.connect(self.update_mode)

    def setup_memory_settings(self):
        """Set up comboBox_7 for the 'memory' setting in [Linpack]."""
        # Define possible Linpack memory options
        self.memory_map = {
            0: "2GB",
            1: "100MB",
            2: "250MB",
            3: "500MB",
            4: "750MB",
            5: "1GB",
            6: "4GB",
            7: "6GB",
            8: "30GB"
        }
        
        # Populate comboBox_7 if it’s empty
        if self.app.comboBox_7.count() == 0:
            for memory in self.memory_map.values():
                self.app.comboBox_7.addItem(memory)
        
        # Set the current selection based on config
        current_memory = self.config["Linpack"].get("memory", "2GB")  # Default to 2GB
        reverse_map = {v: k for k, v in self.memory_map.items()}
        if current_memory in reverse_map:
            self.app.comboBox_7.setCurrentIndex(reverse_map[current_memory])
        else:
            self.app.comboBox_7.setCurrentIndex(0)  # Default to 2GB
        
        # Connect the comboBox_7 signal to update the config
        self.app.comboBox_7.currentIndexChanged.connect(self.update_memory)

    def update_version(self, index):
        """Update the 'version' setting in [Linpack] based on comboBox_5 selection."""
        selected_version = self.version_map.get(index, "2018")
        self.update_config("Linpack", "version", selected_version)

    def update_mode(self, index):
        """Update the 'mode' setting in [Linpack] based on comboBox_6 selection."""
        selected_mode = self.mode_map.get(index, "Medium")
        self.update_config("Linpack", "mode", selected_mode)

    def update_memory(self, index):
        """Update the 'memory' setting in [Linpack] based on comboBox_7 selection."""
        selected_memory = self.memory_map.get(index, "2GB")  # Default to 2GB if index is invalid
        self.update_config("Linpack", "memory", selected_memory)

    def update_config(self, section, option, value):
        """Update a setting in the specified section of config.ini and save it."""
        try:
            if section not in self.config:
                self.config[section] = {}
            self.config[section][option] = str(value)
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
            print(f"Updated config.ini: [{section}] {option} = {value}")
        except Exception as e:
            print(f"Error writing to config.ini: {e}")
            QtWidgets.QMessageBox.critical(self.app, "Error", f"Failed to update config: {str(e)}")
