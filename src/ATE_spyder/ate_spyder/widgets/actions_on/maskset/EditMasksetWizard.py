import os
import re

from ate_spyder.widgets.actions_on.maskset.NewMasksetWizard import NewMasksetWizard
from ate_spyder.widgets.actions_on.maskset.ViewMasksetSettings import ViewMasksetSettings


class EditMasksetWizard(NewMasksetWizard):
    def __init__(self, project_info, maskset_name):
        super().__init__(project_info, read_only=True)

        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))
        ViewMasksetSettings._setup_dialog_fields(self, maskset_name, enable_edit=True)
        self._validate_table()

    def OKButtonPressed(self):
        self.project_info.update_maskset(self.masksetName.text(), self._get_maskset_definition(), self._get_maskset_customer())
        self.accept()


def edit_maskset_dialog(project_info, maskset_name):
    edit_maskset = EditMasksetWizard(project_info, maskset_name)
    edit_maskset.exec_()
    del(edit_maskset)
