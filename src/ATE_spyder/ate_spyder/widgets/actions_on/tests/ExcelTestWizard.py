# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 18:56:05 2022

@author: Zlin526F, hari999333

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
import gzip
import shutil
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
from ate_spyder.widgets.constants import UpdateOptions
from ate_spyder.widgets.actions_on.tests.Utils import POWER
from ate_spyder.widgets.actions_on.program.TestProgramWizard import ORANGE_LABEL, ORANGE

minimal_docstring_length = 80

MAX_OUTPUT_NUMBER = 100
BACKGROUNDCOLOR = (25, 35, 45)
FOREGROUNDCOLOR = (255, 255, 255)
YELLOW = (255, 255, 102)
GREY = (128, 128, 128)
OVERWRITE = 'overwrite'

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
        self.table.mappingDic = {}
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
        self.mapping_save.setEnabled(False)
        self.mapping_save.clicked.connect(self.mapping_save_pressed)

        self.CancelButton.clicked.connect(self.CancelButtonPressed)
        self.OKButton.clicked.connect(self.OKButtonPressed)
        self.OKButton.setEnabled(False)
        self.AcceptAllWarnings.toggled.connect(self.verify)

        self._connect_event_handler()
        self.resize(1200, 650)

        self.table.viewport().installEventFilter(self)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.openNameMenu)

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

    def openNameMenu(self, pos):
        row = self.table.rowAt(pos.y())
        column = self.table.columnAt(pos.x())
        item = self.table.item(row, column)
        if item.text() == "" or self.table.item(0, column).text() != 'name':
            return
        menu = QtWidgets.QMenu()
        menuActions = []
        if row == 0:
            actions = ["enable all", "disable all", "overwrite all"]
            for action in actions:
                menuActions.append(menu.addAction(action))
            action = menu.exec_(self.table.mapToGlobal(pos))
            if action is not None:
                for index in range(1, self.table.rowCount()):
                    item = self.table.item(index, column)
                    if item.text() != "":
                        newaction = action.text().split(" ")[0]
                        if newaction == 'overwrite' and not self._does_test_exist(item.text()):
                            newaction = 'enable'
                        item.action = newaction
        if row > 0:
            actions = ["disable"]
            exists = self._does_test_exist(item.text())
            # create menu:
            if not hasattr(item, 'action'):
                item.action = 'enable'
            if exists and item.action in ['enable', 'disable']:
                actions.append("overwrite")
            elif exists and item.action == 'overwrite':
                actions.append("enable")
            if item.action == 'disable':
                actions[0] = "enable"
            for action in actions:
                menuActions.append(menu.addAction(action))
            # do action:
            action = menu.exec_(self.table.mapToGlobal(pos))
            if action is not None:
                item.action = action.text()
        self.verify()

    def create_excel_table(self, filename):
        self._read_excel_page(filename)
        self.fill_mapping_list()
        # self.map_ATE_2_excel()    # this is not necessary anymore?
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
        for header in self.workpage.columns:
            if header in mappingATEDic.keys() and mappingATEDic[header] != 'NaN':
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
        self.MappingList.addItem('Pattern Path')
        self.mapping_list_dict.append('Pattern Path')

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
                self.table.mappingDic = {self.table.item(row, column).text(): column}
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
        if len(list(mappingATEDic.values())) == list(mappingATEDic.values()).count(''):
            self.mapping_save.setEnabled(False)
        else:
            self.mapping_save.setEnabled(True)
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

    def testNamesAction(self, items, msg):
        result = True
        for i in range(0, len(items)):
            action = 'enable'
            fb = f"{msg}       {items[i].text()}"
            exist = self._does_test_exist(items[i].text())
            if hasattr(items[i], "action"):
                action = items[i].action
            if action == 'overwrite' and exist:
                self._set_widget_color(items[i], YELLOW)
            elif action == 'disable':
                self._set_widget_color(items[i], GREY)

            if action == 'enable' and self.Feedback.text() == "":
                if exist:
                    self.Feedback.setText(fb)
                    result = False
                else:
                    self.Feedback.setText("")
            elif action != 'enable' and fb == self.Feedback.text():
                self.Feedback.setText("")
        return result

    def verify(self):
        def check(mylist, tableColumn, testfunc, invert, msg, addAction=None):
            result = True
            if mylist is not None:
                for value in mylist:
                    if tableColumn != -1:
                        matching_items = []
                        for rowIndex in range(self.table.rowCount()):
                            if self.table.item(rowIndex, tableColumn).text == value:
                                matching_items.append(self.table.item(rowIndex, tableColumn))
                    else:
                        matching_items = self.table.findItems(value, QtCore.Qt.MatchExactly)        # todo: validate only column not the complete table 

                    if testfunc(value) ^ (not invert):
                        for val in range(0, len(matching_items)):
                            # if self.table.column(matching_items[val]) == self.workpage.columns.get_loc(self.get_dicKey(mappingATEDic, 'name')):
                            self._set_widget_color(matching_items[val], ORANGE)
                        if addAction is not None:
                            addAction(matching_items, msg)
                        elif self.Feedback.text() == "":
                            fb = f"{msg}       {value}"
                            self.Feedback.setText(fb)
                            result = False
                    elif addAction is not None:
                        result = addAction(matching_items, msg)
            return result

        def startWithInteger(string):
            return True if string[0].isnumeric() else False

        def checkErrorItem(item, fb):
            if item is not None:
                self._set_widget_color(item, ORANGE)
                if self.Feedback.text() == "":
                    self.Feedback.setText(fb)

        def markAllWarnings(mark, errorfb):
            for key in mark:
                column = self.get_dicKey(mappingATEDic, key)
                if column is not None:
                    self.chooseAceptWarning = True
                    column = self.workpage.columns.get_loc(column)
                    erroritem = self.table.item(index, column)
                    checkErrorItem(erroritem, errorfb)

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
                self.table.item(i, j).setBackground(QtGui.QColor(self._generate_color(BACKGROUNDCOLOR)))
                self.table.item(i, j).setForeground(QtGui.QColor(self._generate_color(FOREGROUNDCOLOR)))

        # 3. Check if we have a test name
        testNames = []
        if 'name' in mappingATEDic.values():
            table_name = self.workpage[self.get_dicKey(mappingATEDic, 'name')]
            testnamelist = list(table_name)
            nameColumn = -1
            if hasattr(self.table.mappingDic, 'name'):
                nameColumn = self.table.mappingDic['name']
                for rowIndex in range(self.table.rowCount()):
                    if hasattr(self.table.item(rowIndex, nameColumn), 'action') and self.table.item(rowIndex, nameColumn).action == 'disable':
                        testnamelist.pop(rowIndex)
            testNames = [str(x).strip() for x in table_name if not pd.isnull(x) and str(x).strip() != '']
            self.testnamelist = [str(x).strip().lower() for x in testnamelist if not pd.isnull(x) and str(x).strip() != '']

        if self.Feedback.text() == "":
            if (testNames == []) or (set(testNames) == {''}):
                self.Feedback.setText("No test names found")

        # 4. make some checks with the test names
        if self.Feedback.text() == "":
            check(testNames, nameColumn, is_valid_test_name, False, "The test name is not valid, e.q. it can not contain the word 'TEST' in any form!")
            check(testNames, nameColumn, startWithInteger, True, "The test name is not valid, e.q. it can not start with a number!")
            check(testNames, nameColumn, self._does_test_exist, True, "test name already exists!", self.testNamesAction)
            check(testNames, nameColumn, keyword.iskeyword, True, "python keyword should not be used as test name! ")

        # 5. Check patterns
        if "patterns" in mappingATEDic.values():
            column = self.workpage.columns.get_loc(self.get_dicKey(mappingATEDic, "patterns"))
            for row in range(1, self.table.rowCount()):
                item = self.table.item(row, column)
                values = item.text()
                if values == '':
                    continue
                for value in values.split(','):
                    value = value.strip()
                    if not is_valid_python_class_name(value):
                        checkErrorItem(item, "The pattern name is not valid, character not allowed!")
                    elif startWithInteger(value):
                        checkErrorItem(item, "The pattern name is not valid, e.q. it can not start with a number!")
                    elif keyword.iskeyword(value):
                        checkErrorItem(item, "python keyword should not be used as pattern name! ")

        # 6. Check the input/output parameters
        self.chooseAceptWarning = False
        # if self.Feedback.text() == "":
        if True:
            for index in range(1, self.table.rowCount()):
                parameters = {'ltl': np.inf, 'utl': np.inf, 'nom': np.nan}
                for key in mappingATEDic.values():
                    if key == '':
                        continue
                    column = self.workpage.columns.get_loc(self.get_dicKey(mappingATEDic, key))
                    if len(key.split('.')) > 1 and key.split('.')[1] == 'name':
                        text = self.table.item(index, column).text()
                        check([text], -1, is_valid_python_class_name, False, "The parameter name is not valid, character not allowed!")
                        check([text], -1, startWithInteger, True, "The parameter name is not valid, e.q. it can not start with a number!")
                        # check([text], self._does_test_exist, True, "parameter name already exists!")
                        check([text], -1, keyword.iskeyword, True, "python keyword should not be used as parameter name! ")
                        continue
                    elif key.split('.')[0] != 'output_parameters' and key.split('.')[0] != 'input_parameters':
                        continue
                    # check values
                    erroritem = None
                    text = self.table.item(index, column).text()
                    paraName = key.split('.')[1]
                    if paraName == 'unit':
                        if not (text in SI or (len(text) > 1 and text[0] in POWER.keys() and text[1:] in SI)):                 # check if exp valid
                            erroritem = self.table.item(index, column)
                    elif not self._validate_isfloat(text):  # check for floats
                        erroritem = self.table.item(index, column)
                    elif paraName in ['ltl', 'utl', 'nom']:
                        parameters[paraName] = float(text)
                    checkErrorItem(erroritem,  f"error in {key}       {text}")
                # validation from ltl, utl, nom
                if (parameters['ltl'] != np.inf or parameters['utl'] != np.inf) and parameters['ltl'] > parameters['utl']:
                    markAllWarnings(['output_parameters.ltl', 'output_parameters.utl'],
                                    f"Warning: ltl({parameters['ltl']}) > utl({parameters['utl']})")
                if (parameters['ltl'] != np.inf or parameters['utl'] != np.inf) and (parameters['nom'] > parameters['utl']
                                                                                     or parameters['nom'] < parameters['ltl']):
                    markAllWarnings(['output_parameters.nom'],
                                    f"Warning: nom({parameters['nom']}) <> ltl({parameters['ltl']}) or utl({parameters['utl']})")
            # check MAX_OUTPUT_NUMBER

        # 7. Check the pattern path exist
        if "Pattern Path" in mappingATEDic.values():
            column = self.workpage.columns.get_loc(self.get_dicKey(mappingATEDic, "Pattern Path"))
            for row in range(1, self.table.rowCount()):
                text = self.table.item(row, column).text()
                if text == '':
                    continue
                elif not os.path.exists(text):
                    checkErrorItem(self.table.item(row, column), f'{self.get_dicKey(mappingATEDic, "Pattern Path")} not exist')

        if not len(self._get_groups()):
            self.Feedback.setText('make sure to select at least one Group')

        if self.req_headers_present is False:
            self.Feedback.setText("make sure to select the 'name' header")

        if self.chooseAceptWarning and self.Feedback.text().find('Warning:') == 0:
            self.AcceptAllWarnings.show()
        else:
            self.AcceptAllWarnings.hide()

        if self.Feedback.text() == "" or (self.AcceptAllWarnings.isVisible() and self.AcceptAllWarnings.isChecked()):
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
        if self.testnamelist.count(test_name.lower()) > 1:
            return True
        return False

    def CancelButtonPressed(self):
        self.reject()

    def OKButtonPressed(self):
        def searchmapping(header):
            return self.get_dicKey(mappingATEDic, header)

        def searchAndAssign(header, default='', write_content=True):
            column = searchmapping(header)
            value = row[column] if column is not None else default
            if write_content:
                test_content[header] = value
            return value

        def assignParameters(pName, parameters):
            for parameterName in mappingATEDic.values():
                parameterName_split = parameterName.split('.')
                if parameterName_split[0] == pName:
                    if parameterName_split[1] != 'name':
                        value = searchAndAssign(parameterName, write_content=False)
                        if parameterName_split[1] == 'unit':
                            if (type(value) == str and value.strip() == '') or (type(value) == float and np.isnan(value)):
                                value = '˽'
                            if type(value) == str and len(value) > 1 and value not in SI and value[0] in POWER.keys():
                                parameters['exp10'] = POWER[value[0]]
                                value = value[1:]
                        parameters[parameterName_split[1]] = value

        def create_default_outputparameters():
            output_parameters = utils.make_default_output_parameter(empty=True)
            output_parameters['lsl'] = -np.inf
            output_parameters['ltl'] = np.nan
            output_parameters['nom'] = 0.0
            output_parameters['utl'] = np.nan
            output_parameters['usl'] = np.inf
            output_parameters['fmt'] = ".3f"
            output_parameters['exp10'] = 0
            return output_parameters

        def create_update_custom_test(test_content, patterns):
            test_content['dependencies'] = {}
            test_content['patterns'] = patterns
            searchAndAssign('dependencies', {})
            matching_item = self.table.findItems(test_content["name"], QtCore.Qt.MatchExactly)[0]
            action = 'enable'
            if 'output_parameters' not in test_content.keys():
                test_content['output_parameters'] = {'new_parameter1': create_default_outputparameters()}
            if hasattr(matching_item, 'action'):
                action = matching_item.action
            if action == 'enable':
                msg = f'create {test_content["name"]}'
                self.Feedback.setText(msg)
                print(msg, test_content)
                self.project_info.add_custom_test(test_content)
            elif action == 'overwrite':
                msg = f'update {test_content["name"]}'
                self.Feedback.setText(msg)
                print(msg, test_content)
                update_option = self.__have_parameters_changed(test_content)
                self.project_info.update_custom_test(test_content, update_option)
            if action != 'disable':
                self.project_info.parent.sig_test_tree_update.emit()

        # QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        test_content = {}
        wp = self.workpage
        patterns = []
        for index in wp.index:
            row = wp.loc[index]
            column = self.get_dicKey(mappingATEDic, 'name')
            TestName = row[column].strip() if not pd.isnull(row[column]) else ''
            if TestName == '' and test_content == {}:
                continue
            elif TestName != '' and test_content != {}:
                create_update_custom_test(test_content, patterns)
                patterns = []
            if TestName != '':
                test_content = {}
                # assign name
                test_content['name'] = TestName

                test_content['type'] = "custom"
                test_content['hardware'] = self.ForHardwareSetup.text()
                test_content['base'] = self.WithBase.text()
                test_content['groups'] = self._get_groups()

                if type(searchAndAssign('docstring', [''])[0]) is not str:
                    test_content['docstring'][0] = str(test_content['docstring'][0])
                test_content['input_parameters'] = {'Temperature': utils.make_default_input_parameter(temperature=True)}
                test_content['input_parameters']['Temperature']['exp10'] = 0
                test_content['input_parameters']['Temperature'] = self.validationInputParameter(test_content['input_parameters']['Temperature'])

            column = searchmapping('input_parameters.name')
            if column is not None:
                name = searchAndAssign('input_parameters.name', write_content=False)
                input_parameters = utils.make_default_input_parameter()
                assignParameters('input_parameters', input_parameters)
                if 'input_parameters' not in test_content:
                    test_content['input_parameters'] = {name: input_parameters}
                else:
                    test_content['input_parameters'][name] = input_parameters

            column = searchmapping('output_parameters.name')
            if column is not None:
                name = searchAndAssign('output_parameters.name', write_content=False)
                output_parameters = create_default_outputparameters()
                assignParameters('output_parameters', output_parameters)

                if 'output_parameters' not in test_content:
                    test_content['output_parameters'] = {name: output_parameters}
                else:
                    test_content['output_parameters'][name] = output_parameters

            column = searchmapping('patterns')
            if column is not None and row[column] != "" and type(row[column]) == str:
                for value in row[column].split(','):
                    patterns.append(value.strip())

            column = searchmapping('Pattern Path')
            if column is not None and TestName != '':
                if type(row[column]) != str:
                    continue
                new_file = os.path.splitext(row[column])[0] if os.path.splitext(row[column])[1] == '.gz' else row[column]
                new_file = os.path.join(self.project_info.project_directory,
                                        'pattern',
                                        self.project_info.active_hardware,
                                        self.project_info.active_base,
                                        self.project_info.active_target,
                                        os.path.basename(new_file))
                if os.path.exists(new_file) and os.stat(row[column]).st_mtime - os.stat(new_file).st_mtime < 0:
                    continue

                if os.path.splitext(row[column])[1] == '.gz':
                    with gzip.open(row[column], 'r') as f_in:
                        with open(new_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                else:
                    shutil.copyfile(row[column], new_file)

        if test_content != {}:
            create_update_custom_test(test_content, patterns)

        # QtWidgets.QApplication.restoreOverrideCursor()
        self.accept()

    def validationInputParameter(self, parameters):
        parameters['min'] = float(parameters['min'])
        parameters['default'] = float(parameters['default'])
        parameters['max'] = float(parameters['max'])

        return parameters

    def _get_test_content(self, name):
        return self.project_info.get_test_table_content(name, self.project_info.active_hardware, self.project_info.active_base)

    def __have_parameters_changed(self, content: dict) -> UpdateOptions:
        db_content = self._get_test_content(content['name'])
        if len(content['input_parameters']) != len(db_content['input_parameters']) \
           or len(content['output_parameters']) != len(db_content['output_parameters']):
            return UpdateOptions.Code_Update()

        if self._check_content(db_content['input_parameters'], content['input_parameters']) \
           or self._check_content(db_content['output_parameters'], content['output_parameters']):
            return UpdateOptions.Code_Update()

        if self._check_content(db_content['patterns'], content['patterns']):
            return UpdateOptions.Code_Update()

        group_names = set([group.name for group in self.project_info.get_groups_for_test(content['name'])])
        if group_names != set(self._get_groups()):
            return UpdateOptions.Group_Update()

        return UpdateOptions.DB_Update()

    @staticmethod
    def _check_content(old_data, new_data):
        if type(old_data) == list:
            if len(old_data) != len(new_data):
                return True
            for index in range(0, len(old_data)):
                if old_data[index] != new_data[index]:
                    return True
            return False
        for key, value in old_data.items():
            if not new_data.get(key):
                return True

            for k, v in new_data[key].items():
                if str(value[k]) != str(v):
                    return True

        return False

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

            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
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
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

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
    del (newTestWizard)


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
    project_directory = homedir + r'\ATE\packages\envs\tb_ate'    # path to your semi-ate project
    project_info = ProjectNavigation(project_directory, homedir, main)
    project_info.active_hardware = 'HW0'
    project_info.active_base = 'FT'
    project_info.active_target = 'Device1'
    file_system_operator = FileSystemOperator(str(project_info.project_directory), project_info.parent)
    selected_file = file_system_operator.get_file('*.xlsx')
    excel_test_dialog(project_info, selected_file)
