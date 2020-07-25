# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 18:56:05 2019

@author: hoeren
"""
import os
import re

import qdarkstyle
import qtawesome as qta
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import uic

from ATE.spyder.widgets.validation import is_valid_python_class_name
from ATE.spyder.widgets.validation import is_valid_test_name
from ATE.spyder.widgets.validation import valid_float_regex
from ATE.spyder.widgets.validation import valid_python_class_name_regex

minimal_description_length = 80


# rxDeviceName = QtCore.QRegExp(valid_device_name_regex)
# DeviceName_validator = QtGui.QRegExpValidator(rxDeviceName, self)

class TableWidgetItemDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, regex, parent=None):
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.validator = QtGui.QRegExpValidator(QtCore.QRegExp(regex))

    def createEditor(self, parent, option, index):
        line_edit = QtWidgets.QLineEdit(parent)
        line_edit.setValidator(self.validator)
        return line_edit


class TestWizard(QtWidgets.QDialog):

    def __init__(self, project_info, fixed=True):
        super().__init__()

        my_ui = __file__.replace('.py', '.ui')
        if not os.path.exists(my_ui):
            raise Exception("can not find %s" % my_ui)
        uic.loadUi(my_ui, self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        self.project_info = project_info

    # ForHardwareSetup
        existing_hardwares = self.project_info.get_active_hardware_names()
        self.ForHardwareSetup.blockSignals(True)
        self.ForHardwareSetup.clear()
        self.ForHardwareSetup.addItems(existing_hardwares)
        # TODO: fix this
        self.ForHardwareSetup.setCurrentIndex(self.ForHardwareSetup.findText(self.project_info.activeHardware))
        # self.ForHardwareSetup.setCurrentIndex(self.ForHardwareSetup.findText(self.hw_combo.currentText()))
        # self.ForHardwareSetup.setDisabled(fixed)
        self.ForHardwareSetup.setDisabled(False)

        # TODO: no connect ?!? (in case fixed=False!!!)
        self.ForHardwareSetup.blockSignals(False)

    # WithBase
        self.WithBase.blockSignals(True)
        self.WithBase.clear()
        self.WithBase.addItems(['PR', 'FT'])
        # TODO: fix this
        self.WithBase.setCurrentIndex(self.WithBase.findText(self.project_info.activeBase))
        # self.WithBase.setCurrentIndex(self.WithBase.findText(self.base_combo.currentText()))
        # self.WithBase.setDisabled(fixed)
        self.WithBase.setDisabled(False)
        self.WithBase.blockSignals(False)

        from ATE.spyder.widgets.validation import valid_test_name_regex
        rxTestName = QtCore.QRegExp(valid_test_name_regex)
        TestName_validator = QtGui.QRegExpValidator(rxTestName, self)

        self.TestName.setText("")
        self.TestName.setValidator(TestName_validator)
        self.TestName.textChanged.connect(self.verify)

        self.Feedback.setStyleSheet('color: orange')

    # DescriptionTab
        self.description.clear()
        #TODO: add user, time and such to the description by default ?!?
        #TODO: add a line at 80 characters (https://stackoverflow.com/questions/30371613/draw-vertical-lines-on-qtextedit-in-pyqt)
        self.description_length = 0
        self.description.textChanged.connect(self.setDescriptionLength)

    # InputParametersTab
        self.inputParameterMoveUp.setIcon(qta.icon('mdi.arrow-up-bold-box-outline', color='white'))
        self.inputParameterMoveUp.setToolTip('Move selected parameter Up')
        self.inputParameterMoveUp.clicked.connect(self.moveInputParameterUp)

        self.inputParameterAdd.setIcon(qta.icon('mdi.plus-box-outline', color='white'))
        self.inputParameterAdd.setToolTip('Add a parameter')
        self.inputParameterAdd.clicked.connect(self.addInputParameter)

        self.inputParameterUnselect.setIcon(qta.icon('mdi.select-off', color='white'))
        self.inputParameterUnselect.setToolTip('Clear selection')
        self.inputParameterUnselect.clicked.connect(self.unselectInputParameter)

        self.inputParameterMoveDown.setIcon(qta.icon('mdi.arrow-down-bold-box-outline', color='white'))
        self.inputParameterMoveDown.setToolTip('Move selected parameter Down')
        self.inputParameterMoveDown.clicked.connect(self.moveInputParameterDown)

        self.inputParameterDelete.setIcon(qta.icon('mdi.minus-box-outline', color='white'))
        self.inputParameterDelete.setToolTip('Delete selected parameter')
        self.inputParameterDelete.clicked.connect(self.deleteInputParameter)

        self.inputParameterTable.clear()
        self.inputParameterTable.setColumnCount(6)
        self.inputParameterTable.setRowCount(1)
        self.inputParameterTable.setHorizontalHeaderLabels(['Name', 'Min', 'Default', 'Max', '10ᵡ', 'Unit'])


        item_name = QtWidgets.QTableWidgetItem("Temperature")
        item_name.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter) # https://doc.qt.io/qt-5/qt.html#AlignmentFlag-enum
        item_name.setFlags(QtCore.Qt.NoItemFlags) # https://doc.qt.io/qt-5/qt.html#ItemFlag-enum
        item_name.setCheckState(QtCore.Qt.Checked) # https://doc.qt.io/qt-5/qt.html#CheckState-enum
        item_name.setToolTip("Real")
        self.inputParameterTable.setItem(0, 0, item_name)

        item_min = QtWidgets.QTableWidgetItem("-40")
        item_min.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        item_min.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        self.inputParameterTable.setItem(0, 1, item_min)

        item_default = QtWidgets.QTableWidgetItem("+25")
        item_default.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
        item_default.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        self.inputParameterTable.setItem(0, 2, item_default)

        item_max = QtWidgets.QTableWidgetItem("+170")
        item_max.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        item_max.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        self.inputParameterTable.setItem(0, 3, item_max)

        item_multiplier = QtWidgets.QTableWidgetItem('')
        item_multiplier.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        item_multiplier.setFlags(QtCore.Qt.NoItemFlags)
        self.inputParameterTable.setItem(0, 4, item_multiplier)

        item_unit = QtWidgets.QTableWidgetItem("°C")
        item_unit.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        item_unit.setFlags(QtCore.Qt.NoItemFlags)
        self.inputParameterTable.setItem(0, 5, item_unit)

        self.inputParameterTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.inputParameterTable.customContextMenuRequested.connect(self.inputParameterTableContextMenu)
        self.inputParameterTable.cellChanged.connect(self.inputParameterTableCellChanged)
        self.inputParameterTable.itemSelectionChanged.connect(self.inputParameterTableSelectionChanged)










    # OutputParametersTab
        self.outputParameterMoveUp.setIcon(qta.icon('mdi.arrow-up-bold-box-outline', color='orange'))
        self.outputParameterMoveDown.setIcon(qta.icon('mdi.arrow-down-bold-box-outline', color='orange'))
        self.outputParameterAdd.setIcon(qta.icon('mdi.plus-box-outline', color='orange'))
        self.outputParameterDelete.setIcon(qta.icon('mdi.minus-box-outline', color='orange'))
        #Idea: limit the number of output parameters to 9, so we have a decade per test-number,
        #      and the '0' is the FTR 🙂

    # buttons
        self.CancelButton.clicked.connect(self.CancelButtonPressed)
        self.OKButton.clicked.connect(self.OKButtonPressed)
        self.OKButton.setEnabled(False)

        self.verify()
        self.show()

        item = self.inputParameterTable.item(0, 0)
        print(item.text())
        # item.setText('++25') # must come after show()




    def resizeEvent(self, event):
        QtWidgets.QWidget.resizeEvent(self, event)
        self.tableAdjust(self.inputParameterTable)

    def inputParameterTableContextMenu(self, point):
        '''
        here we select which context menu (for input_parameters) we need,
        based on the column where we activated the context menu on, and
        dispatch to the appropriate context menu.
        '''
        self.index = self.inputParameterTable.indexAt(point)
        self.col = self.index.column()
        self.row = self.index.row()

        print(f"({point.x()}, {point.y()})-->[{self.row}, {self.col}]")

        if self.col == 5: # Unit
            if self.row != 0: # not temperature
                menu = QtWidgets.QMenu(self)
                # unitContextMenu
                #    reference to SI : https://en.wikipedia.org/wiki/International_System_of_Units
                #    reference to unicode : https://en.wikipedia.org/wiki/List_of_Unicode_characters
                base_units = [
                    ('s (time - second)',
                     lambda: self.setInputParameterUnit('s','time - second')),
                    ('m (length - meter)',
                     lambda: self.setInputParameterUnit('m', 'length - meter')),
                    ('kg (mass - kilogram)',
                     lambda: self.setInputParameterUnit('kg', 'mass - kilogram')),
                    ('A (electric current - ampères)',
                     lambda: self.setInputParameterUnit('A', 'electric current - ampères')),
                    ('K (temperature - Kelvin)',
                     lambda: self.setInputParameterUnit('K', 'temperature - Kelvin')),
                    ('mol (amount of substance - mole)',
                     lambda: self.setInputParameterUnit('mol', 'amount of substance - mole')),
                    ('cd (luminous intensity - candela)',
                     lambda: self.setInputParameterUnit('cd', 'luminous intensity - candela'))]
                for unit in base_units:
                    item = menu.addAction(unit[0])
                    item.triggered.connect(unit[1])
                menu.addSeparator()

                derived_units = [
                    ('rad (plane angle - radian = m/m)',
                     lambda: self.setInputParameterUnit('rad', 'plane angle - radian = m/m')),
                    ('sr (solid angle - steradian = m²/m²)',
                     lambda: self.setInputParameterUnit('sr', 'solid angle - steradian = m²/m²')),
                    ('Hz (frequency - hertz = s⁻¹)',
                     lambda: self.setInputParameterUnit('Hz', 'frequency - hertz = s⁻¹')),
                    ('N (force, weight - newton = kg⋅m⋅s⁻²)',
                     lambda: self.setInputParameterUnit('N', 'force, weight - newton = kg⋅m⋅s⁻²')),
                    ('Pa ( pressure, stress - pascal = kg⋅m⁻¹⋅s⁻²)',
                     lambda: self.setInputParameterUnit('Pa', 'pressure, stress - pascal = kg⋅m⁻¹⋅s⁻²')),
                    ('J (energy, work, heat - joule = kg⋅m²⋅s⁻² = N⋅m = Pa⋅m³)',
                     lambda: self.setInputParameterUnit('J', 'energy, work, heat - joule = kg⋅m²⋅s⁻² = N⋅m = Pa⋅m³')),
                    ('W (power, radiant flux - watt = kg⋅m²⋅s⁻³ = J/s)',
                     lambda: self.setInputParameterUnit('W', 'power, radiant flux - watt = kg⋅m²⋅s⁻³ = J/s')),
                    ('C (electric charge - coulomb = s⋅A)',
                     lambda: self.setInputParameterUnit('C', 'electric charge - coulomb = s⋅A')),
                    ('V (electric potential, emf - volt = kg⋅m²⋅s⁻³⋅A⁻¹ = W/A = J/C)',
                     lambda: self.setInputParameterUnit('V', 'electric potential, emf - volt = kg⋅m²⋅s⁻³⋅A⁻¹ = W/A = J/C')),
                    ('F (electric capacitance - farad = kg⁻¹⋅m⁻²⋅s⁴⋅A² = C/V)',
                     lambda: self.setInputParameterUnit('F', 'electric capacitance - farad = kg⁻¹⋅m⁻²⋅s⁴⋅A² = C/V')),
                    ('Ω (electric resistance, impedance, reactance - ohm = kg⋅m²⋅s⁻³⋅A⁻² = V/A)',
                     lambda: self.setInputParameterUnit('Ω', 'electric resistance, impedance, reactance - ohm = kg⋅m²⋅s⁻³⋅A⁻² = V/A')),
                    ('S (electric conductance - siemens = kg⁻¹⋅m⁻²⋅s³⋅A² = Ω⁻¹)',
                     lambda: self.setInputParameterUnit('S', 'electric conductance - siemens = kg⁻¹⋅m⁻²⋅s³⋅A² = Ω⁻¹')),
                    ('Wb (magnetic flux - weber = kg⋅m²⋅s⁻²⋅A⁻¹ = V⋅s)',
                     lambda: self.setInputParameterUnit('Wb', 'magnetic flux - weber = kg⋅m²⋅s⁻²⋅A⁻¹ = V⋅s')),
                    ('T (magnetic flux density - tesla = kg⋅s⁻²⋅A⁻¹ = Wb/m²)',
                     lambda: self.setInputParameterUnit('T', 'magnetic flux density - tesla = kg⋅s⁻²⋅A⁻¹ = Wb/m²')),
                    ('H (electric inductance - henry = kg⋅m²⋅s⁻²⋅A⁻² = Wb/A)',
                     lambda: self.setInputParameterUnit('H', 'electric inductance - henry = kg⋅m²⋅s⁻²⋅A⁻² = Wb/A')),
                    ('lm (luminous flux - lumen = cd⋅sr)',
                     lambda: self.setInputParameterUnit('lm', 'luminous flux - lumen = cd⋅sr')),
                    ('lx (illuminance - lux = m⁻²⋅cd = lm/m²)',
                     lambda: self.setInputParameterUnit('lx', 'illuminance - lux = m⁻²⋅cd = lm/m²')),
                    ('Bq (radioactivity - Becquerel = s⁻¹)',
                     lambda: self.setInputParameterUnit('Bq', 'radioactivity - Becquerel = s⁻¹')),
                    ('Gy (absorbed dose - gray = m²⋅s⁻² = J/kg)',
                     lambda: self.setInputParameterUnit('Gy', 'absorbed dose - gray = m²⋅s⁻² = J/kg')),
                    ('Sv (equivalent dose - sievert = m²⋅s⁻² = J/kg)',
                     lambda: self.setInputParameterUnit('Sv', 'equivalent dose - sievert = m²⋅s⁻² = J/kg')),
                    ('kat (catalytic activity - katal = mol⋅s⁻¹)',
                     lambda: self.setInputParameterUnit('kat', 'catalytic activity - katal = mol⋅s⁻¹'))]
                for unit in derived_units:
                    item = menu.addAction(unit[0])
                    item.triggered.connect(unit[1])
                menu.addSeparator()

                alternative_units = [
                    ('°C (temperature - degree Celcius = K - 273.15)',
                     lambda: self.setInputParameterUnit('°C', 'temperature - degree Celcius = K - 273.15')),
                    ('Gs (magnetic flux density - gauss = 10⁻⁴ Tesla)',
                     lambda: self.setInputParameterUnit('Gs', 'magnetic flux density - gauss = 10⁻⁴ Tesla')),
                    ('˽ (no dimension / unit)',
                     lambda: self.setInputParameterUnit('', 'no dimension / unit'))]
                for unit in alternative_units:
                    item = menu.addAction(unit[0])
                    item.triggered.connect(unit[1])

                menu.exec_(QtGui.QCursor.pos())

        elif self.col == 4: # multiplier --> reference = STDF V4.pdf @ page 50 & https://en.wikipedia.org/wiki/Order_of_magnitude
            print("yes, it is a lambda now")
            if self.row != 0: # temperature
                menu = QtWidgets.QMenu(self)
                normal_multipliers = [
                    ('y (yocto=10⁻²⁴)',
                     lambda: self.setInputParameterMultiplier('y', 'yocto=10⁻²⁴')),
                    ('z (zepto=10⁻²¹)',
                     lambda: self.setInputParameterMultiplier('z', 'zepto=10⁻²¹')),
                    ('a (atto=10⁻¹⁸)',
                     lambda: self.setInputParameterMultiplier('a', 'atto=10⁻¹⁸')),
                    ('f (femto=10⁻¹⁵)',
                     lambda: self.setInputParameterMultiplier('f', 'femto=10⁻¹⁵')),
                    ('p (pico=10⁻¹²)',
                     lambda: self.setInputParameterMultiplier('p', 'pico=10⁻¹²')),
                    ('η (nano=10⁻⁹)',
                     lambda: self.setInputParameterMultiplier('η', 'nano=10⁻⁹')),
                    ('μ (micro=10⁻⁶)',
                     lambda: self.setInputParameterMultiplier('μ', 'micro=10⁻⁶')),
                    ('m (mili=10⁻³)',
                     lambda: self.setInputParameterMultiplier('m', 'mili=10⁻³')),
                    ('c (centi=10⁻²)',
                     lambda: self.setInputParameterMultiplier('c', 'centi=10⁻²')),
                    ('d (deci=10⁻¹)',
                     lambda: self.setInputParameterMultiplier('d', 'deci=10⁻¹')),
                    ('˽ (no scaling=10⁰)',
                     lambda: self.setInputParameterMultiplier('', 'no scaling=10⁰')),
                    ('㍲ (deca=10¹)',
                     lambda: self.setInputParameterMultiplier('㍲', 'deca=10¹')),
                    ('h (hecto=10²)',
                     lambda: self.setInputParameterMultiplier('h', 'hecto=10²')),
                    ('k (kilo=10³)',
                     lambda: self.setInputParameterMultiplier('k', 'kilo=10³')),
                    ('M (mega=10⁶)',
                     lambda: self.setInputParameterMultiplier('M', 'mega=10⁶')),
                    ('G (giga=10⁹)',
                     lambda: self.setInputParameterMultiplier('G', 'giga=10⁹')),
                    ('T (tera=10¹²)',
                     lambda: self.setInputParameterMultiplier('T', 'tera=10¹²')),
                    ('P (peta=10¹⁵)',
                     lambda: self.setInputParameterMultiplier('P', 'peta=10¹⁵)')),
                    ('E (exa=10¹⁸)',
                     lambda: self.setInputParameterMultiplier('E', 'exa=10¹⁸')),
                    ('Z (zetta=10²¹)',
                     lambda: self.setInputParameterMultiplier('Z', 'zetta=10²¹')),
                    ('ϒ (yotta=10²⁴)',
                     lambda: self.setInputParameterMultiplier('ϒ', 'yotta=10²⁴'))]
                for multiplier in normal_multipliers:
                    item = menu.addAction(multiplier[0])
                    item.triggered.connect(multiplier[1])
                menu.addSeparator()

                dimensionless_multipliers = [
                    ('ppm (parts per million=ᴺ/₁․₀₀₀․₀₀₀)',
                     lambda: self.setInputParameterMultiplier('ppm', 'parts per million=ᴺ/₁․₀₀₀․₀₀₀')),
                    ('‰ (promille=ᴺ/₁․₀₀₀)',
                     lambda: self.setInputParameterMultiplier('‰', 'promille=ᴺ/₁․₀₀₀')),
                    ('% (percent=ᴺ/₁₀₀)',
                     lambda: self.setInputParameterMultiplier('%', 'percent=ᴺ/₁₀₀')),
                    ('dB (decibel=10·log[P/Pref])',
                     lambda: self.setInputParameterMultiplier('dB', 'decibel=10·log[P/Pref]')),
                    ('dBV (decibel=20·log[V/Vref])',
                     lambda: self.setInputParameterMultiplier('dBV', 'decibel=20·log[V/Vref]'))]
                for multiplier in dimensionless_multipliers:
                    item = menu.addAction(multiplier[0])
                    item.triggered.connect(multiplier[1])

                menu.exec_(QtGui.QCursor.pos())

        elif self.col >= 1 and self.col <= 3: # Min, Default, Max
            if self.row != 0: # not for temperature
                menu = QtWidgets.QMenu(self)

                special_values = [
                    ('+∞', self.setValuePlusInfinite),
                    ('<clear>', self.setValueClear),
                    ('-∞', self.setValueMinusInfinite)]
                for special_value in special_values:
                    item = menu.addAction(special_value[0])
                    item.triggered.connect(special_value[1])

                menu.exec_(QtGui.QCursor.pos())

        elif self.col == 0: # Name
            if self.row != 0: # not for temperature
                menu = QtWidgets.QMenu(self)
                # http://www.cplusplus.com/reference/cstdio/fprintf/
                parameter_types =[
                    ("Real", self.setParameterReal),
                    ("Integer (Decimal - '123...')", self.setParameterDecimal),
                    ("Integer (Hexadecimal - '0xFE...')", self.setParameterHexadecimal),
                    ("Integer (Octal - '0o87...')", self.setParameterOctal),
                    ("Integer (Binary - '0b10...')", self.setParameterBinary)]

                check = qta.icon('mdi.check', color='orange')

                parameter = self.inputParameterTable.item(self.row, self.col)
                parameter_type = parameter.toolTip()

                for type_option in parameter_types:
                    if type_option[0] == parameter_type:
                        item = menu.addAction(check, type_option[0])
                    else:
                        item = menu.addAction(type_option[0])
                    item.triggered.connect(type_option[1])

                menu.exec_(QtGui.QCursor.pos())

    def inputParameterTableCellChanged(self, row, col):
        '''
        if one of the cells in self.inputParameterTable is changed, this
        routine is called.
        '''
        self.inputParameterTable.blockSignals(True)
        rows = self.inputParameterTable.rowCount()
        if rows == 1:
            self.inputParameterMoveUp.setDisabled(True)
            self.inputParameterMoveDown.setDisabled(True)
            self.inputParameterDelete.setDisabled(True)
        elif rows == 2:
            self.inputParameterMoveUp.setDisabled(True)
            self.inputParameterMoveDown.setDisabled(True)
            self.inputParameterDelete.setEnabled(True)
        else:
            self.inputParameterMoveUp.setEnabled(True)
            self.inputParameterMoveDown.setEnabled(True)
            self.inputParameterDelete.setEnabled(True)
        selected_items = len(self.inputParameterTable.selectedItems())
        if selected_items == 0:
            self.inputParameterUnselect.setDisabled(True)
        else:
            self.inputParameterUnselect.setEnabled(True)

        item = self.inputParameterTable.item(row, col)



        #TODO: validation on cells

        self.tableAdjust(self.inputParameterTable)
        self.inputParameterTable.blockSignals(False)

    def inputParameterTableSelectionChanged(self):
        print('selection changed')
        selected_items = len(self.inputParameterTable.selectedItems())
        if selected_items == 0:
            self.inputParameterUnselect.setDisabled(True)
        else:
            self.inputParameterUnselect.setEnabled(True)


    def setInputParameterType(self, Type):
        pass

    # def setUnitReal(self):
    #     self.setUnit('𝓡', 'unitless real number')

    # def setUnitInteger(self):
    #     self.setUnit('№', 'unitless integer number')

    # def setParameterReal(self):
    #     print("self.setParameterReal")

    # def setParameterDecimal(self):
    #     print("self.setParameterDecimal")

    # def setParameterHexadecimal(self):
    #     print("self.setParameterHexadecimal")

    # def setParameterOctal(self):
    #     print("self.setParameterOctal")

    # def setParameterBinary(self):
    #     print("self.setParameterBinary")

    def setInputParameterValue(self, value):
        pass

    # def setValuePlusInfinite(self):
    #     for item in self.inputParameterTable.selectedItems():
    #         if item.column()==3 and item.row()!=0: # the only the maximum value can be set to +Inf, but not the temperature!
    #             item.setText('+∞')

    # def setValueClear(self):
    #     for item in self.inputParameterTable.selectedItems():
    #         if item.column() in [1,2,3] and item.row()!=0: # values can be cleared in bulk, but not for temperature
    #             item.setText('')

    # def setValueMinusInfinite(self):
    #     for item in self.inputParameterTable.selectedItems():
    #         if item.column()==1 and item.row()!=0: # the only the minimum value can be set to -Inf, but not the temperature!
    #             item.setText('-∞')

    def setInputParameterMultiplier(self, text, tooltip):
        for item in self.inputParameterTable.selectedItems():
            if item.column() == 4:
                item.setText(text)
                item.setToolTip(tooltip)

    def setInputParameterUnit(self, text, tooltip):
        for item in self.inputParameterTable.selectedItems():
            if item.column() == 5:
                item.setText(text)
                item.setToolTip(tooltip)














    def moveInputParameterUp(self):
        selected_items = self.inputParameterTable.selectedItems()
        selected_rows = []
        for item in selected_items:
            if item.row() not in selected_rows:
                selected_rows.append(item.row())
        if len(selected_rows) == 1: # can move only one row up at a time!
            selected_row = selected_rows[0]
            if selected_row == 0: # temperature
                print(f"Can not move-up 'Temperature' any further!")
            elif selected_row == 1:
                pname = self.inputParameterTable.item(selected_row, 0).text()
                print(f"Can not move-up '{pname}' any further as 'Temperature' is always the first input parameter!")
            else:
                print(f"move row {selected_row} one place up")
        else:
            print(f"Can move-up only one row at a time.")

    def addInputParameter(self):
        new_row = self.inputParameterTable.rowCount()

        existing_parameters = []
        shmooed_parameters = []
        for item_row in range(new_row):
            item = self.inputParameterTable.item(item_row, 0)
            existing_parameters.append(item.text())
            if item.checkState() == QtCore.Qt.Checked:
                shmooed_parameters.append(item.text())

        existing_parameter_indexes = []
        for existing_parameter in existing_parameters:
            if existing_parameter.startswith('new_parameter'):
                existing_index = int(existing_parameter.split('new_parameter')[1])
                if existing_index not in existing_parameter_indexes:
                    existing_parameter_indexes.append(existing_index)

        if len(existing_parameter_indexes) == 0:
            new_parameter_index = 1
        else:
            new_parameter_index = max(existing_parameter_indexes)+1

        reply = QtWidgets.QMessageBox.Yes
        print(f"shmooed parameters = {len(shmooed_parameters)}")
        if len(shmooed_parameters) >= 3:
            reply = QtWidgets.QMessageBox.question(
                self,
                'Warning',
                'It is not advisable to have more than 3 input parameters,\nbecause shmooing will become a nightmare.\n\ndo you still want to continue?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            self.inputParameterTable.insertRow(new_row)

            item_name = QtWidgets.QTableWidgetItem(f"new_parameter{new_parameter_index}")
            item_name.setToolTip("Real")
            item_name.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            item_name.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled) # | QtCore.Qt.ItemIsUserCheckable
            item_name.setCheckState(QtCore.Qt.Unchecked)
            self.inputParameterTable.setItem(new_row, 0, item_name)

            item_min = QtWidgets.QTableWidgetItem("-∞")
            item_min.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            item_min.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
            self.inputParameterTable.setItem(new_row, 1, item_min)

            item_default = QtWidgets.QTableWidgetItem("0")
            item_default.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
            item_default.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
            self.inputParameterTable.setItem(new_row, 2, item_default)

            item_max = QtWidgets.QTableWidgetItem("+∞")
            item_max.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            item_max.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
            self.inputParameterTable.setItem(new_row, 3, item_max)

            item_multiplier = QtWidgets.QTableWidgetItem('')
            item_multiplier.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            item_multiplier.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
            self.inputParameterTable.setItem(new_row, 4, item_multiplier)

            item_unit = QtWidgets.QTableWidgetItem('!')
            item_unit.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            item_unit.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
            self.inputParameterTable.setItem(new_row, 5, item_unit)

    def unselectInputParameter(self):
        self.inputParameterTable.clearSelection()

    def deleteInputParameter(self):
        selected_items = self.inputParameterTable.selectedItems()
        selected_rows = []
        for item in selected_items:
            if item.row() not in selected_rows:
                selected_rows.append(item.row())
        if len(selected_rows) == 1: # can move only delete one parameter at a time!
            if selected_rows[0] == 0: # can not remove the temperature!
                print(f"Can not delete 'temperature', it is an obligatory parameter !")
            else:
                print(f"remove row {selected_rows[0]}")

    def moveInputParameterDown(self):
        selected_items = self.inputParameterTable.selectedItems()
        last_row = self.inputParameterTable.rowCount()-1
        selected_rows = []
        for item in selected_items:
            if item.row() not in selected_rows:
                selected_rows.append(item.row())
        if len(selected_rows) == 1: # can move only one row down at a time!
            selected_row = selected_rows[0]
            if selected_row == 0: # temperature
                print(f"Can not move-down 'Temperature', it needs to be the first input parameter!")
            elif selected_row == last_row:
                pname = self.inputParameterTable.item(selected_row, 0).text()
                print(f"Can not move-down '{pname}' any further!")
            else:
                print(f"move row {selected_row} one place up")
        else:
            print(f"Can move-down only one row at a time.")





    def setDescriptionLength(self):
        self.description_length = len(self.description.toPlainText().replace(' ','').replace('\n', '').replace('\t', ''))
        print(f"{self.description_length}/{minimal_description_length}")
        self.verify()

    def tableAdjust(self, Table):
        columns = Table.columnCount()
        width = 0
        for column in range(1, columns):
            Table.resizeColumnToContents(column)
            width+=Table.columnWidth(column)
        available_width = Table.geometry().width()
        Table.setColumnWidth(0, available_width-width-Table.verticalHeader().width()-Table.columnCount())

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

        # 4. Check if the test name is a valid python class name (covered by LineEdit, but it doesn't hurt)
        if self.Feedback.text() == "":
            if not is_valid_python_class_name(self.TestName.text()):
                fb = f"The test name '{self.TestName.text()}' is not a valid python class name. "
                fb += "(It doesn't comply to RegEx '{valid_python_class_name_regex}'"
                self.Feedback.setText(fb)

        # 5. Check if the test name holds an underscore (useless, as covered by the LineEdit, but it doesn't hurt)
        if self.Feedback.text() == "":
            if '_' in self.TestName.text():
                fb = f"The usage of underscore(s) is disallowed!"
                self.Feedback.setText(fb)

        # 6. Check if the test name holds the word 'Test' in any form
        if self.Feedback.text() == "":
            if not is_valid_test_name(self.TestName.text()):
                fb = "The test name can not contain the word 'TEST' in any form!"
                self.Feedback.setText(fb)

        # 7. Check if the test name already exists
        if self.Feedback.text() == "":
            existing_tests = self.project_info.get_tests_from_files(
                self.ForHardwareSetup.currentText(),
                self.WithBase.currentText())
            if self.TestName.text() in existing_tests:
                self.Feedback.setText("Test already exists!")

        # 8. see if we have at least XX characters in the description.
        if self.Feedback.text() == "":
            self.description_length = len(self.description.toPlainText().replace(' ','').replace('\n', '').replace('\t', ''))
            if self.description_length < minimal_description_length:
                self.Feedback.setText(f"Describe the test in at least {minimal_description_length} characters (spaces don't count, you have {self.description_length} characters)")

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
        self.accept()

    def OKButtonPressed(self):
        name = self.TestName.text()
        hardware = self.ForHardwareSetup.currentText()
        base = self.WithBase.currentText()
        test_data = {'input_parameters' : {},
                     'output_parameters' : {}}
        test_type = "custom"

        self.project_info.add_test(name, hardware, base, test_type, test_data)
        self.accept()

def new_test_dialog(project_info):
    newTestWizard = TestWizard(project_info)
    newTestWizard.exec_()
    del(newTestWizard)

if __name__ == '__main__':
    import sys, qdarkstyle
    from ATE.spyder.widgets.actions.dummy_main import DummyMainWindow

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    dummyMainWindow = DummyMainWindow()
    dialog = NewTestWizard(dummyMainWindow)
    dummyMainWindow.register_dialog(dialog)
    sys.exit(app.exec_())
