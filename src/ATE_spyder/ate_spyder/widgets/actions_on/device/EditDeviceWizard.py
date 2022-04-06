import os
import re

from ate_spyder.widgets.actions_on.device.NewDeviceWizard import NewDeviceWizard
from ate_spyder.widgets.actions_on.device.ViewDeviceWizard import ViewDeviceWizard


class EditDeviceWizard(NewDeviceWizard):
    def __init__(self, project_info, name):
        super().__init__(project_info, read_only=True)
        self.deviceName.setEnabled(False)
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))
        ViewDeviceWizard._setup_dialog_fields(self, name)

    def OKButtonPressed(self):
        configuration = self._get_current_configuration()
        self.project_info.update_device(configuration['name'], configuration['hardware'],
                                        configuration['package'], configuration['definition'])
        self.accept()


def edit_device_dialog(project_info, name):
    edit = EditDeviceWizard(project_info, name)
    edit.exec_()
    del(edit)
