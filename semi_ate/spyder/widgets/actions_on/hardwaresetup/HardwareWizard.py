# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 09:52:27 2020

@author: hoeren
"""

import os
import re

from ATE.org.validation import valid_pcb_name_regex
from PyQt5 import QtCore, QtGui, QtWidgets
from ATE.org.actions_on.utils.BaseDialog import BaseDialog
from ATE.org.plugins.pluginmanager import get_plugin_manager
from ATE.org.actions_on.hardwaresetup.InstrumentListItem import InstrumentListItem
import qtawesome as qta


PR = 'PR'
FT = 'FT'


class HardwareWizard(BaseDialog):
    def __init__(self, project_info):
        super().__init__(__file__)
        self.project_info = project_info
        self._site = None
        self._pattern_type = None
        self._pattern = {}
        self._available_pattern = {}
        self._available_definiton = None
        self._selected_available_item = ''
        self._plugin_manager = get_plugin_manager()

        # These lists store the unique names of
        # plugin based instruments and actuators
        self._availableInstruments = []
        self.is_active = True

        self._setup()
        self._connect_event_handler()
        self._verify()

    def _setup(self):
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))
        self.setFixedSize(self.size())

    # hardware
        self.hardware.setText(self.project_info.get_next_hardware())
        self.hardware.setEnabled(False)

        self.probecardLink.setDisabled(True)
    # PCBs
        rxPCBName = QtCore.QRegExp(valid_pcb_name_regex)
        PCBName_validator = QtGui.QRegExpValidator(rxPCBName, self)

        self.singlesiteLoadboard.setText('')
        self.singlesiteLoadboard.setValidator(PCBName_validator)
        self.singlesiteLoadboard.setEnabled(True)
        self.multisiteLoadboard.setText('')
        self.multisiteLoadboard.setValidator(PCBName_validator)
        self.multisiteLoadboard.setDisabled(True)
        self.singlesiteProbecard.setText('')
        self.singlesiteProbecard.setValidator(PCBName_validator)
        self.singlesiteProbecard.setEnabled(True)
        self.multisiteProbecard.setText('')
        self.multisiteProbecard.setValidator(PCBName_validator)
        self.multisiteProbecard.setDisabled(True)
        self.singlesiteDIB.setText('')
        self.singlesiteDIB.setValidator(PCBName_validator)
        self.singlesiteDIB.setEnabled(True)
        self.multisiteDIB.setText('')
        self.multisiteDIB.setValidator(PCBName_validator)
        self.multisiteDIB.setDisabled(True)

        self.maxParallelism.setCurrentText('1')

    # Instruments
        self.tester.clear()
        self.tester.addItems([''] + self.project_info.get_available_testers())
        self.tester.setCurrentText('')

        # At this point instruments will be displayed as a plain list
        # -> in the prototype the instruments where grouped as tree
        # using the manufacterer of the respective Instrument.
        # We might need something similar here too, but as of now, the
        # Plugin API does not provide us with a means of extracting a group
        instrument_lists = self._plugin_manager.hook.get_instrument_names()
        for instrument_list in instrument_lists:
            for instrument in instrument_list:
                self._append_instrument_to_manufacturer(instrument)

    # Parallelism
        self.finaltestConfiguration.setColumnCount(self._max_parallelism_value)
        self.finaltestConfiguration.setRowCount(self._max_parallelism_value)
        self.finaltestSites.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._set_list_visible_items(self.finaltestSites.count())
        self._init_table()
        # TODO: find a better solution
        self.finaltestConfiguration.setFixedSize(626, 374)

        self.right_button.setEnabled(False)
        self.probing_button.setChecked(True)
        self._pattern_type = PR

    # general
        self.feedback.setText('')
        self.feedback.setStyleSheet('color: orange')

        self.tabLayout.setCurrentIndex(0)

        self._set_icons()

        self.OKButton.setEnabled(False)
        self.CancelButton.setEnabled(True)

    def _get_manufacturer_node(self, manufacterer):
        for mfg in range(0, self.availableInstruments.topLevelItemCount()):
            item = self.availableInstruments.topLevelItem(mfg)
            if item.text(0) == manufacterer:
                return item

        # Manufacturer does not exist yet, create it and return it:
        the_manufacturer = QtWidgets.QTreeWidgetItem([manufacterer])
        self.availableInstruments.addTopLevelItem(the_manufacturer)
        return the_manufacturer

    def _append_instrument_to_manufacturer(self, instrument):
        manufacturer = instrument["manufacturer"]
        manufacturer_node = self._get_manufacturer_node(manufacturer)
        instrumentNode = InstrumentListItem(manufacturer_node, instrument)
        manufacturer_node.addChild(instrumentNode)

    def _set_icons(self):
        self.right_button.setIcon(qta.icon('mdi.arrow-right-bold', color='orange'))
        self.left_button.setIcon(qta.icon('mdi.arrow-left-bold', color='orange'))
        # self.availableInstruments.clear()
        # self.availableInstruments.addItems([''])
        # self.parent.project_info.get_available_instruments())
        # TODO: move from list to tree for this widget!
        self.collapse.setIcon(qta.icon('mdi.unfold-less-horizontal', color='orange'))
        self.expand.setIcon(qta.icon('mdi.unfold-more-horizontal', color='orange'))
        self.addInstrument.setIcon(qta.icon('mdi.arrow-right-bold', color='orange'))
        self.removeInstrument.setIcon(qta.icon('mdi.arrow-left-bold', color='orange'))
        # self.tableWidget.clear()
        # TODO: move from list to tree for this widget!

    # Actuator
        self.probecardLink.setIcon(qta.icon('mdi.link', color='orange'))

    def _connect_event_handler(self):
        # Parallelism
        self.finaltestConfiguration.cellClicked.connect(self._table_cell_clicked)
        self.finaltestConfiguration.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.finaltestConfiguration.customContextMenuRequested.connect(self._clear_cell)
        self.probecardLink.clicked.connect(self._link_probecard)
        self.probing_button.clicked.connect(self._on_probing_toggeled)
        self.final_test_button.clicked.connect(self._on_final_test_toggeled)
        self.finaltestSites.clicked.connect(self._final_test_list_clicked)
        self.reset_button.clicked.connect(self._init_table)
        self.right_button.clicked.connect(self._right_button_clicked)
        self.left_button.clicked.connect(self._left_button_clicked)
        self.finaltestAvailableConfigurations.clicked.connect(self._edit_pattern)

        # PCBs
        self.singlesiteLoadboard.textChanged.connect(self._verify)
        self.singlesiteDIB.textChanged.connect(self._verify)
        self.singlesiteProbecard.textChanged.connect(self._verify)
        self.multisiteLoadboard.textChanged.connect(self._verify)
        self.multisiteProbecard.textChanged.connect(self._verify)
        self.multisiteDIB.textChanged.connect(self._verify)
        self.maxParallelism.currentTextChanged.connect(self._max_parallelism_value_changed)

        # Instruments
        self.tester.currentTextChanged.connect(self.testerChanged)
        self.collapse.clicked.connect(self.collapseAvailableInstruments)
        self.expand.clicked.connect(self.expandAvailableInstruments)
        self.addInstrument.clicked.connect(self.addingInstrument)
        self.removeInstrument.clicked.connect(self.removingInstrument)
        self.checkInstruments.clicked.connect(self.checkInstrumentUsage)
        self.availableInstruments.itemSelectionChanged.connect(self.availableInstrumentsSelectionChanged)
        self.availableInstruments.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.availableInstruments.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.usedInstruments.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.usedInstruments.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        # Actuator
        self.checkActuators.clicked.connect(self.checkActuatorUsage)

        # general
        self.CancelButton.clicked.connect(self.CancelButtonPressed)
        self.OKButton.clicked.connect(self.OKButtonPressed)

    def _edit_pattern(self, index):
        item = self.finaltestAvailableConfigurations.itemFromIndex(index)
        pattern = self._available_pattern[item.text()]
        self._selected_available_item = item.text()

        self.finaltestConfiguration.setColumnCount(len(pattern[0]))
        self.finaltestConfiguration.setRowCount(len(pattern))
        self._set_list_visible_items(len(pattern))
        self._init_table()
        self.maxParallelism.setCurrentText(str(len(pattern)))

        for row in range(self.finaltestConfiguration.rowCount()):
            for col in range(self.finaltestConfiguration.columnCount()):
                element = pattern[row][col]
                if element == 0:
                    element = ''

                item = self.finaltestConfiguration.item(row, col)
                item.setText(str(element))

        self._set_final_test_sites(False)

    def _deselect_list_item(self):
        self._selected_available_item = ''
        for item in self.finaltestAvailableConfigurations.selectedItems():
            item.setSelected(False)

    def _set_final_test_sites(self, visible):
        for index in range(self.finaltestSites.count()):
            item = self.finaltestSites.item(index)
            if not visible:
                item.setFlags(QtCore.Qt.NoItemFlags)
            else:
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

    def _does_name_already_exist(self, name):
        for index in range(self.finaltestAvailableConfigurations.count()):
            item = self.finaltestAvailableConfigurations.item(index)
            if item.text() == name:
                return True

        return False

    def _right_button_clicked(self):
        if not self._does_name_already_exist(self.name):
            self.finaltestAvailableConfigurations.addItem(self.name)

        self._available_pattern.update(self._pattern)
        self._pattern.clear()
        self.name = ''
        self.right_button.setEnabled(False)
        self._init_table()
        self._selected_available_item = ''

    def _left_button_clicked(self):
        self.finaltestAvailableConfigurations.clearFocus()
        item = self.finaltestAvailableConfigurations.currentItem()
        if not item:
            return

        for index in range(self.finaltestAvailableConfigurations.count()):
            element = self.finaltestAvailableConfigurations.item(index)
            if element.text() == item.text():
                self.finaltestAvailableConfigurations.takeItem(index)

        for key, _ in self._available_pattern.items():
            if key == item.text():
                self._available_pattern.pop(key)
                return

    def _init_table(self):
        for row in range(self.finaltestConfiguration.rowCount()):
            for col in range(self.finaltestConfiguration.columnCount()):
                item = self.finaltestConfiguration.item(row, col)
                if not item:
                    item = QtWidgets.QTableWidgetItem('')
                    self.finaltestConfiguration.setItem(row, col, item)

                if item.text():
                    self._update_final_test_item(item.text())

                item.setText('')
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

    def _clear_cell(self, point):
        item = self.finaltestConfiguration.itemAt(point)
        if not item:
            return

        item_content = item.text()
        if not item_content:
            return

        self._update_final_test_item(item_content)
        self.right_button.setEnabled(False)
        item.setText('')

    def _on_probing_toggeled(self):
        self.finaltestConfiguration.setColumnCount(self._max_parallelism_value)
        self.finaltestConfiguration.setRowCount(self._max_parallelism_value)
        self._init_table()
        self._pattern_type = PR

    def _on_final_test_toggeled(self):
        self.finaltestConfiguration.setColumnCount(self._max_parallelism_value)
        self._init_table()
        self.finaltestConfiguration.setRowCount(1)
        self._pattern_type = FT

    def _set_list_visible_items(self, count):
        for index in range(count):
            item = self.finaltestSites.item(index)
            if index < self._max_parallelism_value:
                item.setHidden(False)
                continue

            item.setHidden(True)

    def _final_test_list_clicked(self, index):
        self._site = None
        item = self.finaltestSites.itemFromIndex(index)
        if not self._is_site_selectable(item):
            return

        self._site = item

    def _table_cell_clicked(self, row, column):
        if not self._site:
            return

        if not self._site.text():
            return

        item = self.finaltestConfiguration.item(row, column)
        if not self._is_site_selectable(self._site):
            return

        # we should update site list when we override an already set cell
        if item.text():
            self._update_final_test_item(item.text())

        item.setText(self._site.text())
        self._site.setFlags(QtCore.Qt.NoItemFlags)
        if not self._are_all_sites_used():
            return

        self._verify_table()

    def _is_site_selectable(self, site):
        flag = site.flags()
        if not bool(flag & QtCore.Qt.ItemIsSelectable):
            return False

        return True

    def _update_final_test_item(self, name):
        for index in range(self._max_parallelism_value):
            item = self.finaltestSites.item(index)
            if item.text() == name:
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def _are_all_sites_used(self):
        for index in range(self._max_parallelism_value):
            item = self.finaltestSites.item(index)
            if self._is_site_selectable(item):
                self.right_button.setEnabled(False)
                return False

        return True

# PCBs
    def _max_parallelism_value_changed(self, selected_parallelism):
        if not self.maxParallelism.isEnabled():
            return

        if self._max_parallelism_value == 1:
            self.multisiteLoadboard.setEnabled(False)
            self.multisiteDIB.setEnabled(False)
            self.multisiteProbecard.setEnabled(False)

            self._multi_site_loadboard_value = ''
            self._multi_site_probecard_value = ''
            self._multi_site_dib_value = ''

            self.probecardLink.setDisabled(True)
            self.finaltestConfiguration.setColumnCount(1)
            self.finaltestConfiguration.setRowCount(1)
        else:
            self.multisiteLoadboard.setEnabled(True)
            self.multisiteDIB.setEnabled(True)
            self.multisiteProbecard.setEnabled(True)
            self.probecardLink.setDisabled(False)
            self.finaltestConfiguration.setColumnCount(self._max_parallelism_value)
            if self.probing_button.isChecked():
                self.finaltestConfiguration.setRowCount(self._max_parallelism_value)
            else:
                self.finaltestConfiguration.setRowCount(1)

            self._deselect_list_item()

        self._init_table()
        self._set_list_visible_items(self.finaltestSites.count())
        self._set_final_test_sites(True)
        self._verify()

    def _link_probecard(self):
        if not self._single_site_probecard_value:
            return

        self._multi_site_probecard_value = self._single_site_probecard_value

    def _verify(self):
        if self.hardware.text() == 'HW0':
            # when HW0 is set everything is allowed we do not need to check our entries
            self.OKButton.setEnabled(True)
            self.tabLayout.setTabEnabled(1, False)
            self.tabLayout.setTabEnabled(2, False)
            return

        self.feedback.setText('')
        self.OKButton.setEnabled(False)

        if self._max_parallelism_value == 1:
            if not self._single_site_loadboard_value:
                self.feedback.setText("no singlesite_loadboard is specified")

        else:
            if self._single_site_dib_value and not self._multi_site_dib_value:
                self.feedback.setText("no multisite_dib is specified")

            if not self._single_site_dib_value and self._multi_site_dib_value:
                self.feedback.setText("no singlesite_dib is specified ")

            if self._single_site_probecard_value and not self._multi_site_probecard_value:
                self.feedback.setText("no multisite_Probecard is specified ")

            if not self._single_site_probecard_value and self._multi_site_probecard_value:
                self.feedback.setText("no singlesite_Probecard is specified ")

            if self._single_site_loadboard_value == self._multi_site_loadboard_value:
                self.feedback.setText("single- and multisiteloadboad could not habe same name")

            if not self._multi_site_loadboard_value:
                self.feedback.setText("no multisite_loadboard is specified")

            if not self._single_site_loadboard_value:
                self.feedback.setText("no singlesite_loadboard is specified")

            # TODO: do we need to check this case
            # if self._single_site_dib_value == self._single_site_dib_value:
            #     self.feedback.setText("no singlesite_loadboard is specified")

        if self.feedback.text() == '':
            self.OKButton.setEnabled(True)

    def _verify_table(self):
        pattern = self._get_pattern()
        name = self._pattern_type + str(len(pattern))
        if self._does_pattern_exist(name, pattern):
            self.feedback.setText("pattern exists already")
            self.feedback.setStyleSheet('color: orange')
            self.right_button.setEnabled(False)
            return

        self.feedback.setText("")
        if not self._selected_available_item:
            names = []
            for index in range(self.finaltestAvailableConfigurations.count()):
                item = self.finaltestAvailableConfigurations.item(index)
                if name not in item.text():
                    continue

                names.append(item.text())

            if len(names) == 0:
                name += 'A'
            else:
                name = names[-1]
                new_char = chr(ord(name[-1]) + 1)
                name = name[:-1]
                name += new_char
        else:
            name = self._selected_available_item

        self.name = name
        self._pattern[name] = pattern
        self.right_button.setEnabled(True)

    def _get_pattern(self):
        pattern = []
        for row in range(self.finaltestConfiguration.rowCount()):
            row_elements = []
            for column in range(self.finaltestConfiguration.columnCount()):
                item_content = self.finaltestConfiguration.item(row, column).text()
                if item_content:
                    row_elements.append(int(item_content))
                else:
                    row_elements.append(0)

            pattern.append(tuple(row_elements))

        return pattern

    def _does_pattern_exist(self, name, pattern):
        if self._available_definiton:
            # hardware exists already, edit case
            pass

        for key, value in self._available_pattern.items():
            if name in key:
                if value == pattern:
                    return True

        return False

    @property
    def _max_parallelism_value(self):
        return int(self.maxParallelism.currentText())

    @property
    def _single_site_loadboard_value(self):
        return self.singlesiteLoadboard.text()

    @property
    def _multi_site_loadboard_value(self):
        return self.multisiteLoadboard.text()

    @_multi_site_loadboard_value.setter
    def _multi_site_loadboard_value(self, value):
        self.multisiteLoadboard.setText(value)

    @property
    def _single_site_probecard_value(self):
        return self.singlesiteProbecard.text()

    @property
    def _multi_site_probecard_value(self):
        return self.multisiteProbecard.text()

    @_multi_site_probecard_value.setter
    def _multi_site_probecard_value(self, value):
        self.multisiteProbecard.setText(value)

    @property
    def _single_site_dib_value(self):
        return self.singlesiteDIB.text()

    @property
    def _multi_site_dib_value(self):
        return self.multisiteDIB.text()

    @_multi_site_dib_value.setter
    def _multi_site_dib_value(self, value):
        self.multisiteDIB.setText(value)

    def _collect_instruments(self):
        retVal = []
        for row in range(0, self.usedInstruments.rowCount()):
            item = self.usedInstruments.item(row, 2)
            retVal.append(item.text())
        return retVal

    def _collect_actuators(self):
        retVal = {'PR': [], 'FT': []}
        for row in range(0, self.usedActuators.rowCount()):
            actuator_type = self.usedActuators.item(row, 0).text()
            used_in_probing = self.usedActuators.item(row, 1).checkState() == 2
            used_in_final = self.usedActuators.item(row, 2).checkState() == 2
            if used_in_probing:
                retVal['PR'].append(actuator_type)
            if used_in_final:
                retVal['FT'].append(actuator_type)
        return retVal

    def _get_current_configuration(self):
        return {'hardware': self.hardware.text(),
                'PCB':
                {'SingleSiteLoadboard': self.singlesiteLoadboard.text(),
                 'SingleSiteDIB': self.singlesiteDIB.text(),
                 'SingleSiteDIBisCable': self.singleSiteDIBisCable.isChecked(),
                 'SignleSiteProbeCard': self.singlesiteProbecard.text(),
                 'MultiSiteLoadboard': self.multisiteLoadboard.text(),
                 'MultiSiteDIB': self.multisiteDIB.text(),
                 'MultiSiteDIBisCable': self.multiSiteDIBisCable.isChecked(),
                 'MultiSiteProbeCard': self.multisiteProbecard.text(),
                 'MaxParallelism': int(self.maxParallelism.currentText())},
                'Parallelism': self._available_pattern,
                'tester': self.tester.currentText(),
                'Actuator': self._collect_actuators(),
                'Instruments': self._collect_instruments()}

# instruments
    def testerChanged(self, new_tester):
        print(f"testerChanged to '{new_tester}'")

    def availableInstrumentsSelectionChanged(self):
        print("available Instruments selection changed")

    def addingInstrument(self):
        theInstrument = self.availableInstruments.currentItem()
        if type(theInstrument) is InstrumentListItem:
            self.__add_instrument(theInstrument)

    def __add_instrument(self, instrument):
        rowPosition = self.usedInstruments.rowCount()
        # Don't add the instrument, if it was added before
        for i in range(0, rowPosition):
            used_intrument_name = self.usedInstruments.item(i, 2).text()
            if used_intrument_name == instrument.instrument_data["name"]:
                return

        self.usedInstruments.insertRow(rowPosition)
        self.usedInstruments.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(instrument.instrument_data["display_name"]))
        self.usedInstruments.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(instrument.instrument_data["manufacturer"]))
        self.usedInstruments.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(instrument.instrument_data["name"]))
        for i in range(0, 3):
            theItem = self.usedInstruments.item(rowPosition, i)
            theItem.setFlags(theItem.flags() & ~ QtCore.Qt.ItemIsEditable)

    def populate_selected_instruments(self, instrument_list):
        # The instrumentlist contains just the names of the instrument, we
        # need to find them in the available instrument lists
        for i in range(0, self.availableInstruments.topLevelItemCount()):
            manufacturer_node = self.availableInstruments.topLevelItem(i)
            for i in range(0, manufacturer_node.childCount()):
                instrument_node = manufacturer_node.child(i)
                if type(instrument_node) is InstrumentListItem:
                    if instrument_node.instrument_data["name"] in instrument_list:
                        self.__add_instrument(instrument_node)

    def removingInstrument(self):
        self.usedInstruments.removeRow(self.usedInstruments.currentRow())

    def checkInstrumentUsage(self):
        print("check Instrument Usage")

# Actuator
    def populate_selected_actuators(self, actuator_settings):
        for row in range(0, self.usedActuators.rowCount()):
            actuator_type = self.usedActuators.item(row, 0).text()
            if 'PR' in actuator_settings:
                if actuator_type in actuator_settings['PR']:
                    self.usedActuators.item(row, 1).setCheckState(2)
                else:
                    self.usedActuators.item(row, 1).setCheckState(0)

            if 'FT' in actuator_settings:
                if actuator_type in actuator_settings['FT']:
                    self.usedActuators.item(row, 2).setCheckState(2)
                else:
                    self.usedActuators.item(row, 2).setCheckState(0)

    def collapseAvailableInstruments(self):
        print("collapse available Instruments")

    def expandAvailableInstruments(self):
        print("exapnding available Instruments")

    def checkActuatorUsage(self):
        print("check Actuator Usage")

# Parallelism
# General
    def CancelButtonPressed(self):
        self.reject()

    def OKButtonPressed(self):
        self.project_info.add_hardware(self._get_current_configuration())
        self.accept()


def new_hardwaresetup_dialog(project_info):
    newHardwaresetupWizard = HardwareWizard(project_info)
    newHardwaresetupWizard.exec_()
    del(newHardwaresetupWizard)


if __name__ == '__main__':
    from ATE.org.navigation import ProjectNavigation, run_dummy_main
    project_info = ProjectNavigation(r'C:\Users\hoeren\__spyder_workspace__\CTCA')
    run_dummy_main(project_info, HardwareWizard)
