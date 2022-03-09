import os
import re

from ate_spyder.widgets.actions_on.die.DieWizard import DieWizard
from ate_spyder.widgets.actions_on.die.ViewDieWizard import ViewDieWizard


class EditDieWizard(DieWizard):
    def __init__(self, project_info, name):
        super().__init__(project_info, read_only=True)
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))
        ViewDieWizard._setup_dialog_fields(self, name)
        self.dieName.setEnabled(False)
        self.isAGrade.setEnabled(True)
        self.withHardware.setEnabled(False)

    def ok_button_pressed(self):
        configuration = self._get_current_configuration()
        self.project_info.update_die(configuration['name'], configuration['hardware'], configuration['maskset'],
                                     configuration['grade'], configuration['grade_reference'], configuration['quality'],
                                     configuration['type'], configuration['customer'])
        self.accept()


def edit_die_dialog(project_info, name):
    edit_hw = EditDieWizard(project_info, name)
    edit_hw.exec_()
    del(edit_hw)
