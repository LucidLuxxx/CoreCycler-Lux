import configparser
from PyQt5 import QtWidgets

class YCruncherSettings:
    def __init__(self, config_file, config, app):
        """
        Initialize yCruncher settings with config file and application instance.
        
        Args:
            config_file (str): Path to the config.ini file
            config (configparser.ConfigParser): ConfigParser instance
            app (CoreCyclerApp): Reference to the main application instance
        """
        self.config_file = config_file
        self.config = config
        self.app = app
        self.setup_yCruncher_settings()

    def setup_yCruncher_settings(self):
        """Set up all yCruncher-related settings and connect signals."""
        if "yCruncher" not in self.config:
            self.config["yCruncher"] = {}

        self.setup_mode_settings()
        self.setup_tests_settings()  # For checkBox_29 to checkBox_38
        self.setup_old_tests_settings()  # New method for checkBox_39 to checkBox_47
        self.setup_test_duration_settings()
        self.setup_logging_wrapper_settings()
        self.setup_memory_settings()

    def setup_mode_settings(self):
        """Set up radio buttons (10-22) for the 'mode' setting in [yCruncher]."""
        self.mode_map = {
            10: "04-P4P",
            11: "05-A64 ~ Kasumi",
            12: "08-NHM ~ Ushio",
            13: "11-SNB ~ Hina",
            14: "12-BD2 ~ Miyu",
            15: "13-HSW ~ Airi",
            16: "14-BDW ~ Kurumi",
            17: "17-SKX ~ Kotori",
            18: "17-ZN1 ~ Yukina",
            19: "18-CNL ~ Shinoa",
            20: "19-ZN2 ~ Kagari",
            21: "22-ZN4 ~ Kizuna",
            22: "24-ZN5 ~ Komari"
        }
        
        self.mode_group = QtWidgets.QButtonGroup(self.app)
        
        for i in range(10, 23):
            rb_name = f"radioButton_{i}"
            if hasattr(self.app, rb_name):
                self.mode_group.addButton(getattr(self.app, rb_name), id=i)
            else:
                print(f"Warning: {rb_name} not found in the UI")
        
        self.mode_group.buttonToggled.connect(self.update_mode_config)
        self.set_initial_mode_state()

    def setup_tests_settings(self):
        """Set up checkboxes (29-38) for the 'tests' setting in [yCruncher] when radioButton_4 is selected."""
        self.tests_map = {
            29: "BKT",
            30: "BBP",
            31: "SFT",
            32: "SFTv4",
            33: "SNT",
            34: "SVT",
            35: "FFT",
            36: "FFTv4",
            37: "N63",
            38: "VT3"
        }
        
        for i in range(29, 39):
            cb_name = f"checkBox_{i}"
            if hasattr(self.app, cb_name):
                checkbox = getattr(self.app, cb_name)
                checkbox.stateChanged.connect(self.update_tests_config)
            else:
                print(f"Warning: {cb_name} not found in the UI")
        
        self.set_initial_tests_state()

    def setup_old_tests_settings(self):
        """Set up checkboxes (39-47) for the 'tests' setting in [yCruncher] when radioButton_5 is selected."""
        self.old_tests_map = {
            39: "BKT",
            40: "BBP",
            41: "SFT",
            42: "FFT",
            43: "N32",
            44: "N64",
            45: "HNT",
            46: "VST",
            47: "C17"
        }
        
        for i in range(39, 48):
            cb_name = f"checkBox_{i}"
            if hasattr(self.app, cb_name):
                checkbox = getattr(self.app, cb_name)
                checkbox.stateChanged.connect(self.update_old_tests_config)
            else:
                print(f"Warning: {cb_name} not found in the UI")
        
        self.set_initial_old_tests_state()

    def set_initial_tests_state(self):
        """Set the initial state of the checkboxes (29-38) based on the config."""
        current_tests = self.config["yCruncher"].get("tests", "")
        selected_tests = [test.strip() for test in current_tests.split(",") if test.strip()]
        
        for cb_id, test in self.tests_map.items():
            cb_name = f"checkBox_{cb_id}"
            if hasattr(self.app, cb_name):
                checkbox = getattr(self.app, cb_name)
                checkbox.setChecked(test in selected_tests)

    def set_initial_old_tests_state(self):
        """Set the initial state of the checkboxes (39-47) based on the config."""
        current_tests = self.config["yCruncher"].get("tests", "")
        selected_tests = [test.strip() for test in current_tests.split(",") if test.strip()]
        
        for cb_id, test in self.old_tests_map.items():
            cb_name = f"checkBox_{cb_id}"
            if hasattr(self.app, cb_name):
                checkbox = getattr(self.app, cb_name)
                checkbox.setChecked(test in selected_tests)

    def setup_test_duration_settings(self):
        """Set up spinBox_8 for the 'testDuration' setting in [yCruncher]."""
        if hasattr(self.app, "spinBox_8"):
            self.app.spinBox_8.setMinimum(1)
            self.app.spinBox_8.setMaximum(6000)
            current_duration = self.config["yCruncher"].getint("testDuration", 60)
            if current_duration < 1:
                current_duration = 1
            elif current_duration > 6000:
                current_duration = 6000
            self.app.spinBox_8.setValue(current_duration)
            self.app.spinBox_8.valueChanged.connect(self.update_test_duration)
        else:
            print("Warning: spinBox_8 not found in the UI")

    def setup_logging_wrapper_settings(self):
        """Set up checkBox_49 for the 'enableycruncherloggingwrapper' setting in [yCruncher]."""
        if hasattr(self.app, "checkBox_49"):
            current_state = self.config["yCruncher"].getboolean("enableycruncherloggingwrapper", False)
            self.app.checkBox_49.setChecked(current_state)
            self.app.checkBox_49.stateChanged.connect(self.update_logging_wrapper)
        else:
            print("Warning: checkBox_49 not found in the UI")

    def setup_memory_settings(self):
        """Set up doubleSpinBox_2 and checkBox_48 for the 'memory' setting in [yCruncher]."""
        if hasattr(self.app, "doubleSpinBox_2"):
            # Set range: 0 to 1024
            self.app.doubleSpinBox_2.setMinimum(0)
            self.app.doubleSpinBox_2.setMaximum(1024)
            
            # Set initial value, default to 256 if not "Default"
            current_memory = self.config["yCruncher"].get("memory", "256")
            if current_memory != "Default":
                try:
                    memory_value = float(current_memory)
                    if memory_value < 0:
                        memory_value = 0
                    elif memory_value > 1024:
                        memory_value = 1024
                    self.app.doubleSpinBox_2.setValue(memory_value)
                except ValueError:
                    self.app.doubleSpinBox_2.setValue(256)  # Fallback to 256 if invalid
            else:
                self.app.doubleSpinBox_2.setValue(256)  # Default value when "Default" is set
            
            # Connect signal
            self.app.doubleSpinBox_2.valueChanged.connect(self.update_memory_config)
        else:
            print("Warning: doubleSpinBox_2 not found in the UI")

        if hasattr(self.app, "checkBox_48"):
            # Set initial state: checked if "Default", unchecked otherwise
            current_memory = self.config["yCruncher"].get("memory", "256")
            self.app.checkBox_48.setChecked(current_memory == "Default")
            
            # Connect signal
            self.app.checkBox_48.stateChanged.connect(self.update_memory_config)
        else:
            print("Warning: checkBox_48 not found in the UI")

    def set_initial_mode_state(self):
        """Set the initial state of the radio buttons based on the config."""
        current_mode = self.config["yCruncher"].get("mode", "04-P4P")
        reverse_map = {v: k for k, v in self.mode_map.items()}
        
        if current_mode in reverse_map:
            button_id = reverse_map[current_mode]
            if hasattr(self.app, f"radioButton_{button_id}"):
                getattr(self.app, f"radioButton_{button_id}").setChecked(True)
        else:
            if hasattr(self.app, "radioButton_10"):
                self.app.radioButton_10.setChecked(True)

    def set_initial_tests_state(self):
        """Set the initial state of the checkboxes based on the config."""
        current_tests = self.config["yCruncher"].get("tests", "")
        selected_tests = [test.strip() for test in current_tests.split(",") if test.strip()]
        
        for cb_id, test in self.tests_map.items():
            cb_name = f"checkBox_{cb_id}"
            if hasattr(self.app, cb_name):
                checkbox = getattr(self.app, cb_name)
                checkbox.setChecked(test in selected_tests)

    def update_mode_config(self, button, checked):
        """Update the 'mode' setting in [yCruncher] based on the selected radio button."""
        if not checked:
            return
        
        button_id = self.mode_group.id(button)
        selected_mode = self.mode_map.get(button_id, "04-P4P")
        self.update_config("yCruncher", "mode", selected_mode)
        print(f"Updated yCruncher mode to: {selected_mode}")

    def update_tests_config(self):
        """Update the 'tests' setting in [yCruncher] based on selected checkboxes, only if radioButton_4 is selected."""
        if hasattr(self.app, "radioButton_4") and self.app.radioButton_4.isChecked():
            selected_tests = []
            for cb_id, test in self.tests_map.items():
                cb_name = f"checkBox_{cb_id}"
                if hasattr(self.app, cb_name):
                    checkbox = getattr(self.app, cb_name)
                    if checkbox.isChecked():
                        selected_tests.append(test)
            
            tests_string = ", ".join(selected_tests) if selected_tests else ""
            self.update_config("yCruncher", "tests", tests_string)
            print(f"Updated yCruncher tests to: {tests_string} (radioButton_4 selected)")
        else:
            print("yCruncher not selected (radioButton_4), skipping tests update.")

    def update_old_tests_config(self):
        """Update the 'tests' setting in [yCruncher] based on selected checkboxes, only if radioButton_5 is selected."""
        if hasattr(self.app, "radioButton_5") and self.app.radioButton_5.isChecked():
            selected_tests = []
            for cb_id, test in self.old_tests_map.items():
                cb_name = f"checkBox_{cb_id}"
                if hasattr(self.app, cb_name):
                    checkbox = getattr(self.app, cb_name)
                    if checkbox.isChecked():
                        selected_tests.append(test)
            
            tests_string = ", ".join(selected_tests) if selected_tests else ""
            self.update_config("yCruncher", "tests", tests_string)
            print(f"Updated yCruncher tests to: {tests_string} (radioButton_5 selected)")
        else:
            print("yCruncher Old not selected (radioButton_5), skipping tests update.")

    def update_test_duration(self, value):
        """Update the 'testDuration' setting in [yCruncher] based on spinBox_8 value."""
        self.update_config("yCruncher", "testDuration", value)
        print(f"Updated yCruncher testDuration to: {value}")

    def update_logging_wrapper(self, state):
        """Update the 'enableycruncherloggingwrapper' setting in [yCruncher] based on checkBox_49 state."""
        value = "1" if state else "0"
        self.update_config("yCruncher", "enableycruncherloggingwrapper", value)
        print(f"Updated yCruncher enableycruncherloggingwrapper to: {value}")

    def update_memory_config(self):
        """Update the 'memory' setting in [yCruncher] based on doubleSpinBox_2 and checkBox_48."""
        if hasattr(self.app, "checkBox_48") and self.app.checkBox_48.isChecked():
            memory_value = "Default"
        else:
            if hasattr(self.app, "doubleSpinBox_2"):
                memory_value = self.app.doubleSpinBox_2.value()
            else:
                memory_value = 256  # Fallback if doubleSpinBox_2 is missing
        
        self.update_config("yCruncher", "memory", memory_value)
        print(f"Updated yCruncher memory to: {memory_value}")

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
