'''
Created on Nov 18, 2019

@author: hoeren
'''
import os

import qtawesome as qta
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import uic

from ATE.spyder.widgets.validation import is_valid_project_name
from ATE.spyder.widgets.validation import valid_project_name_regex


class ProjectWizard(QtWidgets.QDialog):

    def __init__(self, parent, project_name, title):
        super().__init__(parent)

        my_ui = __file__.replace('.py', '.ui')
        if not os.path.exists(my_ui):
            raise Exception("can not find %s" % my_ui)
        uic.loadUi(my_ui, self)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(title)

        self.browseRepository.setIcon(qta.icon('mdi.search-web', color='orange'))
        self.browseRepository.setEnabled(True)

        self.userName.setPlaceholderText("")

        self.ProjectName.setText(project_name)
        self.ProjectName.setDisabled(True)

        self.Feedback.setStyleSheet('color: orange')

        self.OKButton.clicked.connect(self.OKButtonPressed)
        self.CancelButton.clicked.connect(self.CancelButtonPressed)

        self.show()

    def OKButtonPressed(self):
        self.accept()

    def CancelButtonPressed(self):
        self.reject()


def NewProjectDialog(parent, project_name):
    """This dialog is called when we want to create a new project"""
    retval = {}
    newProjectWizard = ProjectWizard(parent, project_name, 'New ATE Project Wizard')
    if newProjectWizard.exec_():  # OK button pressed
        status = True
        retval['quality'] = ''
    else:  # Cancel button pressed
        status = False
        retval['quality'] = ''
    del(newProjectWizard)
    return status, retval


def EditProjectDialog(parent, navigator):
    """This dialog is called when we want to edit the project "quality" (name can not be edited)"""
    pass
