import os
import re
from enum import Enum

from ATE.spyder.widgets.actions_on.hardwaresetup.HardwareWizard import HardwareWizard


class ErrorMessage(Enum):
    NoValidConfiguration = "no valid configuration"
    InvalidConfigurationElements = "configuration does not match the template inside constants.py"

    def __call__(self):
        return self.value


class ViewHardwaresetupSettings(HardwareWizard):
    def __init__(self, hw_name, project_info):
        super().__init__(project_info)
        self._setup_view(hw_name)
        self.finaltestConfiguration.setFixedSize(626, 374)
        ViewHardwaresetupSettings._setup_dialog_fields(self, hw_name)

    def _setup_view(self, hw_name):
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        self.hardware.setText(hw_name)
        self.hardware.setEnabled(False)
        self.feedback.setStyleSheet('color: orange')

        self.singlesiteLoadboard.setEnabled(False)
        self.singlesiteProbecard.setEnabled(False)
        self.singlesiteDIB.setEnabled(False)
        self.multisiteLoadboard.setDisabled(True)
        self.multisiteDIB.setDisabled(True)
        self.multisiteProbecard.setDisabled(True)
        self.tester.setEnabled(False)
        self.maxParallelism.setEnabled(False)
        self.finaltestSites.setEnabled(False)
        self.finaltestConfiguration.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.type_box.setEnabled(False)

        self.right_button.setEnabled(False)
        self.left_button.setEnabled(False)

        self.OKButton.setEnabled(True)
        self.OKButton.clicked.connect(self.accept)

        self.addGPFunction.setEnabled(False)
        self.removeGPFunction.setEnabled(False)
        self.usedActuators.setEnabled(False)
        self.addInstrument.setEnabled(False)
        self.removeInstrument.setEnabled(False)

        self.CancelButton.setEnabled(True)
        self.CancelButton.clicked.connect(self.accept)
        self.feedback.setText("")
        self.is_read_only = True

    @staticmethod
    def _setup_dialog_fields(dialog, hw_name):
        hw_configuration = dialog.project_info.get_hardware_definition(hw_name)

        dialog.feedback.setText('')
        dialog.feedback.setStyleSheet('')

        dialog.singlesiteLoadboard.setText(hw_configuration["PCB"]["SingleSiteLoadboard"])
        dialog.singlesiteDIB.setText(hw_configuration["PCB"]["SingleSiteDIB"])
        dialog.singlesiteProbecard.setText(hw_configuration["PCB"]["SingleSiteProbeCard"])
        dialog.multisiteLoadboard.setText(hw_configuration["PCB"]["MultiSiteLoadboard"])
        dialog.multisiteDIB.setText(hw_configuration["PCB"]["MultiSiteDIB"])
        dialog.multisiteProbecard.setText(hw_configuration["PCB"]["MultiSiteProbeCard"])
        dialog.select_tester(hw_configuration["tester"])
        dialog.maxParallelism.setCurrentIndex(hw_configuration["PCB"]["MaxParallelism"] - 1)
        dialog._available_pattern = hw_configuration["Parallelism"]
        dialog.populate_selected_instruments(hw_configuration["Instruments"])
        dialog.populate_selected_actuators(hw_configuration["Actuator"])
        dialog.populate_selected_gpfunctions(hw_configuration["GPFunctions"])
        ViewHardwaresetupSettings._update_available_pattern_list(dialog)
        dialog._verify()

    @staticmethod
    def _update_available_pattern_list(dialog):
        for k, _ in dialog._available_pattern.items():
            dialog.finaltestAvailableConfigurations.addItem(k)

    def OKButtonPressed(self):
        self.accept()


def display_hardware_settings_dialog(hw_name, project_info):
    hardware_wizard = ViewHardwaresetupSettings(hw_name, project_info)
    hardware_wizard.exec_()
    del(hardware_wizard)
