# main.py
import sys
import configparser
import subprocess
import os
import glob
from PyQt5 import QtWidgets, QtCore
from prime95 import Prime95Settings
from linpack import LinpackSettings
from yCruncher import YCruncherSettings
from aida64 import Aida64Settings

from CoreCycler import Ui_CoreCycler  # Import generated GUI class

# ===========================================
# GeneralSettings Class (from General.py)
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
# AutomatedSettings Class (from Automated.py)
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
# Main Application Class (from original main.py)
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
        
        # Now initialize AutomatedSettings after UI is set up
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
