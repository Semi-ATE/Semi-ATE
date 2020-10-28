from ATE.spyder.widgets.actions_on.program.TestProgramWizard import TestProgramWizard
from ATE.spyder.widgets.actions_on.program.ViewTestProgramWizard import ViewTestProgramWizard


class EditTestProgramWizard(TestProgramWizard):
    def __init__(self, name, project_info, owner):
        super().__init__(project_info, owner, enable_edit=False, prog_name=name)
        ViewTestProgramWizard.setup_view(self, name)


def edit_program_dialog(name, project_info, owner):
    testProgramWizard = EditTestProgramWizard(name, project_info, owner)
    testProgramWizard.exec_()
    del(testProgramWizard)
