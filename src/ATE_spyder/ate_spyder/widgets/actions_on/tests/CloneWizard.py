# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 18:56:05 2019

@author: hoeren

"""
import getpass
import os
import re

import numpy as np
import qtawesome as qta
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import uic

from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.validation import is_valid_test_name
from ate_spyder.widgets.validation import valid_default_float_regex
from ate_spyder.widgets.validation import valid_fmt_regex
from ate_spyder.widgets.validation import valid_max_float_regex
from ate_spyder.widgets.validation import valid_min_float_regex
from ate_spyder.widgets.validation import valid_name_regex
from ate_spyder.widgets.validation import valid_name_regex
from datetime import datetime

minimal_docstring_length = 80

class Delegator(QtWidgets.QStyledItemDelegate):

    def __init__(self, regex, parent=None):
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.validator = QtGui.QRegExpValidator(QtCore.QRegExp(regex))

    def createEditor(self, parent, option, index):
        line_edit = QtWidgets.QLineEdit(parent)
        line_edit.setValidator(self.validator)
        return line_edit

# TODO Remove CloneWizard as it is not used anywhere
class CloneWizard(QtWidgets.QDialog):

    def __init__(self, parent, navigator, fromDefinition=None, toDefinition=None):
        super().__init__(parent)
        if not isinstance(navigator, ProjectNavigation):
            raise Exception("I didn't get a navigator of type 'ProjectNavigation'")
        self.navigator = navigator

        if fromDefinition==None:
            fromDefinition = makeBlankFromDefinition(navigator)
        if toDefinition==None:
            toDefinition = makeBlankToDefinition(navigator)

        my_ui = __file__.replace('.py', '.ui')
        if not os.path.exists(my_ui):
            raise Exception("can not find %s" % my_ui)
        uic.loadUi(my_ui, self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

    # Feedback
        self.Feedback.setStyleSheet('color: orange')

    # From

    # To
        TestName_validator = QtGui.QRegExpValidator(QtCore.QRegExp(valid_name_regex), self)
        self.TestName.setText("")
        self.TestName.setValidator(TestName_validator)
        self.TestName.textChanged.connect(self.verify)

    # ForHardwareSetup
        existing_hardwares = self.project_info.get_hardware_names()
        self.ForHardwareSetup.blockSignals(True)
        self.ForHardwareSetup.clear()
        self.ForHardwareSetup.addItems(existing_hardwares)
        self.ForHardwareSetup.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        if definition['hardware'] != '':
            self.ForHardwareSetup.setCurrentText(definition['hardware'])
            self.ForHardwareSetup.setEnabled(False)
        else:
            self.ForHardwareSetup.setCurrentText(sorted(existing_hardwares)[-1])
            self.ForHardwareSetup.setEnabled(True)
        self.ForHardwareSetup.blockSignals(False)

    # WithBase
        existing_bases = ['PR', 'FT']
        self.WithBase.blockSignals(True)
        self.WithBase.clear()
        self.WithBase.addItems(existing_bases)
        self.WithBase.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        if definition['base'] != '':
            self.WithBase.setCurrentText(definition['base'])
            self.WithBase.setEnabled(False)
        else:
            self.WithBase.setCurrentText(definition['PR'])
            self.WithBase.setEnabled(False)
        self.WithBase.blockSignals(False)

    # DescriptionTab
        self.description.blockSignals(True)
        self.description.clear()
        self.description.setLineWrapMode(QtWidgets.QTextEdit.NoWrap) # https://doc.qt.io/qt-5/qtextedit.html#LineWrapMode-enum
        #TODO: add a line at 80 characters (https://stackoverflow.com/questions/30371613/draw-vertical-lines-on-qtextedit-in-pyqt)
        if definition['docstring'] != []:
            self.description.setPlainText('\n'.join(definition['docstring']))
        else:
            user = getpass.getuser()
            domain = str(os.environ.get('USERDNSDOMAIN')) #TODO: maybe move this to 'company specific stuff' later on ?
            if domain == 'None':
                user_email = ''
            else:
                user_email = f"{user}@{domain}".lower()
            default_docstring = f"Created on {self.getDateTime()}\nBy @author: {user} ({user_email})\n"
            self.description.setPlainText(default_docstring)
        self.description_length = self.descriptionLength()
        self.description.textChanged.connect(self.descriptionLength)
        self.description.blockSignals(False)

    # Delegators
        self.nameDelegator = Delegator(valid_name_regex, self)

        self.fmtDelegator = Delegator(valid_fmt_regex, self)

        self.minDelegator = Delegator(valid_min_float_regex, self)
        self.defaultDelegator = Delegator(valid_default_float_regex, self)
        self.maxDelegator = Delegator(valid_max_float_regex, self)

        self.LSLDelegator = Delegator(valid_min_float_regex, self)
        self.LTLDelegator = Delegator(valid_min_float_regex, self)
        self.NomDelegator = Delegator(valid_default_float_regex, self)
        self.UTLDelegator = Delegator(valid_max_float_regex, self)
        self.USLDelegator = Delegator(valid_max_float_regex, self)

    # InputParametersTab
        self.inputParameterMoveUp.setIcon(qta.icon('mdi.arrow-up-bold-box-outline', color='orange'))
        self.inputParameterMoveUp.setToolTip('Move selected parameter Up')
        self.inputParameterMoveUp.clicked.connect(self.moveInputParameterUp)

        self.inputParameterAdd.setIcon(qta.icon('mdi.plus-box-outline', color='orange'))
        self.inputParameterAdd.setToolTip('Add a parameter')
        self.inputParameterAdd.clicked.connect(self.addInputParameter)

        self.inputParameterUnselect.setIcon(qta.icon('mdi.select-off', color='orange'))
        self.inputParameterUnselect.setToolTip('Clear selection')
        self.inputParameterUnselect.clicked.connect(self.unselectInputParameter)

        self.inputParameterFormat.setIcon(qta.icon('mdi.settings', color='orange'))
        self.inputParameterFormat.setToolTip('Show parameter formats')
        self.inputParameterFormat.clicked.connect(self.toggleInputParameterFormatVisible)
        self.inputParameterFormatVisible = False

        self.inputParameterMoveDown.setIcon(qta.icon('mdi.arrow-down-bold-box-outline', color='orange'))
        self.inputParameterMoveDown.setToolTip('Move selected parameter Down')
        self.inputParameterMoveDown.clicked.connect(self.moveInputParameterDown)

        self.inputParameterDelete.setIcon(qta.icon('mdi.minus-box-outline', color='orange'))
        self.inputParameterDelete.setToolTip('Delete selected parameter')
        self.inputParameterDelete.clicked.connect(self.deleteInputParameter)

        inputParameterHeaderLabels = ['Name', 'Min', 'Default', 'Max', '10ᵡ', 'Unit', 'fmt']
        self.inputParameterModel = QtGui.QStandardItemModel()
        self.inputParameterModel.setObjectName('inputParameters')
        self.inputParameterModel.setHorizontalHeaderLabels(inputParameterHeaderLabels)
        self.inputParameterModel.itemChanged.connect(self.inputParameterItemChanged)

        self.inputParameterView.horizontalHeader().setVisible(True)
        self.inputParameterView.verticalHeader().setVisible(True)
        self.inputParameterView.setModel(self.inputParameterModel)
        self.inputParameterView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems) # https://doc.qt.io/qt-5/qabstractitemview.html#SelectionBehavior-enum
        self.inputParameterView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection) # https://doc.qt.io/qt-5/qabstractitemview.html#SelectionMode-enum
        self.inputParameterView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu) # https://doc.qt.io/qt-5/qt.html#ContextMenuPolicy-enum
        self.inputParameterView.customContextMenuRequested.connect(self.inputParameterContextMenu)
        self.inputParameterView.selectionModel().selectionChanged.connect(self.inputParameterSelectionChanged) # https://doc.qt.io/qt-5/qitemselectionmodel.html

        self.inputParameterView.setItemDelegateForColumn(0, self.nameDelegator)
        self.inputParameterView.setItemDelegateForColumn(1, self.minDelegator)
        self.inputParameterView.setItemDelegateForColumn(2, self.defaultDelegator)
        self.inputParameterView.setItemDelegateForColumn(3, self.maxDelegator)
        self.inputParameterView.setItemDelegateForColumn(6, self.fmtDelegator)

        self.setInputpParameters(definition['input_parameters'])
        self.inputParameterView.setColumnHidden(6, True)
        self.inputParameterSelectionChanged()

    # OutputParametersTab
        self.outputParameterMoveUp.setIcon(qta.icon('mdi.arrow-up-bold-box-outline', color='orange'))
        self.outputParameterMoveUp.setToolTip('Move selected parameter Up')
        self.outputParameterMoveUp.clicked.connect(self.moveOutputParameterUp)

        self.outputParameterAdd.setIcon(qta.icon('mdi.plus-box-outline', color='orange'))
        self.outputParameterAdd.setToolTip('Add a parameter')
        self.outputParameterAdd.clicked.connect(self.addOutputParameter)

        self.outputParameterUnselect.setIcon(qta.icon('mdi.select-off', color='orange'))
        self.outputParameterUnselect.setToolTip('Clear selection')
        self.outputParameterUnselect.clicked.connect(self.unselectOutputParameter)

        self.outputParameterFormat.setIcon(qta.icon('mdi.settings', color='orange'))
        self.outputParameterFormat.setToolTip('Show parameter formats')
        self.outputParameterFormat.clicked.connect(self.toggleOutputParameterFormatVisible)
        self.outputParameterFormatVisible = False

        self.outputParameterMoveDown.setIcon(qta.icon('mdi.arrow-down-bold-box-outline', color='orange'))
        self.outputParameterMoveDown.setToolTip('Move selected parameter Down')
        self.outputParameterMoveDown.clicked.connect(self.moveOutputParameterDown)

        self.outputParameterDelete.setIcon(qta.icon('mdi.minus-box-outline', color='orange'))
        self.outputParameterDelete.setToolTip('Delete selected parameter')
        self.outputParameterDelete.clicked.connect(self.deleteOutputParameter)

        outputParameterHeaderLabels = ['Name', 'LSL', '(LTL)', 'Nom', '(UTL)', 'USL', '10ᵡ', 'Unit', 'fmt']
        self.outputParameterModel = QtGui.QStandardItemModel()
        self.outputParameterModel.setObjectName('outputParameters')
        self.outputParameterModel.setHorizontalHeaderLabels(outputParameterHeaderLabels)
        self.outputParameterModel.itemChanged.connect(self.outputParameterItemChanged)

        self.outputParameterView.horizontalHeader().setVisible(True)
        self.outputParameterView.verticalHeader().setVisible(True)
        self.outputParameterView.setModel(self.outputParameterModel)
        self.outputParameterView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems) # https://doc.qt.io/qt-5/qabstractitemview.html#SelectionBehavior-enum
        self.outputParameterView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection) # https://doc.qt.io/qt-5/qabstractitemview.html#SelectionMode-enum
        self.outputParameterView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu) # https://doc.qt.io/qt-5/qt.html#ContextMenuPolicy-enum
        self.outputParameterView.customContextMenuRequested.connect(self.outputParameterContextMenu)
        self.outputParameterView.selectionModel().selectionChanged.connect(self.outputParameterSelectionChanged) # https://doc.qt.io/qt-5/qitemselectionmodel.html

        self.outputParameterView.setItemDelegateForColumn(0, self.nameDelegator)
        self.outputParameterView.setItemDelegateForColumn(1, self.LSLDelegator)
        self.outputParameterView.setItemDelegateForColumn(2, self.LTLDelegator)
        self.outputParameterView.setItemDelegateForColumn(3, self.NomDelegator)
        self.outputParameterView.setItemDelegateForColumn(4, self.UTLDelegator)
        self.outputParameterView.setItemDelegateForColumn(5, self.USLDelegator)

        self.outputParameterView.setColumnHidden(8, True)
        self.setOutputParameters(definition['output_parameters'])
        self.outputParameterSelectionChanged()

        #TODO: Idea:
        #   limit the number of output parameters to 9, so we have a decade per test-number,
        #   and the '0' is the FTR 🙂

    # Tabs
        self.testTabs.currentChanged.connect(self.testTabChanged)
        self.testTabs.setTabEnabled(self.testTabs.indexOf(self.dependenciesTab), False)

    # buttons
        self.CancelButton.clicked.connect(self.CancelButtonPressed)
        self.OKButton.clicked.connect(self.OKButtonPressed)
        self.OKButton.setEnabled(False)

        self.show()
        self.resize(735, 400)
        self.verify()


    def getDateTime(self):
        now = datetime.now()
        quarter = f'(Q{((now.month-1)//3)+1} {now.year})'
        return f'{now.strftime("%A, %B %d %Y @ %H:%M:%S")} {quarter}'

    def verify(self):
        self.Feedback.setText("")
        # 1. Check that we have a hardware selected
        if self.ForHardwareSetup.currentText() == '':
            self.Feedback.setText("Select a 'hardware'")

        # 2. Check that we have a base selected
        if self.Feedback.text() == "":
            if self.WithBase.currentText() == '':
                self.Feedback.setText("Select a 'base'")

        # 3. Check if we have a test name
        if self.Feedback.text() == "":
            if self.TestName.text() == '':
                self.Feedback.setText("Supply a name for the test")

       # 6. Check if the test name holds the word 'Test' in any form
        if self.Feedback.text() == "":
            if not is_valid_test_name(self.TestName.text()):
                fb = "The test name can not contain the word 'TEST' in any form!"
                self.Feedback.setText(fb)
        #TODO: Enable again
        # 7. Check if the test name already exists
        # if self.Feedback.text() == "":
        #     existing_tests = self.project_info.get_tests_from_files(
        #         self.ForHardwareSetup.currentText(),
        #         self.WithBase.currentText())
        #     if self.TestName.text() in existing_tests:
        #         self.Feedback.setText("Test already exists!")

        # 8. see if we have at least XX characters in the description.
        # if self.Feedback.text() == "":
        #     docstring_length = self.descriptionLength()
        #     print(docstring_length)
        #     if docstring_length < minimal_docstring_length:
        #         self.Feedback.setText(f"Describe the test in at least {minimal_docstring_length} characters (spaces don't count, you have {docstring_length} characters)")

        # 9. Check the input parameters
        if self.Feedback.text() == "":
            pass

        # 10. Check the output parameters
        if self.Feedback.text() == "":
            pass

        # 11. Enable/disable the OKButton
        if self.Feedback.text() == "":
            self.OKButton.setEnabled(True)
        else:
            self.OKButton.setEnabled(False)

    def CancelButtonPressed(self):
        self.definition = {}
        self.reject()

    def OKButtonPressed(self):
        self.definition = {}
        self.definition['name'] = self.TestName.text()
        self.definition['type'] = "custom"
        self.definition['hardware'] = self.ForHardwareSetup.currentText()
        self.definition['base'] = self.WithBase.currentText()
        self.definition['docstring'] = self.description.toPlainText().split('\n')
        self.definition['input_parameters'] = self.getInputParameters()
        self.definition['output_parameters'] = self.getOutputParameters()
        self.definition['dependencies'] = {} # TODO: implement
        # self.project_info.add_test(name, hardware, base, test_type, test_data)
        self.accept()

def makeBlankFromDefinition(navigator):
    '''
    this function creates a blank definition dictionary with 'hardware', 'base' and name
    '''
    retval = {}
    retval['hardware'] = navigator.active_hardware
    retval['base'] = navigator.active_base
    retval['name'] = ''
    return retval

def makeBlankToDefinition(navigator):
    '''
    this function creates a blank definition dictionary with 'hardware', 'base' and name
    '''
    retval = {}
    retval['hardware'] = navigator.active_hardware
    retval['base'] = navigator.active_base
    retval['name'] = ''
    return retval

def cloneDialog(parent, navigator, fromDefinition=None, toDefinition=None):
    cloneWizard = CloneWizard(parent, navigator, fromDefinition, toDefinition)
    if cloneFromWizard.exec_(): # OK button pressed, thus exited with accept() and **NOT** with reject()
        definition = cloneFromWizard.definition
        retval = cloner(fromDefinition, toDefinition)
        print(retval)
    del(cloneFromWizard)


if __name__ == '__main__':
    print(make_blank_definition())


    # import sys, qdarkstyle
    # from ate_spyder.widgets.actions.dummy_main import DummyMainWindow

    # app = QtWidgets.QApplication(sys.argv)
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    # dummyMainWindow = DummyMainWindow()
    # dialog = TestWizard(dummyMainWindow)
    # dummyMainWindow.register_dialog(dialog)
    # sys.exit(app.exec_())
