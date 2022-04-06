# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 12:26:00 2020

@author: hoeren
"""
import os
import re

from PyQt5 import QtGui

from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog


class NewStandardTestWizard(BaseDialog):
    def __init__(self, project_info, fixed=True):
        super().__init__(__file__)

        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        self.project_info = project_info

    # ForHardwareSetup ComboBox
        self.existing_hardwaresetups = self.project_info.get_active_hardware_names()
        self.ForHardwareSetup.blockSignals(True)
        self.ForHardwareSetup.clear()
        self.ForHardwareSetup.addItems(self.existing_hardwaresetups)
        # TODO: fix this
        self.ForHardwareSetup.setCurrentIndex(self.ForHardwareSetup.findText(self.project_info.active_hardware))
        # TODO:
        # self.ForHardwareSetup.setDisabled(fixed)
        self.ForHardwareSetup.setDisabled(False)
        self.ForHardwareSetup.currentTextChanged.connect(self._verify)
        self.ForHardwareSetup.blockSignals(False)

    # WithBase ComboBox
        self.WithBase.blockSignals(True)
        self.WithBase.clear()
        self.WithBase.addItems(['PR', 'FT'])
        # TODO: fix this
        self.WithBase.setCurrentIndex(self.WithBase.findText(self.project_info.active_base))
        # self.WithBase.setDisabled(fixed)
        self.WithBase.setDisabled(False)
        self.WithBase.currentTextChanged.connect(self._verify)
        self.WithBase.blockSignals(False)

    # StandardTestName ComboBox
        self.model = QtGui.QStandardItemModel()

        from ate_spyder.widgets.coding.standard_tests import names as standard_test_names
        existing_standard_test_names = \
            self.project_info.tests_get_standard_tests(
                self.ForHardwareSetup.currentText(),
                self.WithBase.currentText())

        for index, standard_test_name in enumerate(standard_test_names):
            item = QtGui.QStandardItem(standard_test_name)
            if standard_test_name in existing_standard_test_names:
                item.setEnabled(False)
                # TODO: maybe also use the flags (Qt::ItemIsSelectable) ?!?
            else:
                item.setEnabled(True)
                # TODO: maybe also use the flags (Qt::ItemIsSelectable) ?!?
            self.model.appendRow(item)

        self.StandardTestName.blockSignals(True)
        self.StandardTestName.clear()
        self.StandardTestName.setModel(self.model)
        self.StandardTestName.currentTextChanged.connect(self._verify)
        self.StandardTestName.blockSignals(False)

    # feedback
        self.feedback.setText("")
        self.feedback.setStyleSheet('color: orange')

    # buttons
        self.CancelButton.clicked.connect(self.CancelButtonPressed)
        self.OKButton.clicked.connect(self.OKButtonPressed)
        self.OKButton.setEnabled(False)

    # go
        self._verify()
        self.show()

    def _verify(self):
        self.feedback.setText('')

        # hardware
        if self.feedback.text() == '':
            if self.ForHardwareSetup.currentText() == '':
                self.feedback.setText("Select a hardware setup")

        # base
        if self.feedback.text() == '':
            if self.WithBase.currentText() not in ['FT', 'PR']:
                self.feedback.setText("Select the base")

        # standard test
        if self.feedback.text() == '':
            if self.StandardTestName.currentText() == '':
                self.feedback.setText("Select a standard test")

        # buttons
        if self.feedback.text() == "":
            self.OKButton.setEnabled(True)
        else:
            self.OKButton.setEnabled(False)

    def CancelButtonPressed(self):
        self.reject()

    def OKButtonPressed(self):
        # TODO: fix me
        # name = self.StandardTestName.currentText()
        # hardware = self.ForHardwareSetup.currentText()
        # type = 'standard'
        # base = self.WithBase.currentText()
        # definition = {'doc_string': [], # list of lines
        #               'input_parameters': {},
        #               'output_parameters': {}}

        # self.project_info.add_standard_test(name, hardware, base)

        # use print as hint
        print('Standard test cannot be stored, fix it !!!')
        self.accept()


def new_standard_test_dialog(project_info):
    newStandardTestWizard = NewStandardTestWizard(project_info)
    newStandardTestWizard.exec_()
    del(newStandardTestWizard)
