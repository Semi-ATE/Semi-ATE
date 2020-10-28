# -*- coding: utf-8 -*-
'''
Created on Aug 20, 2019

@author: hoeren
'''
import os

import qdarkstyle
import qtawesome as qta
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from ATE.Data.Formats.register_map.utils.regedit.MainWindow import Ui_mainWindow
from ATE.Data.Formats.register_map.utils.varia import register_map_load
from ATE.Data.Formats.register_map.utils.varia import register_map_save
from ATE.Data.Formats.register_map.utils.varia import register_maps_in_directory
from ATE.Data.utils.varia import is_binar
from ATE.Data.utils.varia import is_decimal
from ATE.Data.utils.varia import is_hexadecimal
from ATE.Data.utils.varia import is_octal

style = qdarkstyle.load_stylesheet_pyqt5()

__default_word_size__ = 8 # bits
__default_address_size__ = 8 # bits
__default_format__ = "{0:d} Bit{1:s}"

class MainWindow(Ui_mainWindow):

    def adjustUI(self):
        self.debug = True
        # register maps
        self.working_directory = os.getcwd()
        self.directoryLineEdit.setText(self.working_directory)
        self.changeDirectoryPushButton.setIcon(qta.icon('mdi.dots-horizontal', color='white', scale_factor=0.6))
        self.changeDirectoryPushButton.pressed.connect(self.changeDirectoryWithDialog)
        self.directoryLineEdit.editingFinished.connect(self.changeDirectoryWithLineEdit)
        self.registermapComboBox.setEditable(True)
        self.registermapComboBox.currentIndexChanged.connect(self.registermapChanged)
        self.registermapComboBox.lineEdit().editingFinished.connect(self.registermapRenamed)
        self.removeRegistermapPushButton.setIcon(qta.icon('mdi.minus-box-outline', color='white', scale_factor=0.6))
        self.removeRegistermapPushButton.pressed.connect(self.removeRegistermap)
        self.copyRegistermapPushButton.setIcon(qta.icon('mdi.content-copy', color='white', scale_factor=0.6))
        self.copyRegistermapPushButton.pressed.connect(self.copyRegistermap)
        self.exportRegistermapPushButton.setIcon(qta.icon('mdi.export', color='white', scale_factor=0.6))
        self.exportRegistermapPushButton.pressed.connect(self.exportRegistermap)
        self.saveAllPushButton.setIcon(qta.icon('mdi.content-save-all', color='white', scale_factor=0.6))
        self.saveAllPushButton.pressed.connect(self.saveAllRegistermaps)
        self.saveRegistermapPushButton.setIcon(qta.icon('mdi.content-save', color='white', scale_factor=0.6))
        self.saveRegistermapPushButton.pressed.connect(self.saveRegistermap)
        self.importRegistermapPushButton.setIcon(qta.icon('mdi.import', color='white', scale_factor=0.6))
        self.importRegistermapPushButton.pressed.connect(self.importRegistermap)
        self.addRegistermapPushButton.setIcon(qta.icon('mdi.plus-box-outline', color='white', scale_factor=0.6))
        self.addRegistermapPushButton.pressed.connect(self.addRegistermap)

        # register map
        self.registersListWidget.currentTextChanged.connect(self.registerChanged)
        self.removeRegisterPushButton.setIcon(qta.icon('mdi.minus-box-outline', color='white', scale_factor=0.6))
        self.removeRegisterPushButton.pressed.connect(self.removeRegister)
        self.addRegisterPushButton.setIcon(qta.icon('mdi.plus-box-outline', color='white', scale_factor=0.6))
        self.addRegisterPushButton.pressed.connect(self.addRegister)
        self.addressSizeLineEdit.editingFinished.connect(self.addressSizeChanged)
        self.wordSizeLineEdit.editingFinished.connect(self.wordSizeChanged)
        self.decimalRadioButton.clicked.connect(self.setRepresentation)
        self.hexadecimalRadioButton.clicked.connect(self.setRepresentation)
        self.octalRadioButton.clicked.connect(self.setRepresentation)
        self.binaryRadioButton.clicked.connect(self.setRepresentation)
        self.decimalRadioButton.setChecked(True)
        self.format = __default_format__

        # register
        self.registerNameLineEdit.editingFinished.connect(self.registerRenamed)
        self.registerDescriptionLineEdit.editingFinished.connect(self.descriptionChanged)
        self.registerOffsetSpinBox.valueChanged.connect(self.offsetChanged)
        self.registerWordsSpinBox.valueChanged.connect(self.wordsChanged)
        self.registerSliceLineEdit.editingFinished.connect(self.sliceChanged)
        self.registerAccessComboBox.currentTextChanged.connect(self.accessChanged)
        self.registerDefaultLineEdit.editingFinished.connect(self.defaultChanged)
        self.registerPresetsTableWidget.cellChanged.connect(self.presetChanged)

        self.registerPresetsRemovePushButton.setIcon(qta.icon('mdi.minus-box-outline', color='white', scale_factor=0.6))
        self.registerPresetsRemovePushButton.pressed.connect(self.removePreset)
        self.registerPresetsAddPushButton.setIcon(qta.icon('mdi.plus-box-outline', color='white', scale_factor=0.6))
        self.registerPresetsAddPushButton.pressed.connect(self.addPreset)

        self.initialization = True
        self.changedDirectorySettings()

    def addressSizeChanged(self):
        new_address_size = self.addressSizeLineEdit.text().strip().split()[0]
        if is_binar(new_address_size):
            self.regmaps[self.active_regmap]['address_size'] = int(new_address_size, 2)
        elif is_hexadecimal(new_address_size):
            self.regmaps[self.active_regmap]['address_size'] = int(new_address_size, 16)
        elif is_octal(new_address_size):
            self.regmaps[self.active_regmap]['address_size'] = int(new_address_size, 8)
        elif is_decimal(new_address_size):
            self.regmaps[self.active_regmap]['address_size'] = int(new_address_size)
        self.registermapUpdate()

    def wordSizeChanged(self):
        new_word_size = self.wordSizeLineEdit.text().strip().split()[0]
        if is_binar(new_word_size):
            self.regmaps[self.active_regmap]['word_size'] = int(new_word_size, 2)
        elif is_hexadecimal(new_word_size):
            self.regmaps[self.active_regmap]['word_size'] = int(new_word_size, 16)
        elif is_octal(new_word_size):
            self.regmaps[self.active_regmap]['word_size'] = int(new_word_size, 8)
        elif is_decimal(new_word_size):
            self.regmaps[self.active_regmap]['word_size'] = int(new_word_size)
        self.registermapUpdate()

    def setRepresentation(self):
        if self.decimalRadioButton.isChecked():
            self.format = "{0:d} Bit{1:s}"
        elif self.hexadecimalRadioButton.isChecked():
            self.format = "0x{0:X} Bit{1:s}"
        elif self.octalRadioButton.isChecked():
            self.format = "0o{0:o} Bit{1:s}"
        else: # binary
            self.format = "0b{0:b} Bit{1:s}"
        self.registermapUpdate()

    def registermapUpdate(self):
        self.active_regmap = self.registermapComboBox.currentText()
        print("self.active_regmap = '%s'" % self.active_regmap)






        if 'address_size' in self.regmaps[self.active_regmap]:
            Size = self.regmaps[self.active_regmap]['address_size']
            self.addressSizeLineEdit.setText(self.format.format(Size, Suffix(Size)))
        else:
            self.addressSizeLineEdit.setText("???")

        if 'word_size' in self.regmaps[self.active_regmap]:
            Size = self.regmaps[self.active_regmap]['word_size']
            self.wordSizeLineEdit.setText(self.format.format(Size, Suffix(Size)))
        else:
            self.wordSizeLineEdit.setText("???")


        # Offset

        # Words

        # Slice

        # Default

        # Presets

    def registermapChanged(self):
        self.active_regmap = self.registermapComboBox.currentText()
        self.registersGroupBox.setEnabled(True)
        self.registermapUpdate()

    def changeDirectoryWithDialog(self):
        DirDialog = QtWidgets.QFileDialog()
        DirDialog.setWindowIcon(qta.icon('mdi.magnify'))
        DirDialog.setWindowTitle('Select Directory')
        DirDialog.setDirectory(self.working_directory)
        DirDialog.setFileMode(QtWidgets.QFileDialog.Directory)
        DirDialog.setNameFilters(["Register Maps (*.regmap)", "All Files (*.*)]"])
        DirDialog.selectNameFilter("Register Maps (*.regmap)")
        DirDialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog)
        DirDialog.exec()
        new_directory = DirDialog.selectedFiles()[0]
        print(new_directory)
        if os.path.exists(new_directory):
            if os.path.isfile(new_directory):
                new_directory = os.path.split(new_directory)[0]
            self.old_working_directory = self.working_directory
            self.working_directory = new_directory
            self.directoryLineEdit.setText(self.working_directory)
            self.changedDirectorySettings()

    def changeDirectoryWithLineEdit(self):
        path = self.directoryLineEdit.text()
        if os.path.exists(path):
            if os.path.isfile(path):
                path = os.path.split(path)[0]
            self.old_working_directory = self.working_directory
            self.working_directory = path
            self.changedDirectorySettings()
        else:
            self.directoryLineEdit.setText(self.working_directory)


    def changedDirectorySettings(self):

        if not self.initialization:
            for regmap in self.changed_regmaps:
                register_map_save(os.path.join(self.old_working_directory, regmap + '.regmap'), self.regmaps[regmap])

        self.initialization=False
        self.regmaps = {}
        self.changed_regmaps = {}
        self.active_regmap = None
        self.active_register = None

        regmaps_on_disk = register_maps_in_directory(self.working_directory)
        self.registermapComboBox.setEnabled(True)
        self.registermapComboBox.clear()
        if len(regmaps_on_disk)>0:
            self.registersGroupBox.setEnabled(True)
            self.registermapComboBox.blockSignals(True)
            for regmap in regmaps_on_disk:
                regmap_name = regmap.replace('.regmap', '')
                self.regmaps[regmap_name] = register_map_load(os.path.join(self.working_directory, regmap))
                self.registermapComboBox.addItem(regmap_name) #
                self.changed_regmaps[regmap_name] = False
            self.registermapComboBox.setCurrentIndex(0)
            self.active_regmap = self.registermapComboBox.currentText()
            self.registermapComboBox.blockSignals(False)

            self.addressSizeLineEdit.setEnabled(True)
            Size = self.regmaps[self.active_regmap]['address_size']
            self.addressSizeLineEdit.setText(self.format.format(Size, Suffix(Size)))

            self.wordSizeLineEdit.setEnabled(True)
            Size = self.regmaps[self.active_regmap]['word_size']
            self.wordSizeLineEdit.setText(self.format.format(Size, Suffix(Size)))

            self.removeRegistermapPushButton.setEnabled(True)
            self.copyRegistermapPushButton.setEnabled(True)
            self.exportRegistermapPushButton.setEnabled(True)
            self.saveAllPushButton.setEnabled(False)
            self.saveRegistermapPushButton.setEnabled(False)
            self.importRegistermapPushButton.setEnabled(True)
            self.addRegistermapPushButton.setEnabled(True)

            self.registersListWidget.clear()
            for register in self.regmaps[self.active_regmap]:
                if not isinstance(self.regmaps[self.active_regmap][register], dict): continue
                self.registersListWidget.addItem(register)
            if self.registersListWidget.count()!=0:
                self.registersListWidget.setCurrentIndex(0)
                self.active_register = self.registersListWidget.currentItem().text()
                self.registerNameLineEdit.setText(self.active_register)
                self.registerDescriptionLineEdit = self.regmaps[self.active_regmap][self.active_register]['desc']
            else:
                self.active_register = None


            #...


        else:
            self.registermapComboBox.setEnabled(False)
            self.addressSizeLineEdit.setText('?!?')
            self.addressSizeLineEdit.setEnabled(False)
            self.wordSizeLineEdit.setText('?!?')
            self.wordSizeLineEdit.setEnabled(False)

            self.removeRegistermapPushButton.setEnabled(False)
            self.copyRegistermapPushButton.setEnabled(False)
            self.exportRegistermapPushButton.setEnabled(False)
            self.saveAllPushButton.setEnabled(False)
            self.saveRegistermapPushButton.setEnabled(False)
            self.importRegistermapPushButton.setEnabled(True)
            self.addRegistermapPushButton.setEnabled(True)

            self.registersGroupBox.setEnabled(False)
            self.registersListWidget.clear()
            self.registerNameLineEdit.setText('')








    def addRegistermap(self):
        if self.debug: print("add register map ... ", end='')
        new_map = {'address_size': __default_address_size__, 'word_size': __default_word_size__}
        print(new_map)
        regmaps = register_maps_in_directory(self.working_directory)
        print(regmaps)
        tmp = []
        for regmap in regmaps:
            print(regmap)
            tmp.append(regmap.replace('.regmap', ''))
        fmt = "new{0:s}"
        nr = ''
        while fmt.format(nr) in tmp:
            if nr == '':
                nr = 0
            nr+=1
        if self.debug: print(fmt.format(nr), '...', end='')
        register_map_save(fmt.format(nr)+'.regmap', new_map)
        if self.debug: print("Done")
        self.changedDirectorySettings()

    def removeRegistermap(self):
        print("remove register map")

    def importRegistermap(self):
        self.registersGroupBox.setEnabled(True)

