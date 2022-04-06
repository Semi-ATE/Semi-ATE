# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 18:18:41 2019

        current_target_index = self.target.findText(self.project_info.active_target, QtCore.Qt.MatchExactly)
@author: hoeren
"""
import os
import shutil
import re
import tempfile

from ate_spyder.widgets.validation import valid_package_name_regex
from PyQt5 import QtCore, QtGui, QtWidgets
from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog


class NewPackageWizard(BaseDialog):
    def __init__(self, project_info, read_only=False):
        super().__init__(__file__, project_info.parent)
        self.project_info = project_info
        self.read_only = read_only

        self._setup()
        self._connect_event_handler()

    def _setup(self):
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        # create a temporary directory to store the drawing(s)
        self.temp_dir = tempfile.mkdtemp()
        self.temp_drawing = None

        # name
        rxPackageName = QtCore.QRegExp(valid_package_name_regex)
        PackageName_validator = QtGui.QRegExpValidator(rxPackageName, self)
        self.packageName.blockSignals(True)
        self.packageName.setValidator(PackageName_validator)
        self.packageName.textChanged.connect(self.validate)
        self.packageName.blockSignals(False)

        # leads
        self.leads.setMinimum(2)
        self.leads.setMaximum(99)
        self.leads.setValue(2)

        # drawing
        self.drawingGroup.setVisible(False)
        self.drawingLabel.setText("N/A")
        self.findOnFilesystem.clicked.connect(self.FindOnFileSystem)
        companies = ['', 'Semi-ATE', 'InvenSense', 'IC-Sense', '...']
        self.importFor.clear()
        self.importFor.addItems(companies)
        self.importFor.setCurrentIndex(0)  # empty string
        self.doImport.setEnabled(False)
        self.feedback.setText("")
        self.feedback.setStyleSheet('color: orange')

        self.validate()

    def _connect_event_handler(self):
        self.OKButton.clicked.connect(self.OKButtonPressed)
        self.CancelButton.clicked.connect(self.CancelButtonPressed)
        self.importFor.currentTextChanged.connect(self.importForChanged)
        self.doImport.clicked.connect(self.doImportFor)

    def __del__(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def FindOnFileSystem(self):
        print("Find On File System not yet implemented")
        # TODO: Implement 'FindOnFileSystem'

    def importForChanged(self, Company):
        if Company == '':
            self.doImport.setEnabled(False)
            self.validate()
        else:
            self.doImport.setEnabled(True)
            self.OKButton.setEnabled(False)

    def doImportFor(self):
        '''
        this method will find (per company) somehow the drawings for
        the package and save it in the self.temp_dir directory with the
        name of the package with the .png extension.
        upon OK button, this file is copied in ~/src/drawings/packages.
        '''
        print("Import for '{self.importFor.currentText()}' not yet implemented")

        # TODO: Implement, save the file in self.temp_dir under the name of the package !!!
        self.importFor.setCurrentIndex(0)  # empty
        self.drawingLabel.setText(f"imported for '{self.importFor.currentText()}'")
        self.doImport.setEnabled(False)

    def validate(self):
        self.feedback.setText('')

        package_name = self.packageName.text()
        if package_name == "":
            self.feedback.setText("Supply a name for the Package")
            self.drawingGroup.setVisible(False)
        else:
            if not self.read_only and self.project_info.does_package_name_exist(package_name):
                self.feedback.setText("Package already defined")
            else:
                self.drawingGroup.setVisible(True)

        if self.feedback.text() == "":
            self.OKButton.setEnabled(True)
        else:
            self.OKButton.setEnabled(False)

    def _get_current_configuration(self):
        return {'name': self.packageName.text(),
                'leads': self.leads.value(),
                'is_naked_die': self.isNakedDie.isChecked()}

    def OKButtonPressed(self):
        configuration = self._get_current_configuration()
        self.project_info.add_package(configuration['name'], configuration['leads'], configuration["is_naked_die"])
        self.accept()

    def CancelButtonPressed(self):
        self.accept()


def new_package_dialog(project_info):
    newPackageWizard = NewPackageWizard(project_info)
    newPackageWizard.exec_()
    del(newPackageWizard)


if __name__ == '__main__':
    import sys, qdarkstyle
    from ate_spyder.widgets.actions.dummy_main import DummyMainWindow

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    dummyMainWindow = DummyMainWindow()
    dialog = NewPackageWizard(dummyMainWindow)
    dummyMainWindow.register_dialog(dialog)
    sys.exit(app.exec_())
