from ate_projectdatabase.Utils import DB_KEYS
import os
import re
from enum import Enum

from ate_spyder.widgets.actions_on.hardwaresetup.HardwareWizard import HardwareWizard


class ErrorMessage(Enum):
    NoValidConfiguration = "no valid configuration"
    InvalidConfigurationElements = "configuration does not match the template inside constants.py"

    def __call__(self):
        return self.value


class ViewHardwaresetupSettings(HardwareWizard):
    def __init__(self, hw_name, project_info):
        super().__init__(project_info)
        self._setup_view(hw_name)
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

        self.parallelism_widget.set_ui_enabled(False)

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

        # The tester must be set/initialized before maxParallelism
        dialog.select_tester(hw_configuration[DB_KEYS.HARDWARE.DEFINITION.TESTER])

        pcb = hw_configuration[DB_KEYS.HARDWARE.DEFINITION.PCB.KEY()]
        dialog.singlesiteLoadboard.setText(pcb[DB_KEYS.HARDWARE.DEFINITION.PCB.SINGLE_SITE_LOADBOARD])
        dialog.singlesiteDIB.setText(pcb[DB_KEYS.HARDWARE.DEFINITION.PCB.SINGLE_SITE_DIB])
        dialog.singlesiteProbecard.setText(pcb[DB_KEYS.HARDWARE.DEFINITION.PCB.SINGLE_SITE_PROBE_CARD])
        dialog.multisiteLoadboard.setText(pcb[DB_KEYS.HARDWARE.DEFINITION.PCB.MULTI_SITE_LOADBOARD])
        dialog.multisiteDIB.setText(pcb[DB_KEYS.HARDWARE.DEFINITION.PCB.MULTI_SITE_DIB])
        dialog.multisiteProbecard.setText(pcb[DB_KEYS.HARDWARE.DEFINITION.PCB.MULTI_SITE_CARD])
        dialog.maxParallelism.setCurrentIndex(pcb[DB_KEYS.HARDWARE.DEFINITION.PCB.MAX_PARALLELISM] - 1)

        dialog.populate_selected_instruments(hw_configuration[DB_KEYS.HARDWARE.DEFINITION.INSTRUMENTS.KEY()])
        dialog.populate_selected_actuators(hw_configuration[DB_KEYS.HARDWARE.DEFINITION.ACTUATOR.KEY()])
        dialog.populate_selected_gpfunctions(hw_configuration[DB_KEYS.HARDWARE.DEFINITION.GP_FUNCTIONS.KEY()])

        dialog.parallelism_widget.parallelism_store = dialog.project_info.get_hardware_parallelism_store(hw_name)

        dialog._verify()

    def OKButtonPressed(self):
        self.accept()


def display_hardware_settings_dialog(hw_name, project_info):
    hardware_wizard = ViewHardwaresetupSettings(hw_name, project_info)
    hardware_wizard.exec_()
    del(hardware_wizard)
