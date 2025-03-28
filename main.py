# main.py
import sys
import configparser
import subprocess
import os
import glob
from PyQt5 import QtWidgets, QtCore, QtGui

# ===========================================
# Ui_CoreCycler Class (from CoreCycler.py)
# ===========================================
class Ui_CoreCycler:
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.comboBox_5 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_5.setGeometry(QtCore.QRect(50, 50, 200, 30))
        self.comboBox_5.setObjectName("comboBox_5")
        self.comboBox_6 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_6.setGeometry(QtCore.QRect(50, 100, 200, 30))
        self.comboBox_6.setObjectName("comboBox_6")
        self.comboBox_7 = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox_7.setGeometry(QtCore.QRect(50, 150, 200, 30))
        self.comboBox_7.setObjectName("comboBox_7")
        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "CoreCycler"))

# ===========================================
# LinpackSettings Class
# ===========================================
class LinpackSettings:
    def __init__(self, config_file, config, app):
        self.config_file = config_file
        self.config = config
        self.app = app
        self.setup_linpack_settings()

    def setup_linpack_settings(self):
        if "Linpack" not in self.config:
            self.config["Linpack"] = {}

        self.setup_version_settings()
        self.setup_mode_settings()
        self.setup_memory_settings()

    def setup_version_settings(self):
        self.version_map = {0: "2018", 1: "2019", 2: "2021", 3: "2024"}
        if self.app.comboBox_5.count() == 0:
            for version in self.version_map.values():
                self.app.comboBox_5.addItem(version)

        current_version = self.config["Linpack"].get("version", "2018")
        reverse_map = {v: k for k, v in self.version_map.items()}
        self.app.comboBox_5.setCurrentIndex(reverse_map.get(current_version, 0))
        self.app.comboBox_5.currentIndexChanged.connect(self.update_version)

    def setup_mode_settings(self):
        self.mode_map = {0: "Medium", 1: "Slowest", 2: "Slow", 3: "Fast", 4: "Fastest"}
        if self.app.comboBox_6.count() == 0:
            for mode in self.mode_map.values():
                self.app.comboBox_6.addItem(mode)

        current_mode = self.config["Linpack"].get("mode", "Medium")
        reverse_map = {v: k for k, v in self.mode_map.items()}
        self.app.comboBox_6.setCurrentIndex(reverse_map.get(current_mode, 0))
        self.app.comboBox_6.currentIndexChanged.connect(self.update_mode)

    def setup_memory_settings(self):
        self.memory_map = {
            0: "2GB", 1: "100MB", 2: "250MB", 3: "500MB", 4: "750MB",
            5: "1GB", 6: "4GB", 7: "6GB", 8: "30GB"
        }
        if self.app.comboBox_7.count() == 0:
            for memory in self.memory_map.values():
                self.app.comboBox_7.addItem(memory)

        current_memory = self.config["Linpack"].get("memory", "2GB")
        reverse_map = {v: k for k, v in self.memory_map.items()}
        self.app.comboBox_7.setCurrentIndex(reverse_map.get(current_memory, 0))
        self.app.comboBox_7.currentIndexChanged.connect(self.update_memory)

    def update_version(self, index):
        selected_version = self.version_map.get(index, "2018")
        self.update_config("Linpack", "version", selected_version)

    def update_mode(self, index):
        selected_mode = self.mode_map.get(index, "Medium")
        self.update_config("Linpack", "mode", selected_mode)

    def update_memory(self, index):
        selected_memory = self.memory_map.get(index, "2GB")
        self.update_config("Linpack", "memory", selected_memory)

    def update_config(self, section, option, value):
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

# ===========================================
# Prime95Settings Class (originally from prime95.py)
# ===========================================
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
            self.update_config("Prime95Custom", option, value)
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

# ===========================================
# YCruncherSettings Class (originally from ycruncher.py)
# ===========================================
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

# ===========================================
# Aida64Settings Class (originally from aida64.py)
# ===========================================
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
        mode_list = [m.strip()for m in initial_mode.split(",")]

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

