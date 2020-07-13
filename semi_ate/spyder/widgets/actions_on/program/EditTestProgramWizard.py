from ATE.org.actions_on.program.TestProgramWizard import TestProgramWizard
from ATE.org.actions_on.program.ViewTestProgramWizard import ViewTestProgramWizard


class EditTestProgramWizard(TestProgramWizard):
    def __init__(self, name, project_info, owner):
        super().__init__(project_info, owner, edit_on=False, prog_name=name)
        ViewTestProgramWizard.setup_view(self, name)


def edit_program_dialog(name, project_info, owner):
    testProgramWizard = EditTestProgramWizard(name, project_info, owner)
    testProgramWizard.exec_()
    del(testProgramWizard)
