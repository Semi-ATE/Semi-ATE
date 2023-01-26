# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 18:56:05 2022

@author: Zlin526F

Starting from TestWizard.py

"""
import os
import re
from typing import Optional
import json

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
from ate_spyder.widgets.validation import is_valid_python_class_name
import ate_spyder.widgets.actions_on.tests.Utils as utils
from ate_spyder.widgets.actions_on.tests.Utils import POWER
from ate_spyder.widgets.actions_on.program.TestProgramWizard import ORANGE_LABEL, ORANGE

minimal_docstring_length = 80

MAX_OUTPUT_NUMBER = 100

mappingATEDic = {'Empty_Field_999': ''}


SI = ['s', 'm', 'g', 'A', 'K', 'mol', 'cd', 'rad', 'sr', 'Hz', 'N', 'Pa', 'J', 'W', 'C', 'V', 'F', 'Ω', 'S', 'Wb', 'T', 'H', 'lm'
      'lx', 'Bq', 'Gy', 'Sv', 'kat', '°C', 'Gs', '˽', '', ' ']


class CDelegator(utils.Delegator):
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


class ExcelTestWizard(BaseDialog):
    """Wizard to import an Exel-file with the 'Test' definitions."""

    def __init__(self, project_info, filename):
        super().__init__(__file__, parent=project_info.parent)
        self.project_info = project_info

        test_content = utils.make_blank_definition(project_info)
        self.test_content = test_content

        self.Feedback.setStyleSheet(ORANGE_LABEL)
        self.edit_feedback.setStyleSheet(ORANGE_LABEL)

        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        # TestName
        self.TestName = ''

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
        self.fmtDelegator = utils.Delegator(valid_fmt_regex, self)
        self.minDelegator = utils.Delegator(valid_min_float_regex, self)
        self.defaultDelegator = utils.Delegator(valid_default_float_regex, self)
        self.maxDelegator = utils.Delegator(valid_max_float_regex, self)
        self.lslDelegator = CDelegator(valid_min_float_regex, self)
        self.ltlDelegator = CDelegator(valid_min_float_regex, self)
        self.nomDelegator = utils.Delegator(valid_default_float_regex, self)
        self.utlDelegator = utils.Delegator(valid_max_float_regex, self)
        self.uslDelegator = utils.Delegator(valid_max_float_regex, self)

        # table
        self.table.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
        self.req_headers_present = False

        self.get_excel_pages(filename)
        self.create_excel_table(filename)

        self._init_group()

        # Tabs
        # buttons
        self.mapping_load.setIcon(qta.icon('mdi.file-import', color='orange'))
        self.mapping_load.setToolTip('load mapping file')
        self.mapping_load.setEnabled(True)
        self.mapping_load.clicked.connect(self.mapping_load_pressed)
        self.mapping_save.setIcon(qta.icon('mdi.content-save', color='orange'))
        self.mapping_save.setToolTip('save mapping file')
        self.mapping_save.setEnabled(True)
        self.mapping_save.clicked.connect(self.mapping_save_pressed)

        self.CancelButton.clicked.connect(self.CancelButtonPressed)
        self.OKButton.clicked.connect(self.OKButtonPressed)
        self.OKButton.setEnabled(False)

        self._connect_event_handler()
        self.resize(1200, 650)

        self.table.viewport().installEventFilter(self)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

    def eventFilter(self, source, event):
        if source is self.table.viewport() and event.type() == QtCore.QEvent.Drop:
            pos = event.pos()
            row = self.table.rowAt(pos.y())
            column = self.table.columnAt(pos.x())
            if row > 0 or self.table.item(row, column).text() != "":
                event.ignore()
                return True
            else:
                return super().eventFilter(source, event)
        return super().eventFilter(source, event)

    def create_excel_table(self, filename):
        self._read_excel_page(filename)
        self.fill_mapping_list()
        self.map_ATE_2_excel()
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

        # remove empty columns
        wp.dropna(how='all', axis=1, inplace=True)
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
                if row != 0:
                    self.table.item(row, col).setFlags(QtCore.Qt.NoItemFlags)
                row += 1
            col += 1
        self.table.resizeColumnsToContents()
        mappingATEDic.update(dict.fromkeys(wp.columns, ''))
        if 'Empty_Field_999' in mappingATEDic.keys():
            mappingATEDic.pop('Empty_Field_999')
        self.workpage = wp

    def map_ATE_2_excel(self):
        """map header to the ATE test_content and coloration the used parameters in the table

        create mapping Dictionary excel to table columns
        """
        col = 0
        backgroundcolor = self.table.horizontalHeaderItem(0).background().color().name()
        self.table.mapping = {}
        for header in self.workpage.columns:
            if header in mappingATEDic.keys() and mappingATEDic[header] != 'NaN':
                self.table.mapping[str(mappingATEDic[header])] = col
                delegatorname = mappingATEDic[header].split('.')[1] if len(mappingATEDic[header].split('.')) > 1 else None
                if delegatorname is not None and delegatorname != 'name' and delegatorname != 'unit':
                    self.table.setItemDelegateForColumn(col, self.__getattribute__(f'{delegatorname}Delegator'))
                for index in range(self.MappingList.count()):
                    if self.MappingList.item(index).text() == mappingATEDic[header]:
                        self.MappingList.item(index).setForeground(QtGui.QColor(255, 255, 255))
            self.table.item(0, col).setBackground(QtGui.QColor(backgroundcolor))
            col += 1
        self.table.resizeColumnsToContents()

    def fill_mapping_list(self):
        self.mapping_list_dict = []
        testContent = self.test_content
        testContent['No'] = ''
        if 'hardware' in testContent:
            testContent.pop('hardware')
        if 'base' in testContent:
            testContent.pop('base')
        self.MappingList.clear()
        for key in testContent.keys():
            if type(testContent[key]) is not dict or len(testContent[key]) == 0:
                self.MappingList.addItem(key)
                self.mapping_list_dict.append(key)
            else:
                self.MappingList.addItem(f'{key}.name')
                self.mapping_list_dict.append(f'{key}.name')
                for childkey in testContent[key][list(testContent[key].keys())[0]].keys():
                    self.MappingList.addItem(f'{key}.{childkey}')
                    self.mapping_list_dict.append(f'{key}.{childkey}')

    def _connect_event_handler(self):
        self.table.cellChanged.connect(self.makeHeaderBold)
        self.MappingList.itemChanged.connect(self.makeElementNormal)

    def makeHeaderBold(self, row, column):
        if row == 0:
            bold_font = QtGui.QFont()
            bold_font.setBold(True)
            bold_font.setPointSize(11)
            try:
                self.table.item(row, column).setBackground(QtGui.QColor(25, 35, 45))
                self.table.item(row, column).setFont(bold_font)
            except AttributeError:
                pass
        else:
            return

        self.req_headers_present = False
        current_header_list = []
        for col in range(len(self.workpage.columns)):
            if self.table.item(0, col) is None:
                empty_text = ''
                self.table.setItem(0, col, QtWidgets.QTableWidgetItem(str(empty_text)))
            if self.table.item(0, col) is not None:
                current_header_list.append(self.table.item(0, col).text())
            try:
                if 'name' in current_header_list:
                    self.req_headers_present = True
                else:
                    self.req_headers_present = False
            except AttributeError:
                pass

        mappingATEDic_update = dict(zip(mappingATEDic, current_header_list))
        mappingATEDic.update(mappingATEDic_update)
        self.verify()

    def makeElementNormal(self, item_selected):
        unbold_font = QtGui.QFont()
        unbold_font.setBold(False)
        unbold_font.setPointSize(9)
        for i in range(self.MappingList.count()):
            self.MappingList.item(i).setFont(unbold_font)
        self.MappingList.setSortingEnabled(True)
        self.MappingList.sortItems()

    @staticmethod
    def get_dicKey(dict, attribute) -> Optional[str]:
        for key, value in dict.items():
            if attribute == value:
                return key

    @staticmethod
    def _generate_color(color: tuple):
        return QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2]))

    def _set_widget_color(self, item, color):
        item.setBackground(self._generate_color(color))
        item.setForeground(QtCore.Qt.black)

    def verify(self):
        def check(mylist, testfunc, invert, msg, addAction=None):
            if mylist is not None:
                for value in mylist:
                    if testfunc(value) ^ (not invert):
                        if self.Feedback.text() == "":
                            fb = f"{msg}       {value}"
                            self.Feedback.setText(fb)
                        matching_items = self.table.findItems(value, QtCore.Qt.MatchExactly)
                        for val in range(0, len(matching_items)):
                            if self.table.column(matching_items[val]) == self.workpage.columns.get_loc(self.get_dicKey(mappingATEDic, 'name')):
                                self._set_widget_color(matching_items[val], ORANGE)
                                break
                        if addAction is not None:
                            addAction(matching_items)

        def startWithInteger(string):
            return True if string[0].isnumeric() else False

        def addMenuOverwrite(item):
            pass

        self.Feedback.setText("")

        # 1. Check that we have a hardware selected
        if self.ForHardwareSetup.text() == '':
            self.Feedback.setText("Select a 'hardware'")

        # 2. Check that we have a base selected
        if self.Feedback.text() == "":
            if self.WithBase.text() == '':
                self.Feedback.setText("Select a 'base'")

        for i in range(1, self.table.rowCount()):
            for j in range(0, self.table.columnCount()):
                self.table.item(i, j).setBackground(QtGui.QColor(25, 35, 45))
                self.table.item(i, j).setForeground(QtGui.QColor(255, 255, 255))

        # 3. Check if we have a test name
        testNames = []
        if 'name' in mappingATEDic.values():
            table_name = self.workpage[self.get_dicKey(mappingATEDic, 'name')]
            testNames = [str(x).strip() for x in table_name if not pd.isnull(x) and str(x).strip() != '']

        if self.Feedback.text() == "":
            if (testNames == []) or (set(testNames) == {''}):
                self.Feedback.setText("No test names found")

        # 4. make some checks with the test names
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

        if self.req_headers_present is False:
            self.Feedback.setText("make sure to select the 'name' header")

        if self.Feedback.text() == "":
            self.OKButton.setEnabled(True)
        else:
            self.OKButton.setEnabled(False)
            # self.Feedback.setText('make sure to select all the headers')
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
                self.Feedback.setText('create {test_content["name"]}')
                self.project_info.add_custom_test(test_content)
            if TestName != '':
                test_content = {}
                test_content['type'] = "custom"
                test_content['hardware'] = self.ForHardwareSetup.text()
                test_content['base'] = self.WithBase.text()
                test_content['groups'] = self._get_groups()
                test_content['patterns'] = {}

                # assign name
                test_content['name'] = TestName

                if type(searchAndAssign('docstring', [''])[0]) is not str:
                    test_content['docstring'][0] = str(test_content['docstring'][0])
                searchAndAssign('dependencies', {})
                test_content['input_parameters'] = {'Temperature': utils.make_default_input_parameter(temperature=True)}
                test_content['input_parameters']['Temperature']['exp10'] = 0

            column = searchmapping('input_parameters.name')
            if column is not None:
                pass

            column = searchmapping('output_parameters.name')
            if column is not None:
                name = searchAndAssign('output_parameters.name', write_content=False)
                output_parameters = utils.make_default_output_parameter(empty=True)
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

    def mapping_save_pressed(self):
        try:
            new_excel_import_path = os.path.join(self.project_info.project_directory, "definitions/excel_import")
            if not os.path.exists(new_excel_import_path):
                os.mkdir(new_excel_import_path)

            json_file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save .json File', new_excel_import_path, 'JSON File (*.json)')
            json_file = os.path.join(new_excel_import_path, json_file_name)

            self.table.setUpdatesEnabled(True)
            self.table.update()
            dict_to_list = list(mappingATEDic.items())
            for col in range(len(mappingATEDic)):
                header_item = self.table.item(0, col).text()
                dict_to_list[col] = list(dict_to_list[col])
                dict_to_list[col][1] = header_item
            list_to_dict = dict(dict_to_list)

            j = json.dumps(list_to_dict, indent=4)
            with open(json_file, 'w') as f:
                f.write(j)
                f.close()

        except FileNotFoundError:
            pass

    def mapping_load_pressed(self):
        try:
            json_import_path = os.path.join(self.project_info.project_directory, "definitions/excel_import")
            if not os.path.exists(json_import_path):
                os.mkdir(json_import_path)
            json_file, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Load .json File', json_import_path, 'JSON File (*.json)')

            with open(json_file, 'r') as f:
                self.json_header_data = json.load(f)

            dict_to_list = list(self.json_header_data.items())
            for col in range(len(dict_to_list)):
                dict_to_list[col] = list(dict_to_list[col])
                header_item = dict_to_list[col][1]
                self.table.setItem(0, col, QtWidgets.QTableWidgetItem(str(header_item)))

            for header in range(len(dict_to_list)):
                for item in range(self.MappingList.count()):
                    try:
                        if (dict_to_list[header][1] == self.MappingList.item(item).text()):
                            self.MappingList.takeItem(item)
                    except AttributeError:
                        pass
        except FileNotFoundError:
            pass

    def _get_groups(self):
        groups = []
        for index in range(self.group_combo.count()):
            item = self.group_combo.model().item(index, 0)
            if item.checkState() == QtCore.Qt.Unchecked:
                continue

            groups.append(item.text())

        return groups

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


# if __name__ == "__main__":
#     from ate_spyder.widgets.navigation import ProjectNavigation
#     from ate_spyder.widgets.actions_on.utils.FileSystemOperator import FileSystemOperator
#     from PyQt5.QtWidgets import QApplication
#     from qtpy.QtWidgets import QMainWindow
#     import qdarkstyle
#     import sys

#     app = QApplication(sys.argv)
#     app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
#     app.references = set()
#     main = QMainWindow()
#     homedir = os.path.expanduser("~")
#     project_directory = homedir + r'\ATE\tb_ate'       # path to your semi-ate project
#     project_info = ProjectNavigation(project_directory, homedir, main)
#     project_info.active_hardware = 'HW0'
#     project_info.active_base = 'FT'
#     project_info.active_target = 'Device1'
#     file_system_operator = FileSystemOperator(str(project_info.project_directory), project_info.parent)
#     selected_file = file_system_operator.get_file('*.xlsx')
#     excel_test_dialog(project_info, selected_file)
