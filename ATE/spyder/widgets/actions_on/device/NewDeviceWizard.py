# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 15:09:41 2019

@author: hoeren
"""
from ATE.spyder.widgets.validation import valid_device_name_regex
from ATE.spyder.widgets.actions_on.utils.BaseDialog import BaseDialog
from PyQt5 import QtCore, QtGui, QtWidgets

import qtawesome as qta
import os
import re


class NewDeviceWizard(BaseDialog):
    def __init__(self, project_info, read_only=False):
        super().__init__(__file__)
        self.project_info = project_info
        self.read_only = read_only
        self._setup()
        self._connect_event_handler()

    def _setup(self):
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        # hardware
        self.existing_hardwares = self.project_info.get_active_hardware_names()
        self.hardware.clear()
        self.hardware.addItems(self.existing_hardwares)
        self.hardware.setCurrentText(self.project_info.active_hardware)

        self.existing_dies = self.project_info.get_active_die_names_for_hardware(self.project_info.active_hardware)

        rxDeviceName = QtCore.QRegExp(valid_device_name_regex)
        DeviceName_validator = QtGui.QRegExpValidator(rxDeviceName, self)
        self.deviceName.setValidator(DeviceName_validator)
        self.deviceName.setText('')
        self.existing_devices = self.project_info.get_devices_for_hardwares()

        # packages
        self.existing_packages = self.project_info.get_available_packages()
        self.package.clear()
        self.package.addItems([''] + self.existing_packages)
        self.package.setCurrentText('' if not len(self.existing_packages) else self.existing_packages[0])
        # TODO: should we just take the first available one, as below
        # self.package.setCurrentIndex(0)  # this is the empty string !

        # Dies/Pins
        if self.hardware.currentText() == '':
            self.tabWidget.setEnabled(False)
            self.available_dies = []
        else:
            self.tabWidget.setEnabled(True)
            self.pins.setEnabled(False)
            self.available_dies = self.project_info.get_active_die_names_for_hardware(self.hardware.currentText())
        self.dies_in_device = []

        # available dies
        self.availableDies.clear()
        self.availableDies.clearSelection()
        self.availableDies.addItems(self.available_dies)
        self.availableDies.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # dies in device
        self.diesInDevice.clear()
        self.diesInDevice.clearSelection()
        self.diesInDevice.addItems(self.dies_in_device)
        self.diesInDevice.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # add die(s) to device
        self.addDie.setEnabled(True)
        self.addDie.setIcon(qta.icon('mdi.arrow-right-bold-outline', color='orange'))

        # remove die(s) from device
        self.removeDie.setEnabled(True)
        self.removeDie.setIcon(qta.icon('mdi.arrow-left-bold-outline', color='orange'))

        self.addPin.setEnabled(True)
        self.addPin.setIcon(qta.icon('mdi.arrow-right-bold-outline', color='orange'))

        self.removePin.setEnabled(True)
        self.removePin.setIcon(qta.icon('mdi.arrow-left-bold-outline', color='orange'))

        self.pinUp.setEnabled(True)
        self.pinUp.setIcon(qta.icon('mdi.arrow-up-bold-outline', color='orange'))

        self.pinDown.setEnabled(True)
        self.pinDown.setIcon(qta.icon('mdi.arrow-down-bold-outline', color='orange'))

        # Type
        # TODO: also add the Type = ['ASSP' or 'ASIC']
        self.pinsTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.pinsTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

        # feedback
        self.feedback.setStyleSheet('color: orange')

        # buttons
        self.OKButton.setDisabled(True)
        self._verify()

    def _connect_event_handler(self):
        self.hardware.currentTextChanged.connect(self.hardwareChanged)
        self.deviceName.textChanged.connect(self._verify)
        self.package.currentTextChanged.connect(self.packageChanged)
        self.addDie.clicked.connect(self.add_dies)
        self.removeDie.clicked.connect(self.remove_dies)
        self.CancelButton.clicked.connect(self.CancelButtonPressed)
        self.OKButton.clicked.connect(self.OKButtonPressed)

    def hardwareChanged(self, SelectedHardware):
        '''
        if the selected hardware changes, make sure the active_hardware
        at the parent level is also changed, the dies in device list is cleared,
        and the available dies is reloaded.
        '''
        self.parent.hardware_activated.emit(self.hardware.currentText())

        self.diesInDevice.clear()
        self.existing_dies = self.project_info.get_active_die_names_for_hardware(self.project_info.active_hardware)
        self.availableDies.blockSignals(True)
        self.availableDies.clear()
        self.availableDies.addItems(self.existing_dies)
        self.availableDies.clearSelection()
        self.availableDies.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.availableDies.blockSignals(False)
        self._verify()

    def nameChanged(self, DeviceName):
        pass

    def packageChanged(self, Package):
        if self.package.currentText() == '':  # no package
            self.pins.setVisible(False)
        elif self.package.currentText() == 'Naked Die':  # naked die
            self.pins.setVisible(True)
            self.diesInDevice.clear()
            self.pinsTable.setRowCount(0)
        else:  # normal package
            self.pins.setVisible(True)
            # Variable is never used!
            # packages_info = self.project_info.get_available_packages()
            # TODO: what to do here
            # pins_in_package = packages_info[self.package.currentText()]
            # self.pinsTable.setRowCount(len(pins_in_package))

    def check_for_dual_die(self):
        '''
        this mentod will check if a configuration qualifies for 'DualDie',
        if so, the radio will be enabled, if not disabled (and cleared)
        '''
        temp = []
        for die in self.diesInDevice.findItems('*', QtCore.Qt.MatchWrap | QtCore.Qt.MatchWildcard):
            temp.append(die.text())
        if len(temp) == 2:
            self.dualDie.setCheckState(QtCore.Qt.Unchecked)
            if temp[0] == temp[1]:
                self.dualDie.setEnabled(True)
            else:
                self.dualDie.setEnabled(False)
        else:
            self.dualDie.setCheckState(QtCore.Qt.Unchecked)
            self.dualDie.setEnabled(False)

    def _verify(self):
        if not self.existing_hardwares:
            self.feedback.setText("No hardware is available")
            return

        if not self.existing_packages:
            self.feedback.setText("No package is available")
            return

        if not self.existing_dies:
            self.feedback.setText("no die is availabe for the current hardware")
            return

        self.feedback.setText('')

    # Check hardware
        if self.feedback.text() == '':
            if self.hardware.currentText() == '':
                self.feedback.setText("Select a hardware setup")

    # Check Device Name
        if self.feedback.text() == '':
            if self.deviceName.text() == '':
                self.feedback.setText("Supply a Device Name")
            elif not self.read_only and self.deviceName.text() in self.existing_devices:
                self.feedback.setText(f"Device '{self.deviceName.text()}' already defined!")

    # Check Package
        if self.feedback.text() == '':
            if self.package.currentText() == '':
                self.feedback.setText("Select a Package")
    # Check Pins
    # Check Type

        if self.feedback.text() == '':
            package_name = self.package.currentText()
            if package_name == '':
                self.feedback.setText("No package selected")
            elif package_name != 'Naked Die':
                number_of_dies_in_device = self.diesInDevice.count()
                if not self.dualDie.checkState():  # no dual die
                    if number_of_dies_in_device == 0:
                        self.feedback.setText('Need at least ONE die')
            else:  # Naked die
                number_of_dies_in_device = self.diesInDevice.count()
                if number_of_dies_in_device == 0:
                    self.feedback.setText("select the naked die")
                elif number_of_dies_in_device > 1:
                    self.feedback.setText("Only one die allowed in 'Naked Die'")
                else:  # one selected
                    self.feedback.setText('')

    # Check the pins table
        if self.feedback.text() == '':
            pass

        if self.feedback.text() == "":
            self.OKButton.setEnabled(True)
        else:
            self.OKButton.setEnabled(False)

    def add_dies(self):
        '''
        this method is called when the 'add die' (tool)button is pressed
        '''
        if self.dualDie.isChecked():
            pass

        self.diesInDevice.blockSignals(True)
        for die_to_add in self.availableDies.selectedItems():
            self.diesInDevice.insertItem(self.diesInDevice.count(), die_to_add.text())
        self.diesInDevice.clearSelection()
        self.availableDies.clearSelection()
        self.diesInDevice.blockSignals(False)

        self.check_for_dual_die()
        self._verify()

    def remove_dies(self):
        '''
        this method is called when the 'remove die' (tool)button is pressed
        '''
        self.diesInDevice.blockSignals(True)
        self.diesInDevice.takeItem(self.diesInDevice.selectedIndexes()[0].row())  # DiesInDevice set to SingleSelection ;-)
        self.diesInDevice.clearSelection()
        self.availableDies.clearSelection()
        self.diesInDevice.blockSignals(False)
        self.check_for_dual_die()
        self._verify()

    def CancelButtonPressed(self):
        self.reject()

    def _get_current_configuration(self):
        dies_in_package = []
        for die in self.diesInDevice.findItems('*', QtCore.Qt.MatchWrap | QtCore.Qt.MatchWildcard):
            dies_in_package.append(die.text())
        definition = {'dies_in_package': dies_in_package,
                      'is_dual_die': self.dualDie.checkState(),
                      'pin_names': {}}

        return {'hardware': self.hardware.currentText(),
                'name': self.deviceName.text(),
                'package': self.package.currentText(),
                'definition': definition}

    def OKButtonPressed(self):
        configuration = self._get_current_configuration()
        self.project_info.add_device(configuration['name'], configuration['hardware'],
                                     configuration['package'], configuration['definition'])
        self.accept()


def new_device_dialog(project_info):
    newDeviceWizard = NewDeviceWizard(project_info)
    newDeviceWizard.exec_()
    del(newDeviceWizard)


if __name__ == '__main__':
    import sys, qdarkstyle
    from ATE.spyder.widgets.actions.dummy_main import DummyMainWindow

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    dummyMainWindow = DummyMainWindow()
    dialog = NewDeviceWizard(dummyMainWindow)
    dummyMainWindow.register_dialog(dialog)
    sys.exit(app.exec_())
