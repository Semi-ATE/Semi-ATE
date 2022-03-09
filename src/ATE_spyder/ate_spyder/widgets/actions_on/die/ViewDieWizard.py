import os
import re
from enum import Enum

from ate_spyder.widgets.actions_on.die.DieWizard import DieWizard


class ErrorMessage(Enum):
    NoValidConfiguration = "no valid configuration"
    InvalidConfigurationElements = "configuration does not match the template inside constants.py"

    def __call__(self):
        return self.value


class ViewDieWizard(DieWizard):
    def __init__(self, name, project_info):
        super().__init__(project_info)
        self._setup_view(name)
        ViewDieWizard._setup_dialog_fields(self, name)

    def _setup_view(self, name):
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        self.withHardware.setEnabled(False)
        self.dieName.setEnabled(False)
        self.fromMaskset.setEnabled(False)
        self.qualityGrade.setEnabled(False)
        self.isAGrade.setChecked(True)
        self.isAGrade.setEnabled(False)
        self.referenceGrade.setEnabled(False)
        self.grade.setEnabled(False)
        self.Type.setEnabled(False)
        self.customer.setEnabled(False)

        self.CancelButton.setEnabled(True)
        self.CancelButton.clicked.connect(self.accept)
        self.feedback.setText("")

    @staticmethod
    def _setup_dialog_fields(dialog, name):
        configuration = dialog.project_info.get_die(name)

        dialog.dieName.setText(name)
        dialog.withHardware.setCurrentText(configuration.hardware)
        dialog.fromMaskset.setCurrentText(configuration.maskset)
        if not configuration.grade == 'A':
            dialog.isAGrade.setChecked(False)
            dialog.grade.setHidden(False)
            dialog.gradeLabel.setHidden(False)
            dialog.gradeLabel.setEnabled(True)
            dialog.referenceGrade.setHidden(False)
            dialog.referenceGradeLabel.setHidden(False)
            dialog.referenceGradeLabel.setEnabled(True)

        dialog.grade.setCurrentText(configuration.grade)
        dialog.referenceGrade.setCurrentText(configuration.grade_reference)
        dialog.qualityGrade.setCurrentText(configuration.quality)

        if configuration.type == 'ASSP':
            dialog.Type.setCurrentText('ASSP')
        else:
            dialog.Type.setCurrentText(configuration.type)
            dialog.customer.setText(configuration.customer)
            dialog.customer.setHidden(False)
            dialog.customerLabel.setHidden(False)
            dialog.customerLabel.setEnabled(True)

        dialog.feedback.setText('')
        dialog.OKButton.setEnabled(True)
        dialog.isAGrade.setEnabled(False)

    def ok_button_pressed(self):
        self.accept()


def display_die_settings_dialog(name, project_info):
    view_wizard = ViewDieWizard(name, project_info)
    view_wizard.exec_()
    del(view_wizard)
