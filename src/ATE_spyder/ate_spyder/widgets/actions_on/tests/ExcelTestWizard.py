# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 18:56:05 2022

@author: Zlin526F

References:
    TestWizard


todo:  dieser Wizard stellt zur Zeit nur einen einfachen Import von einer Exel liste zur Verfügung.
       es wird die datenbank und die zugehörigen python files für die einzelnen Test erzeugt.

       es fehlt:
           - parameter.name wird nicht auf fehlerhafte zeichen überprüft!
           - falsche einträge werden farbig dargestellt, nach dem editieren sollte die Farbe wieder auf den Default wert gesetzt werden
           - wenn Item ediert wird, muss danach automatisch der verify aktualisiert werden.
           - wenn ein Test name existiert, sollte ein Menü angeboten werden, für overwrite oder disable des Tests
           - Mapping file von Exel Paramter spalten zu Semi-ATE Parameter name sollte speicher und ladbar sein, im Moment nur fest kodiert
               siehe mappingATEDic
           - Mappjng file interactive erstellen
           - die erste Zeile, in der ein Wert in einer Spalte steht,  wird in dem Excel file genommen als Header. Es sollte über ein Menue
             auch andere Zeile gesetzt werden können
           - bei Änderung von Units sollte ein Menue angeboten werden mit möglichen SI-Einheiten
           - bei Import von Units, check if POWER.key exist, if yes dann zusätzliche Spalte erzeugen
           - Excel liste abspeicherbar nach Änderung

