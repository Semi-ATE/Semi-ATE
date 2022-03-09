# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 18:56:05 2019

@author: hoeren

References:
    http://www.cplusplus.com/reference/cstdio/fprintf/
    https://docs.python.org/3/library/functions.html#float
    https://docs.python.org/3.6/library/string.html#format-specification-mini-language
"""
import os
import re

import numpy as np
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
from ate_spyder.widgets.validation import valid_name_regex
from ate_spyder.widgets.actions_on.tests.Utils import POWER
from ate_spyder.widgets.constants import UpdateOptions

minimal_docstring_length = 80

MAX_OUTPUT_NUMBER = 100
INPUTSHMOO_COLUMN_INDEX = 0
INPUT_NAME_COLUMN_INDEX = 1
INPUT_MIN_COLUMN_INDEX = 2
INPUT_DEFAULT_COLUMN_INDEX = 3
INPUT_MAX_COLUMN_INDEX = 4
INPUT_MULTIPLIER_COLUMN_INDEX = 5
INPUT_UNIT_COLUMN_INDEX = 6
INPUT_FMT_COLUMN_INDEX = 7
INPUT_MAX_NUM_COLUMNS = INPUT_FMT_COLUMN_INDEX + 1  # Adjust this to match the highest column index, if columns are added!


# ToDo: Use constants for all accesses to the output table.
OUTPUT_NAME_COLUMN_INDEX = 0
OUTPUT_LSL_COLUMN_INDEX = 1
OUTPUT_LTL_COLUMN_INDEX = 2
OUTPUT_NOM_COLUMN_INDEX = 3
OUTPUT_UTL_COLUMN_INDEX = 4
OUTPUT_USL_COLUMN_INDEX = 5
OUTPUT_POWER_COLUMN_INDEX = 6
OUTPUT_UNIT_COLUMN_INDEX = 7
OUTPUT_FMT_COLUMN_INDEX = 8


class Delegator(QtWidgets.QStyledItemDelegate):
    """General Custom Delegator Class that works with regex."""

    def __init__(self, regex, table=None, column=None, parent=None):
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.table: QtWidgets.QTableView = table
        self.column = column
        self.validator = QtGui.QRegExpValidator(QtCore.QRegExp(regex))

    def createEditor(self, parent, option, index):
        """Overloading to customize."""
        line_edit = QtWidgets.QLineEdit(parent)
        line_edit.setValidator(self.validator)
        line_edit.editingFinished.connect(lambda: self.validate_text(line_edit))

        return line_edit

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
        # TODO: implement
        if editor.text() in self.existing_names:
            pass


class TestWizard(BaseDialog):
    """Wizard to work with 'Test' definition."""

    def __init__(self, project_info, test_content=None, read_only=False):
        super().__init__(__file__, parent=project_info.parent)

        self.read_only = read_only
        self.project_info = project_info
        self.test_content = test_content

        if test_content is None:
            test_content = make_blank_definition(project_info)
        else:
            self.TestName.setText(test_content['name'])
            self.TestName.setEnabled(False)

        self.Feedback.setStyleSheet('color: orange')
        self.edit_feedback.setStyleSheet('color: orange')

        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

    # TestName
        TestName_validator = QtGui.QRegExpValidator(QtCore.QRegExp(valid_name_regex), self)
        self.TestName.setValidator(TestName_validator)

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

    # DescriptionTab
        self.description.clear()
        self.description.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)  # https://doc.qt.io/qt-5/qtextedit.html#LineWrapMode-enum
        # TODO: add a line at 80 characters (PEP8/E501) (https://stackoverflow.com/questions/30371613/draw-vertical-lines-on-qtextedit-in-pyqt)
        self.description.setPlainText('\n'.join(test_content['docstring']))

    # Delegators
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

        self.inputParameterAdd.setIcon(qta.icon('mdi.plus-box-outline', color='orange'))
        self.inputParameterAdd.setToolTip('Add a parameter')

        self.inputParameterUnselect.setIcon(qta.icon('mdi.select-off', color='orange'))
        self.inputParameterUnselect.setToolTip('Clear selection')

        self.inputParameterFormat.setIcon(qta.icon('mdi.cog', color='orange'))
        self.inputParameterFormat.setToolTip('Show parameter formats')
        self.inputParameterFormatVisible = False

        self.inputParameterMoveDown.setIcon(qta.icon('mdi.arrow-down-bold-box-outline', color='orange'))
        self.inputParameterMoveDown.setToolTip('Move selected parameter Down')

        self.inputParameterDelete.setIcon(qta.icon('mdi.minus-box-outline', color='orange'))
        self.inputParameterDelete.setToolTip('Delete selected parameter')

        inputParameterHeaderLabels = ['Shmoo', 'Name', 'Min', 'Default', 'Max', '10ᵡ', 'Unit', 'fmt']
        self.inputParameterModel = QtGui.QStandardItemModel()
        self.inputParameterModel.setObjectName('inputParameters')
        self.inputParameterModel.setHorizontalHeaderLabels(inputParameterHeaderLabels)
        self.nameDelegator_input_parameters_view = Delegator(valid_name_regex, parent=self, table=self.inputParameterView, column=INPUT_NAME_COLUMN_INDEX)

        self.inputParameterView.horizontalHeader().setVisible(True)
        self.inputParameterView.verticalHeader().setVisible(True)
        self.inputParameterView.setModel(self.inputParameterModel)
        self.inputParameterView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)  # https://doc.qt.io/qt-5/qabstractitemview.html#SelectionBehavior-enum
        self.inputParameterView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)  # https://doc.qt.io/qt-5/qabstractitemview.html#SelectionMode-enum
        self.inputParameterView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)  # https://doc.qt.io/qt-5/qt.html#ContextMenuPolicy-enum

        self.inputParameterView.setItemDelegateForColumn(INPUT_NAME_COLUMN_INDEX, self.nameDelegator_input_parameters_view)
        self.inputParameterView.setItemDelegateForColumn(INPUT_MIN_COLUMN_INDEX, self.minDelegator)
        self.inputParameterView.setItemDelegateForColumn(INPUT_DEFAULT_COLUMN_INDEX, self.defaultDelegator)
        self.inputParameterView.setItemDelegateForColumn(INPUT_MAX_COLUMN_INDEX, self.maxDelegator)
        self.inputParameterView.setItemDelegateForColumn(INPUT_FMT_COLUMN_INDEX, self.fmtDelegator)

        self.setInputpParameters(test_content['input_parameters'])
        self.inputParameterView.setColumnHidden(INPUT_FMT_COLUMN_INDEX, True)
        self.inputParameterSelectionChanged()

    # OutputParametersTab
        self.outputParameterMoveUp.setIcon(qta.icon('mdi.arrow-up-bold-box-outline', color='orange'))
        self.outputParameterMoveUp.setToolTip('Move selected parameter Up')

        self.outputParameterAdd.setIcon(qta.icon('mdi.plus-box-outline', color='orange'))
        self.outputParameterAdd.setToolTip('Add a parameter')

        self.outputParameterUnselect.setIcon(qta.icon('mdi.select-off', color='orange'))
        self.outputParameterUnselect.setToolTip('Clear selection')

        self.outputParameterFormat.setIcon(qta.icon('mdi.cog', color='orange'))
        self.outputParameterFormat.setToolTip('Show parameter formats')
        self.outputParameterFormatVisible = False

        self.outputParameterMoveDown.setIcon(qta.icon('mdi.arrow-down-bold-box-outline', color='orange'))
        self.outputParameterMoveDown.setToolTip('Move selected parameter Down')

        self.outputParameterDelete.setIcon(qta.icon('mdi.minus-box-outline', color='orange'))
        self.outputParameterDelete.setToolTip('Delete selected parameter')

        outputParameterHeaderLabels = ['Name', 'LSL', '(LTL)', 'Nom', '(UTL)', 'USL', '10ᵡ', 'Unit', 'fmt']
        self.outputParameterModel = QtGui.QStandardItemModel()
        self.outputParameterModel.setObjectName('outputParameters')
        self.outputParameterModel.setHorizontalHeaderLabels(outputParameterHeaderLabels)

        self.outputParameterView.horizontalHeader().setVisible(True)
        self.outputParameterView.verticalHeader().setVisible(True)
        self.outputParameterView.setModel(self.outputParameterModel)
        self.outputParameterView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectItems)  # https://doc.qt.io/qt-5/qabstractitemview.html#SelectionBehavior-enum
        self.outputParameterView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)  # https://doc.qt.io/qt-5/qabstractitemview.html#SelectionMode-enum
        self.outputParameterView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)  # https://doc.qt.io/qt-5/qt.html#ContextMenuPolicy-enum
        self.nameDelegator_output_parameters_view = Delegator(valid_name_regex, parent=self, table=self.outputParameterView, column=0)

        self.outputParameterView.setItemDelegateForColumn(0, self.nameDelegator_output_parameters_view)
        self.outputParameterView.setItemDelegateForColumn(1, self.LSLDelegator)
        self.outputParameterView.setItemDelegateForColumn(2, self.LTLDelegator)
        self.outputParameterView.setItemDelegateForColumn(3, self.NomDelegator)
        self.outputParameterView.setItemDelegateForColumn(4, self.UTLDelegator)
        self.outputParameterView.setItemDelegateForColumn(5, self.USLDelegator)

        self.outputParameterView.setColumnHidden(OUTPUT_FMT_COLUMN_INDEX, True)
        self.setOutputParameters(test_content['output_parameters'])
        self.outputParameterSelectionChanged()

        self._init_group()

        # TODO: Idea:
        #   limit the number of output parameters to 9, so we have a decade per test-number,
        #   and the '0' is the FTR 🙂

    # Tabs
        self.testTabs.setTabEnabled(self.testTabs.indexOf(self.dependenciesTab), False)

    # buttons
        self.CancelButton.clicked.connect(self.CancelButtonPressed)
        self.OKButton.clicked.connect(self.OKButtonPressed)
        self.OKButton.setEnabled(False)

        self._connect_event_handler()
        self.resize(735, 400)
        self.verify()

    def _connect_event_handler(self):
        self.outputParameterMoveUp.clicked.connect(self.moveOutputParameterUp)
        self.outputParameterAdd.clicked.connect(self.addOutputParameter)
        self.outputParameterUnselect.clicked.connect(self.unselectOutputParameter)
        self.outputParameterFormat.clicked.connect(self.toggleOutputParameterFormatVisible)
        self.outputParameterMoveDown.clicked.connect(self.moveOutputParameterDown)
        self.outputParameterDelete.clicked.connect(self.deleteOutputParameter)
        self.outputParameterModel.itemChanged.connect(self.outputParameterItemChanged)
        self.outputParameterView.customContextMenuRequested.connect(self.outputParameterContextMenu)
        self.outputParameterView.selectionModel().selectionChanged.connect(self.outputParameterSelectionChanged)  # https://doc.qt.io/qt-5/qitemselectionmodel.html
        self.testTabs.currentChanged.connect(self.testTabChanged)
        self.inputParameterView.customContextMenuRequested.connect(self.inputParameterContextMenu)
        self.inputParameterModel.itemChanged.connect(self.inputParameterItemChanged)
        self.inputParameterMoveUp.clicked.connect(self.moveInputParameterUp)
        self.inputParameterAdd.clicked.connect(self.addInputParameter)
        self.inputParameterUnselect.clicked.connect(self.unselectInputParameter)
        self.inputParameterFormat.clicked.connect(self.toggleInputParameterFormatVisible)
        self.inputParameterMoveDown.clicked.connect(self.moveInputParameterDown)
        self.inputParameterDelete.clicked.connect(self.deleteInputParameter)
        self.inputParameterView.selectionModel().selectionChanged.connect(self.inputParameterSelectionChanged)  # https://doc.qt.io/qt-5/qitemselectionmodel.html
        self.TestName.textChanged.connect(self.verify)

    def testTabChanged(self, activatedTabIndex):
        """Slot for when the Tab is changed."""
        if activatedTabIndex == self.testTabs.indexOf(self.inputParametersTab):
            self.tableAdjust(self.inputParameterView, INPUT_NAME_COLUMN_INDEX)
        elif activatedTabIndex == self.testTabs.indexOf(self.outputParametersTab):
            self.tableAdjust(self.outputParameterView, OUTPUT_NAME_COLUMN_INDEX)
        else:
            pass

    def resizeEvent(self, event):
        """Overload of Slot for when the Wizard is resized."""

        QtWidgets.QWidget.resizeEvent(self, event)
        self.tableAdjust(self.inputParameterView, INPUT_NAME_COLUMN_INDEX)
        self.tableAdjust(self.outputParameterView, OUTPUT_NAME_COLUMN_INDEX)

    def tableAdjust(self, TableView, NameColumnIndex):
        """Call that adjust the table columns in 'TableView' to the available space."""
        TableView.resizeColumnsToContents()
        autoVisibleWidth = 0
        for column in range(TableView.model().columnCount()):
            if column != NameColumnIndex:
                autoVisibleWidth += TableView.columnWidth(column)
        vHeaderWidth = TableView.verticalHeader().width()
        availableWidth = TableView.geometry().width()
        nameWidth = availableWidth - vHeaderWidth - autoVisibleWidth - 6  # no clue where this '6' comes from, but it works
        TableView.setColumnWidth(NameColumnIndex, nameWidth)

    def unitContextMenu(self, unitSetter):
        """Deploys the 'Unit' context menu and applies selection to 'unitSetter'.

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
            ('η (nano=10⁻⁹)',
             lambda: multiplierSetter('η', 'nano=10⁻⁹')),
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

    def inputParameterContextMenu(self, point):
        '''
        here we select which context menu (for input_parameters) we need,
        based on the column where we activated the context menu on, and
        dispatch to the appropriate context menu.
        '''
        index = self.inputParameterView.indexAt(point)
        col = index.column()
        row = index.row()
        formatSetter = self.setInputParameterFormat
        valueSetter = self.setInputParameterValue
        multiplierSetter = self.setInputParameterMultiplier
        unitSetter = self.setInputParameterUnit

        if col == INPUT_NAME_COLUMN_INDEX or col == INPUT_FMT_COLUMN_INDEX:
            if row != 0:  # not for temperature
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

        elif index.column() in [INPUT_MIN_COLUMN_INDEX, INPUT_DEFAULT_COLUMN_INDEX, INPUT_MAX_COLUMN_INDEX]:
            if index.row() != 0:  # not for temperature
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

        elif index.column() == INPUT_MULTIPLIER_COLUMN_INDEX:  # --> reference = STDF V4.pdf @ page 50 & https://en.wikipedia.org/wiki/Order_of_magnitude
            if index.row() != 0:  # temperature
                menu = self.multiplierContextMenu(multiplierSetter)
                menu.exec_(QtGui.QCursor.pos())

        elif index.column() == INPUT_UNIT_COLUMN_INDEX:  # Unit
            if index.row() != 0:  # not temperature
                menu = self.unitContextMenu(unitSetter)
                menu.exec_(QtGui.QCursor.pos())

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
        # shmooed_parameters = 0
        # for item_row in range(self.inputParameterModel.rowCount()):
        #     name_item = self.inputParameterModel.item(item_row, 0)
        #     if name_item.checkState() == QtCore.Qt.Checked:
        #         shmooed_parameters+=1

        # if shmooed_parameters > 2:
        #     QtWidgets.QMessageBox.question(
        #         self,
        #         'Warning',
        #         'It is not advisable to have more than\n2 input parameters Shmoo-able.',
        #         QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)

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

        if numberOfSelectedRows == 0:
            self.inputParameterUnselect.setEnabled(False)
            self.inputParameterMoveUp.setEnabled(False)
            self.inputParameterDelete.setEnabled(False)
            self.inputParameterMoveDown.setEnabled(False)
        elif numberOfSelectedRows == 1:
            selectedRow = list(selectedRows)[0]
            self.inputParameterUnselect.setEnabled(True)
            if selectedRow > 1:
                self.inputParameterMoveUp.setEnabled(True)
            else:
                self.inputParameterMoveUp.setEnabled(False)
            self.inputParameterDelete.setEnabled(True)
            if selectedRow < lastRow:
                self.inputParameterMoveDown.setEnabled(True)
            else:
                self.inputParameterMoveDown.setEnabled(False)
        else:
            self.inputParameterUnselect.setEnabled(True)
            self.inputParameterMoveUp.setEnabled(False)
            self.inputParameterDelete.setEnabled(False)
            self.inputParameterMoveDown.setEnabled(False)

    def setInputParameterFormat(self, Format):
        index_selection = self.inputParameterView.selectedIndexes()

        for index in index_selection:
            if index.row() != 0:  # not for 'Temperature'
                fmt_item = self.__get_input_parameter_column(index.row(), INPUT_FMT_COLUMN_INDEX)
                fmt_item.setData(Format, QtCore.Qt.DisplayRole)

        self.inputParameterView.clearSelection()

    def setInputParameterValue(self, value):
        '''
        value is **ALWAYS** a float (might be inf & nan)
        '''
        index_selection = self.inputParameterView.selectedIndexes()

        if not isinstance(value, float):
            raise Exception("Woops, a float is mandatory !!!")

        for index in index_selection:
            item = self.inputParameterModel.itemFromIndex(index)
            fmt_item = self.__get_input_parameter_column(index.row(), INPUT_FMT_COLUMN_INDEX)
            Fmt = fmt_item.data(QtCore.Qt.DisplayRole)
            if np.isinf(value):
                if np.isposinf(value):  # only for Max
                    if index.column() == INPUT_MAX_COLUMN_INDEX:
                        item.setData('+∞', QtCore.Qt.DisplayRole)
                else:  # np.isneginf(value) # only for Min
                    if index.column() == INPUT_MIN_COLUMN_INDEX:
                        item.setData('-∞', QtCore.Qt.DisplayRole)
            elif np.isnan(value):  # forget about it! translate
                if index.column() == INPUT_MIN_COLUMN_INDEX:  # Min --> -np.inf
                    item.setData('-∞', QtCore.Qt.DisplayRole)
                elif index.column() == INPUT_DEFAULT_COLUMN_INDEX:  # Default --> 0.0
                    item.setData(f"{0.0:{Fmt}}", QtCore.Qt.DisplayRole)
                    pass
                elif index.column() == INPUT_MAX_COLUMN_INDEX:  # Max --> np.inf
                    item.setData('-∞', QtCore.Qt.DisplayRole)
            else:  # for columns 1, 2 and 3
                if index.column() in [INPUT_MIN_COLUMN_INDEX, INPUT_DEFAULT_COLUMN_INDEX, INPUT_MAX_COLUMN_INDEX]:
                    item.setData(f"{value:{Fmt}}", QtCore.Qt.DisplayRole)

        self.inputParameterView.clearSelection()

    def __set_input_parameter_attribtue(self, attribute_column, text, tooltip):
        selection = self.inputParameterView.selectedIndexes()

        for index in selection:
            if index.column() == attribute_column:
                self.inputParameterModel.setData(index, text, QtCore.Qt.DisplayRole)
                self.inputParameterModel.setData(index, tooltip, QtCore.Qt.ToolTipRole)

    def setInputParameterMultiplier(self, text, tooltip):
        self.__set_input_parameter_attribtue(INPUT_MULTIPLIER_COLUMN_INDEX, text, tooltip)

    def setInputParameterUnit(self, text, tooltip):
        self.__set_input_parameter_attribtue(INPUT_UNIT_COLUMN_INDEX, text, tooltip)

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
            'Temperature' : {'Shmoo' : True,  'Min' :     -40, 'Default' : 25, 'Max' :     170, '10ᵡ' :  '', 'Unit' : '°C', 'fmt' : '.0f'}, # Obligatory !
            'i'           : {'Shmoo' : False, 'Min' : -np.inf, 'Default' :  0, 'Max' : +np.inf, '10ᵡ' : 'μ', 'Unit' :  'A', 'fmt' : '.3f'},
            'j'           : {'Shmoo' : False, 'Min' :    '-∞', 'Default' :  0, 'Max' :    '+∞', '10ᵡ' : 'μ', 'Unit' :  'A', 'fmt' : '.3f'}}

        References:
            https://doc.qt.io/qt-5/qt.html#CheckState-enum
            https://doc.qt.io/qt-5/qt.html#ItemFlag-enum
            https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum
            https://doc.qt.io/qt-5/qstandarditem.html
        '''
        rowCount = self.inputParameterModel.rowCount()

        if name == 'Temperature':  # must be at row 0, regardless what row says
            if rowCount == 0:  # make first entry
                self.inputParameterModel.appendRow([QtGui.QStandardItem() for i in range(INPUT_MAX_NUM_COLUMNS)])
            item_row = 0
        else:
            if row is None:  # append
                self.inputParameterModel.appendRow([QtGui.QStandardItem() for i in range(INPUT_MAX_NUM_COLUMNS)])
                item_row = rowCount
            else:  # update
                if row > rowCount:
                    raise Exception(f"row({row}) > rowCount({rowCount})")
                item_row = row

        shmoo_item = self.__get_input_parameter_column(item_row, INPUTSHMOO_COLUMN_INDEX)
        name_item = self.__get_input_parameter_column(item_row, INPUT_NAME_COLUMN_INDEX)
        min_item = self.__get_input_parameter_column(item_row, INPUT_MIN_COLUMN_INDEX)
        default_item = self.__get_input_parameter_column(item_row, INPUT_DEFAULT_COLUMN_INDEX)
        max_item = self.__get_input_parameter_column(item_row, INPUT_MAX_COLUMN_INDEX)
        multiplier_item = self.__get_input_parameter_column(item_row, INPUT_MULTIPLIER_COLUMN_INDEX)
        unit_item = self.__get_input_parameter_column(item_row, INPUT_UNIT_COLUMN_INDEX)
        fmt_item = self.__get_input_parameter_column(item_row, INPUT_FMT_COLUMN_INDEX)

        self.inputParameterModel.blockSignals(True)
        Fmt = '.0f'

    # fmt
        if name == 'Temperature':
            Fmt = '.0f'
            fmt_item.setFlags(QtCore.Qt.NoItemFlags)
        else:
            if 'fmt' not in attributes:
                Fmt = '.3f'
            else:
                Fmt = attributes['fmt']
            fmt_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

        fmt_item.setData(Fmt, QtCore.Qt.DisplayRole)
        fmt_item.setData(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)

    # Min
        if name == 'Temperature':
            if isinstance(attributes['Min'], str):
                if '∞' in attributes['Min']:  # forget about it --> -60
                    Min = -60.0
                else:
                    Min = float(attributes['Min'])
                    if Min < -60.0:
                        Min = -60.0
            elif isinstance(attributes['Min'], (float, int)):
                Min = float(attributes['Min'])
                if Min < -60.0:
                    Min = -60.0
            else:
                raise Exception("type(attribute['Min']) = {type(attribute['Min'])}, which is not (str, float or int) ... WTF?!?")
            min_item.setData(f"{Min:{Fmt}}", QtCore.Qt.DisplayRole)
        else:
            if isinstance(attributes['Min'], str):
                if '∞' in attributes['Min']:
                    Min = -np.inf
                    min_item.setData('-∞', QtCore.Qt.DisplayRole)
                else:
                    Min = float(attributes['Min'])
                    min_item.setData(f"{Min:{Fmt}}", QtCore.Qt.DisplayRole)
            elif isinstance(attributes['Min'], (float, int)):
                if attributes['Min'] == -np.inf:
                    Min = -np.inf
                    min_item.setData('-∞', QtCore.Qt.DisplayRole)
                else:
                    Min = float(attributes['Min'])
                    min_item.setData(f"{Min:{Fmt}}", QtCore.Qt.DisplayRole)
            else:
                raise Exception("type(attribute['Min']) = {type(attribute['Min'])}, which is not (str, float or int) ... WTF?!?")
        min_item.setData(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        min_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # Max
        if name == 'Temperature':
            if isinstance(attributes['Max'], str):
                if '∞' in attributes['Max']:  # forget about it --> 200
                    Max = 200.0
                else:
                    Max = float(attributes['Max'])
                    if Max > 200.0:
                        Max = 200.0
            elif isinstance(attributes['Max'], (float, int)):
                Max = float(attributes['Max'])
                if Max > 200.0:
                    Max = 200.0
            else:
                raise Exception("type(attribute['Max']) = {type(attribute['Max'])}, which is not (str, float or int) ... WTF?!?")
            max_item.setData(f"{Max:{Fmt}}", QtCore.Qt.DisplayRole)
        else:
            if isinstance(attributes['Max'], str):
                if '∞' in attributes['Max']:
                    Max = np.inf
                    max_item.setData('+∞', QtCore.Qt.DisplayRole)
                else:
                    Max = float(attributes['Max'])
                    max_item.setData(f"{Max:{Fmt}}", QtCore.Qt.DisplayRole)
            elif isinstance(attributes['Max'], (float, int)):
                if attributes['Max'] == np.inf:
                    Max = np.inf
                    max_item.setData('+∞', QtCore.Qt.DisplayRole)
                else:
                    Max = float(attributes['Max'])
                    max_item.setData(f"{Max:{Fmt}}", QtCore.Qt.DisplayRole)
            else:
                raise Exception("type(attribute['Max']) = {type(attribute['Max'])}, which is not (str, float or int) ... WTF?!?")
        max_item.setData(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        max_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # Default
        if name == 'Temperature':
            if isinstance(attributes['Default'], str):
                if '∞' in attributes['Default']:  # forget about it --> 25
                    Default = 25.0
                else:
                    Default = float(attributes['Default'])
                    if Default > Max or Default < Min:
                        Default = 25.0
            elif isinstance(attributes['Default'], (float, int)):
                Default = float(attributes['Default'])
                if Default > Max or Default < Min:
                    Default = 25.0
            else:
                raise Exception("type(attribute['Default']) = {type(attribute['Default'])}, which is not (str, float or int) ... WTF?!?")
        else:
            if isinstance(attributes['Default'], str):
                if attributes['Default'] == '-∞':
                    Default = -np.inf
                elif attributes['Default'] in ['∞', '+∞']:
                    Default = np.inf
                else:
                    Default = float(attributes['Default'])
            elif isinstance(attributes['Default'], (float, int)):
                Default = float(attributes['Default'])
            else:
                raise Exception("type(attribute['Default']) = {type(attribute['Default'])}, which is not (str, float or int) ... WTF?!?")
            Default = self.__select_default(Min, Default, Max)

        default_item.setData(f"{Default:{Fmt}}", QtCore.Qt.DisplayRole)
        default_item.setData(int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        default_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # name
        name_item.setData(name, QtCore.Qt.DisplayRole)  # https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum
        name_item.setData(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)

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

        if attributes['Shmoo'] is True:
            shmoo_item.setData(QtCore.Qt.Checked, QtCore.Qt.CheckStateRole)
        else:
            shmoo_item.setData(QtCore.Qt.Unchecked, QtCore.Qt.CheckStateRole)

    # Multiplier
        if name == 'Temperature':  # fixed regardless what the attributes say
            multiplier_item.setData('', QtCore.Qt.DisplayRole)
            multiplier_item.setData(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
            multiplier_item.setFlags(QtCore.Qt.NoItemFlags)
        else:
            multiplier_item.setData(str(self.get_key(attributes['10ᵡ'])), QtCore.Qt.DisplayRole)
            multiplier_item.setData(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
            multiplier_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
    # Unit
        if name == 'Temperature':  # fixed regardless what the attribues say
            unit_item.setData('°C', QtCore.Qt.DisplayRole)
            unit_item.setData(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
            unit_item.setFlags(QtCore.Qt.NoItemFlags)
        else:
            unit_item.setData(str(attributes['Unit']), QtCore.Qt.DisplayRole)
            unit_item.setData(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
            unit_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

        self.inputParameterModel.blockSignals(False)
        self.tableAdjust(self.inputParameterView, INPUT_NAME_COLUMN_INDEX)

    def setInputpParameters(self, definition):
        for name in definition:
            attributes = definition[name]
            self.setInputParameter(name, attributes)

    def getInputParameter(self, row):
        attributes = {'Shmoo': None, 'Min': None, 'Default': None, 'Max': None, '10ᵡ': '˽', 'Unit': '˽', 'fmt': None}

        name_item = self.__get_input_parameter_column(row, INPUT_NAME_COLUMN_INDEX)

        if not isinstance(name_item, QtGui.QStandardItem):
            raise Exception("WTF")

        name = name_item.data(QtCore.Qt.DisplayRole)

        shmoo_item = self.__get_input_parameter_column(row, INPUTSHMOO_COLUMN_INDEX)
        shmoo = shmoo_item.data(QtCore.Qt.CheckStateRole)

        if shmoo == QtCore.Qt.Checked:
            attributes['Shmoo'] = True
        else:
            attributes['Shmoo'] = False

        fmt_item = self.__get_input_parameter_column(row, INPUT_FMT_COLUMN_INDEX)
        Fmt = fmt_item.data(QtCore.Qt.DisplayRole)
        attributes['fmt'] = Fmt

        min_item = self.__get_input_parameter_column(row, INPUT_MIN_COLUMN_INDEX)
        Min = min_item.data(QtCore.Qt.DisplayRole)
        if '∞' in Min:
            attributes['Min'] = -np.Inf
        else:
            Min = float(Min)
            attributes['Min'] = float(f"{Min:{Fmt}}")

        default_item = self.__get_input_parameter_column(row, INPUT_DEFAULT_COLUMN_INDEX)
        Default = float(default_item.data(QtCore.Qt.DisplayRole))
        attributes['Default'] = float(f"{Default:{Fmt}}")

        max_item = self.__get_input_parameter_column(row, INPUT_MAX_COLUMN_INDEX)
        Max = max_item.data(QtCore.Qt.DisplayRole)
        if '∞' in Max:
            attributes['Max'] = np.Inf
        else:
            Max = float(Max)
            attributes['Max'] = float(f"{Max:{Fmt}}")

        multiplier_item = self.__get_input_parameter_column(row, INPUT_MULTIPLIER_COLUMN_INDEX)
        Multiplier = multiplier_item.data(QtCore.Qt.DisplayRole)
        attributes['10ᵡ'] = Multiplier if Multiplier else attributes['10ᵡ']

        unit_item = self.__get_input_parameter_column(row, INPUT_UNIT_COLUMN_INDEX)
        Unit = unit_item.data(QtCore.Qt.DisplayRole)
        attributes['Unit'] = Unit

        return name, attributes

    def getInputParameters(self):
        retval = {}
        rows = self.inputParameterModel.rowCount()
        for row in range(rows):
            name, attributes = self.getInputParameter(row)
            self._update_power_with_correct_value(attributes)
            retval[name] = attributes

        return retval

    def _update_power_with_correct_value(self, attributes):
        try:
            attributes['10ᵡ'] = POWER[attributes['10ᵡ']]
        except KeyError:
            attributes['10ᵡ'] = self.get_key(attributes['10ᵡ'])

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
            item = self.__get_input_parameter_column(item_row, INPUT_NAME_COLUMN_INDEX)
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
        attributes = {'Shmoo': False, 'Min': '-∞', 'Default': 0, 'Max': '+∞', '10ᵡ': '˽', 'Unit': '˽', 'fmt': '.3f'}
        self.setInputParameter(name, attributes)
        self.verify()

    def unselectInputParameter(self):
        self.inputParameterView.clearSelection()

    def toggleInputParameterFormatVisible(self):
        if self.inputParameterFormatVisible:
            self.inputParameterFormat.setIcon(qta.icon('mdi.cog', color='orange'))
            self.inputParameterFormatVisible = False
            self.inputParameterFormat.setToolTip('Show parameter formats')
            self.inputParameterView.setColumnHidden(INPUT_FMT_COLUMN_INDEX, True)
        else:
            self.inputParameterFormat.setIcon(qta.icon('mdi.cog-outline', color='orange'))
            self.inputParameterFormatVisible = True
            self.inputParameterFormat.setToolTip('Hide parameter formats')
            self.inputParameterView.setColumnHidden(INPUT_FMT_COLUMN_INDEX, False)
        self.tableAdjust(self.inputParameterView, INPUT_NAME_COLUMN_INDEX)

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

        if col == 0 or col == 8:  # Name or format
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

        elif index.column() >= 1 and index.column() <= 5:  # LSL, (LTL), Nom, (UTL), USL
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

        elif index.column() == OUTPUT_POWER_COLUMN_INDEX:  # multiplier --> reference = STDF V4.pdf @ page 50 & https://en.wikipedia.org/wiki/Order_of_magnitude
            menu = self.multiplierContextMenu(multiplierSetter)
            menu.exec_(QtGui.QCursor.pos())

        elif index.column() == OUTPUT_UNIT_COLUMN_INDEX:  # Unit
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
            if index.column() == 0 or index.column() == 8:
                fmt_item = self.outputParameterModel.item(index.row(), 8)
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
                    if index.column() in [OUTPUT_LSL_COLUMN_INDEX, OUTPUT_LTL_COLUMN_INDEX]:
                        item.setData('+∞', QtCore.Qt.DisplayRole)
                else:  # np.isneginf(value) # only for columsn 4 & 5
                    if index.column() in [OUTPUT_USL_COLUMN_INDEX, OUTPUT_UTL_COLUMN_INDEX]:
                        item.setData('-∞', QtCore.Qt.DisplayRole)
            elif np.isnan(value):  # only for columns 2 & 4
                if index.column() in [OUTPUT_LTL_COLUMN_INDEX, OUTPUT_UTL_COLUMN_INDEX]:
                    item.setData('', QtCore.Qt.DisplayRole)
            else:  # for columns 1, 2, 3, 4 and 5
                if index.column() in [OUTPUT_LSL_COLUMN_INDEX, OUTPUT_LTL_COLUMN_INDEX, OUTPUT_NOM_COLUMN_INDEX, OUTPUT_UTL_COLUMN_INDEX, OUTPUT_USL_COLUMN_INDEX]:
                    fmt_item = self.outputParameterModel.item(index.row(), 8)
                    Fmt = fmt_item.data(QtCore.Qt.DisplayRole)
                    item.setData(f"{value:{Fmt}}", QtCore.Qt.DisplayRole)
        self.outputParameterView.clearSelection()

    def setOutputParameterMultiplier(self, text, tooltip):
        selection = self.outputParameterView.selectedIndexes()

        for index in selection:
            if index.column() in (OUTPUT_FMT_COLUMN_INDEX, OUTPUT_POWER_COLUMN_INDEX):
                self.outputParameterModel.setData(index, text, QtCore.Qt.DisplayRole)
                self.outputParameterModel.setData(index, tooltip, QtCore.Qt.ToolTipRole)
        self.outputParameterView.clearSelection()

    def setOutputParameterUnit(self, text, tooltip):
        selection = self.outputParameterView.selectedIndexes()

        for index in selection:
            if index.column() == OUTPUT_UNIT_COLUMN_INDEX: 
                self.outputParameterModel.setData(index, text, QtCore.Qt.DisplayRole)
                self.outputParameterModel.setData(index, tooltip, QtCore.Qt.ToolTipRole)
        self.outputParameterView.clearSelection()

    def setOutputParameter(self, name, attributes, row=None):
        '''
        sets the outputParameter name and it's attribues
        if row==None, append to the list.
        if row is given, it **must** already exist!

        Structure (of all output parameters):
        output_parameters = {                          # https://docs.python.org/3.6/library/string.html#format-specification-mini-language
            'parameter1_name' : {'LSL' : -inf, 'LTL' : None, 'Nom' :    0, 'UTL' : None, 'USL' :  inf, '10ᵡ' :  '', 'Unit' :  'Ω', 'fmt' : '.3f'},
            'parameter2_name' : {'LSL' :  0.0, 'LTL' : None, 'Nom' :  3.5, 'UTL' : None, 'USL' :  2.5, '10ᵡ' : 'μ', 'Unit' :  'V', 'fmt' : '.3f'},
            'R_vdd_contact'   : {'LSL' :  5.0, 'LTL' :  9.0, 'Nom' : 10.0, 'UTL' : 11.0, 'USL' : 20.0, '10ᵡ' : 'k', 'Unit' : 'Hz', 'fmt' : '.1f'}}

        References:
            https://doc.qt.io/qt-5/qt.html#CheckState-enum
            https://doc.qt.io/qt-5/qt.html#ItemFlag-enum
            https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum
            https://doc.qt.io/qt-5/qstandarditem.html
        '''
        rowCount = self.outputParameterModel.rowCount()

        if row is None:  # append
            self.outputParameterModel.appendRow([QtGui.QStandardItem() for i in range(9)])
            item_row = rowCount
        else:  # update
            if row > rowCount:
                raise Exception(f"row({row}) > rowCount({rowCount})")
            item_row = row

        name_item = self.outputParameterModel.item(item_row, 0)
        LSL_item = self.outputParameterModel.item(item_row, 1)
        LTL_item = self.outputParameterModel.item(item_row, 2)
        Nom_item = self.outputParameterModel.item(item_row, 3)
        UTL_item = self.outputParameterModel.item(item_row, 4)
        USL_item = self.outputParameterModel.item(item_row, 5)
        multiplier_item = self.outputParameterModel.item(item_row, 6)
        unit_item = self.outputParameterModel.item(item_row, 7)
        fmt_item = self.outputParameterModel.item(item_row, 8)

        self.outputParameterModel.blockSignals(True)

    # fmt
        if 'fmt' not in attributes:
            Fmt = '.3f'
        else:
            Fmt = attributes['fmt']
        fmt_item.setData(Fmt, QtCore.Qt.DisplayRole)
        fmt_item.setData(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        fmt_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # LSL
        if attributes['LSL'] is None:  # None on LSL doesn't exist --> = -Inf
            LSL_ = -np.inf
            LSL = '-∞'
        elif isinstance(attributes['LSL'], (float, int)):
            if abs(attributes['LSL']) == np.inf:
                LSL_ = -np.inf
                LSL = '-∞'
            elif np.isnan(attributes['LSL']):  # NaN on LSL doesn't exist --> = -Inf
                LSL_ = np.inf
                LSL = '-∞'
            else:
                LSL_ = float(attributes['LSL'])
                LSL = f"{LSL_:{Fmt}}"
        else:
            raise Exception(f"type(attributes['LSL']) = {type(attributes['LSL'])}, which is not (NoneType, float or int) ... WTF?!?")
        LSL_item.setData(LSL, QtCore.Qt.DisplayRole)
        LSL_item.setData(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        LSL_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # LTL
        if isinstance(attributes['LTL'], str):
            if attributes['LTL'] == '' or 'NAN' in attributes['LTL'].upper():
                LTL_ = np.nan
                LTL = ''
            elif '∞' in attributes['LTL']:
                LTL_ = -np.inf
                LTL = '-∞'
            else:
                LTL_ = float(attributes['LTL'])
                LTL = f"{LTL_:{Fmt}}"
        elif attributes['LTL'] is None:  # None on LTL = NaN
            LTL_ = np.nan
            LTL = ''
        elif isinstance(attributes['LTL'], (float, int)):
            if abs(attributes['LTL']) == np.inf:
                LTL_ = -np.inf
                LTL = '-∞'
            elif np.isnan(attributes['LTL']):
                LTL_ = np.nan
                LTL = ''
            else:
                LTL_ = float(attributes['LTL'])
                LTL = f"{LTL_:{Fmt}}"
        else:
            raise Exception(f"type(attributes['LTL']) = {type(attributes['LTL'])}, which is not (str, NoneType, float or int) ... WTF?!?")
        LTL_item.setData(LTL, QtCore.Qt.DisplayRole)
        LTL_item.setData(int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        LTL_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # USL
        if attributes['USL'] is None:  # None on USL doesn't exist --> = +Inf
            USL_ = np.inf
            USL = '+∞'
        elif isinstance(attributes['USL'], (float, int)):
            if abs(attributes['USL']) == np.inf:
                USL_ = np.inf
                USL = '+∞'
            elif np.isnan(attributes['USL']):  # NaN on USL doesn't extist --> = +Inf
                USL_ = np.inf
                USL = '+∞'
            else:
                USL_ = float(attributes['USL'])
                USL = f"{USL_:{Fmt}}"
        else:
            raise Exception(f"type(attributes['USL']) = {type(attributes['USL'])}, which is not (NoneType, float or int) ... WTF?!?")
        USL_item.setData(USL, QtCore.Qt.DisplayRole)
        USL_item.setData(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        USL_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # UTL
        if isinstance(attributes['UTL'], str):
            if attributes['UTL'] == '' or 'NAN' in attributes['UTL'].upper():
                UTL_ = np.nan
                UTL = ''
            elif '∞' in attributes['UTL']:
                UTL_ = -np.inf
                UTL = '+∞'
            else:
                UTL_ = float(attributes['LTL'])
                UTL = f"{UTL_:{Fmt}}"
        elif attributes['UTL'] is None:  # None on UTL = Nan
            UTL_ = np.nan
            UTL = ''
        elif isinstance(attributes['UTL'], (float, int)):
            if abs(attributes['UTL']) == np.inf:
                UTL_ = np.inf
                UTL = '+∞'
            elif np.isnan(attributes['UTL']):
                UTL_ = np.nan
                UTL = ''
            else:
                UTL_ = float(attributes['UTL'])
                UTL = f"{UTL_:{Fmt}}"
        else:
            raise Exception(f"type(attributes['UTL']) = {type(attributes['UTL'])}, which is not (str, NoneType, float or int) ... WTF?!?")
        UTL_item.setData(UTL, QtCore.Qt.DisplayRole)
        UTL_item.setData(int(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        UTL_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

    # Nom
        if attributes['Nom'] is None:  # None on Nom = 0.0
            Nom_ = 0.0
        elif isinstance(attributes['Nom'], (float, int)):
            Nom_ = float(attributes['Nom'])
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
            raise Exception(f"type(attribute['Nom']) = {type(attributes['Nom'])}, which is not (float or int) ... WTF?!?")
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
        multiplier_item.setData(str(self.get_key(attributes['10ᵡ'])), QtCore.Qt.DisplayRole)
        multiplier_item.setData(int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        multiplier_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
    # Unit
        unit_item.setData(str(attributes['Unit']), QtCore.Qt.DisplayRole)
        unit_item.setData(int(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter), QtCore.Qt.TextAlignmentRole)
        unit_item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

        self.outputParameterModel.blockSignals(False)
        self.tableAdjust(self.outputParameterView, OUTPUT_NAME_COLUMN_INDEX)

    def setOutputParameters(self, definition):
        for name in definition:
            attributes = definition[name]
            self.setOutputParameter(name, attributes)

    def getOutputParameter(self, row):
        '''
        the result is always a float (might be np.inf or np.nan) for LSL, LTL, Nom, UTL and USL (rest is string)
        the source is in the model, and always a string.
        '''
        attributes = {'LSL': None, 'LTL': None, 'Nom': None, 'UTL': None, 'USL': None, '10ᵡ': '˽', 'Unit': '˽', 'fmt': ''}

        name_item = self.outputParameterModel.item(row, 0)
        name = name_item.data(QtCore.Qt.DisplayRole)

    # LSL
        LSL_item = self.outputParameterModel.item(row, 1)
        LSL = LSL_item.data(QtCore.Qt.DisplayRole)
        if '∞' in LSL:
            attributes['LSL'] = -np.inf
        else:
            attributes['LSL'] = float(LSL)

    # LTL
        LTL_item = self.outputParameterModel.item(row, 2)
        LTL = LTL_item.data(QtCore.Qt.DisplayRole)
        if '∞' in LTL:
            attributes['LTL'] = -np.inf
        elif LTL == '':
            attributes['LTL'] = np.nan
        else:
            attributes['LTL'] = float(LTL)

    # Nom
        Nom_item = self.outputParameterModel.item(row, 3)
        attributes['Nom'] = float(Nom_item.data(QtCore.Qt.DisplayRole))

    # UTL
        UTL_item = self.outputParameterModel.item(row, 4)
        UTL = UTL_item.data(QtCore.Qt.DisplayRole)
        if '∞' in UTL:
            attributes['UTL'] = +np.inf
        elif UTL == '':
            attributes['UTL'] = np.nan
        else:
            attributes['UTL'] = float(UTL)

    # USL
        USL_item = self.outputParameterModel.item(row, 5)
        USL = USL_item.data(QtCore.Qt.DisplayRole)
        if '∞' in USL:
            attributes['USL'] = np.inf
        else:
            attributes['USL'] = float(USL)

    # multiplier
        multiplier_item = self.outputParameterModel.item(row, 6)
        multiplier = multiplier_item.data(QtCore.Qt.DisplayRole)
        attributes['10ᵡ'] = multiplier if multiplier else attributes['10ᵡ']

    # unit
        unit_item = self.outputParameterModel.item(row, 7)
        attributes['Unit'] = unit_item.data(QtCore.Qt.DisplayRole)

    # format
        fmt_item = self.outputParameterModel.item(row, 8)
        attributes['fmt'] = fmt_item.data(QtCore.Qt.DisplayRole)

        return name, attributes

    def getOutputParameters(self):
        retval = {}
        rows = self.outputParameterModel.rowCount()
        for row in range(rows):
            name, attributes = self.getOutputParameter(row)
            self._update_power_with_correct_value(attributes)
            retval[name] = attributes
        return retval

    def moveOutputParameterUp(self, row):
        selectedIndexes = self.outputParameterView.selectedIndexes()
        selectedRows = set()
        for index in selectedIndexes:
            if index.row() not in selectedRows:
                selectedRows.add(index.row())
        if len(selectedRows) == 1:  # can move only delete one parameter at a time!
            row = list(selectedRows)[0]
            data = self.outputParameterModel.takeRow(row)
            self.outputParameterModel.insertRow(row - 1, data)
            self.outputParameterView.clearSelection()
            self.outputParameterView.selectRow(row - 1)

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
        attributes = {'LSL': -np.inf, 'LTL': np.nan, 'Nom': 0.0, 'UTL': np.nan, 'USL': np.inf, '10ᵡ': '˽', 'Unit': '˽', 'fmt': '.3f'}
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
            self.outputParameterView.setColumnHidden(OUTPUT_FMT_COLUMN_INDEX, True)
        else:
            self.outputParameterFormat.setIcon(qta.icon('mdi.cog-outline', color='orange'))
            self.outputParameterFormatVisible = True
            self.outputParameterFormat.setToolTip('Hide parameter formats')
            self.outputParameterView.setColumnHidden(OUTPUT_FMT_COLUMN_INDEX, False)
        self.tableAdjust(self.outputParameterView, OUTPUT_NAME_COLUMN_INDEX)

    def deleteOutputParameter(self, row):
        selectedIndexes = self.outputParameterView.selectedIndexes()
        selectedRows = set()
        for index in selectedIndexes:
            if index.row() not in selectedRows:
                selectedRows.add(index.row())
        if len(selectedRows) == 1:  # can move only delete one parameter at a time!
            row = list(selectedRows)[0]
            self.outputParameterModel.takeRow(row)
            self.outputParameterView.clearSelection()

    def moveOutputParameterDown(self, row):
        selectedIndexes = self.outputParameterView.selectedIndexes()
        selectedRows = set()
        for index in selectedIndexes:
            if index.row() not in selectedRows:
                selectedRows.add(index.row())
        if len(selectedRows) == 1:  # can move only delete one parameter at a time!
            row = list(selectedRows)[0]
            data = self.outputParameterModel.takeRow(row)
            self.outputParameterModel.insertRow(row + 1, data)
            self.outputParameterView.clearSelection()
            self.outputParameterView.selectRow(row + 1)

    def getDescription(self):
        return self.description.toPlainText().split('\n')

    def descriptionLength(self):
        retval = ''.join(self.getDescription()).replace(' ', '').replace('\t', '')
        return len(retval)

    def verify(self):
        self.Feedback.setText("")
        if self.read_only:
            dependant_programs = self.project_info.get_dependant_objects_for_test(self.TestName.text())
            # we don't care if the test not used yet !
            if len(dependant_programs):
                text = "edit test can invalidate the following test-program(s):\n"
                for _, programs in dependant_programs.items():
                    for program in programs:
                        text += f"{ program }"

                    text += ", "

                self.edit_feedback.setText(text)

        # 1. Check that we have a hardware selected
        if self.ForHardwareSetup.text() == '':
            self.Feedback.setText("Select a 'hardware'")

        # 2. Check that we have a base selected
        if self.Feedback.text() == "":
            if self.WithBase.text() == '':
                self.Feedback.setText("Select a 'base'")

        # 3. Check if we have a test name
        if not self.read_only and self.Feedback.text() == "":
            if self.TestName.text() == '':
                self.Feedback.setText("Supply a name for the test")

        # 6. Check if the test name holds the word 'Test' in any form
        if self.Feedback.text() == "":
            test_name = self.TestName.text()
            if not is_valid_test_name(test_name):
                fb = "The test name can not contain the word 'TEST' in any form!"
                self.Feedback.setText(fb)

            # 7. Check if the test name already exists
            if not self.read_only and self._does_test_exist(test_name):
                fb = "test name exists already"
                self.Feedback.setText(fb)

            if keyword.iskeyword(test_name):
                fb = "python keyword should not be used as test name"
                self.Feedback.setText(fb)

        # TODO: Enable again
        # 8. see if we have at least XX characters in the description.
        # if self.Feedback.text() == "":
        #     docstring_length = self.descriptionLength()
        #     print(docstring_length)
        #     if docstring_length < minimal_docstring_length:
        #         self.Feedback.setText(f"Describe the test in at least {minimal_docstring_length} characters (spaces don't count, you have {docstring_length} characters)")

        # 9. Check the input parameters
        if self.Feedback.text() == "":
            self._validate_input_parameters()

        # 10. Check the output parameters
        if self.Feedback.text() == "":
            self._validate_output_parameters()

        if not len(self._get_groups()):
            self.Feedback.setText('make sure to select at least one Group')

        if self.Feedback.text() == "":
            self.OKButton.setEnabled(True)
        else:
            self.OKButton.setEnabled(False)

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
        tests = [test.name for test in self.project_info.get_tests_from_db(self.ForHardwareSetup.text(), self.WithBase.text())]
        if test_name in tests:
            return True

        return False

    def CancelButtonPressed(self):
        self.reject()

    def OKButtonPressed(self):
        test_content = {}
        test_content['name'] = self.TestName.text()
        test_content['type'] = "custom"
        test_content['hardware'] = self.ForHardwareSetup.text()
        test_content['base'] = self.WithBase.text()
        test_content['groups'] = self._get_groups()
        test_content['docstring'] = self.description.toPlainText().split('\n')
        test_content['input_parameters'] = self.getInputParameters()
        test_content['output_parameters'] = self.getOutputParameters()
        test_content['dependencies'] = {}  # TODO: implement this
        if not self.read_only:
            self.project_info.add_custom_test(test_content)
        else:
            update_option = self.__have_parameters_changed(test_content)
            self.project_info.update_custom_test(test_content, update_option)

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

        if not (set(self.project_info.get_groups_for_test(self.TestName.text())) & set(self._get_groups())):
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
            groups = [group.name for group in self.project_info.get_groups_for_test(self.TestName.text())]
            if groups:
                item.setCheckState(QtCore.Qt.Checked if group in groups else QtCore.Qt.Unchecked)
            else:
                item.setCheckState(QtCore.Qt.Unchecked)

            if self._is_test_used_in_group(group):
                item.setEnabled(False)

        self.group_combo.setCurrentIndex(0)
        self.group_combo.blockSignals(False)

    def _is_test_used_in_group(self, group):
        test_name = self.TestName.text()
        sections = [target.split('_')[1] for target in self.project_info.get_available_test_targets(self.ForHardwareSetup.text(), self.WithBase.text(), test_name)]
        return group in sections

    @QtCore.pyqtSlot(int)
    def _group_selected(self, index: int):
        item = self.group_combo.model().item(index, 0)
        is_checked = item.checkState() == QtCore.Qt.Unchecked
        item.setCheckState(QtCore.Qt.Checked if is_checked else QtCore.Qt.Unchecked)

        # keep popup active till user change the focus
        self.group_combo.showPopup()
        self.verify()


def make_blank_definition(project_info):
    '''
    this function creates a blank definition dictionary with 'hardware', 'base' and Type
    '''
    retval = {}
    retval['name'] = ''
    retval['type'] = ''
    retval['hardware'] = project_info.active_hardware
    retval['base'] = project_info.active_base
    retval['docstring'] = []
    retval['input_parameters'] = {'Temperature': {'Shmoo': True, 'Min': -40, 'Default': 25, 'Max': 170, '10ᵡ': '˽', 'Unit': '°C', 'fmt': '.0f'}}
    retval['output_parameters'] = {'new_parameter1': {'LSL': -np.inf, 'LTL': np.nan, 'Nom': 0.0, 'UTL': np.nan, 'USL': np.inf, '10ᵡ': '˽', 'Unit': '˽', 'fmt': '.3f'}}
    retval['dependencies'] = {}
    return retval


def load_definition_from_file(File):
    '''
    this function will load the defintion from an existing (test) file.
    '''
    pass


def new_test_dialog(project_info):
    newTestWizard = TestWizard(project_info)
    newTestWizard.exec_()
    del(newTestWizard)


def edit_test_dialog(project_info, test_content):
    edit = TestWizard(project_info, test_content=test_content, read_only=True)
    edit.exec_()
    del(edit)