#         self.registermapComboBox.addItem(qta.icon("mdi.access-point"), "Boe")


        print("import register map")

    def exportRegistermap(self):
        print("export register map")

    def copyRegistermap(self):
        print("copy register map")

    def saveRegistermap(self):
        print("save register map")

    def saveAllRegistermaps(self):
        print("save ALL register maps")



    def removeRegister(self):
        print("remove register")

    def addRegister(self):
        new_register = {'offset' : 0, 'words' : 1, 'slice' : (0,), 'access' : 'RW', 'default': None, 'presets': {}}
        print("add register")



    def registermapRenamed(self, value):
        print(self.active_regmap)
        print(value)





        print("register map renamed")

    def registerChanged(self):
        print("register changed")

    def registerRenamed(self):
        print("register changed")

    def descriptionChanged(self):
        print

    def offsetChanged(self):
        print("offset changed")

    def wordsChanged(self):
        print("words changed")

    def sliceChanged(self):
        print("slice changed")

    def accessChanged(self):
        print("access changed")

    def defaultChanged(self):
        print("default changed")

    def removePreset(self):
        print("remove preset")

    def addPreset(self):
        print("add preset")

    def presetChanged(self, row, column):
        print("preset changed %s %s" % (row, column))


def Suffix(n):
    if n>1:
        return 's'
    else:
        return ''


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(style)
    mainWindow = QtWidgets.QMainWindow()
    ui = MainWindow()
    ui.setupUi(mainWindow)
    ui.adjustUI()
    mainWindow.show()
    sys.exit(app.exec_())
