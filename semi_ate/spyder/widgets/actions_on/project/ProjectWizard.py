'''
Created on Nov 18, 2019

@author: hoeren
'''

import os
from PyQt5 import QtCore, QtGui, QtWidgets, uic
import qtawesome as qta

from ATE.org.validation import is_valid_project_name, valid_project_name_regex


class ProjectWizard(QtWidgets.QDialog):

    def __init__(self, parent, navigator, title):
        super().__init__(parent)

        self.project_info = navigator
        my_ui = __file__.replace('.py', '.ui')
        if not os.path.exists(my_ui):
            raise Exception("can not find %s" % my_ui)
        uic.loadUi(my_ui, self)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(title)

        self.browseRepository.setIcon(qta.icon('mdi.search-web', color='orange'))
        self.browseRepository.setEnabled(True)

        self.userName.setPlaceholderText(self.project_info.user)

        # TODO: based on title, need to decide if we are creating or editing.

        rxProjectName = QtCore.QRegExp(valid_project_name_regex)
        ProjectName_validator = QtGui.QRegExpValidator(rxProjectName, self)
        self.ProjectName.setValidator(ProjectName_validator)
        self.ProjectName.setText("")
        self.ProjectName.textChanged.connect(self.verify)

        self.existing_projects = navigator.list_ATE_projects(navigator.workspace_path)

        self.Feedback.setStyleSheet('color: orange')

        self.OKButton.clicked.connect(self.OKButtonPressed)
        self.CancelButton.clicked.connect(self.CancelButtonPressed)

        self.verify()
        self.show()

    def verify(self):
        feedback = ""

        project_name = self.ProjectName.text()
        if project_name == "":
            feedback = "Invalid project name"
        elif project_name in self.existing_projects:
            feedback = "project already defined"
        else:
            if not is_valid_project_name(project_name):
                feedback = "Invalid project name"

        self.Feedback.setText(feedback)

        if feedback == "":
            self.OKButton.setEnabled(True)
        else:
            self.OKButton.setEnabled(False)

    def OKButtonPressed(self):
        self.project_name = self.ProjectName.text()
        self.project_quality = self.projectQuality.currentText()
        if self.project_name:
            self.project_info.add_project(self.project_name, self.project_quality)

        self.accept()

    def CancelButtonPressed(self):
        self.reject()


def NewProjectDialog(parent, navigator):
    """This dialog is called when we want to create a new project"""
    newProjectWizard = ProjectWizard(parent, navigator, 'New Project Wizard')
    if newProjectWizard.exec_():  # OK button pressed
        project_name = newProjectWizard.project_name
        project_quality = newProjectWizard.project_quality
    else:
        project_name = ''
        project_quality = ''
    del(newProjectWizard)
    return project_name, project_quality


def EditProjectDialog(parent, navigator):
    """This dialog is called when we want to edit the project "quality" (name can not be edited)"""
    pass