# ===========================================
# GeneralSettings Class (already in main.py)
# ===========================================
class GeneralSettings:
    def __init__(self, config_file, config):
        self.config_file = config_file
        self.config = config
        self.app = None  # Will store reference to CoreCyclerApp instance

    def update_config(self, option, value):
        """Update a setting in the [General] section of config.ini and save it."""
        try:
            if "General" not in self.config:
                self.config["General"] = {}
            self.config["General"][option] = str(value)
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
            print(f"Updated config.ini: [General] {option} = {value}")
        except Exception as e:
            print(f"Error writing to config.ini: {e}")
            return False
        return True

    def load_general_settings(self):
        """Load initial settings from [General] section into variables."""
        selected_program = self.config["General"].get("stressTestProgram", "PRIME95")
        return selected_program

    def load_checkbox_settings(self, checkboxes):
        """Load checkbox settings from [General] section."""
        settings = {}
        for option, checkbox in checkboxes.items():
            value = self.config.get("General", option, fallback="0")
            settings[option] = value == "1"
        return settings

    def get_runtime_per_core(self):
        """Get runtimePerCore setting from [General] section."""
        return self.config["General"].get("runtimePerCore", "auto")

    def get_config_file_path(self):
        """Get useConfigFile setting from [General] section."""
        return self.config["General"].get("useConfigFile", "")

    def setup_general_controls(self, app):
        """Set up controls for maxIterations, delayBetweenCores, coresToIgnore, and coreTestOrder."""
        self.app = app  # Store reference to the app instance

        # Load and set up spinBox_12 for maxIterations
        max_iterations = self.config.getint("General", "maxIterations", fallback=5)
        self.app.spinBox_12.setValue(max_iterations)
        self.app.spinBox_12.valueChanged.connect(self.update_max_iterations)

        # Load and set up spinBox_2 for delayBetweenCores
        delay_between_cores = self.config.getint("General", "delayBetweenCores", fallback=15)
        self.app.spinBox_2.setValue(delay_between_cores)
        self.app.spinBox_2.valueChanged.connect(self.update_delay_between_cores)

        # Load and set up lineEdit for coresToIgnore
        ignored_cores = self.config.get("General", "coresToIgnore", fallback="")
        self.app.lineEdit.setText(ignored_cores)
        self.app.lineEdit.textChanged.connect(self.update_ignored_cores)

        # Existing coreTestOrder setup
        self.setup_core_test_order_controls(app)

    def update_max_iterations(self, value):
        """Update maxIterations setting from spinBox_12."""
        self.update_config("maxIterations", value)

    def update_delay_between_cores(self, value):
        """Update delayBetweenCores setting from spinBox_2."""
        self.update_config("delayBetweenCores", value)

    def update_ignored_cores(self, text):
        """Update coresToIgnore setting from lineEdit."""
        value = text.strip()
        self.update_config("coresToIgnore", value)

    def setup_core_test_order_controls(self, app):
        """Set up lineEdit_6 and comboBox_1 for coreTestOrder and connect signals."""
        # Load initial coreTestOrder value
        core_test_order = self.config.get("General", "coreTestOrder", fallback="Default")
        
        # Map comboBox_1 indices to coreTestOrder values
        self.order_map = {
            0: "Default",
            1: "Alternate",
            2: "Sequential",
            3: "Random",
            4: "Custom"
        }
        
        # Reverse map for setting comboBox_1 index
        reverse_map = {v: k for k, v in self.order_map.items()}

        # Set initial state of comboBox_1 and lineEdit_6
        if core_test_order in reverse_map:
            app.comboBox_1.setCurrentIndex(reverse_map[core_test_order])
            if core_test_order != "Custom":
                app.lineEdit_6.setText("")  # Clear lineEdit_6 for predefined options
            else:
                # If "Custom" was saved, load the last custom value if available
                app.lineEdit_6.setText(self.config.get("General", "coreTestOrder", fallback=""))
        else:
            app.comboBox_1.setCurrentIndex(4)  # Set to "Custom"
            app.lineEdit_6.setText(core_test_order)  # Display custom value

        # Connect lineEdit_6 signal
        app.lineEdit_6.textChanged.connect(self.update_core_test_order_from_lineedit)

        # Connect comboBox_1 signal
        app.comboBox_1.currentIndexChanged.connect(self.update_core_test_order_from_combobox)

    def update_core_test_order_from_lineedit(self, text):
        """Update coreTestOrder from lineEdit_6 input when comboBox_1 is on Custom."""
        if self.app.comboBox_1.currentIndex() == 4:  # Only update if "Custom" is selected
            value = text.strip()
            if value:  # Only update if there's actual input
                self.update_config("coreTestOrder", value)
            else:
                self.update_config("coreTestOrder", "Custom")  # Default to "Custom" if empty

    def update_core_test_order_from_combobox(self, index):
        """Update coreTestOrder from comboBox_1 selection."""
        value = self.order_map.get(index, "Default")
        if value == "Custom":
            # Use the current text in lineEdit_6, or "Custom" if empty
            custom_value = self.app.lineEdit_6.text().strip()
            self.update_config("coreTestOrder", custom_value if custom_value else "Custom")
        else:
            self.update_config("coreTestOrder", value)
            self.app.lineEdit_6.setText("")  # Clear lineEdit_6 for non-Custom options

