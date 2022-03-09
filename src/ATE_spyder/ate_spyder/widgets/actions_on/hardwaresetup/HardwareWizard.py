# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 09:52:27 2020

@author: hoeren
"""
import os
import re

import qtawesome as qta
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from ate_projectdatabase.Hardware import DB_KEYS
from ate_projectdatabase.Utils import BaseType
from ate_semiateplugins.pluginmanager import get_plugin_manager
from ate_spyder.widgets.actions_on.hardwaresetup.HardwareWizardListItem import HardwareWizardListItem
from ate_spyder.widgets.actions_on.hardwaresetup.ParallelismWidget import ParallelismWidget
from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog
from ate_spyder.widgets.validation import valid_pcb_name_regex


class HardwareWizard(BaseDialog):
    def __init__(self, project_info):
        super().__init__(__file__, project_info.parent)
        self.project_info = project_info
        self._plugin_manager = get_plugin_manager()
        self._plugin_configurations = {}

        self._availableTesters = {}
        self.is_active = True
        self.is_read_only = False

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

    # Testers
        for tester_list in self._plugin_manager.hook.get_tester_names():
            for tester_type in tester_list:
                self._availableTesters[tester_type["display_name"]] = tester_type["name"]
                self.tester.addItem(tester_type["display_name"])
        if self.tester.count() > 0:
            self.tester.setCurrentIndex(0)

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

        self._set_parallelism_sites_count()

    # Instruments
        # At this point instruments will be displayed as a plain list
        # -> in the prototype the instruments where grouped as tree
        # using the manufacterer of the respective Instrument.
        # We might need something similar here too, but as of now, the
        # Plugin API does not provide us with a means of extracting a group
        instrument_lists = self._plugin_manager.hook.get_instrument_names()
        for instrument_list in instrument_lists:
            for instrument in instrument_list:
                self._append_instrument_to_manufacturer(instrument)

    # GP Functions
        gpfunction_lists = self._plugin_manager.hook.get_general_purpose_function_names()
        for gpfunction_list in gpfunction_lists:
            for gpfunction in gpfunction_list:
                self._append_gpfunction_to_manufacturer(gpfunction)

    # general
        self.feedback.setText('')
        self.feedback.setStyleSheet('color: orange')

        self.tabLayout.setCurrentIndex(0)
        self.parallelism_widget = ParallelismWidget(self, self._max_parallelism_value)
        self.tabLayout.addTab(self.parallelism_widget, "Parallelism")

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
        instrumentNode = HardwareWizardListItem(manufacturer_node, instrument)
        manufacturer_node.addChild(instrumentNode)

    def _get_gpmanufacturer_node(self, manufacterer):
        for mfg in range(0, self.availableFunctions.topLevelItemCount()):
            item = self.availableFunctions.topLevelItem(mfg)
            if item.text(0) == manufacterer:
                return item

        # Manufacturer does not exist yet, create it and return it:
        the_manufacturer = QtWidgets.QTreeWidgetItem([manufacterer])
        self.availableFunctions.addTopLevelItem(the_manufacturer)
        return the_manufacturer

    def _append_gpfunction_to_manufacturer(self, gpfunction):
        # ToDo: Rename instrument node to something more generic
        manufacturer = gpfunction["manufacturer"]
        manufacturer_node = self._get_gpmanufacturer_node(manufacturer)
        instrumentNode = HardwareWizardListItem(manufacturer_node, gpfunction)
        manufacturer_node.addChild(instrumentNode)

    def _set_icons(self):
        self.collapse.setIcon(qta.icon('mdi.unfold-less-horizontal', color='orange'))
        self.expand.setIcon(qta.icon('mdi.unfold-more-horizontal', color='orange'))
        self.addInstrument.setIcon(qta.icon('mdi.arrow-right-bold', color='orange'))
        self.removeInstrument.setIcon(qta.icon('mdi.arrow-left-bold', color='orange'))
        self.addGPFunction.setIcon(qta.icon('mdi.arrow-right-bold', color='orange'))
        self.removeGPFunction.setIcon(qta.icon('mdi.arrow-left-bold', color='orange'))

    # Actuator
        self.probecardLink.setIcon(qta.icon('mdi.link', color='orange'))

    def _connect_event_handler(self):
        # PCBs
        self.singlesiteLoadboard.textChanged.connect(self._verify)
        self.singlesiteDIB.textChanged.connect(self._verify)
        self.singlesiteProbecard.textChanged.connect(self._verify)

        self.probecardLink.clicked.connect(self._link_probecard)

        self.maxParallelism.currentTextChanged.connect(self._max_parallelism_value_changed)
        self.multisiteLoadboard.textChanged.connect(self._verify)
        self.multisiteProbecard.textChanged.connect(self._verify)
        self.multisiteDIB.textChanged.connect(self._verify)

        # Instruments
        self.tester.currentTextChanged.connect(self.testerChanged)
        self.collapse.clicked.connect(self.collapseAvailableInstruments)
        self.expand.clicked.connect(self.expandAvailableInstruments)
        self.addInstrument.clicked.connect(self.addingInstrument)
        self.addGPFunction.clicked.connect(self.addingGPFunction)
        self.removeInstrument.clicked.connect(self.removingInstrument)
        self.removeGPFunction.clicked.connect(self.removingGPFunction)
        self.checkInstruments.clicked.connect(self.checkInstrumentUsage)
        self.availableInstruments.itemSelectionChanged.connect(self.availableInstrumentsSelectionChanged)
        self.availableInstruments.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.availableInstruments.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.usedFunctions.doubleClicked.connect(lambda: self.__display_config_dialog(self.usedFunctions))

        self.usedInstruments.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.usedInstruments.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.usedInstruments.doubleClicked.connect(lambda: self.__display_config_dialog(self.usedInstruments))

        # Actuator
        self.checkActuators.clicked.connect(self.checkActuatorUsage)

        # general
        self.CancelButton.clicked.connect(self.CancelButtonPressed)
        self.OKButton.clicked.connect(self.OKButtonPressed)

# PCBs
    def _max_parallelism_value_changed(self, selected_parallelism):
        self.parallelism_widget.parallelism_count = self._max_parallelism_value
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
        else:
            self.multisiteLoadboard.setEnabled(True)
            self.multisiteDIB.setEnabled(True)
            self.multisiteProbecard.setEnabled(True)
            self.probecardLink.setDisabled(False)
        self._verify()

    def _link_probecard(self):
        if not self._single_site_probecard_value:
            return

        self._multi_site_probecard_value = self._single_site_probecard_value

    def _verify(self):
        if self.hardware.text() == 'HW0':
            # when HW0 is set everything is allowed we do not need to check our entries
            self.OKButton.setEnabled(True)
            return

        self.feedback.setText('')
        self.OKButton.setEnabled(False)

        if self.tester.currentIndex() < 0:
            self.feedback.setText("no tester selected")

        elif self._max_parallelism_value == 1:
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
                self.feedback.setText("single- and multisiteloadboad could not have the same name")

            if not self._multi_site_loadboard_value:
                self.feedback.setText("no multisite_loadboard is specified")

            if not self._single_site_loadboard_value:
                self.feedback.setText("no singlesite_loadboard is specified")

            # TODO: do we need to check this case
            # if self._single_site_dib_value == self._single_site_dib_value:
            #     self.feedback.setText("no singlesite_loadboard is specified")

        min_required_parallelism = self.parallelism_widget.parallelism_store.min_required_parallelism()
        if self._max_parallelism_value < min_required_parallelism:
            self.feedback.setText(f'There is a parallelism configuration which needs more sites enabled. At least {min_required_parallelism}.')

        if self.feedback.text() == '':
            self.OKButton.setEnabled(True)

    @property
    def _max_parallelism_value(self):
        ret_val = 0
        try:
            ret_val = int(self.maxParallelism.currentText())
        except ValueError:
            pass
        return ret_val

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

    def _collect_gpfunctions(self):
        retVal = []
        for row in range(0, self.usedFunctions.rowCount()):
            item = self.usedFunctions.item(row, 2)
            retVal.append(item.text())
        return retVal

    def _collect_actuators(self):
        retVal = {BaseType.PR.value: [], BaseType.FT.value: []}
        for row in range(0, self.usedActuators.rowCount()):
            actuator_type = self.usedActuators.item(row, 0).text()
            used_in_probing = self.usedActuators.item(row, 1).checkState() == 2
            used_in_final = self.usedActuators.item(row, 2).checkState() == 2
            if used_in_probing:
                retVal[BaseType.PR.value].append(actuator_type)
            if used_in_final:
                retVal[BaseType.FT.value].append(actuator_type)
        return retVal

    def _get_current_configuration(self):
        testername = ""
        if self.tester.currentIndex() >= 0:
            testername = self._availableTesters[self.tester.currentText()]

        return {
            DB_KEYS.HARDWARE.DEFINITION.PCB.KEY(): {
                DB_KEYS.HARDWARE.DEFINITION.PCB.SINGLE_SITE_LOADBOARD: self.singlesiteLoadboard.text(),
                DB_KEYS.HARDWARE.DEFINITION.PCB.SINGLE_SITE_DIB: self.singlesiteDIB.text(),
                DB_KEYS.HARDWARE.DEFINITION.PCB.SINGLE_SITE_DIB_IS_CABLE: self.singleSiteDIBisCable.isChecked(),
                DB_KEYS.HARDWARE.DEFINITION.PCB.SINGLE_SITE_PROBE_CARD: self.singlesiteProbecard.text(),
                DB_KEYS.HARDWARE.DEFINITION.PCB.MULTI_SITE_LOADBOARD: self.multisiteLoadboard.text(),
                DB_KEYS.HARDWARE.DEFINITION.PCB.MULTI_SITE_DIB: self.multisiteDIB.text(),
                DB_KEYS.HARDWARE.DEFINITION.PCB.MULTI_SITE_DIB_IS_CABLE: self.multiSiteDIBisCable.isChecked(),
                DB_KEYS.HARDWARE.DEFINITION.PCB.MULTI_SITE_CARD: self.multisiteProbecard.text(),
                DB_KEYS.HARDWARE.DEFINITION.PCB.MAX_PARALLELISM: int(self.maxParallelism.currentText())
            },
            DB_KEYS.HARDWARE.DEFINITION.PARALLELISM.KEY(): self.parallelism_widget.parallelism_store.serialize(),
            DB_KEYS.HARDWARE.DEFINITION.TESTER: testername,
            DB_KEYS.HARDWARE.DEFINITION.ACTUATOR.KEY(): self._collect_actuators(),
            DB_KEYS.HARDWARE.DEFINITION.INSTRUMENTS.KEY(): self._collect_instruments(),
            DB_KEYS.HARDWARE.DEFINITION.GP_FUNCTIONS.KEY(): self._collect_gpfunctions()
        }

# instruments
    def testerChanged(self, new_tester):
        self._set_parallelism_sites_count()

    def _set_parallelism_sites_count(self):
        if not self._availableTesters:
            return
        selected_name = self._availableTesters[self.tester.currentText()]
        selected_tester = self._plugin_manager.hook.get_tester(tester_name=selected_name)[0]
        tester_sites_count = selected_tester.get_sites_count()

        sites = [str(site + 1) for site in range(tester_sites_count)]
        self.maxParallelism.blockSignals(True)
        self.maxParallelism.clear()
        self.maxParallelism.addItems(sites)
        self.maxParallelism.setCurrentIndex(0)
        self.maxParallelism.blockSignals(False)

    def availableInstrumentsSelectionChanged(self):
        print("available Instruments selection changed")

    def addingInstrument(self):
        theInstrument = self.availableInstruments.currentItem()
        if type(theInstrument) is HardwareWizardListItem:
            self.__add_instrument(theInstrument)

    def addingGPFunction(self):
        theFunction = self.availableFunctions.currentItem()
        if type(theFunction) is HardwareWizardListItem:
            self.__add_gpfunction(theFunction)

    def __add_instrument(self, instrument):
        self.__add_unique_item_to_list(instrument, self.usedInstruments)

    def __add_gpfunction(self, gpfunction):
        self.__add_unique_item_to_list(gpfunction, self.usedFunctions)

    def __add_unique_item_to_list(self, item, table_widget):
        rowPosition = table_widget.rowCount()
        # Don't add the item, if it was added before
        for i in range(0, rowPosition):
            used_function_name = table_widget.item(i, 2).text()
            if used_function_name == item.item_data["name"]:
                return

        table_widget.insertRow(rowPosition)
        table_widget.setItem(rowPosition, 0, QtWidgets.QTableWidgetItem(item.item_data["display_name"]))
        table_widget.setItem(rowPosition, 1, QtWidgets.QTableWidgetItem(item.item_data["manufacturer"]))
        table_widget.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(item.item_data["name"]))
        for i in range(0, 3):
            theItem = table_widget.item(rowPosition, i)
            theItem.setFlags(theItem.flags() & ~ QtCore.Qt.ItemIsEditable)

    def popuplate_item_list_widget(self, item_list, widget, add_cb):
        # The instrumentlist contains just the names of the instrument, we
        # need to find them in the available instrument lists
        for i in range(0, widget.topLevelItemCount()):
            manufacturer_node = widget.topLevelItem(i)
            for i in range(0, manufacturer_node.childCount()):
                item_node = manufacturer_node.child(i)
                if type(item_node) is HardwareWizardListItem:
                    if item_node.item_data["name"] in item_list:
                        add_cb(item_node)

    def populate_selected_instruments(self, instrument_list):
        self.popuplate_item_list_widget(instrument_list, self.availableInstruments, self.__add_instrument)

    def populate_selected_gpfunctions(self, function_list):
        self.popuplate_item_list_widget(function_list, self.availableFunctions, self.__add_gpfunction)

    def removingInstrument(self):
        self.usedInstruments.removeRow(self.usedInstruments.currentRow())

    def removingGPFunction(self):
        self.usedFunctions.removeRow(self.usedFunctions.currentRow())

    def checkInstrumentUsage(self):
        print("check Instrument Usage")

    def __display_config_dialog(self, table):
        function_row = table.currentItem().row()
        item = table.item(function_row, 2)
        function_name = item.text()
        cfgs = get_plugin_manager().hook.get_configuration_options(object_name=function_name)[0]
        from ate_spyder.widgets.actions_on.hardwaresetup.PluginConfigurationDialog import PluginConfigurationDialog
        current_config = self._plugin_configurations.get(function_name)
        dialog = PluginConfigurationDialog(self, function_name, cfgs, self.hardware.text(), self.project_info, current_config, self.is_read_only)
        dialog.exec_()
        self._plugin_configurations[function_name] = dialog.get_cfg()
        del(dialog)

# Actuator
    def populate_selected_actuators(self, actuator_settings):
        for row in range(self.usedActuators.rowCount()):
            actuator_type = self.usedActuators.item(row, 0).text()
            if BaseType.PR.value in actuator_settings:
                if actuator_type in actuator_settings[BaseType.PR.value]:
                    self.usedActuators.item(row, 1).setCheckState(QtCore.Qt.Checked)
                else:
                    self.usedActuators.item(row, 1).setCheckState(QtCore.Qt.Unchecked)

            if BaseType.FT.value in actuator_settings:
                if actuator_type in actuator_settings[BaseType.FT.value]:
                    self.usedActuators.item(row, 2).setCheckState(QtCore.Qt.Checked)
                else:
                    self.usedActuators.item(row, 2).setCheckState(QtCore.Qt.Unchecked)

    def collapseAvailableInstruments(self):
        print("collapse available Instruments")

    def expandAvailableInstruments(self):
        print("exapnding available Instruments")

    def checkActuatorUsage(self):
        print("check Actuator Usage")

    def select_tester(self, tester_name):
        for (display_name, available_tester_name) in self._availableTesters.items():
            if available_tester_name == tester_name:
                self.tester.setCurrentText(display_name)
                return

    def _store_plugin_configuration(self):
        for plugin_name, plugin_cfg in self._plugin_configurations.items():
            if plugin_cfg is not None:
                self.project_info.store_plugin_cfg(self.hardware.text(), plugin_name, plugin_cfg)

    def CancelButtonPressed(self):
        self.reject()

    def OKButtonPressed(self):
        self.project_info.add_hardware(self.hardware.text(), self._get_current_configuration())
        self._store_plugin_configuration()
        self.accept()


def new_hardwaresetup_dialog(project_info):
    newHardwaresetupWizard = HardwareWizard(project_info)
    newHardwaresetupWizard.exec_()
    del(newHardwaresetupWizard)
