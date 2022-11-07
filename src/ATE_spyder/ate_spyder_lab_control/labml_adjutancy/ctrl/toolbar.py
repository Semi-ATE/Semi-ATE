from enum import Enum
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from qtpy.QtCore import Signal
from spyder.api.widgets.toolbars import ApplicationToolbar

from ate_spyder.widgets.navigation import ProjectNavigation


class Event(Enum):
    Hardware = "hardware"
    Base = "base"
    Group = "group"


class ToolbarItems:
    RunGroupLabel = "rungroup_label"
    RunGroupCombo = "rungroup_combo"
    RunFlowLabel = "runflow_label"
    RunFlowCombo = "runflow_combo"


class ControlToolBar(ApplicationToolbar):
    ID = "control"

    # --- Signals
    # ------------------------------------------------------------------------
    sig_run_changed = Signal(str)

    def __init__(self, parent, identifier):
        super().__init__(parent, identifier)
        self.parent = parent
        self.project_info: ProjectNavigation = parent.project_info

        self._setup()
        self._connect_event_handler()

    def get_items(self):
        self.run_action = self.parent.create_action(name="rune", text="RunControl", icon=self.parent.create_icon("run"), triggered=self._run_flow)
        return [self.run_action, self.rungroup_label, self.rungroup_combo, self.runflow_label, self.runflow_combo]

    def _setup(self):
        self._setup_rungroup()
        self._setup_runflow()

    def _run_flow(self):
        prog_path = self.project_info.project_directory.joinpath(
            self.project_info.project_directory.name,
            self.project_info.active_hardware,
            self.project_info.active_base, f'{self.runflow_combo.currentText()}.py'
        )

        self.project_info.parent.sig_edit_goto_requested.emit(str(prog_path), 1, "")
        self.project_info.parent.sig_run_cell.emit()
        self.project_info.parent.sig_ate_progname.emit(self.runflow_combo.currentText())

    @QtCore.pyqtSlot()
    def _post_main_plugin_init(self):
        self._update_rungroup()
        self._update_runflow()

    def _setup_rungroup(self):
        self.rungroup_label = QtWidgets.QLabel("Flow Group:")
        self.rungroup_label.setStyleSheet("background-color: transparent;")
        self.rungroup_label.ID = ToolbarItems.RunGroupLabel

        self.rungroup_combo = QtWidgets.QComboBox()
        self.rungroup_combo.ID = ToolbarItems.RunGroupCombo
        self.rungroup_combo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)

    def _setup_runflow(self):
        self.runflow_label = QtWidgets.QLabel("Program:")
        self.runflow_label.setStyleSheet("background-color: transparent;")
        self.runflow_label.ID = ToolbarItems.RunFlowLabel

        self.runflow_combo = QtWidgets.QComboBox()
        self.runflow_combo.ID = ToolbarItems.RunFlowCombo
        self.runflow_combo.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)

    def _connect_event_handler(self):
        self.rungroup_combo.currentTextChanged.connect(self._rungroup_changed)
        self.runflow_combo.currentTextChanged.connect(self._runflow_changed)
        self.parent.init_done.connect(self._post_main_plugin_init)
        self.parent.select_hardware.connect(self._update_runflow)
        self.parent.select_base.connect(self._update_runflow)
        self.parent.select_target.connect(self._update_runflow)
        self.parent.database_changed.connect(self._update_runflow)
        self.parent.group_added.connect(self._update_rungroup)
        self.parent.group_removed.connect(self._update_rungroup)

    @QtCore.pyqtSlot(str)
    def _rungroup_changed(self, selected_group: str):
        self.rungroup_combo.blockSignals(True)
        self.rungroup_combo.setCurrentText(selected_group)
        self._update_runflow()
        self.rungroup_combo.blockSignals(False)
        self.sig_run_changed.emit(self.runflow_combo.currentText())

    @QtCore.pyqtSlot(str)
    def _runflow_changed(self, selected_flow: str):
        self.runflow_combo.setCurrentText(selected_flow)
        self.sig_run_changed.emit(self.runflow_combo.currentText())

    def _update_rungroup(self):
        groups = self.project_info.get_groups()
        self.rungroup_combo.blockSignals(True)
        current_group = self.rungroup_combo.currentText()
        self.rungroup_combo.clear()
        for group in groups:
            self.rungroup_combo.addItem(group.name)

        if current_group:
            self.rungroup_combo.setCurrentText(current_group)
        self.rungroup_combo.blockSignals(False)

    def _update_runflow(self):
        self.run_action.setEnabled(True)
        current_prog = self.runflow_combo.currentText()
        self.runflow_combo.clear()
        active_group = self.rungroup_combo.currentText()
        for program in self.project_info.get_programs():
            if program.hardware == self.project_info.active_hardware \
               and program.base == self.project_info.active_base \
               and program.target == self.project_info.active_target:

                if active_group != program.owner_name[-len(active_group) :]:
                    continue
                self.runflow_combo.blockSignals(True)
                self.runflow_combo.addItem(program.prog_name)
                self.runflow_combo.blockSignals(False)

        if self.runflow_combo.count() == 0:
            self.run_action.setEnabled(False)
            return

        if current_prog:
            self.runflow_combo.setCurrentText(current_prog)
