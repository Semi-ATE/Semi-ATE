import os
import re

from ate_spyder.widgets.actions_on.product.NewProductWizard import NewProductWizard
from ate_spyder.widgets.actions_on.product.ViewProductWizard import ViewProductWizard


class EditProductWizard(NewProductWizard):
    def __init__(self, project_info, name):
        super().__init__(project_info, read_only=True)
        self.ProductName.setEnabled(False)
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))
        ViewProductWizard._setup_dialog_fields(self, name)

    def ok_button_pressed(self):
        configuration = self._get_actual_defintion()
        self.project_info.update_product(configuration['name'], configuration['device'],
                                         configuration['hardware'], configuration['quality'],
                                         configuration['grade'], configuration['grade_reference'],
                                         configuration['type'], configuration['customer'])
        self.accept()


def edit_product_dialog(project_info, name):
    edit = EditProductWizard(project_info, name)
    edit.exec_()
    del(edit)