# ===========================================
# AutomatedSettings Class (already in main.py)
# ===========================================
class AutomatedSettings:
    def __init__(self, config_file, config, app):
        self.config_file = config_file
        self.config = config
        self.app = app  # Reference to the CoreCyclerApp instance
        self.setup_automated_settings()

    def setup_automated_settings(self):
        """Set up the automated test settings and connect signals."""
        # Load initial states from config
        if "AutomaticTestMode" in self.config:
            self.app.checkBox_1.setChecked(self.config.getboolean("AutomaticTestMode", "enableAutomaticAdjustment", fallback=False))
            self.app.checkBox_17.setChecked(self.config.getboolean("AutomaticTestMode", "repeatCoreOnError", fallback=False))
            self.app.checkBox_18.setChecked(self.config.getboolean("AutomaticTestMode", "enableResumeAfterUnexpectedExit", fallback=False))

            # Handle maxValue with spinBox_11
            max_value = self.config.getint("AutomaticTestMode", "maxValue", fallback=5)
            self.app.spinBox_11.setValue(max_value)

            # Handle incrementBy with spinBox_10
            increment_by = self.config.getint("AutomaticTestMode", "incrementBy", fallback=1)
            self.app.spinBox_10.setValue(increment_by)

            # Handle startValues with lineEdit_3
            start_values = self.config.get("AutomaticTestMode", "startValues", fallback="Default")
            self.app.lineEdit_3.setText(start_values)

        # Connect checkbox signals
        self.app.checkBox_1.stateChanged.connect(lambda state: self.update_config("enableAutomaticAdjustment", 1 if state else 0))
        self.app.checkBox_17.stateChanged.connect(lambda state: self.update_config("repeatCoreOnError", 1 if state else 0))
        self.app.checkBox_18.stateChanged.connect(lambda state: self.update_config("enableResumeAfterUnexpectedExit", 1 if state else 0))
        
        # Connect spin box signals
        self.app.spinBox_11.valueChanged.connect(lambda value: self.update_config("maxValue", value))
        self.app.spinBox_10.valueChanged.connect(lambda value: self.update_config("incrementBy", value))

        # Connect lineEdit_3 signal
        self.app.lineEdit_3.textChanged.connect(self.update_start_values)

    def update_config(self, option, value):
        """Update a setting in the [AutomaticTestMode] section of config.ini and save it."""
        try:
            if "AutomaticTestMode" not in self.config:
                self.config["AutomaticTestMode"] = {}
            self.config["AutomaticTestMode"][option] = str(value)
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
            print(f"Updated config.ini: [AutomaticTestMode] {option} = {value}")
        except Exception as e:
            print(f"Error writing to config.ini: {e}")

    def update_start_values(self, text):
        """Update the startValues setting based on lineEdit_3 input."""
        value = text.strip()
        if not value:  # If the input is empty
            value = "Default"
        self.update_config("startValues", value)

