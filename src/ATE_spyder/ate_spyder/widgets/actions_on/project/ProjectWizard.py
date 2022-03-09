'''
Created on Nov 18, 2019

@author: hoeren
'''
import qtawesome as qta
from PyQt5 import QtCore

from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog
from ate_spyder.widgets.navigation import ProjectNavigation


class ProjectWizard(BaseDialog):

    def __init__(self, project_info: ProjectNavigation):
        super().__init__(__file__, project_info.parent)
        self.project_info = project_info
        self._setup_ui()

    def _setup_ui(self):
        self.ProjectName.setText(self.project_info.project_name)
        self.ProjectName.setDisabled(True)

        self.qualityGrade.setCurrentText("")

        # Revisioning QGroupBox
        self.browseRepository.setIcon(qta.icon('mdi.search-web', color='orange'))
        self.browseRepository.setEnabled(True)

        self.userName.setPlaceholderText("")
        # end Revisioning

        self.Feedback.setStyleSheet('color: orange')

        self.OKButton.clicked.connect(self.OKButtonPressed)
        self.CancelButton.clicked.connect(self.CancelButtonPressed)

    def _get_current_configuration(self):
        return {
            'quality_grade': self.qualityGrade.currentText()
        }

    @QtCore.pyqtSlot()
    def OKButtonPressed(self):
        configuration = self._get_current_configuration()
        self.project_info.add_settings(
            quality_grade=configuration['quality_grade']
        )
        self.accept()

    @QtCore.pyqtSlot()
    def CancelButtonPressed(self):
        self.reject()


def new_project_dialog(project_info):
    newProjectWizard = ProjectWizard(project_info)
    newProjectWizard.exec_()
    del(newProjectWizard)
