'''
Created on Nov 18, 2019

@author: hoeren
'''
import qtawesome as qta
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QDialog

from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog
from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.validation import valid_name_regex

import os
import re
from pathlib import Path


class ProjectWizard(BaseDialog):

    def __init__(self, project_info: ProjectNavigation, project_path: str):
        super().__init__(__file__, project_info.parent)
        self.project_info = project_info
        self.project_path_set_by_spyder = project_path
        self._setup_ui()

    @property
    def project_name_set_by_spyder(self):
        return os.path.basename(self.project_path_set_by_spyder)

    def _setup_ui(self):
        regx = QtCore.QRegExp(valid_name_regex)
        name_validator = QtGui.QRegExpValidator(regx, self)

        self.ProjectName.setText(self.project_name_set_by_spyder)
        self.ProjectName.setValidator(name_validator)
        self.ProjectName.textChanged.connect(self._validate_project_name)

        self.qualityGrade.setCurrentText("")

        # Revisioning QGroupBox
        self.browseRepository.setIcon(qta.icon('mdi.search-web', color='orange'))
        self.browseRepository.setEnabled(True)
        self.userName.setPlaceholderText("")
        # end Revisioning

        self.Feedback.setStyleSheet('color: orange')

        self.OKButton.clicked.connect(self.OKButtonPressed)
        self.CancelButton.clicked.connect(self.CancelButtonPressed)
        self._validate_project_name()

    def _validate_project_name(self):
        project_name = self.ProjectName.text()
        if not re.match(valid_name_regex, project_name):
            self.Feedback.setText('project name is invalid')
            self.OKButton.setEnabled(False)
        else:
            self.Feedback.setText('')
            self.OKButton.setEnabled(True)

    @QtCore.pyqtSlot()
    def OKButtonPressed(self):
        project_name = self.ProjectName.text()
        new_path = Path(os.path.dirname(self.project_path_set_by_spyder)).joinpath(project_name)
        Path(self.project_path_set_by_spyder).rename(new_path)

        self.project_info(str(new_path))
        # config step shall be done first after the re-initialization of the project_info is done
        configuration = self._get_current_configuration()
        self.project_info.add_settings(
            quality_grade=configuration['quality_grade']
        )

        self.done(QDialog.DialogCode.Accepted)

    def _get_current_configuration(self):
        return {
            'quality_grade': self.qualityGrade.currentText()
        }

    @QtCore.pyqtSlot()
    def CancelButtonPressed(self):
        self.done(QDialog.DialogCode.Rejected)


def new_project_dialog(project_info: ProjectNavigation, project_path: str) -> QDialog:
    newProjectWizard = ProjectWizard(project_info, project_path)
    status = newProjectWizard.exec_()
    del(newProjectWizard)
    return status
