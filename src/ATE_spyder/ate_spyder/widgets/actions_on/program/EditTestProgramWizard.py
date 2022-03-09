from PyQt5.QtGui import QStandardItem
from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.actions_on.program.TestProgramWizard import TestProgramWizard
from ate_spyder.widgets.actions_on.program.ViewTestProgramWizard import ViewTestProgramWizard


class EditTestProgramWizard(TestProgramWizard):
    def __init__(self, name: str, project_info: ProjectNavigation, owner: str, parent: QStandardItem):
        super().__init__(project_info, owner, parent=parent, enable_edit=False, prog_name=name)
        ViewTestProgramWizard.setup_view(self, name)


def edit_program_dialog(name: str, project_info: ProjectNavigation, owner: str, parent: QStandardItem):
    testProgramWizard = EditTestProgramWizard(name, project_info, owner, parent)
    testProgramWizard.exec_()
    del(testProgramWizard)
