# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 17:51:48 2020

@author: hoeren
"""

import getpass
import importlib
import os
import platform
import re
import sys

from PyQt5 import QtCore, QtWidgets, uic, QtGui

import qdarkstyle
import qtawesome as qta


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, app=None):
        super().__init__()
        self.app = app

        # get the appropriate .ui file and load it.
        my_ui = __file__.replace('.py', '.ui')
        if not os.path.exists(my_ui):
            raise Exception("'%s' doesn't exist" % my_ui)
        uic.loadUi(my_ui, self)

        # get some base info
        self.os = platform.system()
        self.username = getpass.getuser()
        if self.os == "Windows":
            self.userhome = f"{os.environ['HOMEDRIVE']}{os.environ['HOMEPATH']}"
        else:
            self.userhome = os.path.expanduser("~")

        # Initialize the main window
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))
        self.projectDirectoryExisting.setChecked(False)
        self.projectDirectoryExisting.toggled.connect(self.projectDirectoryStateChanged)
        self.projectDirectoryNew.setChecked(True)
        self.projectDirectoryNew.toggled.connect(self.projectDirectoryStateChanged)
        self.projectDirectory = "New"
        self.projectName.clear()
        self.projectName.editingFinished.connect(self.projectNameChanged)
        self.projectLocation.setText(self.userhome)
        self.projectLocationButton.clicked.connect(self.locationButtonPressed)
        self.cancelButton.clicked.connect(self.cancelButtonPressed)
        self.createButton.clicked.connect(self.createButtonPressed)
        self.createButton.setEnabled(False)

        # go
        self.show()

    def locationButtonPressed(self):
        new_location = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                                  'Select Directory',
                                                                  self.userhome,
                                                                  QtWidgets.QFileDialog.ShowDirsOnly
                                                                  | QtWidgets.QFileDialog.DontResolveSymlinks
                                                                  | QtWidgets.QFileDialog.DontUseNativeDialog)
        self.projectLocation.setText(new_location)
        self.evaluate()

    def projectNameChanged(self):
        projectName = self.projectName.text()
        print(projectName)

    def projectDirectoryStateChanged(self, state):
        radioButton = self.sender()
        if radioButton.objectName() == "projectDirectoryNew":
            if state is True:  # create a new directory
                self.projectDirectory = "New"
            else:  # use existing directory
                self.projectDirectory = "Existing"

    def cancelButtonPressed(self):
        pass

    def createButtonPressed(self):
        pass

    def evaluate(self):
        if self.projectName.text() != "":
            self.createButton.setEnabled(True)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MainWindow(app)
    res = app.exec_()
    sys.exit(res)