# ===========================================
# Main Application Class (already in main.py)
# ===========================================
class CoreCyclerApp(QtWidgets.QMainWindow, Ui_CoreCycler):
    def __init__(self):
        super().__init__()
        
        # Configuration file setup
        self.config_file = "config.ini"
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        self.general = GeneralSettings(self.config_file, self.config)  # Initialize General settings

        # Initialize UI elements first
        self.setupUi(self)  # This attaches all UI elements to self
        
        # Now initialize settings classes after UI is set up
        self.automated = AutomatedSettings(self.config_file, self.config, self)  # Initialize Automated settings
        self.prime95 = Prime95Settings(self.config_file, self.config, self)  # Add Prime95 settings
        self.linpack_settings = LinpackSettings(self.config_file, self.config, self)
        self.yCruncher_settings = YCruncherSettings(self.config_file, self.config, self)  # New initialization
        self.aida64_settings = Aida64Settings(self.config_file, self.config, self)  # Add Aida64 settings

        # Continue with other setup
        self.setup_test_buttons()
        self.load_settings()
        self.setup_checkboxes()
        self.setup_spinbox()
        self.setup_config_file_controls()
        self.setup_runtime_per_core()
        self.setup_update_frequency()
        self.general.setup_general_controls(self)  # Set up general controls including core test order
        
        # Connect push buttons
        self.pushButton_1.clicked.connect(self.launch_core_cycler)
        self.pushButton_4.clicked.connect(self.launch_boost_tester)
        self.pushButton_5.clicked.connect(self.launch_pbo2_tuner)
        self.pushButton_6.clicked.connect(self.launch_intel_voltage_control)
        self.pushButton_8.clicked.connect(self.launch_apicid)
        self.pushButton_9.clicked.connect(self.launch_core_tuner_x)
        self.pushButton_10.clicked.connect(self.run_performance_counters)
        self.pushButton_12.clicked.connect(self.open_script_folder)

        self.checkBox_14.stateChanged.connect(self.update_enable_update_check)

    def setup_test_buttons(self):
        self.testButtonGroup = QtWidgets.QButtonGroup(self)
        self.testButtonGroup.addButton(self.radioButton_1, id=1)  # PRIME95
        self.testButtonGroup.addButton(self.radioButton_2, id=2)  # LINPACK
        self.testButtonGroup.addButton(self.radioButton_3, id=3)  # AIDA64
        self.testButtonGroup.addButton(self.radioButton_4, id=4)  # YCRUNCHER
        self.testButtonGroup.addButton(self.radioButton_5, id=5)  # YCRUNCHER_OLD
        self.testButtonGroup.buttonToggled.connect(self.on_test_selection)

    def setup_checkboxes(self):
        general_checkboxes = {
            "skipCoreOnError": self.checkBox_2,
            "stopOnError": self.checkBox_3,
            "assignBothVirtualCoresForSingleThread": self.checkBox_4,
            "suspendPeriodically": self.checkBox_5,
            "beepOnError": self.checkBox_6,
            "flashOnError": self.checkBox_7,
            "lookForWheaErrors": self.checkBox_8,
            "treatWheaWarningAsError": self.checkBox_9,
            "restartTestProgramForEachCore": self.checkBox_10
        }
        settings = self.general.load_checkbox_settings(general_checkboxes)
        for option, value in settings.items():
            general_checkboxes[option].setChecked(value)

        self.checkBox_2.stateChanged.connect(lambda state: self.general.update_config("skipCoreOnError", 1 if state else 0))
        self.checkBox_3.stateChanged.connect(lambda state: self.general.update_config("stopOnError", 1 if state else 0))
        self.checkBox_4.stateChanged.connect(lambda state: self.general.update_config("assignBothVirtualCoresForSingleThread", 1 if state else 0))
        self.checkBox_5.stateChanged.connect(lambda state: self.general.update_config("suspendPeriodically", 1 if state else 0))
        self.checkBox_6.stateChanged.connect(lambda state: self.general.update_config("beepOnError", 1 if state else 0))
        self.checkBox_7.stateChanged.connect(lambda state: self.general.update_config("flashOnError", 1 if state else 0))
        self.checkBox_8.stateChanged.connect(lambda state: self.general.update_config("lookForWheaErrors", 1 if state else 0))
        self.checkBox_9.stateChanged.connect(lambda state: self.general.update_config("treatWheaWarningAsError", 1 if state else 0))
        self.checkBox_10.stateChanged.connect(lambda state: self.general.update_config("restartTestProgramForEachCore", 1 if state else 0))

    def setup_spinbox(self):
        self.spinBox1.valueChanged.connect(lambda value: self.general.update_config("numberOfThreads", value))

    def setup_config_file_controls(self):
        try:
            config_file_path = self.general.get_config_file_path()
            self.lineEdit_11.setText(config_file_path)
            self.checkBox_12.setChecked(bool(config_file_path))
            self.checkBox_12.stateChanged.connect(self.on_config_checkbox_changed)
            self.lineEdit_11.textChanged.connect(self.on_config_path_changed)
            print("Successfully set up config file controls")
        except Exception as e:
            print(f"Error setting up config file controls: {e}")

    def setup_runtime_per_core(self):
        try:
            runtime_value = self.general.get_runtime_per_core()
            if runtime_value.lower() == "auto":
                self.spinBox_9.setValue(0)
            else:
                numeric_value = runtime_value.replace("m", "").strip()
                try:
                    self.spinBox_9.setValue(int(numeric_value))
                except ValueError:
                    self.spinBox_9.setValue(0)
            self.spinBox_9.setSuffix("m")
            self.spinBox_9.valueChanged.connect(self.on_runtime_changed)
            print("Successfully set up runtime per core control")
        except Exception as e:
            print(f"Error setting up runtime per core control: {e}")

    def setup_update_frequency(self):
        try:
            frequency_hours = self.config["Update"].get("updateCheckFrequency", "24")
            try:
                frequency_days = int(frequency_hours) // 24
            except ValueError:
                frequency_days = 1
            self.spinBox_3.setValue(frequency_days)
            self.spinBox_3.setMinimum(1)
            self.spinBox_3.valueChanged.connect(self.update_check_frequency)
            print("Successfully set up update frequency control")
        except Exception as e:
            print(f"Error setting up update frequency control: {e}")

    def load_settings(self):
        selected_program = self.general.load_general_settings()
        selection_map = {
            "PRIME95": self.radioButton_1,
            "LINPACK": self.radioButton_2,
            "AIDA64": self.radioButton_3,
            "YCRUNCHER": self.radioButton_4,
            "YCRUNCHER_OLD": self.radioButton_5
        }
        if selected_program in selection_map:
            selection_map[selected_program].setChecked(True)

        if "Update" in self.config:
            enable_update = self.config.getboolean("Update", "enableUpdateCheck", fallback=False)
            self.checkBox_14.setChecked(enable_update)

    def update_config(self, section, option, value):
        try:
            if section not in self.config:
                self.config[section] = {}
            self.config[section][option] = str(value)
            with open(self.config_file, 'w') as configfile:
                self.config.write(configfile)
            print(f"Updated config.ini: [{section}] {option} = {value}")
        except Exception as e:
            print(f"Error writing to config.ini: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to write to config: {str(e)}")

    def on_test_selection(self, button, checked):
        if checked:
            selection_map = {
                1: "PRIME95",
                2: "LINPACK",
                3: "AIDA64",
                4: "YCRUNCHER",
                5: "YCRUNCHER_OLD"
            }
            selected_test = selection_map[self.testButtonGroup.id(button)]
            self.general.update_config("stressTestProgram", selected_test)

    def on_runtime_changed(self, value):
        if value == 0:
            self.spinBox_9.setSpecialValueText("Auto")
            self.general.update_config("runtimePerCore", "auto")
        else:
            runtime_value = f"{value}m"
            self.spinBox_9.setSpecialValueText("")
            self.general.update_config("runtimePerCore", runtime_value)

    def on_config_checkbox_changed(self, state):
        if state:
            config_path = self.lineEdit_11.text().strip()
            if config_path:
                self.general.update_config("useConfigFile", config_path)
        else:
            self.general.update_config("useConfigFile", "")

    def on_config_path_changed(self, text):
        if self.checkBox_12.isChecked():
            config_path = text.strip()
            self.general.update_config("useConfigFile", config_path)

    def update_enable_update_check(self, state):
        enabled = state == QtCore.Qt.Checked
        self.update_config("Update", "enableUpdateCheck", 1 if enabled else 0)

    def update_check_frequency(self, days):
        hours = days * 24
        self.update_config("Update", "updateCheckFrequency", hours)

    def launch_core_cycler(self):
        try:
            working_dir = os.path.dirname(os.path.abspath(__file__))
            bat_path = os.path.join(working_dir, "Run CoreCycler.bat")
            command = f'Start-Process "{bat_path}" -Verb RunAs'
            subprocess.Popen(["powershell", "-Command", command], shell=True)
            print(f"Requested admin launch for {bat_path}")
        except FileNotFoundError:
            print(f"Error: {bat_path} not found.")
            QtWidgets.QMessageBox.warning(self, "Error", f"Could not find {bat_path}")
        except Exception as e:
            print(f"Error launching Run CoreCycler.bat: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to launch Run CoreCycler.bat: {str(e)}")

    def launch_boost_tester(self):
        try:
            exe_path = r"tools\BoostTester.sp00n.exe"
            subprocess.Popen([exe_path], creationflags=subprocess.CREATE_NEW_CONSOLE)
            print(f"Launched {exe_path} in a new console window")
        except FileNotFoundError:
            print(f"Error: {exe_path} not found.")
            QtWidgets.QMessageBox.warning(self, "Error", f"Could not find {exe_path}")
        except Exception as e:
            print(f"Error launching BoostTester: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to launch BoostTester: {str(e)}")

    def launch_pbo2_tuner(self):
        try:
            exe_path = r"tools\PBO2Tuner\PBO2Tuner.exe"
            command = f'Start-Process "{exe_path}" -Verb RunAs'
            subprocess.Popen(["powershell", "-Command", command], shell=True)
            print(f"Requested admin launch for {exe_path}")
        except FileNotFoundError:
            print(f"Error: {exe_path} not found.")
            QtWidgets.QMessageBox.warning(self, "Error", f"Could not find {exe_path}")
        except Exception as e:
            print(f"Error launching PBO2Tuner: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to launch PBO2Tuner: {str(e)}")

    def launch_intel_voltage_control(self):
        try:
            exe_path = r"tools\IntelVoltageControl\IntelVoltageControl.exe"
            command = f'Start-Process "{exe_path}" -Verb RunAs'
            subprocess.Popen(["powershell", "-Command", command], shell=True)
            print(f"Requested admin launch for {exe_path}")
        except FileNotFoundError:
            print(f"Error: {exe_path} not found.")
            QtWidgets.QMessageBox.warning(self, "Error", f"Could not find {exe_path}")
        except Exception as e:
            print(f"Error launching IntelVoltageControl: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to launch IntelVoltageControl: {str(e)}")

    def launch_apicid(self):
        try:
            exe_path = r"tools\APICID.exe"
            working_dir = os.path.dirname(exe_path)
            generated_file_name = "APICID.txt"
            generated_file_path = os.path.join(working_dir, generated_file_name)
            before_files = set(glob.glob(os.path.join(working_dir, "*.txt")))
            subprocess.run(exe_path, cwd=working_dir, check=True)
            print(f"Executed {exe_path}")
            if os.path.exists(generated_file_path):
                os.startfile(generated_file_path)
                print(f"Opened {generated_file_path}")
            else:
                after_files = set(glob.glob(os.path.join(working_dir, "*.txt")))
                new_files = after_files - before_files
                if new_files:
                    new_file = new_files.pop()
                    os.startfile(new_file)
                    print(f"Opened newly generated file: {new_file}")
                else:
                    raise FileNotFoundError("No new .txt file was generated.")
        except FileNotFoundError as e:
            print(f"Error: {str(e)}")
            QtWidgets.QMessageBox.warning(self, "Error", str(e))
        except subprocess.CalledProcessError as e:
            print(f"Error: APICID.exe failed with exit code {e.returncode}")
            QtWidgets.QMessageBox.critical(self, "Error", f"APICID.exe failed with exit code {e.returncode}")
        except Exception as e:
            print(f"Error launching APICID or opening file: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to launch APICID or open file: {str(e)}")

    def launch_core_tuner_x(self):
        try:
            exe_path = r"tools\CoreTunerX.exe"
            subprocess.Popen(exe_path)
            print(f"Launched {exe_path}")
        except FileNotFoundError:
            print(f"Error: {exe_path} not found.")
            QtWidgets.QMessageBox.warning(self, "Error", f"Could not find {exe_path}")
        except Exception as e:
            print(f"Error launching CoreTunerX: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to launch CoreTunerX: {str(e)}")

    def run_performance_counters(self):
        try:
            bat_path = r"tools\enable_performance_counter.bat"
            command = f'Start-Process "{bat_path}" -Verb RunAs'
            subprocess.Popen(["powershell", "-Command", command], shell=True)
            print(f"Requested admin launch for {bat_path}")
        except FileNotFoundError:
            print(f"Error: {bat_path} not found.")
            QtWidgets.QMessageBox.warning(self, "Error", f"Could not find {bat_path}")
        except Exception as e:
            print(f"Error running PerformanceCounters.bat: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to run PerformanceCounters.bat: {str(e)}")

    def open_script_folder(self):
        try:
            working_dir = os.path.dirname(os.path.abspath(__file__))
            target_folder_name = "helpers"
            target_folder_path = os.path.join(working_dir, target_folder_name)
            if not os.path.exists(target_folder_path):
                os.makedirs(target_folder_path)
                print(f"Created folder: {target_folder_path}")
            os.startfile(target_folder_path)
            print(f"Opened Windows Explorer to {target_folder_path}")
        except FileNotFoundError:
            print(f"Error: {target_folder_path} could not be found or created.")
            QtWidgets.QMessageBox.warning(self, "Error", f"Could not find or create {target_folder_path}")
        except Exception as e:
            print(f"Error opening folder: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to open folder: {str(e)}")

# Entry point
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CoreCyclerApp()
    window.show()
    sys.exit(app.exec_())
