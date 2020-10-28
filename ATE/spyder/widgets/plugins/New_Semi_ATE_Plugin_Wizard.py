# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 16:55:05 2020

@author: hoeren
"""

import os
from qtpy import QtCore, QtGui, QtWidgets, uic

class New_Semi_ATE_Plugin_Wizard(QtWidgets.QDialog):

    def __init__(self, parent, project_root, title=None):
        super().__init__(parent)
        self.parent = parent

        my_ui = __file__.replace('.py', '.ui')
        if not os.path.exists(my_ui):
            raise Exception(f"can not find {my_ui}")
        uic.loadUi(my_ui, self)

        if title is None:
            self.setWindowTitle(os.path.basename(__file__).replace('.py', '').replace('_', ' '))
        else:
            self.setWindowTitle(title)

        # Project Tab
        self.fullName.clear()
        tmp = ''
        if 'USERNAME' in os.environ:
            tmp += os.environ['USERNAME'].lower()
        if 'USERDNSDOMAIN' in os.environ:
            tmp += '@' + os.environ['USERDNSDOMAIN'].lower()
        self.email.setText(tmp)
        self.projectRepoName.clear()

        # GitHub Tab

        # Plugin/Importers Tab

        # Plugin/Exporters Tab

        # Plugin/Instruments Tab

        # Plugin/Tester Tab

        # Plugin/Equipment Tab

        self.OKButton.clicked.connect(self.OKButtonPressed)
        self.CancelButton.clicked.connect(self.CancelButtonPressed)

        self.show()

    def OKButtonPressed(self):
        self.accept()

    def CancelButtonPressed(self):
        self.reject()

    def get_data(self):
        retval = {}
        return retval

def New_Semi_ATE_Plugin_Dialog(parent, project_root, title=None):
    """This dialog is called when we want to create a new Semi-ATE Plugin project"""
    retval = {}
    newProjectWizard = New_Semi_ATE_Plugin_Wizard(parent, project_root, title)
    if newProjectWizard.exec_():  # OK button pressed
        status = True
        retval = newProjectWizard.get_data()
    else:  # Cancel button pressed
        status = False
    del(newProjectWizard)
    return status, retval
