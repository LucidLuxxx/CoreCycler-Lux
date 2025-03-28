import configparser
from PyQt5 import QtWidgets

class Prime95Settings:
    def __init__(self, config_file, config, app):
        """
        Initialize Prime95 settings with config file and application instance.
        
        Args:
            config_file (str): Path to the config.ini file
            config (configparser.ConfigParser): ConfigParser instance
            app (CoreCyclerApp): Reference to the main application instance
        """
        self.config_file = config_file
        self.config = config
        self.app = app
        self.setup_prime95_settings()

    def setup_prime95_settings(self):
        """Set up all Prime95-related settings and connect signals."""
        if "Prime95" not in self.config:
            self.config["Prime95"] = {}
        if "Prime95Custom" not in self.config:
            self.config["Prime95Custom"] = {}

        self.setup_mode_settings()
        self.setup_fft_size_settings()
        self.setup_checkbox_settings()
        self.setup_custom_torture_settings()
        self.setup_cpu_support_settings()

    def setup_mode_settings(self):
        """Set up comboBox_2 for the 'mode' setting."""
        self.mode_map = {
            0: "SSE",
            1: "AVX",
            2: "AVX2",
            3: "AVX512"
        }
        if self.app.comboBox_2.count() == 0:
            for mode in self.mode_map.values():
                self.app.comboBox_2.addItem(mode)
        current_mode = self.config["Prime95"].get("mode", "SSE")
        reverse_map = {v: k for k, v in self.mode_map.items()}
        if current_mode in reverse_map and current_mode != "custom":
            self.app.comboBox_2.setCurrentIndex(reverse_map[current_mode])
        elif current_mode == "custom":
            self.app.comboBox_2.setCurrentIndex(0)
        else:
            self.app.comboBox_2.setCurrentIndex(0)
        self.app.comboBox_2.currentIndexChanged.connect(self.update_mode)

    def setup_fft_size_settings(self):
        """Set up comboBox_8 and lineEdit_4 for the 'fftSize' setting."""
        self.fft_size_map = {
            0: "Huge",
            1: "Smallest",
            2: "Small",
            3: "Large",
            4: "Moderate",
            5: "Heavy",
            6: "HeavyShort",
            7: "All",
            8: "Custom"
        }
        if self.app.comboBox_8.count() == 0:
            for fft_size in self.fft_size_map.values():
                self.app.comboBox_8.addItem(fft_size)
        current_fft_size = self.config["Prime95"].get("fftSize", "Small")
        reverse_map = {v: k for k, v in self.fft_size_map.items()}
        if current_fft_size in reverse_map:
            self.app.comboBox_8.setCurrentIndex(reverse_map[current_fft_size])
            if current_fft_size != "Custom":
                self.app.lineEdit_4.setText("")
        else:
            self.app.comboBox_8.setCurrentIndex(8)
            self.app.lineEdit_4.setText(current_fft_size)
        self.app.comboBox_8.currentIndexChanged.connect(self.update_fft_size_from_combobox)
        self.app.lineEdit_4.textChanged.connect(self.update_fft_size_from_lineedit)

    def setup_checkbox_settings(self):
        """Set up checkBox_11 to override 'mode' to 'custom' when checked."""
        current_mode = self.config["Prime95"].get("mode", "SSE")
        self.app.checkBox_11.setChecked(current_mode == "custom")
        self.app.checkBox_11.stateChanged.connect(self.update_mode_from_checkbox)

    def setup_custom_torture_settings(self):
        """Set up lineEdit_7, lineEdit_8, lineEdit_9, and lineEdit_10 for custom Prime95 settings."""
        min_fft = self.config["Prime95Custom"].get("mintorturefft", "4")
        max_fft = self.config["Prime95Custom"].get("maxtorturefft", "8192")
        torture_mem = self.config["Prime95Custom"].get("torturemem", "0")
        torture_time = self.config["Prime95Custom"].get("torturetime", "1")
        self.app.lineEdit_7.setText(min_fft)
        self.app.lineEdit_8.setText(max_fft)
        self.app.lineEdit_9.setText(torture_mem)
        self.app.lineEdit_10.setText(torture_time)
        self.app.lineEdit_7.textChanged.connect(lambda text: self.update_custom_setting("mintorturefft", text))
        self.app.lineEdit_8.textChanged.connect(lambda text: self.update_custom_setting("maxtorturefft", text))
        self.app.lineEdit_9.textChanged.connect(lambda text: self.update_custom_setting("torturemem", text))
        self.app.lineEdit_10.textChanged.connect(lambda text: self.update_custom_setting("torturetime", text))

    def setup_cpu_support_settings(self):
        """Set up radio buttons to control CPU support settings in a mutually exclusive group."""
        self.cpu_support_group = QtWidgets.QButtonGroup(self.app)
        
        if hasattr(self.app, "radioButton_23"):
            self.cpu_support_group.addButton(self.app.radioButton_23, id=0)
        else:
            print("Warning: radioButton_23 not found in the UI")

        if hasattr(self.app, "radioButton_6"):
            self.cpu_support_group.addButton(self.app.radioButton_6, id=1)
        else:
            print("Warning: radioButton_6 not found in the UI")

        if hasattr(self.app, "radioButton_7"):
            self.cpu_support_group.addButton(self.app.radioButton_7, id=2)
        else:
            print("Warning: radioButton_7 not found in the UI")

        if hasattr(self.app, "radioButton_8"):
            self.cpu_support_group.addButton(self.app.radioButton_8, id=3)
        else:
            print("Warning: radioButton_8 not found in the UI")

        if hasattr(self.app, "radioButton_9"):
            self.cpu_support_group.addButton(self.app.radioButton_9, id=4)
        else:
            print("Warning: radioButton_9 not found in the UI")

        self.cpu_support_group.buttonToggled.connect(self.update_cpu_support_config)
        self.set_initial_cpu_support_state()

    def set_initial_cpu_support_state(self):
        """Set the initial state of the radio buttons based on the config."""
        avx = self.config["Prime95Custom"].getboolean("cpusupportsavx", fallback=False)
        avx2 = self.config["Prime95Custom"].getboolean("cpusupportsavx2", fallback=False)
        fma3 = self.config["Prime95Custom"].getboolean("cpusupportsfma3", fallback=False)
        avx512 = self.config["Prime95Custom"].getboolean("cpusupportsavx512", fallback=False)

        if avx512 and fma3 and avx2 and avx:
            if hasattr(self.app, "radioButton_9"):
                self.app.radioButton_9.setChecked(True)
        elif fma3 and avx2 and avx:
            if hasattr(self.app, "radioButton_8"):
                self.app.radioButton_8.setChecked(True)
        elif avx2 and avx:
            if hasattr(self.app, "radioButton_7"):
                self.app.radioButton_7.setChecked(True)
        elif avx:
            if hasattr(self.app, "radioButton_6"):
                self.app.radioButton_6.setChecked(True)
        else:
            if hasattr(self.app, "radioButton_23"):
                self.app.radioButton_23.setChecked(True)

    def update_cpu_support_config(self, button, checked):
        """Update CPU support settings in [Prime95Custom] based on the selected radio button."""
        if not checked:
            return

        button_id = self.cpu_support_group.id(button)
        
        if button_id == 0:  # radioButton_23 (SSE)
            settings = {
                "cpusupportsavx": "0",
                "cpusupportsavx2": "0",
                "cpusupportsfma3": "0",
                "cpusupportsavx512": "0"
            }
        elif button_id == 1:  # radioButton_6 (AVX)
            settings = {
                "cpusupportsavx": "1",
                "cpusupportsavx2": "0",
                "cpusupportsfma3": "0",
                "cpusupportsavx512": "0"
            }
        elif button_id == 2:  # radioButton_7 (AVX2)
            settings = {
                "cpusupportsavx": "1",
                "cpusupportsavx2": "1",
                "cpusupportsfma3": "0",
                "cpusupportsavx512": "0"
            }
        elif button_id == 3:  # radioButton_8 (FMA3)
            settings = {
                "cpusupportsavx": "1",
                "cpusupportsavx2": "1",
                "cpusupportsfma3": "1",
                "cpusupportsavx512": "0"
            }
        elif button_id == 4:  # radioButton_9 (AVX512)
            settings = {
                "cpusupportsavx": "1",
                "cpusupportsavx2": "1",
                "cpusupportsfma3": "1",
                "cpusupportsavx512": "1"
            }
        else:
            return

        for option, value in settings.items():
            self.update_config("Prime95Custom", option, value)  # Changed from "Prime95" to "Prime95Custom"
        print(f"Updated CPU support settings for button {button_id} in [Prime95Custom]")

    def update_mode(self, index):
        """Update the 'mode' setting based on comboBox_2 selection, if checkBox_11 is unchecked."""
        if not self.app.checkBox_11.isChecked():
            selected_mode = self.mode_map.get(index, "SSE")
            self.update_config("Prime95", "mode", selected_mode)

    def update_mode_from_checkbox(self, state):
        """Update the 'mode' setting based on checkBox_11 state."""
        if state:
            self.update_config("Prime95", "mode", "custom")
        else:
            selected_index = self.app.comboBox_2.currentIndex()
            selected_mode = self.mode_map.get(selected_index, "SSE")
            self.update_config("Prime95", "mode", selected_mode)

    def update_fft_size_from_combobox(self, index):
        """Update the 'fftSize' setting based on comboBox_8 selection."""
        selected_fft_size = self.fft_size_map.get(index, "Small")
        if selected_fft_size == "Custom":
            custom_value = self.app.lineEdit_4.text().strip()
            self.update_config("Prime95", "fftSize", custom_value if custom_value else "Custom")
        else:
            self.update_config("Prime95", "fftSize", selected_fft_size)
            self.app.lineEdit_4.setText("")

    def update_fft_size_from_lineedit(self, text):
        """Update 'fftSize' from lineEdit_4 input when comboBox_8 is on Custom."""
        if self.app.comboBox_8.currentIndex() == 8:
            value = text.strip()
            self.update_config("Prime95", "fftSize", value if value else "Custom")

    def update_custom_setting(self, option, text):
        """Update a custom setting in [Prime95Custom] regardless of checkBox_11 state."""
        value = text.strip()
        if value:
            try:
                int(value)
                self.update_config("Prime95Custom", option, value)
            except ValueError:
                print(f"Invalid input for {option}: {value} (must be an integer)")
                QtWidgets.QMessageBox.warning(self.app, "Invalid Input", f"{option} must be an integer.")
        else:
            defaults = {
                "mintorturefft": "4",
                "maxtorturefft": "8192",
                "torturemem": "0",
                "torturetime": "1"
            }
            self.update_config("Prime95Custom", option, defaults[option])
            getattr(self.app, f"lineEdit_{7 + list(defaults.keys()).index(option)}").setText(defaults[option])

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
