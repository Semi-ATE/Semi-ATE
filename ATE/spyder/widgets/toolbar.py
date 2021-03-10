# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 18:18:33 2020

@author: hoeren
"""
# from ATE.testers import SCT_testers
import qtawesome as qta
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from spyder.api.widgets.toolbars import ApplicationToolbar


class ToolBar(ApplicationToolbar):
    ID = 'ate_toolbar'

    def __init__(self, project_info, parent, identifier):
        super().__init__(parent, identifier)
        self.parent = parent
        self.setMovable(False)
        self.active_tester = ''
        self.active_hardware = ''
        self.active_base = ''
        self.active_target = ''
        self.project_info = project_info

        self._setup()
        self.init_toolbar_items()
        self._connect_event_handler()

    def __call__(self, project_info):
        self.project_info = project_info

        self.hardware_combo.blockSignals(True)
        self._init_hardware()
        self.hardware_combo.blockSignals(False)
        self._update_target()
        hardware, base, target = self.project_info.load_project_settings()
        self._hardware_changed(hardware)
        self._base_changed(base)
        self._update_target()

        self.project_info.update_toolbar_elements(hardware, base, target)
        self.project_info.store_settings(hardware, base, target)

    def init_toolbar_items(self):
        run_action = self.parent.create_action(
            name="rune",
            text="RunE",
            icon=self.parent.create_icon("run"),
            triggered=self.parent.run_ate_project,
        )

        # Add items to toolbar
        for item in [run_action, self.hardware_label,
                     self.hardware_combo, self.base_label, self.base_combo,
                     self.target_label, self.target_combo]:
            self.parent.add_item_to_toolbar(
                item,
                self,
                "run",
            )

    def _setup(self):
        self._setup_hardware()
        self._setup_base()
        self._setup_target()

    def _setup_hardware(self):
        self.hardware_label = QtWidgets.QLabel("Hardware:")
        self.hardware_label.setStyleSheet("background-color: transparent;")
        self.hardware_combo = QtWidgets.QComboBox()
        self.hardware_combo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.hardware_combo.setCurrentText(self.active_hardware)

    def _init_hardware(self):
        self.hardware_combo.clear()
        available_hardwares = self.project_info.get_active_hardware_names()
        self.hardware_combo.addItems(available_hardwares)
        # for hw in available_hardwares:
        #     self.hardware_combo.addItem(hw.name)
        self.active_hardware = '' if len(available_hardwares) == 0 else available_hardwares[len(available_hardwares) - 1]
        self.hardware_combo.setCurrentIndex(0 if len(available_hardwares) == 0 else len(available_hardwares) - 1)

    def _setup_base(self):
        self.base_label = QtWidgets.QLabel("Base:")
        self.base_label.setStyleSheet("background-color: transparent;")

        self.base_combo = QtWidgets.QComboBox()
        self.base_combo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.base_combo.addItems(['', 'PR', 'FT'])

    def _setup_target(self):
        self.target_label = QtWidgets.QLabel("Target:")
        self.target_label.setStyleSheet("background-color: transparent;")

        self.target_combo = QtWidgets.QComboBox()
        self.target_combo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)
        self.target_combo.addItems([''])
        self.target_combo.setCurrentText(self.active_target)

    def _connect_event_handler(self):
        self.hardware_combo.currentTextChanged.connect(self._hardware_changed)
        self.base_combo.currentTextChanged.connect(self._base_changed)
        self.target_combo.currentTextChanged.connect(self._target_changed)
        self.parent.hardware_added.connect(self._add_new_hardware)
        self.parent.hardware_removed.connect(self._remove_hardware)
        self.parent.update_target.connect(self._target_update)
        self.parent.select_target.connect(self._target_selected)
        self.parent.update_settings.connect(self._settings_update)
        self.parent.hardware_activated.connect(self._update_hardware)


    @QtCore.pyqtSlot(str)
    def _target_selected(self, target):
        self.target_combo.setCurrentText(target)
        # self.project_info.update_toolbar_elements(self._get_hardware(), self._get_base(), self._get_target())

    @QtCore.pyqtSlot(str, str, str)
    def _settings_update(self, hardware, base, target):
        self.hardware_combo.setCurrentText(hardware)
        self.base_combo.setCurrentText(base)
        self._update_target()
        self.target_combo.setCurrentText(target)

    @QtCore.pyqtSlot(str)
    def _add_new_hardware(self, hardware):
        self.hardware_combo.addItem(hardware)
        self.hardware_combo.setCurrentText(hardware)

    @QtCore.pyqtSlot(str)
    def _remove_hardware(self, hardware):
        self.hardware_combo.removeItem(self.hardware_combo.findText(hardware))

    @QtCore.pyqtSlot()
    def _target_update(self):
        self._update_target()

    @QtCore.pyqtSlot(str)
    def _update_hardware(self, hardware):
        self.hardware_combo.setCurrentText(hardware)

    @QtCore.pyqtSlot()
    def _rescan_testers(self):
        self.tester_combo.blockSignals(True)
        self.testers.rescan()
        tester_list = [''] + self.testers.report()
        self.tester_combo.clear()
        self.tester_combo.addItems(tester_list)
        if self.active_tester in tester_list:
            current_target_index = self.tester_combo.findText(self.project_info.active_target, QtCore.Qt.MatchExactly)
            self.tester_combo.setCurrentIndex(current_target_index)
        else:
            # TODO: what to do here ?
            self.tester_combo.setCurrentIndex(0)
        self.tester_combo.blockSignals(False)

    @QtCore.pyqtSlot(str)
    def _tester_changed(self, selected_tester):
        self.active_tester = selected_tester

    @QtCore.pyqtSlot(str)
    def _hardware_changed(self, selected_hardware):
        self.active_hardware = selected_hardware
        self.project_info.active_hardware = selected_hardware
        self._update_target()
        self.project_info.update_toolbar_elements(self._get_hardware(), self._get_base(), self._get_target())
        self.project_info.store_settings(self._get_hardware(), self._get_base(), self._get_target())
        self.parent.select_hardware.emit(selected_hardware)

    @QtCore.pyqtSlot(str)
    def _base_changed(self, selected_base):
        if(self.active_base == selected_base):
            return

        self.active_base = selected_base
        self.project_info.active_base = selected_base
        self._update_target()

        self.parent.select_base.emit(selected_base)
        self.project_info.update_toolbar_elements(self._get_hardware(), self._get_base(), self._get_target())
        self.project_info.store_settings(self._get_hardware(), self._get_base(), self._get_target())

    @QtCore.pyqtSlot(str)
    def _target_changed(self, selected_target):
        # the fact that we have a target to change to, means that there is a navigator ... no?
        self.active_target = selected_target
        self.project_info.active_target = selected_target
        self.parent.select_target.emit(selected_target)

        if self.active_target in self.project_info.get_active_device_names_for_hardware(self.active_hardware):
            self.base_combo.blockSignals(True)
            self.base_combo.setCurrentText('FT')
            self.base_combo.blockSignals(False)
        elif self.active_target in self.project_info.get_active_die_names_for_hardware(self.active_hardware):
            self.base_combo.blockSignals(True)
            self.base_combo.setCurrentText('PR')
            self.base_combo.blockSignals(False)
        else:
            pass

        self.project_info.update_toolbar_elements(self._get_hardware(), self._get_base(), self._get_target())
        self.project_info.store_settings(self._get_hardware(), self._get_base(), self._get_target())

    def _update_target(self):
        self.target_combo.blockSignals(True)
        self.target_combo.clear()
        self.target_combo.addItem('')
        if self._get_base() == 'FT':
            self.target_combo.addItems(self.project_info.get_active_device_names_for_hardware(self.active_hardware))

        elif self._get_base() == 'PR':
            self.target_combo.addItems(self.project_info.get_active_die_names_for_hardware(self.active_hardware))

        else:
            pass

        self.project_info.update_toolbar_elements(self._get_hardware(), self._get_base(), self._get_target())
        self.target_combo.blockSignals(False)

    def on_run(self):
        print("run button pressed")

    def info_pressed(self):
        print("info button pressed")

    def setting_pressed(self):
        pass

    def _get_hardware(self):
        return self.hardware_combo.currentText()

    def _get_base(self):
        return self.base_combo.currentText()

    def _get_target(self):
        return self.target_combo.currentText()

    def clean_up(self):
        self.hardware_combo.blockSignals(True)
        self.base_combo.blockSignals(True)
        self.target_combo.blockSignals(True)
        self.hardware_combo.clear()
        self.base_combo.setCurrentText('')
        self.target_combo.clear()
        self.hardware_combo.blockSignals(False)
        self.base_combo.blockSignals(False)
        self.target_combo.blockSignals(False)
