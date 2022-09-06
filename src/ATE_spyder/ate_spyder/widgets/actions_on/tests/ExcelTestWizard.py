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
from ate_spyder.widgets.validation import valid_name_regex
from ate_spyder.widgets.validation import is_valid_python_class_name
from ate_spyder.widgets.actions_on.tests import TestWizard
from ate_spyder.widgets.actions_on.tests.Utils import POWER
from ate_spyder.widgets.actions_on.program.TestProgramWizard import ORANGE_LABEL, ORANGE
from ate_common.parameter import InputColumnKey, OutputColumnKey

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


@unique
class InputColumnIndex(Enum):
    SHMOO = 0
    NAME = 1
    MIN = 2
    DEFAULT = 3
    MAX = 4
    POWER = 5
    UNIT = 6
    FMT = 7

    def __call__(self):
        return self.value

@unique
class OutputColumnIndex(Enum):
    NAME = 0
    LSL = 1
    LTL = 2
    NOM = 3
    UTL = 4
    USL = 5
    POWER = 6
    UNIT = 7
    MPR = 8
    FMT = 9

    def __call__(self):
        return self.value


class CDelegator(TestWizard.Delegator):
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


class NameDelegator(TestWizard.Delegator):
    """Custom Delegator Class for 'Name'.

    It works with regex AND verifies that the name doesn't exist
    """

    def __init__(self, regex, existing_names, parent=None):
        self.super().__init__(regex, parent)
        self.existing_names = existing_names
        self.commitData.commitData.connect(self.validate_name)

    def validate_name(self, editor):
        """Make sure the entered name does not exist already."""
        # TODO: implement
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
        self.fmtDelegator = TestWizard.Delegator(valid_fmt_regex, self)                             # todo: selectionModel isn't available!
        self.minDelegator = TestWizard.Delegator(valid_min_float_regex, self)
        self.defaultDelegator = TestWizard.Delegator(valid_default_float_regex, self)
        self.maxDelegator = TestWizard.Delegator(valid_max_float_regex, self)
        self.lslDelegator = CDelegator(valid_min_float_regex, self)                                 # todo: in work, try to switch color to default value after editing a wrong value...
        self.ltlDelegator = CDelegator(valid_min_float_regex, self)
        self.nomDelegator = TestWizard.Delegator(valid_default_float_regex, self)
        self.utlDelegator = TestWizard.Delegator(valid_max_float_regex, self)
        self.uslDelegator = TestWizard.Delegator(valid_max_float_regex, self)
        # self.nameDelegator = TestWizard.Delegator(valid_name_regex, parent=self, table=self.inputParameterView, column=InputColumnIndex.NAME())

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
        backgroundcolor = self.table.horizontalHeaderItem(0).background().color().name()        # todo: color is not corrrect, how I get the used color?
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

    def unitContextMenu(self, unitSetter):
        """Deploys the OutputColumnKey.UNIT() context menu and applies selection to 'unitSetter'.

        _References_
            - SI: https://en.wikipedia.org/wiki/International_System_of_Units
            - unicode characters: https://en.wikipedia.org/wiki/List_of_Unicode_characters

        """
        menu = QtWidgets.QMenu(self)

        base_units = [
            ('s (time - second)',
             lambda: unitSetter('s', 'time - second')),
            ('m (length - meter)',
             lambda: unitSetter('m', 'length - meter')),
            ('kg (mass - kilogram)',
             lambda: unitSetter('kg', 'mass - kilogram')),
            ('A (electric current - ampères)',
             lambda: unitSetter('A', 'electric current - ampères')),
            ('K (temperature - Kelvin)',
             lambda: unitSetter('K', 'temperature - Kelvin')),
            ('mol (amount of substance - mole)',
             lambda: unitSetter('mol', 'amount of substance - mole')),
            ('cd (luminous intensity - candela)',
             lambda: unitSetter('cd', 'luminous intensity - candela'))]
        for unit in base_units:
            item = menu.addAction(unit[0])
            item.triggered.connect(unit[1])
        menu.addSeparator()

        derived_units = [
            ('rad (plane angle - radian = m/m)',
             lambda: unitSetter('rad', 'plane angle - radian = m/m')),
            ('sr (solid angle - steradian = m²/m²)',
             lambda: unitSetter('sr', 'solid angle - steradian = m²/m²')),
            ('Hz (frequency - hertz = s⁻¹)',
             lambda: unitSetter('Hz', 'frequency - hertz = s⁻¹')),
            ('N (force, weight - newton = kg⋅m⋅s⁻²)',
             lambda: unitSetter('N', 'force, weight - newton = kg⋅m⋅s⁻²')),
            ('Pa ( pressure, stress - pascal = kg⋅m⁻¹⋅s⁻²)',
             lambda: unitSetter('Pa', 'pressure, stress - pascal = kg⋅m⁻¹⋅s⁻²')),
            ('J (energy, work, heat - joule = kg⋅m²⋅s⁻² = N⋅m = Pa⋅m³)',
             lambda: unitSetter('J', 'energy, work, heat - joule = kg⋅m²⋅s⁻² = N⋅m = Pa⋅m³')),
            ('W (power, radiant flux - watt = kg⋅m²⋅s⁻³ = J/s)',
             lambda: unitSetter('W', 'power, radiant flux - watt = kg⋅m²⋅s⁻³ = J/s')),
            ('C (electric charge - coulomb = s⋅A)',
             lambda: unitSetter('C', 'electric charge - coulomb = s⋅A')),
            ('V (electric potential, emf - volt = kg⋅m²⋅s⁻³⋅A⁻¹ = W/A = J/C)',
             lambda: unitSetter('V', 'electric potential, emf - volt = kg⋅m²⋅s⁻³⋅A⁻¹ = W/A = J/C')),
            ('F (electric capacitance - farad = kg⁻¹⋅m⁻²⋅s⁴⋅A² = C/V)',
             lambda: unitSetter('F', 'electric capacitance - farad = kg⁻¹⋅m⁻²⋅s⁴⋅A² = C/V')),
            ('Ω (electric resistance, impedance, reactance - ohm = kg⋅m²⋅s⁻³⋅A⁻² = V/A)',
             lambda: unitSetter('Ω', 'electric resistance, impedance, reactance - ohm = kg⋅m²⋅s⁻³⋅A⁻² = V/A')),
            ('S (electric conductance - siemens = kg⁻¹⋅m⁻²⋅s³⋅A² = Ω⁻¹)',
             lambda: unitSetter('S', 'electric conductance - siemens = kg⁻¹⋅m⁻²⋅s³⋅A² = Ω⁻¹')),
            ('Wb (magnetic flux - weber = kg⋅m²⋅s⁻²⋅A⁻¹ = V⋅s)',
             lambda: unitSetter('Wb', 'magnetic flux - weber = kg⋅m²⋅s⁻²⋅A⁻¹ = V⋅s')),
            ('T (magnetic flux density - tesla = kg⋅s⁻²⋅A⁻¹ = Wb/m²)',
             lambda: unitSetter('T', 'magnetic flux density - tesla = kg⋅s⁻²⋅A⁻¹ = Wb/m²')),
            ('H (electric inductance - henry = kg⋅m²⋅s⁻²⋅A⁻² = Wb/A)',
             lambda: unitSetter('H', 'electric inductance - henry = kg⋅m²⋅s⁻²⋅A⁻² = Wb/A')),
            ('lm (luminous flux - lumen = cd⋅sr)',
             lambda: unitSetter('lm', 'luminous flux - lumen = cd⋅sr')),
            ('lx (illuminance - lux = m⁻²⋅cd = lm/m²)',
             lambda: unitSetter('lx', 'illuminance - lux = m⁻²⋅cd = lm/m²')),
            ('Bq (radioactivity - Becquerel = s⁻¹)',
             lambda: unitSetter('Bq', 'radioactivity - Becquerel = s⁻¹')),
            ('Gy (absorbed dose - gray = m²⋅s⁻² = J/kg)',
             lambda: unitSetter('Gy', 'absorbed dose - gray = m²⋅s⁻² = J/kg')),
            ('Sv (equivalent dose - sievert = m²⋅s⁻² = J/kg)',
             lambda: unitSetter('Sv', 'equivalent dose - sievert = m²⋅s⁻² = J/kg')),
            ('kat (catalytic activity - katal = mol⋅s⁻¹)',
             lambda: unitSetter('kat', 'catalytic activity - katal = mol⋅s⁻¹'))]
        for unit in derived_units:
            item = menu.addAction(unit[0])
            item.triggered.connect(unit[1])
        menu.addSeparator()

        alternative_units = [
            ('°C (temperature - degree Celcius = K - 273.15)',
             lambda: unitSetter('°C', 'temperature - degree Celcius = K - 273.15')),
            ('Gs (magnetic flux density - gauss = 10⁻⁴ Tesla)',
             lambda: unitSetter('Gs', 'magnetic flux density - gauss = 10⁻⁴ Tesla')),
            ('˽ (no dimension / unit)',
             lambda: unitSetter('˽', 'no dimension / unit'))]
        for unit in alternative_units:
            item = menu.addAction(unit[0])
            item.triggered.connect(unit[1])
        return menu

    def multiplierContextMenu(self, multiplierSetter):
        """Deploys the 'multiplier' context menu and applies selection to 'multiplierSetter'."""
        menu = QtWidgets.QMenu(self)
        normal_multipliers = [
            ('y (yocto=10⁻²⁴)',
             lambda: multiplierSetter('y', 'yocto=10⁻²⁴')),
            ('z (zepto=10⁻²¹)',
             lambda: multiplierSetter('z', 'zepto=10⁻²¹')),
            ('a (atto=10⁻¹⁸)',
             lambda: multiplierSetter('a', 'atto=10⁻¹⁸')),
            ('f (femto=10⁻¹⁵)',
             lambda: multiplierSetter('f', 'femto=10⁻¹⁵')),
            ('p (pico=10⁻¹²)',
             lambda: multiplierSetter('p', 'pico=10⁻¹²')),
            ('n (nano=10⁻⁹)',
             lambda: multiplierSetter('n', 'nano=10⁻⁹')),
            ('μ (micro=10⁻⁶)',
             lambda: multiplierSetter('μ', 'micro=10⁻⁶')),
            ('m (mili=10⁻³)',
             lambda: multiplierSetter('m', 'mili=10⁻³')),
            ('c (centi=10⁻²)',
             lambda: multiplierSetter('c', 'centi=10⁻²')),
            ('d (deci=10⁻¹)',
             lambda: multiplierSetter('d', 'deci=10⁻¹')),
            ('˽ (no scaling=10⁰)',
             lambda: multiplierSetter('', 'no scaling=10⁰')),
            ('㍲ (deca=10¹)',
             lambda: multiplierSetter('㍲', 'deca=10¹')),
            ('h (hecto=10²)',
             lambda: multiplierSetter('h', 'hecto=10²')),
            ('k (kilo=10³)',
             lambda: multiplierSetter('k', 'kilo=10³')),
            ('M (mega=10⁶)',
             lambda: multiplierSetter('M', 'mega=10⁶')),
            ('G (giga=10⁹)',
             lambda: multiplierSetter('G', 'giga=10⁹')),
            ('T (tera=10¹²)',
             lambda: multiplierSetter('T', 'tera=10¹²')),
            ('P (peta=10¹⁵)',
             lambda: multiplierSetter('P', 'peta=10¹⁵)')),
            ('E (exa=10¹⁸)',
             lambda: multiplierSetter('E', 'exa=10¹⁸')),
            ('Z (zetta=10²¹)',
             lambda: multiplierSetter('Z', 'zetta=10²¹')),
            ('ϒ (yotta=10²⁴)',
             lambda: multiplierSetter('ϒ', 'yotta=10²⁴'))]
        for multiplier in normal_multipliers:
            item = menu.addAction(multiplier[0])
            item.triggered.connect(multiplier[1])
        menu.addSeparator()

        dimensionless_multipliers = [
            ('ppm (parts per million=ᴺ/₁․₀₀₀․₀₀₀)',
             lambda: multiplierSetter('ppm', 'parts per million=ᴺ/₁․₀₀₀․₀₀₀')),
            ('‰ (promille=ᴺ/₁․₀₀₀)',
             lambda: multiplierSetter('‰', 'promille=ᴺ/₁․₀₀₀')),
            ('% (percent=ᴺ/₁₀₀)',
             lambda: multiplierSetter('%', 'percent=ᴺ/₁₀₀')),
            ('dB (decibel=10·log[P/Pref])',
             lambda: multiplierSetter('dB', 'decibel=10·log[P/Pref]')),
            ('dBV (decibel=20·log[V/Vref])',
             lambda: multiplierSetter('dBV', 'decibel=20·log[V/Vref]'))]
        for multiplier in dimensionless_multipliers:
            item = menu.addAction(multiplier[0])
            item.triggered.connect(multiplier[1])
        return menu

    def __get_input_parameter_column(self, item_row, column_index):
        return self.inputParameterModel.item(item_row, column_index)

    def inputParameterItemChanged(self, item=None):
        '''
        if one of the cells in self.inputParameterModel is changed, this
        routine is called, and it could be cause to re-size the table columns,
        and it could be cause to make a checkbox change.
        '''
        if item is None:  # process the whole table
            rows = self.inputParameterModel.rowCount()
            for row in range(rows):
                name, attributes = self.getInputParameter(row)
                self.setInputParameter(name, attributes, row)
        else:  # process only the one line
            row = item.row()
            name, attributes = self.getInputParameter(row)
            self.setInputParameter(name, attributes, row)

        self.verify()
        self.inputParameterView.clearSelection()

    def inputParameterSelectionChanged(self):
        '''
        here we enable the right buttons.
        '''
        selectedIndexes = self.inputParameterView.selectedIndexes()
        rowCount = self.inputParameterModel.rowCount()
        lastRow = rowCount - 1
        selectedRows = set()
        for index in selectedIndexes:
            selectedRows.add(index.row())
        numberOfSelectedRows = len(selectedRows)

    def setInputParameterValue(self, value):
        '''
        value is **ALWAYS** a float (might be inf & nan)
        '''
        index_selection = self.inputParameterView.selectedIndexes()

        if not isinstance(value, float):
            raise Exception("Woops, a float is mandatory !!!")

        for index in index_selection:
            item = self.inputParameterModel.itemFromIndex(index)
            fmt_item = self.__get_input_parameter_column(index.row(), InputColumnIndex.FMT())
            Fmt = fmt_item.data(QtCore.Qt.DisplayRole)
            if np.isinf(value):
                if np.isposinf(value):  # only for Max
                    if index.column() == InputColumnIndex.MAX():
                        item.setData('+∞', QtCore.Qt.DisplayRole)
                else:  # np.isneginf(value) # only for Min
                    if index.column() == InputColumnIndex.MIN():
                        item.setData('-∞', QtCore.Qt.DisplayRole)
            elif np.isnan(value):  # forget about it! translate
                if index.column() == InputColumnIndex.MIN():  # Min --> -np.inf
                    item.setData('-∞', QtCore.Qt.DisplayRole)
                elif index.column() == InputColumnIndex.DEFAULT():  # Default --> 0.0
                    item.setData(f"{0.0:{Fmt}}", QtCore.Qt.DisplayRole)
                    pass
                elif index.column() == InputColumnIndex.MAX():  # Max --> np.inf
                    item.setData('-∞', QtCore.Qt.DisplayRole)
            else:  # for columns 1, 2 and 3
                if index.column() in [InputColumnIndex.MIN(), InputColumnIndex.DEFAULT(), InputColumnIndex.MAX()]:
                    item.setData(f"{value:{Fmt}}", QtCore.Qt.DisplayRole)

        self.inputParameterView.clearSelection()

    def __set_input_parameter_attribtue(self, attribute_column, text, tooltip):
        selection = self.inputParameterView.selectedIndexes()

        for index in selection:
            if index.column() == attribute_column:
                self.inputParameterModel.setData(index, text, QtCore.Qt.DisplayRole)
                self.inputParameterModel.setData(index, tooltip, QtCore.Qt.ToolTipRole)

    def setInputParameterMultiplier(self, text, tooltip):
        self.__set_input_parameter_attribtue(InputColumnIndex.POWER(), text, tooltip)

    def setInputParameterUnit(self, text, tooltip):
        self.__set_input_parameter_attribtue(InputColumnIndex.UNIT(), text, tooltip)

    def __select_default(self, Min, Default, Max):
        if Min == -np.inf and Max == np.inf:
            if Default == -np.inf:
                Default = 0
            if Default == np.inf:
                Default = 0
        elif Min == -np.inf:
            if Default > Max:
                Default = Max
            if Default == -np.inf:
                Default = Max
        elif Max == np.inf:
            if Default < Min:
                Default = Min
            if Default == np.inf:
                Default = Min
        else:
            if Default > Max:
                Default = Max
            if Default < Min:
                Default = Min
        return Default

    def setInputParameter(self, name, attributes, row=None):
        '''
        sets the inputParameter name and it's attribues
        if row==None, append to the list.
        if row is given, it **must** already exist!

        Structure (of all input parameters):

        input_parameters = {                          # https://docs.python.org/3.6/library/string.html#format-specification-mini-language
            'Temperature' : {'Shmoo' : True,  'Min' :     -40, 'Default' : 25, 'Max' :     170, OutputColumnKey.POWER() :  '', OutputColumnKey.UNIT() : '°C', OutputColumnKey.FMT() : '.0f'}, # Obligatory !
            'i'           : {'Shmoo' : False, 'Min' : -np.inf, 'Default' :  0, 'Max' : +np.inf, OutputColumnKey.POWER() : 'μ', OutputColumnKey.UNIT() :  'A', OutputColumnKey.FMT() : '.3f'},
            'j'           : {'Shmoo' : False, 'Min' :    '-∞', 'Default' :  0, 'Max' :    '+∞', OutputColumnKey.POWER() : 'μ', OutputColumnKey.UNIT() :  'A', OutputColumnKey.FMT() : '.3f'}}

        References:
            https://doc.qt.io/qt-5/qt.html#CheckState-enum
            https://doc.qt.io/qt-5/qt.html#ItemFlag-enum
            https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum
            https://doc.qt.io/qt-5/qstandarditem.html
        '''
        rowCount = self.inputParameterModel.rowCount()

        if name == 'Temperature':  # must be at row 0, regardless what row says
            if rowCount == 0:  # make first entry
                self.inputParameterModel.appendRow([QtGui.QStandardItem() for i in range(TestWizard.INPUT_MAX_NUM_COLUMNS)])
            item_row = 0
        else:
            if row is None:  # append
                self.inputParameterModel.appendRow([QtGui.QStandardItem() for i in range(TestWizard.INPUT_MAX_NUM_COLUMNS)])
                item_row = rowCount
            else:  # update
                if row > rowCount:
                    raise Exception(f"row({row}) > rowCount({rowCount})")
                item_row = row

        shmoo_item = self.__get_input_parameter_column(item_row, InputColumnIndex.SHMOO())
        name_item = self.__get_input_parameter_column(item_row, InputColumnIndex.NAME())
        min_item = self.__get_input_parameter_column(item_row, InputColumnIndex.MIN())
        default_item = self.__get_input_parameter_column(item_row, InputColumnIndex.DEFAULT())
        max_item = self.__get_input_parameter_column(item_row, InputColumnIndex.MAX())
        multiplier_item = self.__get_input_parameter_column(item_row, InputColumnIndex.POWER())
        unit_item = self.__get_input_parameter_column(item_row, InputColumnIndex.UNIT())
        fmt_item = self.__get_input_parameter_column(item_row, InputColumnIndex.FMT())

        self.inputParameterModel.blockSignals(True)
        Fmt = '.0f'

    # fmt
        if name == 'Temperature':
            Fmt = '.0f'
            fmt_item.setFlags(QtCore.Qt.NoItemFlags)
        else:
            if OutputColumnKey.FMT() not in attributes:
                Fmt = '.3f'
            else:
                Fmt = attributes[OutputColumnKey.FMT()]
            fmt_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

        fmt_item.setData(Fmt, QtCore.Qt.DisplayRole)
        fmt_item.setData(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)

    # Min
        if name == 'Temperature':
            if isinstance(attributes[InputColumnKey.MIN()], str):
                if '∞' in attributes[InputColumnKey.MIN()]:  # forget about it --> -60
                    Min = -60.0
                else:
                    Min = float(attributes[InputColumnKey.MIN()])
                    if Min < -60.0:
                        Min = -60.0
            elif isinstance(attributes[InputColumnKey.MIN()], (float, int)):
                Min = float(attributes[InputColumnKey.MIN()])
                if Min < -60.0:
                    Min = -60.0
            else:
                raise Exception("type(attribute[InputColumnKey.MIN()]) = {type(attribute[InputColumnKey.MIN()])}, which is not (str, float or int) ... WTF?!?")
            min_item.setData(f"{Min:{Fmt}}", QtCore.Qt.DisplayRole)
        else:
            if isinstance(attributes[InputColumnKey.MIN()], str):
                if '∞' in attributes[InputColumnKey.MIN()]:
                    Min = -np.inf
                    min_item.setData('-∞', QtCore.Qt.DisplayRole)
                else:
                    Min = float(attributes[InputColumnKey.MIN()])
                    min_item.setData(f"{Min:{Fmt}}", QtCore.Qt.DisplayRole)
            elif isinstance(attributes[InputColumnKey.MIN()], (float, int)):
                if attributes[InputColumnKey.MIN()] == -np.inf:
                    Min = -np.inf
                    min_item.setData('-∞', QtCore.Qt.DisplayRole)
                else:
                    Min = float(attributes[InputColumnKey.MIN()])
                    min_item.setData(f"{Min:{Fmt}}", QtCore.Qt.DisplayRole)
            else:
                raise Exception("type(attribute[InputColumnKey.MIN()]) = {type(attribute[InputColumnKey.MIN()])}, which is not (str, float or int) ... WTF?!?")
        min_item.setData(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        min_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # Max
        if name == 'Temperature':
            if isinstance(attributes[InputColumnKey.MAX()], str):
                if '∞' in attributes[InputColumnKey.MAX()]:  # forget about it --> 200
                    Max = 200.0
                else:
                    Max = float(attributes[InputColumnKey.MAX()])
                    if Max > 200.0:
                        Max = 200.0
            elif isinstance(attributes[InputColumnKey.MAX()], (float, int)):
                Max = float(attributes[InputColumnKey.MAX()])
                if Max > 200.0:
                    Max = 200.0
            else:
                raise Exception("type(attribute[InputColumnKey.MAX()]) = {type(attribute[InputColumnKey.MAX()])}, which is not (str, float or int) ... WTF?!?")
            max_item.setData(f"{Max:{Fmt}}", QtCore.Qt.DisplayRole)
        else:
            if isinstance(attributes[InputColumnKey.MAX()], str):
                if '∞' in attributes[InputColumnKey.MAX()]:
                    Max = np.inf
                    max_item.setData('+∞', QtCore.Qt.DisplayRole)
                else:
                    Max = float(attributes[InputColumnKey.MAX()])
                    max_item.setData(f"{Max:{Fmt}}", QtCore.Qt.DisplayRole)
            elif isinstance(attributes[InputColumnKey.MAX()], (float, int)):
                if attributes[InputColumnKey.MAX()] == np.inf:
                    Max = np.inf
                    max_item.setData('+∞', QtCore.Qt.DisplayRole)
                else:
                    Max = float(attributes[InputColumnKey.MAX()])
                    max_item.setData(f"{Max:{Fmt}}", QtCore.Qt.DisplayRole)
            else:
                raise Exception("type(attribute[InputColumnKey.MAX()]) = {type(attribute[InputColumnKey.MAX()])}, which is not (str, float or int) ... WTF?!?")
        max_item.setData(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        max_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # Default
        if name == 'Temperature':
            if isinstance(attributes[InputColumnKey.DEFAULT()], str):
                if '∞' in attributes[InputColumnKey.DEFAULT()]:  # forget about it --> 25
                    Default = 25.0
                else:
                    Default = float(attributes[InputColumnKey.DEFAULT()])
                    if Default > Max or Default < Min:
                        Default = 25.0
            elif isinstance(attributes[InputColumnKey.DEFAULT()], (float, int)):
                Default = float(attributes[InputColumnKey.DEFAULT()])
                if Default > Max or Default < Min:
                    Default = 25.0
            else:
                raise Exception("type(attribute[InputColumnKey.DEFAULT()]) = {type(attribute[InputColumnKey.DEFAULT()])}, which is not (str, float or int) ... WTF?!?")
        else:
            if isinstance(attributes[InputColumnKey.DEFAULT()], str):
                if attributes[InputColumnKey.DEFAULT()] == '-∞':
                    Default = -np.inf
                elif attributes[InputColumnKey.DEFAULT()] in ['∞', '+∞']:
                    Default = np.inf
                else:
                    Default = float(attributes[InputColumnKey.DEFAULT()])
            elif isinstance(attributes[InputColumnKey.DEFAULT()], (float, int)):
                Default = float(attributes[InputColumnKey.DEFAULT()])
            else:
                raise Exception("type(attribute[InputColumnKey.DEFAULT()]) = {type(attribute[InputColumnKey.DEFAULT()])}, which is not (str, float or int) ... WTF?!?")
            Default = self.__select_default(Min, Default, Max)

        default_item.setData(f"{Default:{Fmt}}", QtCore.Qt.DisplayRole)
        default_item.setData(int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        default_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # name
        name_item.setData(name, QtCore.Qt.DisplayRole)  # https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum
        name_item.setData(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)

        if name == 'Temperature':  # Shmoo is always enabled, user can not change
            name_item.setFlags(QtCore.Qt.NoItemFlags)

    # shmoo
        shmoo_item.setData(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        if name == 'Temperature':  # Shmoo is always enabled, user can not change
            shmoo_item.setData(QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)  # https://doc.qt.io/qt-5/qt.html#CheckState-enum
            shmoo_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsUserCheckable)  # https://doc.qt.io/qt-5/qt.html#ItemFlag-enum
        else:
            if Min <= Default <= Max and Min != -np.Inf and Max != np.Inf:
                shmoo_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
            else:
                shmoo_item.setFlags(QtCore.Qt.ItemIsEnabled)

            # shmoo_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)

        if attributes[InputColumnKey.SHMOO()] is True:
            shmoo_item.setData(QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)
        else:
            shmoo_item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)

    # Multiplier
        if name == 'Temperature':  # fixed regardless what the attributes say
            multiplier_item.setData('', QtCore.Qt.DisplayRole)
            multiplier_item.setData(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
            multiplier_item.setFlags(QtCore.Qt.NoItemFlags)
        else:
            multiplier_item.setData(str(self.get_key(attributes[OutputColumnKey.POWER()])), QtCore.Qt.DisplayRole)
            multiplier_item.setData(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
            multiplier_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
    # Unit
        if name == 'Temperature':  # fixed regardless what the attribues say
            unit_item.setData('°C', QtCore.Qt.DisplayRole)
            unit_item.setData(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
            unit_item.setFlags(QtCore.Qt.NoItemFlags)
        else:
            unit_item.setData(str(attributes[OutputColumnKey.UNIT()]), QtCore.Qt.DisplayRole)
            unit_item.setData(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
            unit_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

        self.inputParameterModel.blockSignals(False)

    def setInputpParameters(self, definition):
        for name in definition:
            attributes = definition[name]
            self.setInputParameter(name, attributes)

    def getInputParameter(self, row):
        attributes = TestWizard.make_default_input_parameter()

        name_item = self.__get_input_parameter_column(row, InputColumnIndex.NAME())

        if not isinstance(name_item, QtGui.QStandardItem):
            raise Exception("WTF")

        name = name_item.data(QtCore.Qt.DisplayRole)

        shmoo_item = self.__get_input_parameter_column(row, InputColumnIndex.SHMOO())
        shmoo = shmoo_item.data(QtCore.Qt.CheckStateRole)

        if shmoo == QtCore.Qt.Checked:
            attributes[InputColumnKey.SHMOO()] = True
        else:
            attributes[InputColumnKey.SHMOO()] = False

        fmt_item = self.__get_input_parameter_column(row, InputColumnIndex.FMT())
        Fmt = fmt_item.data(QtCore.Qt.DisplayRole)
        attributes[OutputColumnKey.FMT()] = Fmt

        min_item = self.__get_input_parameter_column(row, InputColumnIndex.MIN())
        Min = min_item.data(QtCore.Qt.DisplayRole)
        if '∞' in Min:
            attributes[InputColumnKey.MIN()] = -np.Inf
        else:
            Min = float(Min)
            attributes[InputColumnKey.MIN()] = float(f"{Min:{Fmt}}")

        default_item = self.__get_input_parameter_column(row, InputColumnIndex.DEFAULT())
        Default = float(default_item.data(QtCore.Qt.DisplayRole))
        attributes[InputColumnKey.DEFAULT()] = float(f"{Default:{Fmt}}")

        max_item = self.__get_input_parameter_column(row, InputColumnIndex.MAX())
        Max = max_item.data(QtCore.Qt.DisplayRole)
        if '∞' in Max:
            attributes[InputColumnKey.MAX()] = np.Inf
        else:
            Max = float(Max)
            attributes[InputColumnKey.MAX()] = float(f"{Max:{Fmt}}")

        multiplier_item = self.__get_input_parameter_column(row, InputColumnIndex.POWER())
        Multiplier = multiplier_item.data(QtCore.Qt.DisplayRole)
        attributes[OutputColumnKey.POWER()] = Multiplier if Multiplier else attributes[OutputColumnKey.POWER()]

        unit_item = self.__get_input_parameter_column(row, InputColumnIndex.UNIT())
        Unit = unit_item.data(QtCore.Qt.DisplayRole)
        attributes[OutputColumnKey.UNIT()] = Unit

        return name, attributes

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

    def moveInputParameterUp(self):
        selectedIndexes = self.inputParameterView.selectedIndexes()
        selectedRows = set()
        for index in selectedIndexes:
            if index.row() not in selectedRows:
                selectedRows.add(index.row())
        if len(selectedRows) == 1:  # can move only delete one parameter at a time!
            row = list(selectedRows)[0]
            data = self.inputParameterModel.takeRow(row)
            self.inputParameterModel.insertRow(row - 1, data)
            self.inputParameterView.clearSelection()
            self.inputParameterView.selectRow(row - 1)

    def addInputParameter(self):
        new_row = self.inputParameterModel.rowCount()
        existing_parameters = []
        for item_row in range(new_row):
            item = self.__get_input_parameter_column(item_row, InputColumnIndex.NAME())
            existing_parameters.append(item.text())

        existing_parameter_indexes = []
        for existing_parameter in existing_parameters:
            if existing_parameter.startswith('new_parameter'):
                existing_index = int(existing_parameter.split('new_parameter')[1])
                if existing_index not in existing_parameter_indexes:
                    existing_parameter_indexes.append(existing_index)

        if len(existing_parameter_indexes) == 0:
            new_parameter_index = 1
        else:
            new_parameter_index = max(existing_parameter_indexes) + 1
        name = f'new_parameter{new_parameter_index}'
        attributes = {
            InputColumnKey.SHMOO(): False,
            InputColumnKey.MIN(): '-∞',
            InputColumnKey.DEFAULT(): 0,
            InputColumnKey.MAX(): '+∞',
            InputColumnKey.POWER(): '˽',
            InputColumnKey.UNIT(): '˽',
            InputColumnKey.FMT(): '.3f'
        }
        self.setInputParameter(name, attributes)
        self.verify()

    def unselectInputParameter(self):
        self.inputParameterView.clearSelection()

    def deleteInputParameter(self):
        selectedIndexes = self.inputParameterView.selectedIndexes()
        selectedRows = set()
        for index in selectedIndexes:
            if index.row() not in selectedRows:
                selectedRows.add(index.row())
        if len(selectedRows) == 1:  # can move only delete one parameter at a time!
            row = list(selectedRows)[0]
            self.inputParameterModel.takeRow(row)
            self.inputParameterView.clearSelection()

    def moveInputParameterDown(self):
        selectedIndexes = self.inputParameterView.selectedIndexes()
        selectedRows = set()
        for index in selectedIndexes:
            if index.row() not in selectedRows:
                selectedRows.add(index.row())
        if len(selectedRows) == 1:  # can move only delete one parameter at a time!
            row = list(selectedRows)[0]
            data = self.inputParameterModel.takeRow(row)
            self.inputParameterModel.insertRow(row + 1, data)
            self.inputParameterView.clearSelection()
            self.inputParameterView.selectRow(row + 1)

    def outputParameterContextMenu(self, point):
        index = self.outputParameterView.indexAt(point)
        col = index.column()
        formatSetter = self.setOutputParameterFormat
        valueSetter = self.setOutputParameterValue
        multiplierSetter = self.setOutputParameterMultiplier
        unitSetter = self.setOutputParameterUnit

        if col in [OutputColumnIndex.NAME(), OutputColumnIndex.FMT()]:
            menu = QtWidgets.QMenu(self)
            parameter_formats = [
                ("6 decimal places float", lambda: formatSetter('.6f')),
                ("3 decimal places float", lambda: formatSetter('.3f')),
                ("2 decimal places float", lambda: formatSetter('.2f')),
                ("1 decimal places float", lambda: formatSetter('.1f')),
                ("0 decimal places float", lambda: formatSetter('.0f'))]

            for format_option in parameter_formats:
                item = menu.addAction(format_option[0])
                item.triggered.connect(format_option[1])
            menu.exec_(QtGui.QCursor.pos())

        elif index.column() in [OutputColumnIndex.LSL(), OutputColumnIndex.LTL(), OutputColumnIndex.NOM(), OutputColumnIndex.UTL(), OutputColumnIndex.USL()]:
            menu = QtWidgets.QMenu(self)
            special_values = [
                ('+∞', lambda: valueSetter(np.inf)),
                ('0', lambda: valueSetter(0.0)),
                ('<clear>', lambda: valueSetter(np.nan)),
                ('-∞', lambda: valueSetter(-np.inf))]
            for special_value in special_values:
                item = menu.addAction(special_value[0])
                item.triggered.connect(special_value[1])
            menu.exec_(QtGui.QCursor.pos())

        elif index.column() == OutputColumnIndex.POWER():  # multiplier --> reference = STDF V4.pdf @ page 50 & https://en.wikipedia.org/wiki/Order_of_magnitude
            menu = self.multiplierContextMenu(multiplierSetter)
            menu.exec_(QtGui.QCursor.pos())

        elif index.column() == OutputColumnIndex.UNIT():  # Unit
            menu = self.unitContextMenu(unitSetter)
            menu.exec_(QtGui.QCursor.pos())

    def outputParameterItemChanged(self, item=None):
        if item is None:  # process the whole table
            rows = self.outputParameterModel.rowCount()
            for row in range(rows):
                name, attributes = self.getOutputParameter(row)
                self.setOutputParameter(name, attributes, row)
        else:  # process only the one line
            row = item.row()
            name, attributes = self.getOutputParameter(row)

            self.setOutputParameter(name, attributes, row)

        self.verify()
        self.outputParameterView.clearSelection()

    def outputParameterSelectionChanged(self):
        '''
        here we enable the right buttons.
        '''
        selectedIndexes = self.outputParameterView.selectedIndexes()
        rowCount = self.outputParameterModel.rowCount()
        lastRow = rowCount - 1
        selectedRows = set()
        for index in selectedIndexes:
            selectedRows.add(index.row())
        numberOfSelectedRows = len(selectedRows)

        if numberOfSelectedRows == 0:
            self.outputParameterUnselect.setEnabled(False)
            self.outputParameterMoveUp.setEnabled(False)
            self.outputParameterDelete.setEnabled(False)
            self.outputParameterMoveDown.setEnabled(False)
        elif numberOfSelectedRows == 1:
            selectedRow = list(selectedRows)[0]
            self.outputParameterUnselect.setEnabled(True)
            if selectedRow > 0:
                self.outputParameterMoveUp.setEnabled(True)
            else:
                self.outputParameterMoveUp.setEnabled(False)
            self.outputParameterDelete.setEnabled(True)
            if selectedRow < lastRow:
                self.outputParameterMoveDown.setEnabled(True)
            else:
                self.outputParameterMoveDown.setEnabled(False)
        else:
            self.outputParameterUnselect.setEnabled(True)
            self.outputParameterMoveUp.setEnabled(False)
            self.outputParameterDelete.setEnabled(False)
            self.outputParameterMoveDown.setEnabled(False)

    def setOutputParameterFormat(self, Format):
        index_selection = self.outputParameterView.selectedIndexes()

        for index in index_selection:
            if index.column() in [OutputColumnIndex.NAME(), OutputColumnIndex.FMT()]:
                fmt_item = self.outputParameterModel.item(index.row(), OutputColumnIndex.FMT())
                fmt_item.setData(Format, QtCore.Qt.DisplayRole)
        self.outputParameterView.clearSelection()

    def setOutputParameterValue(self, value):
        '''
        value is **ALWAYS** a float (might be +/-np.inf or np.nan)
        '''
        index_selection = self.outputParameterView.selectedIndexes()

        if not isinstance(value, float):
            raise Exception("Woops, a float is mandatory !!!")

        for index in index_selection:
            item = self.outputParameterModel.itemFromIndex(index)
            if np.isinf(value):
                if np.isposinf(value):  # only for columns 1 & 2
                    if index.column() in [OutputColumnIndex.LSL(), OutputColumnIndex.LTL()]:
                        item.setData('+∞', QtCore.Qt.DisplayRole)
                else:  # np.isneginf(value) # only for columsn 4 & 5
                    if index.column() in [OutputColumnIndex.USL(), OutputColumnIndex.UTL()]:
                        item.setData('-∞', QtCore.Qt.DisplayRole)
            elif np.isnan(value):  # only for columns 2 & 4
                if index.column() in [OutputColumnIndex.LTL(), OutputColumnIndex.UTL()]:
                    item.setData('', QtCore.Qt.DisplayRole)
            else:  # for columns 1, 2, 3, 4 and 5
                if index.column() in [OutputColumnIndex.LSL(), OutputColumnIndex.LTL(), OutputColumnIndex.NOM(), OutputColumnIndex.UTL(), OutputColumnIndex.USL()]:
                    fmt_item = self.outputParameterModel.item(index.row(), OutputColumnIndex.FMT())
                    Fmt = fmt_item.data(QtCore.Qt.DisplayRole)
                    item.setData(f"{value:{Fmt}}", QtCore.Qt.DisplayRole)
        self.outputParameterView.clearSelection()

    def setOutputParameterMultiplier(self, text, tooltip):
        selection = self.outputParameterView.selectedIndexes()

        for index in selection:
            if index.column() in (OutputColumnIndex.FMT(), OutputColumnIndex.POWER()):
                self.outputParameterModel.setData(index, text, QtCore.Qt.DisplayRole)
                self.outputParameterModel.setData(index, tooltip, QtCore.Qt.ToolTipRole)
        self.outputParameterView.clearSelection()

    def setOutputParameterUnit(self, text, tooltip):
        selection = self.outputParameterView.selectedIndexes()

        for index in selection:
            if index.column() == OutputColumnIndex.UNIT(): 
                self.outputParameterModel.setData(index, text, QtCore.Qt.DisplayRole)
                self.outputParameterModel.setData(index, tooltip, QtCore.Qt.ToolTipRole)
        self.outputParameterView.clearSelection()

    def setOutputParameter(self, name, attributes, row=None):
        '''
        sets the outputParameter name and it's attributes
        if row==None, append to the list.
        if row is given, it **must** already exist!

        Structure (of all output parameters):
        output_parameters = {                          # https://docs.python.org/3.6/library/string.html#format-specification-mini-language
            'parameter1_name' : {OutputColumnKey.LSL() : -inf, OutputColumnKey.LTL() : None, OutputColumnKey.NOM() :    0, OutputColumnKey.UTL() : None, OutputColumnKey.USL() :  inf, OutputColumnKey.POWER() :  '', OutputColumnKey.UNIT() :  'Ω', OutputColumnKey.FMT() : '.3f', OutputColumnKey.MPR() : False},
            'parameter2_name' : {OutputColumnKey.LSL() :  0.0, OutputColumnKey.LTL() : None, OutputColumnKey.NOM() :  3.5, OutputColumnKey.UTL() : None, OutputColumnKey.USL() :  2.5, OutputColumnKey.POWER() : 'μ', OutputColumnKey.UNIT() :  'V', OutputColumnKey.FMT() : '.3f', OutputColumnKey.MPR() : False},
            'R_vdd_contact'   : {OutputColumnKey.LSL() :  5.0, OutputColumnKey.LTL() :  9.0, OutputColumnKey.NOM() : 10.0, OutputColumnKey.UTL() : 11.0, OutputColumnKey.USL() : 20.0, OutputColumnKey.POWER() : 'k', OutputColumnKey.UNIT() : 'Hz', OutputColumnKey.FMT() : '.1f', OutputColumnKey.MPR() : False}}

        References:
            https://doc.qt.io/qt-5/qt.html#CheckState-enum
            https://doc.qt.io/qt-5/qt.html#ItemFlag-enum
            https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum
            https://doc.qt.io/qt-5/qstandarditem.html
        '''
        rowCount = self.outputParameterModel.rowCount()

        if row is None:  # append
            self.outputParameterModel.appendRow([QtGui.QStandardItem() for i in range(TestWizard.OUTPUT_MAX_NUM_COLUMNS)])
            item_row = rowCount
        else:  # update
            if row > rowCount:
                raise Exception(f"row({row}) > rowCount({rowCount})")
            item_row = row

        name_item = self.outputParameterModel.item(item_row, OutputColumnIndex.NAME())
        LSL_item = self.outputParameterModel.item(item_row, OutputColumnIndex.LSL())
        LTL_item = self.outputParameterModel.item(item_row, OutputColumnIndex.LTL())
        Nom_item = self.outputParameterModel.item(item_row, OutputColumnIndex.NOM())
        UTL_item = self.outputParameterModel.item(item_row, OutputColumnIndex.UTL())
        USL_item = self.outputParameterModel.item(item_row, OutputColumnIndex.USL())
        multiplier_item = self.outputParameterModel.item(item_row, OutputColumnIndex.POWER())
        unit_item = self.outputParameterModel.item(item_row, OutputColumnIndex.UNIT())
        fmt_item = self.outputParameterModel.item(item_row, OutputColumnIndex.FMT())
        MPR_item = self.outputParameterModel.item(item_row, OutputColumnIndex.MPR())

        self.outputParameterModel.blockSignals(True)

    # fmt
        if OutputColumnKey.FMT() not in attributes:
            Fmt = '.3f'
        else:
            Fmt = attributes[OutputColumnKey.FMT()]
        fmt_item.setData(Fmt, QtCore.Qt.DisplayRole)
        fmt_item.setData(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        fmt_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # MPR
        MPR_item.setData(int(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        MPR_item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsUserCheckable)
        if attributes[OutputColumnKey.MPR()] is None or attributes[OutputColumnKey.MPR()] is False:
            MPR_item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)
        else:
            MPR_item.setData(QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)
        
    # LSL
        if attributes[OutputColumnKey.LSL()] is None:  # None on LSL doesn't exist --> = -Inf
            LSL_ = -np.inf
            LSL = '-∞'
        elif isinstance(attributes[OutputColumnKey.LSL()], (float, int)):
            if abs(attributes[OutputColumnKey.LSL()]) == np.inf:
                LSL_ = -np.inf
                LSL = '-∞'
            elif np.isnan(attributes[OutputColumnKey.LSL()]):  # NaN on LSL doesn't exist --> = -Inf
                LSL_ = np.inf
                LSL = '-∞'
            else:
                LSL_ = float(attributes[OutputColumnKey.LSL()])
                LSL = f"{LSL_:{Fmt}}"
        else:
            raise Exception(f"type(attributes[OutputColumnKey.LSL()]) = {type(attributes[OutputColumnKey.LSL()])}, which is not (NoneType, float or int) ... WTF?!?")
        LSL_item.setData(LSL, QtCore.Qt.DisplayRole)
        LSL_item.setData(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        LSL_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # LTL
        if isinstance(attributes[OutputColumnKey.LTL()], str):
            if attributes[OutputColumnKey.LTL()] == '' or 'NAN' in attributes[OutputColumnKey.LTL()].upper():
                LTL_ = np.nan
                LTL = ''
            elif '∞' in attributes[OutputColumnKey.LTL()]:
                LTL_ = -np.inf
                LTL = '-∞'
            else:
                LTL_ = float(attributes[OutputColumnKey.LTL()])
                LTL = f"{LTL_:{Fmt}}"
        elif attributes[OutputColumnKey.LTL()] is None:  # None on LTL = NaN
            LTL_ = np.nan
            LTL = ''
        elif isinstance(attributes[OutputColumnKey.LTL()], (float, int)):
            if abs(attributes[OutputColumnKey.LTL()]) == np.inf:
                LTL_ = -np.inf
                LTL = '-∞'
            elif np.isnan(attributes[OutputColumnKey.LTL()]):
                LTL_ = np.nan
                LTL = ''
            else:
                LTL_ = float(attributes[OutputColumnKey.LTL()])
                LTL = f"{LTL_:{Fmt}}"
        else:
            raise Exception(f"type(attributes[OutputColumnKey.LTL()]) = {type(attributes[OutputColumnKey.LTL()])}, which is not (str, NoneType, float or int) ... WTF?!?")
        LTL_item.setData(LTL, QtCore.Qt.DisplayRole)
        LTL_item.setData(int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        LTL_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # USL
        if attributes[OutputColumnKey.USL()] is None:  # None on USL doesn't exist --> = +Inf
            USL_ = np.inf
            USL = '+∞'
        elif isinstance(attributes[OutputColumnKey.USL()], (float, int)):
            if abs(attributes[OutputColumnKey.USL()]) == np.inf:
                USL_ = np.inf
                USL = '+∞'
            elif np.isnan(attributes[OutputColumnKey.USL()]):  # NaN on USL doesn't extist --> = +Inf
                USL_ = np.inf
                USL = '+∞'
            else:
                USL_ = float(attributes[OutputColumnKey.USL()])
                USL = f"{USL_:{Fmt}}"
        else:
            raise Exception(f"type(attributes[OutputColumnKey.USL()]) = {type(attributes[OutputColumnKey.USL()])}, which is not (NoneType, float or int) ... WTF?!?")
        USL_item.setData(USL, QtCore.Qt.DisplayRole)
        USL_item.setData(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        USL_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # UTL
        if isinstance(attributes[OutputColumnKey.UTL()], str):
            if attributes[OutputColumnKey.UTL()] == '' or 'NAN' in attributes[OutputColumnKey.UTL()].upper():
                UTL_ = np.nan
                UTL = ''
            elif '∞' in attributes[OutputColumnKey.UTL()]:
                UTL_ = -np.inf
                UTL = '+∞'
            else:
                UTL_ = float(attributes[OutputColumnKey.LTL()])
                UTL = f"{UTL_:{Fmt}}"
        elif attributes[OutputColumnKey.UTL()] is None:  # None on UTL = Nan
            UTL_ = np.nan
            UTL = ''
        elif isinstance(attributes[OutputColumnKey.UTL()], (float, int)):
            if abs(attributes[OutputColumnKey.UTL()]) == np.inf:
                UTL_ = np.inf
                UTL = '+∞'
            elif np.isnan(attributes[OutputColumnKey.UTL()]):
                UTL_ = np.nan
                UTL = ''
            else:
                UTL_ = float(attributes[OutputColumnKey.UTL()])
                UTL = f"{UTL_:{Fmt}}"
        else:
            raise Exception(f"type(attributes[OutputColumnKey.UTL()]) = {type(attributes[OutputColumnKey.UTL()])}, which is not (str, NoneType, float or int) ... WTF?!?")
        UTL_item.setData(UTL, QtCore.Qt.DisplayRole)
        UTL_item.setData(int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        UTL_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # Nom
        if attributes[OutputColumnKey.NOM()] is None:  # None on Nom = 0.0
            Nom_ = 0.0
        elif isinstance(attributes[OutputColumnKey.NOM()], (float, int)):
            Nom_ = float(attributes[OutputColumnKey.NOM()])
            if LSL_ == -np.inf and USL_ == np.inf:
                if Nom_ == -np.inf or Nom_ == np.inf or np.isnan(Nom_):
                    Nom_ = 0.0
                if Nom_ > UTL_:
                    Nom_ = UTL_
                if Nom_ < LTL_:
                    Nom_ = LTL_
            elif LSL_ == -np.inf:
                if Nom_ > USL_:
                    Nom_ = USL_
            elif USL_ == np.inf:
                if Nom_ < LSL_:
                    Nom_ = LSL_
            else:
                if Nom_ > USL_:
                    Nom_ = USL_
                if Nom_ > UTL_:
                    Nom_ = UTL_
                if Nom_ < LSL_:
                    Nom_ = LSL_
                if Nom_ < LTL_:
                    Nom_ = LTL_
        else:
            raise Exception(f"type(attribute[OutputColumnKey.NOM()]) = {type(attributes[OutputColumnKey.NOM()])}, which is not (float or int) ... WTF?!?")
        # complience to SL
        Nom = f"{Nom_:{Fmt}}"
        Nom_item.setData(Nom, QtCore.Qt.DisplayRole)
        Nom_item.setData(int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        Nom_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # name
        name_item.setData(name, QtCore.Qt.DisplayRole)  # https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum
        name_item.setData(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        name_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # Multiplier
        multiplier_item.setData(str(self.get_key(attributes[OutputColumnKey.POWER()])), QtCore.Qt.DisplayRole)
        multiplier_item.setData(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        multiplier_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
    # Unit
        unit_item.setData(str(attributes[OutputColumnKey.UNIT()]), QtCore.Qt.DisplayRole)
        unit_item.setData(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        unit_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

        self.outputParameterModel.blockSignals(False)

    def setOutputParameters(self, definition):
        for name in definition:
            attributes = definition[name]
            self.setOutputParameter(name, attributes)

    def getOutputParameter(self, row):
        '''
        the result is always a float (might be np.inf or np.nan) for LSL, LTL, Nom, UTL and USL (rest is string)
        the source is in the model, and always a string.
        '''
        attributes = TestWizard.make_default_output_parameter(empty=True)
        name_item = self.outputParameterModel.item(row, OutputColumnIndex.NAME())
        name = name_item.data(QtCore.Qt.DisplayRole)

    # LSL
        LSL_item = self.outputParameterModel.item(row, OutputColumnIndex.LSL())
        LSL = LSL_item.data(QtCore.Qt.DisplayRole)
        if '∞' in LSL:
            attributes[OutputColumnKey.LSL()] = -np.inf
        else:
            attributes[OutputColumnKey.LSL()] = float(LSL)

    # LTL
        LTL_item = self.outputParameterModel.item(row, OutputColumnIndex.LTL())
        LTL = LTL_item.data(QtCore.Qt.DisplayRole)
        if '∞' in LTL:
            attributes[OutputColumnKey.LTL()] = -np.inf
        elif LTL == '':
            attributes[OutputColumnKey.LTL()] = np.nan
        else:
            attributes[OutputColumnKey.LTL()] = float(LTL)

    # Nom
        Nom_item = self.outputParameterModel.item(row, OutputColumnIndex.NOM())
        attributes[OutputColumnKey.NOM()] = float(Nom_item.data(QtCore.Qt.DisplayRole))

    # UTL
        UTL_item = self.outputParameterModel.item(row, OutputColumnIndex.UTL())
        UTL = UTL_item.data(QtCore.Qt.DisplayRole)
        if '∞' in UTL:
            attributes[OutputColumnKey.UTL()] = +np.inf
        elif UTL == '':
            attributes[OutputColumnKey.UTL()] = np.nan
        else:
            attributes[OutputColumnKey.UTL()] = float(UTL)

    # USL
        USL_item = self.outputParameterModel.item(row, OutputColumnIndex.USL())
        USL = USL_item.data(QtCore.Qt.DisplayRole)
        if '∞' in USL:
            attributes[OutputColumnKey.USL()] = np.inf
        else:
            attributes[OutputColumnKey.USL()] = float(USL)

    # multiplier
        multiplier_item = self.outputParameterModel.item(row, OutputColumnIndex.POWER())
        multiplier = multiplier_item.data(QtCore.Qt.DisplayRole)
        attributes[OutputColumnKey.POWER()] = multiplier if multiplier else attributes[OutputColumnKey.POWER()]

    # unit
        unit_item = self.outputParameterModel.item(row, OutputColumnIndex.UNIT())
        attributes[OutputColumnKey.UNIT()] = unit_item.data(QtCore.Qt.DisplayRole)

    # format
        fmt_item = self.outputParameterModel.item(row, OutputColumnIndex.FMT())
        attributes[OutputColumnKey.FMT()] = fmt_item.data(QtCore.Qt.DisplayRole)

    # MPR
        MPR_item = self.outputParameterModel.item(row, OutputColumnIndex.MPR())
        mpr = MPR_item.data(QtCore.Qt.CheckStateRole)
        if mpr == QtCore.Qt.Checked:
            attributes[OutputColumnKey.MPR()] = True
        else:
            attributes[OutputColumnKey.MPR()] = False

        return name, attributes

    def getOutputParameters(self):
        retval = {}
        rows = self.outputParameterModel.rowCount()
        for row in range(rows):
            name, attributes = self.getOutputParameter(row)
            self._update_power_with_correct_value(attributes)
            retval[name] = attributes
        return retval

    def addOutputParameter(self):
        new_row = self.outputParameterModel.rowCount()
        if new_row == MAX_OUTPUT_NUMBER:
            self.Feedback.setText("max number of output parameters is reached")
            return

        existing_parameters = []
        for item_row in range(new_row):
            item = self.outputParameterModel.item(item_row, 0)
            existing_parameters.append(item.text())

        existing_parameter_indexes = []
        for existing_parameter in existing_parameters:
            if existing_parameter.startswith('new_parameter'):
                existing_index = int(existing_parameter.split('new_parameter')[1])
                if existing_index not in existing_parameter_indexes:
                    existing_parameter_indexes.append(existing_index)

        if len(existing_parameter_indexes) == 0:
            new_parameter_index = 1
        else:
            new_parameter_index = max(existing_parameter_indexes) + 1
        name = f'new_parameter{new_parameter_index}'
        attributes = TestWizard.make_default_output_parameter()
        self.setOutputParameter(name, attributes)
        if new_row == 0:  # switch tabs back and fore to get the 'table adjust' bug out of the way
            self.testTabs.setCurrentWidget(self.inputParametersTab)
            self.testTabs.setCurrentWidget(self.outputParametersTab)

        self.verify()

    def unselectOutputParameter(self):
        self.outputParameterView.clearSelection()

    def toggleOutputParameterFormatVisible(self):
        if self.outputParameterFormatVisible:
            self.outputParameterFormat.setIcon(qta.icon('mdi.cog', color='orange'))
            self.outputParameterFormatVisible = False
            self.outputParameterFormat.setToolTip('Show parameter formats')
            self.outputParameterView.setColumnHidden(OutputColumnIndex.FMT(), True)
        else:
            self.outputParameterFormat.setIcon(qta.icon('mdi.cog-outline', color='orange'))
            self.outputParameterFormatVisible = True
            self.outputParameterFormat.setToolTip('Hide parameter formats')
            self.outputParameterView.setColumnHidden(OutputColumnIndex.FMT(), False)

    def deleteOutputParameter(self, row):
        selectedIndexes = self.outputParameterView.selectedIndexes()
        selectedRows = set()
        for index in selectedIndexes:
            if index.row() not in selectedRows:
                selectedRows.add(index.row())
        if len(selectedRows) == 1:  # can only delete one parameter at a time!
            row = list(selectedRows)[0]
            self.outputParameterModel.takeRow(row)
            self.outputParameterView.clearSelection()

    def getDescription(self):
        return self.description.toPlainText().split('\n')

    def descriptionLength(self):
        retval = ''.join(self.getDescription()).replace(' ', '').replace('\t', '')
        return len(retval)

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
            #menu = QtWidgets.QMenu(self)
            #overwrite = menu.addAction("overwrite")
            #action = menu.exec_(self.table.mapToGlobal(item))
            print(item.text())

        self.Feedback.setText("")

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
                        #check([text], is_valid_test_name, False, "The parameter name is not valid, character not allowed!")
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

    def _validate_output_parameters(self):
        rows = self.outputParameterModel.rowCount()
        for row in range(rows):
            name, attributes = self.getOutputParameter(row)
            self._validate_attributes(name, attributes, 'output')

    def _validate_input_parameters(self):
        rows = self.inputParameterModel.rowCount()
        for row in range(rows):
            name, attributes = self.getInputParameter(row)
            self._validate_attributes(name, attributes, 'input')

    def _validate_attributes(self, name: str, attributes: dict, type: str):
        if name == '':
            self.Feedback.setText(f"name attribute in {type} parameter table is missing")
            return

        for attribute, value in attributes.items():
            if value != '':
                continue

            self.Feedback.setText(f"attribute {attribute} in parameter {name} is invalid")

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
                # if TestName not exist:
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

                for parameterName in mappingATEDic.values():
                    parameterName_split = parameterName.split('.')
                    if parameterName_split[0] == 'output_parameters':
                        if parameterName_split[1] != 'name':
                            value = searchAndAssign(parameterName, write_content=False)
                            if parameterName_split[1] == 'unit':
                                if value == '' or value == ' ' or (type(value) == float and np.isnan(value)):
                                    value == '˽'
                                if type(value) == str and len(value) > 1 and value not in SI and value[0] in POWER.keys():
                                    output_parameters['exp10'] = POWER[value[0]]
                                    value = value[1:]
                            elif parameterName_split[1] == 'unit':
                                output_parameters['exp10'] = 0
                            output_parameters[parameterName_split[1]] = value
                if 'output_parameters' not in test_content:
                    test_content['output_parameters'] = {name: output_parameters}
                else:
                    test_content['output_parameters'][name] = output_parameters

            # self._update_power_with_correct_value(attributes)
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
    #app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    #app.references = set()
    main = QMainWindow()
    project_directory = r'C:\Users\jung\ATE\packages\envs\semi-ate-4\tb_ate'
    homedir = os.path.expanduser("~")
    project_info = ProjectNavigation(project_directory, homedir, main)
    project_info.active_hardware = 'HW0'
    project_info.active_base = 'FT'
    project_info.active_target = 'Device1'
    file_system_operator = FileSystemOperator(str(project_info.project_directory), project_info.parent)
    # selected_file = file_system_operator.get_file('*.xlsx')
    selected_file = r"C:\Users\jung\ATE\packages\envs\semi-ate-4\tb_ate\Output_HATB_65.xlsx"
    excel_test_dialog(project_info, selected_file)
