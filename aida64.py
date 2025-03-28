# aida64.py
import configparser

class Aida64Settings:
    def __init__(self, config_file, config, app):
        self.config_file = config_file
        self.config = config
        self.app = app  # Reference to the CoreCyclerApp instance
        self.setup_aida64_settings()

    def setup_aida64_settings(self):
        """Set up the Aida64 settings and connect checkbox and spinbox signals."""
        # Ensure [Aida64] section exists in config
        if "Aida64" not in self.config:
            self.config["Aida64"] = {}

        # Load initial mode from config
        initial_mode = self.config["Aida64"].get("mode", "CACHE")
        mode_list = [m.strip() for m in initial_mode.split(",")]

        # Map checkboxes to their corresponding mode values
        self.checkbox_map = {
            "CACHE": self.app.checkBox_24,
            "CPU": self.app.checkBox_25,
            "FPU": self.app.checkBox_26,
            "RAM": self.app.checkBox_27
        }

        # Set initial checkbox states based on config
        for mode, checkbox in self.checkbox_map.items():
            checkbox.setChecked(mode in mode_list)

        # Connect checkbox signals to update_config method
        self.app.checkBox_24.stateChanged.connect(self.update_mode)
        self.app.checkBox_25.stateChanged.connect(self.update_mode)
        self.app.checkBox_26.stateChanged.connect(self.update_mode)
        self.app.checkBox_27.stateChanged.connect(self.update_mode)

        # Load and set initial state for useavx checkbox (checkBox_28)
        use_avx = self.config["Aida64"].getboolean("useavx", fallback=False)
        self.app.checkBox_28.setChecked(use_avx)
        # Connect checkBox_28 signal to update_useavx method
        self.app.checkBox_28.stateChanged.connect(self.update_useavx)

        # Load and set initial value for maxmemory spinbox (spinBox_7)
        max_memory = self.config["Aida64"].getint("maxmemory", fallback=90)
        self.app.spinBox_7.setRange(0, 100)  # Set range from 0 to 100
        self.app.spinBox_7.setValue(max_memory)  # Set initial value
        # Connect spinBox_7 signal to update_maxmemory method
        self.app.spinBox_7.valueChanged.connect(self.update_maxmemory)

    def update_mode(self):
        """Update the 'mode' setting in [Aida64] section based on checkbox states."""
        selected_modes = []
        for mode, checkbox in self.checkbox_map.items():
            if checkbox.isChecked():
                selected_modes.append(mode)

        # If no modes are selected, default to "CACHE"
        if not selected_modes:
            selected_modes.append("CACHE")

        # Join selected modes with commas
        mode_value = ", ".join(selected_modes)
        self.update_config("mode", mode_value)

    def update_useavx(self, state):
        """Update the 'useavx' setting in [Aida64] section based on checkBox_28 state."""
        value = 1 if state else 0
        self.update_config("useavx", value)

    def update_maxmemory(self, value):
        """Update the 'maxmemory' setting in [Aida64] section based on spinBox_7 value."""
        self.update_config("maxmemory", value)

    def update_config(self, option, value):
        """Update a setting in the [Aida64] section of config.ini and save it."""
        try:
            if "Aida64" not in self.config:
                self.config["Aida64"] = {}
            self.config["Aida64"][option] = str(value)
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
            print(f"Updated config.ini: [Aida64] {option} = {value}")
        except Exception as e:
            print(f"Error writing to config.ini: {e}")