"""
from enum import Enum, unique
import os
import re

import numpy as np
import pandas as pd
import keyword
import qtawesome as qta
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog
from ate_spyder.widgets.validation import is_valid_test_name
from ate_spyder.widgets.validation import valid_default_float_regex
from ate_spyder.widgets.validation import valid_fmt_regex
from ate_spyder.widgets.validation import valid_max_float_regex
from ate_spyder.widgets.validation import valid_min_float_regex
# from ate_spyder.widgets.validation import valid_name_regex                 # TODO: add for validation
from ate_spyder.widgets.validation import is_valid_python_class_name
from ate_spyder.widgets.actions_on.utils import Delegator
from ate_spyder.widgets.actions_on.tests.Utils import POWER
from ate_spyder.widgets.actions_on.program.TestProgramWizard import ORANGE_LABEL, ORANGE
from ate_common.parameter import OutputColumnKey

from ate_spyder.widgets.constants import UpdateOptions

minimal_docstring_length = 80

MAX_OUTPUT_NUMBER = 100

mappingATEDic = {'Unnamed: 1': 'name',
                 'Test': 'No',
                 'FlowID': 'NaN',
                 'Name': 'output_parameters.name',
                 'Type': 'NaN',                            # function or parameter
                 'Low Limit': 'output_parameters.ltl',
                 'Units': 'output_parameters.unit',
                 'High Limit': 'output_parameters.utl',
                 'Mean': 'output_parameters.nom',
                 'Units.2': 'NaN',
                 'Unnamed: 12': 'NaN',                     # only for test, NaN
                 }


SI = ['s', 'm', 'g', 'A', 'K', 'mol', 'cd', 'rad', 'sr', 'Hz', 'N', 'Pa', 'J', 'W', 'C', 'V', 'F', 'Ω', 'S', 'Wb', 'T', 'H', 'lm'
      'lx', 'Bq', 'Gy', 'Sv', 'kat', '°C', 'Gs', '˽', '', ' ']


class CDelegator(Delegator):
    """in work isn't running correctly....

    It works with regex AND verifies that the name doesn't exist
    """

    def validate_text(self, line_edit: QtWidgets.QLineEdit):
        if not keyword.iskeyword(line_edit.text()):
            return

        if self.table is None or self.column is None:
            return

        col = self.table.selectionModel().currentIndex().column()
        row = self.table.selectionModel().currentIndex().row()
        if col == self.column:
            item = self.table.model().item(row, col)
            item.setText("")


class NameDelegator(Delegator):
    """Custom Delegator Class for 'Name'.

    It works with regex AND verifies that the name doesn't exist
    """

    def __init__(self, regex, existing_names, parent=None):
        self.super().__init__(regex, parent)
        self.existing_names = existing_names
        self.commitData.commitData.connect(self.validate_name)

    def validate_name(self, editor):
        """Make sure the entered name does not exist already."""
        # TODO: implement, e.q use valid_name_regex
        if editor.text() in self.existing_names:
            pass


class ExcelTestWizard(BaseDialog):
    """Wizard to import an Exel-file with the 'Test' definitions."""

    def __init__(self, project_info, filename):
        super().__init__(__file__, parent=project_info.parent)
        self.project_info = project_info

        test_content = TestWizard.make_blank_definition(project_info)
        self.test_content = test_content

        self.Feedback.setStyleSheet(ORANGE_LABEL)
        self.edit_feedback.setStyleSheet(ORANGE_LABEL)

        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

    # TestName
        self.TestName = ''     # todo: change self._init_group()

    # ForHardwareSetup
        self.ForHardwareSetup.setStyleSheet("font-weight: bold;")
        self.ForHardwareSetup.setText(self.project_info.active_hardware)
        if test_content['hardware'] != '':
            self.ForHardwareSetup.setText(test_content['hardware'])

    # WithBase
        self.WithBase.setStyleSheet("font-weight: bold")
        self.WithBase.setText(self.project_info.active_base)
        if test_content['base'] != '':
            self.WithBase.setText(test_content['base'])

    # Delegators
        self.fmtDelegator = Delegator(valid_fmt_regex, self)                             # TODO: selectionModel isn't available!
        self.minDelegator = Delegator(valid_min_float_regex, self)
        self.defaultDelegator = Delegator(valid_default_float_regex, self)
        self.maxDelegator = Delegator(valid_max_float_regex, self)
        self.lslDelegator = CDelegator(valid_min_float_regex, self)                                 # TODO: in work, try to switch color to default value after editing a wrong value...
        self.ltlDelegator = CDelegator(valid_min_float_regex, self)
        self.nomDelegator = Delegator(valid_default_float_regex, self)
        self.utlDelegator = Delegator(valid_max_float_regex, self)
        self.uslDelegator = Delegator(valid_max_float_regex, self)
        # self.nameDelegator = TestWizard.Delegator(valid_name_regex, parent=self, table=self.inputParameterView, column=InputColumnIndex.NAME())  # TODO: not running correcty

    # table
        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)

        self.get_excel_pages(filename)
        self.create_excel_table(filename)

        self._init_group()      # todo: if one test in a group, all other test will be enabled for this group :-(

    # Tabs
    # buttons
        self.mapping_load.setIcon(qta.icon('mdi.file-import', color='orange'))
        self.mapping_load.setToolTip('load mapping file')
        self.mapping_load.setEnabled(False)
        self.mapping_save.setIcon(qta.icon('mdi.content-save', color='orange'))
        self.mapping_save.setToolTip('save mapping file')
        self.mapping_save.setEnabled(False)

        self.CancelButton.clicked.connect(self.CancelButtonPressed)
        self.OKButton.clicked.connect(self.OKButtonPressed)
        self.OKButton.setEnabled(False)

        self._connect_event_handler()
        self.resize(1200, 650)

    def create_excel_table(self, filename):
        self._read_excel_page(filename)
        self.fillMappingList()
        self.mappATE2Excel()
        self.verify()

    def get_excel_pages(self, filename):
        self.ForFilename.setText(filename)
        self.ForFilename.setStyleSheet("font-weight: bold;")
        wb = pd.ExcelFile(filename)
        for page in wb.sheet_names:
            self.ForExcelPages.addItem(page)
        self.ForExcelPages.setCurrentIndex(0)
        self.ForExcelPages.activated.connect(lambda filename, value=filename: self.create_excel_table(value))

    def _read_excel_page(self, filename, headerindex=-1):
        def read_excel():
            return pd.read_excel(filename, engine='openpyxl', header=header, sheet_name=self.ForExcelPages.currentText())

        # find header: Is there an easier way to find the correct header line, if the first lines are empty?
        if headerindex == -1:
            for header in range(0, 10):
                wp = read_excel()
                index = 0
                for headertab in wp.columns:
                    if headertab.find(f'Unnamed: {index}') != 0:
                        headerindex = header
                        break
                    index += 1
                if headerindex != -1:
                    break
        else:
            header = headerindex
            wp = read_excel()
        self.headerindex = headerindex

        wp.dropna(how='all', axis=1, inplace=True)      # remove empty columns
        tb = self.table
        if tb.rowCount() > 0:
            tb.setRowCount(0)
        if tb.columnCount() > 0:
            tb.setColumnCount(0)

    # set headerline
        for column in wp.columns:
            tb.insertColumn(tb.columnCount())
            tb.setHorizontalHeaderItem(tb.columnCount()-1, QtWidgets.QTableWidgetItem(str(column)))
    # add an empty row for the mappings
        wp.loc[-1] = np.array([0] * wp.columns, dtype=str)
        wp.index += 1
        wp.sort_index(inplace=True)

    # fill the rows from the table with the excel-workpage
        col = 0
        for column in wp.columns:
            row = 0
            for val in wp[column]:
                if col == 0:
                    self.table.insertRow(row)
                if val == '' or pd.isnull(val):
                    val = ''
                item = QtWidgets.QTableWidgetItem()
                item.setText(str(val).strip())
                self.table.setItem(row, col, item)
                row += 1
            col += 1
        self.table.resizeColumnsToContents()
        self.workpage = wp

    def mappATE2Excel(self):
        """map header to the ATE test_content and coloration the used parameters in the table

        create mapping Dictionary excel to table columns
        """
        col = 0
        backgroundcolor = self.table.horizontalHeaderItem(0).background().color().name()        # TODO: color is not corrrect, how I get the used color?
        self.table.mapping = {}
        for header in self.workpage.columns:
            # self.table.setItem(0, col, QtWidgets.QTableWidgetItem(''))          #removeItem
            # self.table.removeCellWidget(0, col)
            if header in mappingATEDic.keys() and mappingATEDic[header] != 'NaN':
                self.table.setItem(0, col, QtWidgets.QTableWidgetItem(str(mappingATEDic[header])))
                self.table.item(0, col).setForeground(QtGui.QColor(0, 255, 0))
                self.table.mapping[str(mappingATEDic[header])] = col
                delegatorname = mappingATEDic[header].split('.')[1] if len(mappingATEDic[header].split('.')) > 1 else None
                if delegatorname is not None and delegatorname != 'name' and delegatorname != 'unit':
                    self.table.setItemDelegateForColumn(col, self.__getattribute__(f'{delegatorname}Delegator'))
                for index in range(self.MappingList.count()):
                    if self.MappingList.item(index).text() == mappingATEDic[header]:
                        self.MappingList.item(index).setForeground(QtGui.QColor(0, 255, 0))
            self.table.item(0, col).setBackground(QtGui.QColor(backgroundcolor))
            col += 1
        self.table.resizeColumnsToContents()

    def fillMappingList(self):
        testContent = self.test_content
        if 'hardware' in testContent:
            testContent.pop('hardware')
        if 'base' in testContent:
            testContent.pop('base')
        self.MappingList.clear()
        for key in testContent.keys():
            if type(testContent[key]) is not dict or len(testContent[key]) == 0:
                self.MappingList.addItem(key)
            else:
                self.MappingList.addItem(f'{key}.name')
                for childkey in testContent[key][list(testContent[key].keys())[0]].keys():
                    self.MappingList.addItem(f'{key}.{childkey}')

    def _connect_event_handler(self):
        self.testTabs.currentChanged.connect(self.testTabChanged)

    def testTabChanged(self, activatedTabIndex):
        """Slot for when the Tab is changed."""
        pass

    def resizeEvent(self, event):
        """Overload of Slot for when the Wizard is resized."""

        QtWidgets.QWidget.resizeEvent(self, event)

    def _update_power_with_correct_value(self, attributes):
        try:
            attributes[OutputColumnKey.POWER()] = POWER[attributes[OutputColumnKey.POWER()]]
        except KeyError:
            attributes[OutputColumnKey.POWER()] = self.get_key(attributes[OutputColumnKey.POWER()])

    # hack til the testwizard is refactored
    @staticmethod
    def get_key(attribute):
        for key, value in POWER.items():
            if value != attribute:
                continue

            return key

        return attribute

    @staticmethod
    def get_dicKey(dict, attribute):
        for key, value in dict.items():
            if attribute == value:
                return key
        # return attribute

    @staticmethod
    def _generate_color(color: tuple):
        return QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2]))

    def _set_widget_color(self, item, color):
        item.setBackground(self._generate_color(color))
        item.setForeground(QtCore.Qt.black)

    def verify(self):
        def check(mylist, testfunc, invert, msg, addAction=None):
            for value in mylist:
                if testfunc(value) ^ (not invert):
                    if self.Feedback.text() == "":
                        fb = f"{msg}       {value}"
                        self.Feedback.setText(fb)
                    matching_items = self.table.findItems(value, QtCore.Qt.MatchExactly)[0]
                    self._set_widget_color(matching_items, ORANGE)
                    if addAction is not None:
                        addAction(matching_items)

        def startWithInteger(string):
            return True if string[0].isnumeric() else False

        def addMenuOverwrite(item):
            # TODO: add ability for  overwriting
            # menu = QtWidgets.QMenu(self)
            # overwrite = menu.addAction("overwrite")
            # action = menu.exec_(self.table.mapToGlobal(item))
            print(item.text())

        self.Feedback.setText("")

        # TODO:  following code is an example if testname already exist,   add this ability in a future version
        # if self.read_only:
        #     dependant_programs = self.project_info.get_dependant_objects_for_test(self.TestName)
        #     # we don't care if the test not used yet !
        #     if len(dependant_programs):
        #         text = "edit test can invalidate the following test-program(s):\n"
        #         for _, programs in dependant_programs.items():
        #             for program in programs:
        #                 text += f"{ program }"

        #             text += ", "

        #         self.edit_feedback.setText(text)

        # 1. Check that we have a hardware selected
        if self.ForHardwareSetup.text() == '':
            self.Feedback.setText("Select a 'hardware'")

        # 2. Check that we have a base selected
        if self.Feedback.text() == "":
            if self.WithBase.text() == '':
                self.Feedback.setText("Select a 'base'")

        # 3. Check if we have a test name
        table_name = self.workpage[self.get_dicKey(mappingATEDic, 'name')]                     # todo: use it from table
        testNames = [str(x).strip() for x in table_name if not pd.isnull(x) and x != '']

        if self.Feedback.text() == "":
            if testNames == []:
                self.Feedback.setText("No test names found")

        # 4. make some checks with the test names
# todo: allow edit or overwrite
        if self.Feedback.text() == "":
            check(testNames, is_valid_test_name, False, "The test name is not valid, e.q. it can not contain the word 'TEST' in any form!")
            check(testNames, startWithInteger, True, "The test name is not valid, e.q. it can not start with a number!")
            check(testNames, self._does_test_exist, True, "test name already exists!", addMenuOverwrite)
            check(testNames, keyword.iskeyword, True, "python keyword should not be used as test name! ")

        # 5. Check the input/output parameters
        if self.Feedback.text() == "":
            for key in self.table.mapping.keys():
                if len(key.split('.')) > 1 and key.split('.')[1] == 'name':
                    for index in range(1, self.table.rowCount()):
                        text = self.table.item(index, self.table.mapping[key]).text()
                        check([text], is_valid_python_class_name, False, "The parameter name is not valid, character not allowed!")
                        check([text], startWithInteger, True, "The parameter name is not valid, e.q. it can not start with a number!")
                        # check(testNames, self._does_test_exist, True, "parameter name already exists!")
                        check([text], keyword.iskeyword, True, "python keyword should not be used as parameter name! ")
                    continue
                elif key.split('.')[0] != 'output_parameters' and key.split('.')[0] != 'input_parameters':
                    continue
                for index in range(1, self.table.rowCount()):
                    erroritem = None
                    text = self.table.item(index, self.table.mapping[key]).text()
                    if key.split('.')[1] == 'unit':
                        if not (text in SI or (len(text) > 1 and text[0] in POWER.keys() and text[1:] in SI)):                 # check if exp valid
                            erroritem = self.table.item(index, self.table.mapping[key])
                    elif not self._validate_isfloat(text):  # check for floats
                        erroritem = self.table.item(index, self.table.mapping[key])
                    if erroritem is not None:
                        self._set_widget_color(erroritem, ORANGE)
                        if self.Feedback.text() == "":
                            fb = f"error in {key}       {erroritem.text()}"
                            self.Feedback.setText(fb)
            # check MAX_OUTPUT_NUMBER

        if not len(self._get_groups()):
            self.Feedback.setText('make sure to select at least one Group')

        if self.Feedback.text() == "":
            self.OKButton.setEnabled(True)
        else:
            self.OKButton.setEnabled(False)
        self.testNames = testNames

    def _validate_isfloat(self, string):
        try:
            float(string)
            return True
        except ValueError:
            return False

    def _does_test_exist(self, test_name):
        tests = [test.name.lower() for test in self.project_info.get_tests_from_db(self.ForHardwareSetup.text(), self.WithBase.text())]
        if test_name.lower() in tests:
            return True

        return False

    def CancelButtonPressed(self):
        self.reject()

    def OKButtonPressed(self):
        def searchmapping(header):
            return self.get_dicKey(mappingATEDic, header)

        def searchAndAssign(header, default='', write_content=True):
            column = searchmapping(header)
            value = raw[column] if column is not None else default
            if write_content:
                test_content[header] = value
            return value

        test_content = {}
        wp = self.workpage
        for index in wp.index:
            raw = wp.loc[index]
            column = self.get_dicKey(mappingATEDic, 'name')
            TestName = raw[column].strip() if not pd.isnull(raw[column]) else ''
            if TestName == '' and test_content == {}:
                continue
            elif TestName != '' and test_content != {}:
                # if TestName not exist:                      # TODO: add
                self.project_info.add_custom_test(test_content)
                # else:
                #     update_option = self.__have_parameters_changed(test_content)
                #     self.project_info.update_custom_test(test_content, update_option)
            if TestName != '':
                test_content = {}
                test_content['type'] = "custom"
                test_content['hardware'] = self.ForHardwareSetup.text()
                test_content['base'] = self.WithBase.text()
                test_content['groups'] = self._get_groups()

                # assign name
                test_content['name'] = TestName

                searchAndAssign('docstring', [''])
                searchAndAssign('dependencies', {})
                test_content['input_parameters'] = {'Temperature': TestWizard.make_default_input_parameter(temperature=True)}
                test_content['input_parameters']['Temperature']['exp10'] = 0

            column = searchmapping('input_parameters.name')
            if column is not None:
                pass                      # todo: create input_parameters from the excel workpage

            column = searchmapping('output_parameters.name')
            if column is not None:
                name = searchAndAssign('output_parameters.name', write_content=False)
                output_parameters = TestWizard.make_default_output_parameter(empty=True)
                output_parameters['lsl'] = -np.inf
                output_parameters['usl'] = np.inf
                output_parameters['fmt'] = ".3f"
                output_parameters['exp10'] = 0

                for parameterName in mappingATEDic.values():
                    parameterName_split = parameterName.split('.')
                    if parameterName_split[0] == 'output_parameters':
                        if parameterName_split[1] != 'name':
                            value = searchAndAssign(parameterName, write_content=False)
                            if parameterName_split[1] == 'unit':
                                if (type(value) == str and value.strip() == '') or (type(value) == float and np.isnan(value)):
                                    value = '˽'
                                if type(value) == str and len(value) > 1 and value not in SI and value[0] in POWER.keys():
                                    output_parameters['exp10'] = POWER[value[0]]
                                    value = value[1:]
                            output_parameters[parameterName_split[1]] = value
                if 'output_parameters' not in test_content:
                    test_content['output_parameters'] = {name: output_parameters}
                else:
                    test_content['output_parameters'][name] = output_parameters

        if test_content != {}:
            self.project_info.add_custom_test(test_content)

        self.accept()

    def _get_groups(self):
        groups = []
        for index in range(self.group_combo.count()):
            item = self.group_combo.model().item(index, 0)
            if item.checkState() == QtCore.Qt.Unchecked:
                continue

            groups.append(item.text())

        return groups

    def __have_parameters_changed(self, content: dict) -> UpdateOptions:
        if len(content['input_parameters']) != len(self.test_content['input_parameters']) \
           or len(content['output_parameters']) != len(self.test_content['output_parameters']):
            return UpdateOptions.Code_Update()

        if self._check_content(self.test_content['input_parameters'], content['input_parameters']) \
           or self._check_content(self.test_content['output_parameters'], content['output_parameters']):
            return UpdateOptions.Code_Update()

        if not (set(self.project_info.get_groups_for_test(self.TestName)) & set(self._get_groups())):
            return UpdateOptions.Group_Update()

        return UpdateOptions.DB_Update()

    @staticmethod
    def _check_content(old_data, new_data):
        for key, value in old_data.items():
            if not new_data.get(key):
                return True

            for k, v in new_data[key].items():
                if str(value[k]) != str(v):
                    return True

        return False

    def _init_group(self):
        self.group_combo.blockSignals(True)
        self.group_combo.activated.connect(self._group_selected)
        groups = [group.name for group in self.project_info.get_groups()]

        for group_index, group in enumerate(groups):
            self.group_combo.insertItem(group_index, group)
            item = self.group_combo.model().item(group_index, 0)
            groups = [group.name for group in self.project_info.get_groups_for_test(self.TestName)]
            if groups:
                item.setCheckState(QtCore.Qt.Checked if group in groups else QtCore.Qt.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

        self.group_combo.setCurrentIndex(0)
        self.group_combo.blockSignals(False)

    @QtCore.pyqtSlot(int)
    def _group_selected(self, index: int):
        item = self.group_combo.model().item(index, 0)
        is_checked = item.checkState() == QtCore.Qt.Unchecked
        item.setCheckState(QtCore.Qt.Checked if is_checked else QtCore.Qt.Unchecked)

        # keep popup active till user change the focus
        self.group_combo.showPopup()
        self.verify()


def excel_test_dialog(project_info, selected_file):
    newTestWizard = ExcelTestWizard(project_info, selected_file)
    newTestWizard.exec_()
    del(newTestWizard)


if __name__ == "__main__":
    from ate_spyder.widgets.navigation import ProjectNavigation
    from ate_spyder.widgets.actions_on.utils.FileSystemOperator import FileSystemOperator
    from PyQt5.QtWidgets import QApplication
    from qtpy.QtWidgets import QMainWindow
    import qdarkstyle
    import sys

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    app.references = set()
    main = QMainWindow()
    homedir = os.path.expanduser("~")
    project_directory = homedir + r'\ATE\packages\envs\semi-ate-5\HATB'       # path to your semi-ate project
    project_info = ProjectNavigation(project_directory, homedir, main)
    project_info.active_hardware = 'HW0'
    project_info.active_base = 'FT'
    project_info.active_target = 'Device1'
    file_system_operator = FileSystemOperator(str(project_info.project_directory), project_info.parent)
    selected_file = file_system_operator.get_file('*.xlsx')
    excel_test_dialog(project_info, selected_file)
