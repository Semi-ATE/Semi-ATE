from ate_spyder.widgets.actions_on.package.NewPackageWizard import NewPackageWizard
from ate_spyder.widgets.actions_on.package.ViewPackageWizard import ViewPackageWizard
import re
import os


class EditPackageWizard(NewPackageWizard):
    def __init__(self, project_info, name):
        super().__init__(project_info, read_only=True)
        self.packageName.setEnabled(False)
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))
        ViewPackageWizard._setup_dialog_fields(self, name)

    def OKButtonPressed(self):
        configuration = self._get_current_configuration()
        self.project_info.update_package(configuration['name'], configuration['leads'], configuration['is_naked_die'])
        self.accept()


def edit_package_dialog(project_info, name):
    edit = EditPackageWizard(project_info, name)
    edit.exec_()
    del(edit)
