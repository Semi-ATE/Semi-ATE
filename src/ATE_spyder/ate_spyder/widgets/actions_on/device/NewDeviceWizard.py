# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 15:09:41 2019

@author: hoeren
"""
from PyQt5.QtWidgets import QTreeWidgetItem
from ate_spyder.widgets.validation import valid_device_name_regex
from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog
from PyQt5 import QtCore, QtGui, QtWidgets

import qtawesome as qta
import os
import re


class NewDeviceWizard(BaseDialog):
    def __init__(self, project_info, read_only=False):
        super().__init__(__file__, project_info.parent)
        self.project_info = project_info
        self.read_only = read_only
        self.selected_dies = []
        self._setup()
        self._connect_event_handler()

    def _setup(self):
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))
        self._setup_hardware()
        self._setup_device()
        self._setup_package()
        self._setup_pins()
        self._setup_dies()
        self._setup_buttons()

        self.feedback.setStyleSheet('color: orange')
        self._verify()

    def _setup_hardware(self):
        self.existing_hardwares = self.project_info.get_active_hardware_names()
        self.hardware.clear()
        self.hardware.addItems(self.existing_hardwares)
        self.hardware.setCurrentText(self.project_info.active_hardware)

    def _setup_device(self):
        rxDeviceName = QtCore.QRegExp(valid_device_name_regex)
        DeviceName_validator = QtGui.QRegExpValidator(rxDeviceName, self)
        self.deviceName.setValidator(DeviceName_validator)
        self.deviceName.setText('')
        self.existing_devices = self.project_info.get_devices_for_hardwares()

    def _setup_package(self):
        self.existing_packages = self.project_info.get_available_packages()
        self.package.clear()
        self.package.addItems([''] + self.existing_packages)
        self.package.setCurrentText('' if not len(self.existing_packages) else self.existing_packages[0])
        package = self.package.currentText()
        if package:
            self._set_pins_table_items(self.project_info.get_package(self.package.currentText()))
            self.package_changed(package)

    def _setup_pins(self):
        if self.hardware.currentText() == '':
            self.tabWidget.setEnabled(False)
            self.available_dies = []
        else:
            self.tabWidget.setEnabled(True)
            self.available_dies = self.project_info.get_active_die_names_for_hardware(self.hardware.currentText())
        self.dies_in_device = []

        masksets = [self.project_info.get_die_maskset(die) for die in self.available_dies]
        self.maskset_used = {maskset: self.project_info.get_maskset_definition(maskset)['BondpadTable'] for maskset in masksets}
        self.pinsTable.setAcceptDrops(True)
        self.pinsTable.setDragEnabled(True)
        self.pinsTable.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.pinsTable.setColumnWidth(0, 200)
        self.pinsTable.header().setStretchLastSection(False)
        self.pinsTable.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

    def _setup_dies(self):
        self.existing_dies = self.project_info.get_active_die_names_for_hardware(self.project_info.active_hardware)
        self.availableDies.clear()
        self.availableDies.clearSelection()
        self.availableDies.addItems(self.available_dies)
        self.availableDies.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.diesInDevice.clear()
        self.diesInDevice.clearSelection()
        self.diesInDevice.addItems(self.dies_in_device)
        self.diesInDevice.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.selectedDies.setDragEnabled(True)
        self.selectedDies.setAcceptDrops(True)
        self.selectedDies.setEnabled(True)
        # TODO: feature to select multiple bondpads
        # self.selectedDies.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

    def _setup_buttons(self):
        self.OKButton.setDisabled(True)
        self.addDie.setEnabled(True)
        self.addDie.setIcon(qta.icon('mdi.arrow-right-bold-outline', color='orange'))

        self.removeDie.setEnabled(True)
        self.removeDie.setIcon(qta.icon('mdi.arrow-left-bold-outline', color='orange'))

        # Type
        # TODO: also add the Type = ['ASSP' or 'ASIC']

    def _connect_event_handler(self):
        self.hardware.currentTextChanged.connect(self.hardwareChanged)
        self.deviceName.textChanged.connect(self._verify)
        self.package.currentTextChanged.connect(self.package_changed)
        self.addDie.clicked.connect(self.add_dies)
        self.removeDie.clicked.connect(self.remove_dies)
        self.CancelButton.clicked.connect(self.CancelButtonPressed)
        self.OKButton.clicked.connect(self.OKButtonPressed)
        self.pinsTable.itemChanged.connect(self._pins_table_tree_changed)
        self.selectedDies.itemChanged.connect(self._selected_die_tree_changed)

    def _selected_die_tree_changed(self, item, _):
        text = item.text(0)
        # make sure that is not possible to grab the wrong item from the selected list
        if not item.parent():
            self.selectedDies.takeTopLevelItem(self.selectedDies.indexOfTopLevelItem(item))
        else:
            item.parent().removeChild(item)

        # this should never happend, this case where we could grab the die itself
        if '_' not in text:
            return

        self._update_pins_table_after_removing_items(text)

    def _update_pins_table_after_removing_items(self, text):
        self.selectedDies.blockSignals(True)
        root = self.selectedDies.invisibleRootItem()
        for item_index in range(root.childCount()):
            item = root.child(item_index)
            if not item.text(0) in text:
                continue

            for child_index in range(item.childCount()):
                child_item = item.child(child_index)
                if not child_item.text(0) in text:
                    continue

                child_item.setDisabled(False)
                self._remove_selected_items_from_pins_table()
                break
            break

        self.selectedDies.blockSignals(False)

    def _remove_selected_items_from_pins_table(self):
        self.pinsTable.blockSignals(True)
        for item in self.pinsTable.selectedItems():
            parent = item.parent()
            item.text(0)
            if parent:
                parent.removeChild(item)

        self._deselect_item_after_selected()
        self.pinsTable.blockSignals(False)

    def _pins_table_tree_changed(self, item, col):
        # make sure that is not possible to grab the wrong item from pinsTable list
        if not item.parent():
            if col == 0:
                return

            self.pinsTable.takeTopLevelItem(self.pinsTable.indexOfTopLevelItem(item))
            return

        # remove the item after dropping it
        if item.parent().parent():
            item.parent().removeChild(item)
            return

        if self._do_update_pins_table_tree_after_moving_item():
            return

        self._rename_parent_item_if_needed(item, col)

    def _do_update_pins_table_tree_after_moving_item(self):
        selected_item = self.pinsTable.selectedItems()
        if selected_item:
            parent = selected_item[0].parent()
            if parent:
                parent.removeChild(selected_item[0])
            self._deselect_item_after_selected()
            return True

        return False

    def _rename_parent_item_if_needed(self, item, col):
        self.pinsTable.blockSignals(True)
        self.selectedDies.blockSignals(True)
        parent = item.parent()
        if parent.text(0).isdigit():
            parent.setText(0, item.text(0))
            if '_' in item.text(0):
                parent.setText(0, item.text(0).rsplit('_', 1)[1])

        for selected_item in self.selectedDies.selectedItems():
            if col != 0:
                continue

            for index in range(parent.childCount()):
                item_child = parent.child(index)
                if '_' not in item_child.text(0):
                    item_child.setText(0, f"{selected_item.parent().text(0)}_{item_child.text(0)}")

            break

        self._deselect_item_after_selected()

        self.pinsTable.blockSignals(False)
        self.selectedDies.blockSignals(False)


    def _deselect_item_after_selected(self):
        self._deselect_tree_items(self.selectedDies)
        self._deselect_tree_items(self.pinsTable)

    @staticmethod
    def _deselect_tree_items(tree):
        tree.clearSelection()

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

    def package_changed(self, package):
        self._clear_pin_table()
        if self.package.currentText() == '':
            pass
        elif self._is_naked_die(package):
            self.diesInDevice.clear()
            self.pins.setEnabled(False)
        else:
            package_info = self.project_info.get_package(package)
            self._set_pins_table_items(package_info)
            self.pins.setEnabled(True)

    def _is_naked_die(self, package):
        package_info = self.project_info.get_package(package)
        return package_info.is_naked_die

    def _set_pins_table_items(self, package_info):
        for index in range(package_info.leads):
            _ = self._create_pin_table_item(str(index + 1))

    def _create_pin_table_item(self, name):
        item = QTreeWidgetItem(self.pinsTable)
        item.setExpanded(True)
        item.setFlags(QtCore.Qt.ItemIsDropEnabled | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        item.setText(0, name)
        return item

    def _clear_pin_table(self):
        self.pinsTable.clear()

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
            self.feedback.setText("no die is available for the current hardware")
            return

        self.feedback.setText('')

        if self.feedback.text() == '':
            if self.hardware.currentText() == '':
                self.feedback.setText("Select a hardware setup")

        if self.feedback.text() == '':
            if self.deviceName.text() == '':
                self.feedback.setText("Supply a Device Name")
            elif not self.read_only and self.deviceName.text() in self.existing_devices:
                self.feedback.setText(f"Device '{self.deviceName.text()}' already defined!")

            elif not self.read_only and self.deviceName.text() in self.project_info.get_active_die_names_for_hardware(self.hardware.currentText()):
                self.feedback.setText(f"Die with the same name: '{self.deviceName.text()}' exists already!")

        if self.feedback.text() == '':
            if self.package.currentText() == '':
                self.feedback.setText("Select a Package")

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
        self.selectedDies.blockSignals(True)
        for die_to_add in self.availableDies.selectedItems():

            count = len([die for die in self.selected_dies if die_to_add.text() in die])
            text = f'{die_to_add.text()}_{count + 1}'
            self.diesInDevice.insertItem(self.diesInDevice.count(), text)
            self.selected_dies.append(text)
            self.dies_in_device.append(text)

            maskset = self.project_info.get_die_maskset(die_to_add.text())
            self._update_selected_table(text, maskset)

        self.diesInDevice.clearSelection()
        self.availableDies.clearSelection()
        self.selectedDies.blockSignals(False)
        self.diesInDevice.blockSignals(False)

        self.check_for_dual_die()
        self._verify()

    def _update_selected_table(self, text, maskset):
        item = QTreeWidgetItem(self.selectedDies)
        item.setExpanded(True)
        item.setFlags(QtCore.Qt.ItemIsEnabled)
        item.setText(0, text)

        for key, maskset_pads in self.maskset_used.items():
            if key != maskset:
                continue

            for pad in maskset_pads:
                self._create_table_item_child(item, pad[0], pad[5], pad[6])

    def remove_dies(self):
        self.diesInDevice.blockSignals(True)
        row = self.diesInDevice.selectedIndexes()[0].row()
        item = self.diesInDevice.item(row)
        text = item.text()
        self.diesInDevice.takeItem(row)
        self._remove_from_selected_tree(text)
        self._remove_from_pins_tree(text)

        self.dies_in_device.remove(text)
        self.selected_dies.remove(text)

        self.diesInDevice.clearSelection()
        self.availableDies.clearSelection()
        self.diesInDevice.blockSignals(False)
        self.check_for_dual_die()
        self._verify()

    def _remove_from_selected_tree(self, name):
        root = self.selectedDies.invisibleRootItem()
        for index in range(root.childCount()):
            item = root.child(index)
            if not item:
                return

            if item.text(0) == name:
                self.selectedDies.takeTopLevelItem(self.selectedDies.indexOfTopLevelItem(item))

    def _remove_from_pins_tree(self, name):
        root = self.pinsTable.invisibleRootItem()
        for index in range(root.childCount()):
            item = root.child(index)
            for i in range(item.childCount()):
                child = item.child(i)
                if not child:
                    continue

                if name in child.text(0):
                    item.removeChild(child)
                    self._remove_from_pins_tree(name)

    def _get_current_configuration(self):
        dies_in_package = []
        for die in self.diesInDevice.findItems('*', QtCore.Qt.MatchWrap | QtCore.Qt.MatchWildcard):
            dies_in_package.append(die.text())
        definition = {'dies_in_package': dies_in_package,
                      'is_dual_die': self.dualDie.checkState(),
                      'pin_names': self._get_pin_settings()}

        return {'hardware': self.hardware.currentText(),
                'name': self.deviceName.text(),
                'package': self.package.currentText(),
                'definition': definition}

    def _get_pin_settings(self):
        root = self.pinsTable.invisibleRootItem()
        pins = []
        for i in range(root.childCount()):
            item = root.child(i)
            key = item.text(0)

            elements = []
            for j in range(item.childCount()):
                child = item.child(j)
                elements.append((child.text(0), child.text(1), child.text(2)))

            pins.append({key: elements})

        return pins

    def _setup_pins_table(self, pins_setting):
        self.selectedDies.blockSignals(True)
        self.pinsTable.blockSignals(True)
        self.pinsTable.clear()
        for pins in pins_setting:
            for name, value in pins.items():
                self._create_die_table_items(name, value)
                self._create_pin_table_items(name, value)
        self.selectedDies.blockSignals(False)
        self.pinsTable.blockSignals(False)

    def _create_pin_table_items(self, name, pins):
        pin_item = self._create_pin_table_item(name)
        for value in pins:
            self._create_table_item_child(pin_item, value[0], value[1], value[2])

    def _create_die_table_items(self, _, pins):
        for die in self.dies_in_device:
            if self._does_pin_exist(die):
                continue

            maskset = self.project_info.get_die_maskset(die.split('_')[0])
            self._update_selected_table(die, maskset)

    def _does_pin_exist(self, name):
        root = self.selectedDies.invisibleRootItem()
        for index in range(root.childCount()):
            item = root.child(index)
            if item.text(0) == name:
                return True

        return False

    @staticmethod
    def _create_table_item_child(item, val_1, val_2, val_3):
        pin_child = QTreeWidgetItem()
        pin_child.setText(0, val_1)
        pin_child.setText(1, val_2)
        pin_child.setText(2, val_3)
        item.addChild(pin_child)
        item.setExpanded(True)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        return pin_child

    def OKButtonPressed(self):
        configuration = self._get_current_configuration()
        self.project_info.add_device(configuration['name'], configuration['hardware'],
                                     configuration['package'], configuration['definition'])
        self.accept()

    def CancelButtonPressed(self):
        self.reject()


def new_device_dialog(project_info):
    newDeviceWizard = NewDeviceWizard(project_info)
    newDeviceWizard.exec_()
    del(newDeviceWizard)
