# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 18:56:05 2019

@author: hoeren
"""
import os
import re

from ATE.org.validation import is_valid_test_name, is_valid_python_class_name, valid_python_class_name_regex

from PyQt5 import QtCore, QtGui, QtWidgets, uic


minimal_description_length = 80


class NewTestWizard(QtWidgets.QDialog):

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
        self.ForHardwareSetup.setCurrentIndex(self.ForHardwareSetup.findText(self.project_info.active_hardware))
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
        self.WithBase.setCurrentIndex(self.WithBase.findText(self.project_info.active_base))
        # self.WithBase.setCurrentIndex(self.WithBase.findText(self.base_combo.currentText()))
        # self.WithBase.setDisabled(fixed)
        self.WithBase.setDisabled(False)
        self.WithBase.blockSignals(False)

        from ATE.org.validation import valid_test_name_regex
        rxTestName = QtCore.QRegExp(valid_test_name_regex)
        TestName_validator = QtGui.QRegExpValidator(rxTestName, self)

        self.TestName.setText("")
        self.TestName.setValidator(TestName_validator)
        self.TestName.textChanged.connect(self._verify)

        self.Feedback.setStyleSheet('color: orange')

    # DescriptionTab
        self.description.clear()
        #TODO: add user, time and such to the description by default ?!?
        self.description_length = 0
        self.description.textChanged.connect(self.setDescriptionLength)
        
    # InputParametersTab
        self.inputParameterMoveUp.setIcon(qta.icon('mdi.arrow-up-bold-box-outline', color='orange'))
        self.inputParameterMoveUp.clicked.connect(self.moveInputParameterUp)
        
        self.inputParameterMoveDown.setIcon(qta.icon('mdi.arrow-down-bold-box-outline', color='orange'))
        self.inputParameterMoveDown.clicked.connect(self.moveInputParameterDown)
        
        self.inputParameterAdd.setIcon(qta.icon('mdi.plus-box-outline', color='orange'))
        self.inputParameterAdd.clicked.connect(self.addInputParameter)
        
        self.inputParameterDelete.setIcon(qta.icon('mdi.minus-box-outline', color='orange'))
        self.inputParameterDelete.clicked.connect(self.deleteInputParameter)

        self.inputParameterTable.clear()
        self.inputParameterTable.setColumnCount(6)
        self.inputParameterTable.setRowCount(1)
        self.inputParameterTable.setHorizontalHeaderLabels(['Name', 'Min', 'Default', 'Max', '10ᵡ', 'Unit'])
        self.inputParameterTable.resizeColumnToContents(5)
        self.inputParameterTable.resizeColumnToContents(4)
        self.inputParameterTable.resizeColumnToContents(3)
        self.inputParameterTable.resizeColumnToContents(2)
        self.inputParameterTable.resizeColumnToContents(1)


        item_name = QtWidgets.QTableWidgetItem("Temperature")
        item_name.setFlags(item_name.flags() & QtCore.Qt.ItemIsSelectable & QtCore.Qt.ItemIsEditable)
        item_name.setToolTip("Real")
        self.inputParameterTable.setItem(0,0,item_name)

        item_min = QtWidgets.QTableWidgetItem("-40")
        item_min.setTextAlignment(QtCore.Qt.AlignCenter)
        self.inputParameterTable.setItem(0,1,item_min)

        item_default = QtWidgets.QTableWidgetItem("+25")
        item_default.setTextAlignment(QtCore.Qt.AlignCenter)
        self.inputParameterTable.setItem(0,2,item_default)

        item_max = QtWidgets.QTableWidgetItem("+170")
        item_max.setTextAlignment(QtCore.Qt.AlignCenter)
        self.inputParameterTable.setItem(0,3,item_max)

        item_multiplier = QtWidgets.QTableWidgetItem('')
        item_multiplier.setFlags(item_multiplier.flags() & QtCore.Qt.ItemIsSelectable & QtCore.Qt.ItemIsEditable)
        item_multiplier.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.inputParameterTable.setItem(0,4,item_multiplier)

        item_unit = QtWidgets.QTableWidgetItem("°C")
        item_unit.setFlags(item_unit.flags() & QtCore.Qt.ItemIsSelectable & QtCore.Qt.ItemIsEditable)
        item_unit.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.inputParameterTable.setItem(0,5,item_unit)

        self.inputParameterTable.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.inputParameterTable.customContextMenuRequested.connect(self.input_parameters_context_menu_manager)
        self.inputParameterTable.cellChanged.connect(self.inputParameterCellChanged)
        
        #Idea: limit the number of input parameters to 3, as shmoo-ing on 3 parameters is still
        #      manageable for a human (3D), but more is not ...




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

        self._verify()
        self.show()

    def input_parameters_context_menu_manager(self, point):
        '''
        here we select which context menu (for input_parameters) we need,
        based on the column where we activated the context menu on, and 
        dispatch to the appropriate context menu.
        '''
        self.index = self.inputParameterTable.indexAt(point)
        self.col = self.index.column()
        self.row = self.index.row()

        print(f"({point.x()}, {point.y()})-->[{self.row}, {self.col}] = ", end='')

        if self.col == 5: # Unit
            if self.row != 0: # not temperature
                menu = QtWidgets.QMenu(self)
                # unitContextMenu
                #    reference to SI : https://en.wikipedia.org/wiki/International_System_of_Units
                #    reference to unicode : https://en.wikipedia.org/wiki/List_of_Unicode_characters
                base_units = [
                    ('s (time - second)', self.setUnitSecond),
                    ('m (length - meter)', self.setUnitMeter),
                    ('kg (mass - kilogram)', self.setUnitKilogram),
                    ('A (electric current - ampères)', self.setUnitAmperes),
                    ('K (temperature - Kelvin)', self.setUnitKelvin),
                    ('mol (amount of substance - mole)', self.setUnitMole),
                    ('cd (luminous intensity - candela)', self.setUnitCandela)]
                for unit in base_units:
                    item = menu.addAction(unit[0])
                    item.triggered.connect(unit[1])
                menu.addSeparator()
    
                derived_units = [
                    ('rad (plane angle - radian = m/m)', self.setUnitRadian),
                    ('sr (solid angle - steradian = m²/m²)', self.setUnitSteradian),
                    ('Hz (frequency - hertz = s⁻¹)', self.setUnitHertz),
                    ('N (force, weight - newton = kg⋅m⋅s⁻²)', self.setUnitNewton),
                    ('Pa ( pressure, stress - pascal = kg⋅m⁻¹⋅s⁻²)', self.setUnitPascal),
                    ('J (energy, work, heat - joule = kg⋅m²⋅s⁻² = N⋅m = Pa⋅m³)', self.setUnitJoule),
                    ('W (power, radiant flux - watt = kg⋅m²⋅s⁻³ = J/s)', self.setUnitWatt),
                    ('C (electric charge - coulomb = s⋅A)', self.setUnitCoulomb),
                    ('V (electric potential, emf - volt = kg⋅m²⋅s⁻³⋅A⁻¹ = W/A = J/C)', self.setUnitVolt),
                    ('F (electric capacitance - farad = kg⁻¹⋅m⁻²⋅s⁴⋅A² = C/V)', self.setUnitFarad),
                    ('Ω (electric resistance, impedance, reactance - ohm = kg⋅m²⋅s⁻³⋅A⁻² = V/A)', self.setUnitOhm),
                    ('S (electric conductance - siemens = kg⁻¹⋅m⁻²⋅s³⋅A² = Ω⁻¹)', self.setUnitSiemens),
                    ('Wb (magnetic flux - weber = kg⋅m²⋅s⁻²⋅A⁻¹ = V⋅s)', self.setUnitWeber),
                    ('T (magnetic flux density - tesla = kg⋅s⁻²⋅A⁻¹ = Wb/m²)', self.setUnitTesla),
                    ('H (electric inductance - henry = kg⋅m²⋅s⁻²⋅A⁻² = Wb/A)', self.setUnitHenry),
                    ('lm (luminous flux - lumen = cd⋅sr)', self.setUnitLumen),
                    ('lx (illuminance - lux = m⁻²⋅cd = lm/m²)', self.setUnitLux),
                    ('Bq (radioactivity - Becquerel = s⁻¹)', self.setUnitBecquerel),
                    ('Gy (absorbed dose - gray = m²⋅s⁻² = J/kg)', self.setUnitGray),
                    ('Sv (equivalent dose - sievert = m²⋅s⁻² = J/kg)', self.setUnitSievert),
                    ('kat (catalytic activity - katal = mol⋅s⁻¹)', self.setUnitKatal)]
                for unit in derived_units:
                    item = menu.addAction(unit[0])
                    item.triggered.connect(unit[1])
                menu.addSeparator()
    
                alternative_units = [
                    ('°C (temperature - degree Celcius = K - 273.15)', self.setUnitCelcius),
                    ('Gs (magnetic flux density - gauss = 10⁻⁴ Tesla)', self.setUnitGauss),
                    ('˽ (no dimension / unit)', self.setUnitDimensionless)]
                for unit in alternative_units:
                    item = menu.addAction(unit[0])
                    item.triggered.connect(unit[1])
                
                menu.exec_(QtGui.QCursor.pos())
                
        elif self.col == 4: # multiplier --> reference = STDF V4.pdf @ page 50 & https://en.wikipedia.org/wiki/Order_of_magnitude
            if self.row != 0: # temperature
                menu = QtWidgets.QMenu(self)
                normal_multipliers = [
                    ('y (yocto=10⁻²⁴)', self.setMultiplierYocto),
                    ('z (zepto=10⁻²¹)', self.setMultiplierZepto),
                    ('a (atto=10⁻¹⁸)', self.setMultiplierAtto),
                    ('f (femto=10⁻¹⁵)', self.setMultiplierFemto),
                    ('p (pico=10⁻¹²)', self.setMultiplierPico),
                    ('η (nano=10⁻⁹)', self.setMultiplierNano),
                    ('μ (micro=10⁻⁶)', self.setMultiplierMicro),
                    ('m (mili=10⁻³)', self.setMultiplierMili),
                    ('c (centi=10⁻²)', self.setMultiplierCenti),
                    ('d (deci=10⁻¹)', self.setMultiplierDeci),
                    ('˽ (no scaling=10⁰)', self.setMultiplierNone),
                    ('㍲ (deca=10¹)', self.setMultiplierDeca),
                    ('h (hecto=10²)', self.setMultiplierHecto),
                    ('k (kilo=10³)', self.setMultiplierKilo),
                    ('M (mega=10⁶)', self.setMultiplierMega),
                    ('G (giga=10⁹)', self.setMultiplierGiga),
                    ('T (tera=10¹²)', self.setMultiplierTera),
                    ('P (peta=10¹⁵)', self.setMultiplierPeta),
                    ('E (exa=10¹⁸)', self.setMultiplierExa),
                    ('Z (zetta=10²¹)', self.setMultiplierZetta),
                    ('ϒ (yotta=10²⁴)', self.setMultiplierYotta)]
                for multiplier in normal_multipliers:
                    item = menu.addAction(multiplier[0])
                    item.triggered.connect(multiplier[1])
                menu.addSeparator()
    
                dimensionless_multipliers = [
                    ('ppm (parts per million=ᴺ/₁․₀₀₀․₀₀₀)', self.setMultiplierPPM),
                    ('‰ (promille=ᴺ/₁․₀₀₀)', self.setMultiplierPromille),
                    ('% (percent=ᴺ/₁₀₀)', self.setMultiplierPercent),
                    ('dB (decibel=10·log[P/Pref])', self.setMultiplierdB), 
                    ('dBV (decibel=20·log[V/Vref])', self.setMultiplierdBV)]
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
            
        else: # Name
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

# units
    def setUnit(self, text, tooltip):
        for item in self.inputParameterTable.selectedItems():
            if item.column() == 5:
                item.setText(text)
                item.setToolTip(tooltip)

# base units
    def setUnitSecond(self):
        self.setUnit('s', 'time - second')
        
    def setUnitMeter(self):
        self.setUnit('m', 'length - meter')
        
    def setUnitKilogram(self):
        self.setUnit('kg', 'mass - kilogram')

    def setUnitAmperes(self):
        self.setUnit('A', 'electric current - ampères')

    def setUnitKelvin(self):
        self.setUnit('K', 'temperature - Kelvin')

    def setUnitMole(self):
        self.setUnit('mol', 'amount of substance - mole')

    def setUnitCandela(self):
        self.setUnit('cd', 'luminous intensity - candela')

# derived units
    def setUnitRadian(self):
        self.setUnit('rad', 'plane angle - radian = m/m')
        
    def setUnitSteradian(self):        
        self.setUnit('sr', 'solid angle - steradian = m²/m²')
        
    def setUnitHertz(self):
        self.setUnit('Hz', 'frequency - hertz = s⁻¹')
    
    def setUnitNewton(self):            
        self.setUnit('N', 'force, weight - newton = kg⋅m⋅s⁻²')

    def setUnitPascal(self):            
        self.setUnit('Pa', ' pressure, stress - pascal = kg⋅m⁻¹⋅s⁻²')

    def setUnitJoule(self):            
        self.setUnit('J', 'energy, work, heat - joule = kg⋅m²⋅s⁻² = N⋅m = Pa⋅m³')
        
    def setUnitWatt(self):           
        self.setUnit('W', 'power, radiant flux - watt = kg⋅m²⋅s⁻³ = J/s')
 
    def setUnitCoulomb(self):           
        self.setUnit('C', 'electric charge - coulomb = s⋅A')

    def setUnitVolt(self):
        self.setUnit('V', 'electric potential, emf - volt = kg⋅m²⋅s⁻³⋅A⁻¹ = W/A = J/C')

    def setUnitFarad(self):
        self.setUnit('F', 'electric capacitance - farad = kg⁻¹⋅m⁻²⋅s⁴⋅A² = C/V')

    def setUnitOhm(self):
        self.setUnit('Ω', 'electric resistance, impedance, reactance - ohm = kg⋅m²⋅s⁻³⋅A⁻² = V/A')
    
    def setUnitSiemens(self):
        self.setUnit('S', 'electric conductance - siemens = kg⁻¹⋅m⁻²⋅s³⋅A² = Ω⁻¹')
    
    def setUnitWeber(self):
        self.setUnit('Wb', 'magnetic flux - weber = kg⋅m²⋅s⁻²⋅A⁻¹ = V⋅s')
    
    def setUnitTesla(self):
        self.setUnit('T', 'magnetic flux density - tesla = kg⋅s⁻²⋅A⁻¹ = Wb/m²')
    
    def setUnitHenry(self):
        self.setUnit('H', 'electric inductance - henry = kg⋅m²⋅s⁻²⋅A⁻² = Wb/A')
    
    def setUnitLumen(self):
        self.setUnit('lm', 'luminous flux - lumen = cd⋅sr')
    
    def setUnitLux(self):
        self.setUnit('lx', 'illuminance - lux = m⁻²⋅cd = lm/m²')
    
    def setUnitBecquerel(self):
        self.setUnit('Bq', 'radioactivity - Becquerel = s⁻¹')
    
    def setUnitGray(self):
        self.setUnit('Gy', 'absorbed dose - gray = m²⋅s⁻² = J/kg')
    
    def setUnitSievert(self):
        self.setUnit('Sv', 'equivalent dose - sievert = m²⋅s⁻² = J/kg')
    
    def setUnitKatal(self):
        self.setUnit('kat', 'catalytic activity - katal = mol⋅s⁻¹')
            
# alternative units
    def setUnitCelcius(self):
        self.setUnit('°C', 'temperature - degree Celcius = K - 273.15')
        
    def setUnitGauss(self):
        self.setUnit('Gs', 'magnetic flux density - gauss = 10⁻⁴ Tesla')

    def setUnitDimensionless(self):
        self.setUnit('', 'dimensionless')

# special units
    def setUnitReal(self):
        self.setUnit('𝓡', 'unitless real number')

    def setUnitInteger(self):
        self.setUnit('№', 'unitless integer number')

# multipliers
    def setMultiplier(self, text, tooltip):
        for item in self.inputParameterTable.selectedItems():
            if item.column() == 4:
                item.setText(text)
                item.setToolTip(tooltip)
                
    def setMultiplierYocto(self):
        self.setMultiplier('y', 'yocto=10⁻²⁴')                

    def setMultiplierZepto(self):
        self.setMultiplier('z', 'zepto=10⁻²¹')                 

    def setMultiplierAtto(self):
        self.setMultiplier('a', 'atto=10⁻¹⁸')               

    def setMultiplierFemto(self):
        self.setMultiplier('f', 'femto=10⁻¹⁵')

    def setMultiplierPico(self):
        self.setMultiplier('p', 'pico=10⁻¹²')                

    def setMultiplierNano(self):
        self.setMultiplier('η', 'nano=10⁻⁹')         

    def setMultiplierMicro(self):
        self.setMultiplier('μ', 'micro=10⁻⁶')                

    def setMultiplierPPM(self):
        #TODO: remove the unit, as PPM is dimensionless
        self.setMultiplier('ppm', 'parts per million=ᴺ/₁․₀₀₀․₀₀₀')                

    def setMultiplierMili(self):
        self.setMultiplier('m', 'mili=10⁻³')

    def setMultiplierPromille(self):
        #TODO: remove the unit as promille is dimensionless
        self.setMultiplier('‰', 'promille=ᴺ/₁․₀₀₀')

    def setMultiplierPercent(self):
        #TODO: remove the unit as percent is dimensionless
        self.setMultiplier('%', 'percent=ᴺ/₁₀₀')

    def setMultiplierCenti(self):
        self.setMultiplier('c', 'centi=10⁻²')

    def setMultiplierDeci(self):
        self.setMultiplier('d', 'deci=10⁻¹')

    def setMultiplierNone(self):
        self.setMultiplier('', 'no scaling=10⁰') 

    def setMultiplierDeca(self):
        self.setMultiplier('㍲', 'deca=10¹')

    def setMultiplierHecto(self):
        self.setMultiplier('h', 'hecto=10²')

    def setMultiplierKilo(self):
        self.setMultiplier('k', 'kilo=10³')

    def setMultiplierMega(self):
        self.setMultiplier('M', 'mega=10⁶')

    def setMultiplierGiga(self):
        self.setMultiplier('G', 'giga=10⁹')

    def setMultiplierTera(self):
        self.setMultiplier('T', 'tera=10¹²')

    def setMultiplierPeta(self):
        self.setMultiplier('P', 'peta=10¹⁵')

    def setMultiplierExa(self):
        self.setMultiplier('E', 'exa=10¹⁸')

    def setMultiplierZetta(self):
        self.setMultiplier('Z', 'zetta=10²¹') 

    def setMultiplierYotta(self):
        self.setMultiplier('ϒ', 'yotta=10²⁴')     

    def setMultiplierdB(self):
        print(f"{self.row}, {self.col}")
        self.setMultiplier('dB', 'decibel=10·log[P/Pref]')
        self.setUnit('W', 'power, radiant flux - watt = kg⋅m²⋅s⁻³ = J/s')        
        
    def setMultiplierdBV(self):
        self.setMultiplier('dBV', 'decibel=20·log[V/Vref]')
        self.setUnit('V', 'electric potential, emf - volt = kg⋅m²⋅s⁻³⋅A⁻¹ = W/A = J/C')

    def setValuePlusInfinite(self):
        for item in self.inputParameterTable.selectedItems():
            if item.column()==3 and item.row()!=0: # the only the maximum value can be set to +Inf, but not the temperature!
                item.setText('+∞')

    def setValueClear(self):
        for item in self.inputParameterTable.selectedItems():
            if item.column() in [1,2,3] and item.row()!=0: # values can be cleared in bulk, but not for temperature
                item.setText('')
                
    def setValueMinusInfinite(self):
        for item in self.inputParameterTable.selectedItems():
            if item.column()==1 and item.row()!=0: # the only the minimum value can be set to -Inf, but not the temperature!
                item.setText('-∞')








    def setParameterReal(self):
        print("self.setParameterReal")

    def setParameterDecimal(self):
        print("self.setParameterDecimal")
        
    def setParameterHexadecimal(self):
        print("self.setParameterHexadecimal")

    def setParameterOctal(self):
        print("self.setParameterOctal")

    def setParameterBinary(self):
        print("self.setParameterBinary")
  





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

    def addInputParameter(self):
        new_row = self.inputParameterTable.rowCount()
        
        existing_parameters = []
        for item_row in range(new_row):
            item = self.inputParameterTable.item(item_row, 0)
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
            new_parameter_index = max(existing_parameter_indexes)+1            

        reply = QtWidgets.QMessageBox.Yes
        if new_row >= 3:
            reply = QtWidgets.QMessageBox.question(
                self, 
                'Warning', 
                'It is not advisable to have more than 3 input parameters,\nbecause shmooing will become a nightmare.\n\ndo you still want to continue?', 
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, 
                QtWidgets.QMessageBox.No)
        
        if reply == QtWidgets.QMessageBox.Yes:
            self.inputParameterTable.insertRow(new_row)
        
            item_name = QtWidgets.QTableWidgetItem(f"new_parameter{new_parameter_index}")
            item_name.setFlags(item_name.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable)
            item_name.setToolTip("Real")
            self.inputParameterTable.setItem(new_row, 0, item_name)
    
            item_min = QtWidgets.QTableWidgetItem("-∞")
            item_min.setTextAlignment(QtCore.Qt.AlignCenter)
            self.inputParameterTable.setItem(new_row, 1, item_min)
    
            item_default = QtWidgets.QTableWidgetItem("0")
            item_default.setTextAlignment(QtCore.Qt.AlignCenter)
            self.inputParameterTable.setItem(new_row, 2, item_default)
    
            item_max = QtWidgets.QTableWidgetItem("+∞")
            item_max.setTextAlignment(QtCore.Qt.AlignCenter)
            self.inputParameterTable.setItem(new_row, 3, item_max)
    
            item_multiplier = QtWidgets.QTableWidgetItem('')
            item_multiplier.setFlags(item_multiplier.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable)
            item_multiplier.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.inputParameterTable.setItem(new_row, 4, item_multiplier)
    
            item_unit = QtWidgets.QTableWidgetItem("?")
            item_unit.setFlags(item_unit.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable)
            item_unit.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.inputParameterTable.setItem(new_row, 5, item_unit)

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

    def inputParameterCellChanged(self):
        col = self.inputParameterTable.currentColumn()
        rows = self.inputParameterTable.rowCount()
        for row in range(rows):
            item = self.inputParameterTable.item(row, col)
            if col in [1,2,3]:
                item.setTextAlignment(QtCore.Qt.AlignCenter)
            elif col == 4:
                item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            elif col == 5:
                self.inputParameterTable.blockSignals(True)
                item.setFlags(item.flags() & QtCore.Qt.ItemIsSelectable & QtCore.Qt.ItemIsEditable)
                self.inputParameterTable.blockSignals(False)

    def setDescriptionLength(self):
        self.description_length = len(self.description.toPlainText().replace(' ','').replace('\n', '').replace('\t', ''))
        print(f"{self.description_length}/{minimal_description_length}")
        self._verify()

    def _verify(self):
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
        test_data = {'input_parameters': {},
                     'output_parameters': {}}
        test_type = "custom"

        self.project_info.add_test(name, hardware, base, test_type, test_data)
        self.accept()


def new_test_dialog(project_info):
    newTestWizard = NewTestWizard(project_info)
    newTestWizard.exec_()
    del(newTestWizard)
