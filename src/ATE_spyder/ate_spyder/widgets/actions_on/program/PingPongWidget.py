from typing import TYPE_CHECKING, Optional, Tuple

from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QInputDialog, QListWidgetItem, QMessageBox, QTableWidgetItem, QWidget

from ate_projectdatabase.Utils import BaseType
from ate_projectdatabase.Hardware.ParallelismStore import ParallelismStore
from ate_projectdatabase.Hardware.ParallelismConfig import ParallelismConfig
from ate_projectdatabase.Hardware.PingPong import PingPong, PingPongStage
from ate_spyder.widgets.actions_on.hardwaresetup.EditHardwaresetupWizard import EditHardwaresetupWizard
from ate_spyder.widgets.actions_on.hardwaresetup.ViewHardwaresetupSettings import ViewHardwaresetupSettings
from ate_spyder.widgets.actions_on.utils.ItemTrace import ItemTrace

if TYPE_CHECKING:
    from ate_spyder.widgets.actions_on.program.TestProgramWizard import TestProgramWizard


class PingPongWidget(QWidget):
    def __init__(self, parent: Optional[QWidget]):
        super().__init__(parent=parent)
        self.tp_wizard: TestProgramWizard = parent
        uic.loadUi(__file__.replace(".py", ".ui"), self)

        self._ui_enabled = True
        self._update_parallelism_store()
        self._cur_parallelism = None
        self._cur_ping_pong_config = None
        self._cur_stage_selected = None
        self._setup_ui()
        self._setup_handlers()
        self._generate_parallelism_ui()

    def _update_parallelism_store(self):
        self.tp_wizard.parallelism_store = self.tp_wizard.project_info.get_hardware_parallelism_store(self.tp_wizard.project_info.active_hardware)
        self._generate_parallelism_ui()

    def save_config(self):
        self.tp_wizard.project_info.update_hardware_parallelism_store(self.tp_wizard.project_info.active_hardware, self.parallelism_store)

    @property
    def parallelism_store(self) -> ParallelismStore:
        return self.tp_wizard.parallelism_store

    @property
    def cur_parallelism(self) -> ParallelismConfig:
        return self._cur_parallelism

    @cur_parallelism.setter
    def cur_parallelism(self, value: ParallelismConfig):
        self._cur_parallelism = value
        self.cur_ping_pong_config = None
        self._generate_ping_pong_config_items()

    @property
    def cur_ping_pong_config(self) -> PingPong:
        return self._cur_ping_pong_config

    @cur_ping_pong_config.setter
    def cur_ping_pong_config(self, value: PingPong):
        self._cur_ping_pong_config = value
        self.cur_stage_selected = None
        self._generate_ping_pong_stages_items()

    @property
    def cur_stage_selected(self) -> PingPongStage:
        return self._cur_stage_selected

    @cur_stage_selected.setter
    def cur_stage_selected(self, value: PingPongStage):
        self._cur_stage_selected = value
        self._update_parallelism_view()

    def set_ui_enabled(self, value: bool = True):
        self._ui_enabled = value
        self.parallelism_edit.setEnabled(value)
        self.add_ping_pong_config.setEnabled(value)
        self.remove_ping_pong_config.setEnabled(value)
        self.ping_pong_stage_count.setEnabled(value)
        self.ping_pong_stages_reset.setEnabled(value)
        self.parallelism_view.setEnabled(value)

    def _setup_ui(self):
        self.parallelism.clear()
        self.ping_pong_config.clear()
        self.ping_pong_stages.clear()
        self.default_brush = QListWidgetItem('').background()

    def _setup_handlers(self):
        self.parallelism.currentItemChanged.connect(self._current_parallelism_changed_handler)
        self.parallelism_edit.clicked.connect(self._parallelism_edit_handler)
        self.add_ping_pong_config.clicked.connect(self._add_ping_pong_config_handler)
        self.remove_ping_pong_config.clicked.connect(self._remove_ping_pong_config_handler)
        self.ping_pong_config.currentItemChanged.connect(self._ping_pong_config_changed_handler)
        self.ping_pong_config.itemDoubleClicked.connect(self._ping_pong_config_double_clicked_handler)
        self.ping_pong_stage_count.valueChanged.connect(self._ping_pong_stage_count_handler)
        self.ping_pong_stages.currentItemChanged.connect(self._ping_pong_stages_changed_handler)
        self.ping_pong_stages_reset.clicked.connect(self._ping_pong_stages_reset_handler)
        self.parallelism_view.cellClicked.connect(self._parallelism_view_clicked_handler)
        self.parallelism_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.parallelism_view.customContextMenuRequested.connect(self._parallelism_view_right_clicked_handler)

    def _generate_parallelism_ui(self):
        self.parallelism.clear()
        self.parallelism.addItems(
            list(
                self.parallelism_store.get_all_matching_base(
                    BaseType(self.tp_wizard.project_info.active_base)
                ).keys()
            )
        )

    def _current_parallelism_changed_handler(self, cur_item, old_item):
        if cur_item is None:
            return
        self.cur_parallelism = self.parallelism_store.get(cur_item.text())
        self.ping_pong_stage_count.setMinimum(1)
        self.ping_pong_stage_count.setMaximum(self.cur_parallelism.sites_count)

        self.parallelism_view.clear()
        self._init_parallelism_view_ui()

    def _init_parallelism_view_ui(self):
        row_count = self.cur_parallelism.sites_count
        column_count = self.cur_parallelism.sites_count
        if self.cur_parallelism.base_type == BaseType.FT:
            row_count = 1
        self.parallelism_view.setRowCount(row_count)
        self.parallelism_view.setColumnCount(column_count)
        for site, coord in self.cur_parallelism.cells.items():
            item = QTableWidgetItem(str(site))
            self.parallelism_view.setItem(coord[1], coord[0], item)

    def _parallelism_edit_handler(self):
        if not self._verify_ping_pong():
            return
        self.save_config()
        self.cur_parallelism = None
        hardware_wizard = EditHardwaresetupWizard(self.tp_wizard.project_info, self.tp_wizard.project_info.active_hardware)
        ViewHardwaresetupSettings._setup_view(hardware_wizard, self.tp_wizard.project_info.active_hardware)
        hardware_wizard.parallelism_widget.set_ui_enabled(True)
        hardware_wizard.exec_()
        del(hardware_wizard)
        self._update_parallelism_store()

    def _generate_ping_pong_config_items(self):
        if self.cur_parallelism is None:
            self.ping_pong_config.clear()
            return
        self.ping_pong_config.blockSignals(True)
        self.ping_pong_config.clear()
        self.ping_pong_config.addItems(self.cur_parallelism.get_all_ping_pong_names())
        self.ping_pong_config.blockSignals(False)

    def _get_ping_pong_name_from_user(self) -> Tuple[bool, Optional[str]]:
        add_text = ''
        while True:
            new_name, ok = QInputDialog.getText(self, 'Ping-Pong Name', f'Provide a Ping-Pong name:\n{add_text}')
            if not ok:
                return ok, None
            if not new_name:
                add_text = ""
                continue
            if new_name in self.cur_parallelism.get_all_ping_pong_names():
                add_text = 'This name is already taken.'
                continue
            break
        return ok, new_name

    def _add_ping_pong_config_handler(self):
        if self.cur_parallelism is None:
            self.tp_wizard.Feedback.setText('Select a available parallelism.')
            return
        ok, new_name = self._get_ping_pong_name_from_user()
        if not ok:
            return

        stage_count = self.ping_pong_stage_count.value()
        self.cur_parallelism.add_ping_pong_config(new_name, stage_count)
        self._generate_ping_pong_config_items()
        self.ping_pong_config.setCurrentRow(self.ping_pong_config.count() - 1)
        self._verify_ping_pong()

    def _remove_ping_pong_config_handler(self):
        if self.cur_ping_pong_config is None:
            self.tp_wizard.Feedback.setText('No Ping-Pong configuration selected for removal.')
            return
        where = self.tp_wizard.project_info.get_ping_pong_in_executions(
            self.cur_parallelism.name, self.cur_ping_pong_config.id
        )
        if len(where) > 0:
            # Allow removel if ping_pong is only used in this test program
            if len(where) != 1 or where[0] != self.tp_wizard.prog_name:
                dependency_list = {
                    "Usage in other test programs":
                    [test_name for test_name in where if test_name != self.tp_wizard.prog_name]
                }
                ItemTrace(
                    dependency_list,
                    f'Ping Pong "{self.cur_ping_pong_config.name}"',
                    self,
                    message='Can not remove Ping Pong used by another test program'
                ).exec_()
                return

        warn_msg = QMessageBox(self)
        warn_msg.setText(f'Warning! This action will remove the ping pong configuration "{self.cur_ping_pong_config.name}" .')
        warn_msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        warn_msg.setDefaultButton(QMessageBox.Cancel)
        warn_result = warn_msg.exec_()
        if warn_result == QMessageBox.Cancel:
            return

        self.tp_wizard.execution_widget.ping_pong_remove_handler(
            self.cur_parallelism.name,
            self.cur_ping_pong_config.id
        )
        self.cur_parallelism.remove_ping_pong_config(self.cur_ping_pong_config)
        self.cur_ping_pong_config = None
        self._generate_ping_pong_config_items()
        self._verify_ping_pong()

    def _generate_ping_pong_stages_items(self):
        if self.cur_ping_pong_config is None:
            self.ping_pong_stages.clear()
            return
        selected_row = self.ping_pong_stages.currentRow()
        self.ping_pong_stages.blockSignals(True)
        self.ping_pong_stages.clear()
        self.ping_pong_stages.addItems(
            [
                str(list(pps.stage))
                for pps in self.cur_ping_pong_config.stages
            ]
        )
        self.ping_pong_stages.blockSignals(False)
        self.ping_pong_stages.setCurrentRow(selected_row)

    def _ping_pong_config_changed_handler(self, cur_item, old_item):
        if cur_item is None:
            return
        if not cur_item.text():
            return
        self.cur_ping_pong_config = self.cur_parallelism.get_ping_pong(cur_item.text())
        self.ping_pong_config.setCurrentItem(cur_item)
        self.ping_pong_stage_count.setValue(self.cur_ping_pong_config.stage_count)

    def _ping_pong_config_double_clicked_handler(self, cur_item):
        if cur_item is None:
            return
        if self.cur_ping_pong_config.name != cur_item.text():
            return
        ok, new_name = self._get_ping_pong_name_from_user()
        if not ok:
            return
        self.cur_ping_pong_config.name = new_name
        self._generate_ping_pong_config_items()

    def _ping_pong_stage_count_handler(self, new_value):
        if self.cur_ping_pong_config is None:
            return
        self.cur_ping_pong_config.stage_count = new_value
        self._generate_ping_pong_stages_items()
        self._verify_ping_pong()

    def _ping_pong_stages_changed_handler(self, cur_item, old_item):
        cur_index = self.ping_pong_stages.currentRow()
        if not cur_index >= 0:
            return
        self.cur_stage_selected = self.cur_ping_pong_config.stages[cur_index]

    def _ping_pong_stages_reset_handler(self):
        if self.cur_ping_pong_config is None:
            self.tp_wizard.Feedback.setText('No Ping-Pong configuration selected to reset.')
            return
        for stage in self.cur_ping_pong_config.stages:
            stage.stage.clear()
        self._generate_ping_pong_stages_items()
        self._verify_ping_pong()

    def _parallelism_view_clicked_handler(self, row, column):
        self.parallelism_view.clearSelection()
        if self.cur_stage_selected is None:
            return
        item = self.parallelism_view.item(row, column)
        if item is None:
            return
        site_num = int(item.text())
        if self.cur_ping_pong_config.is_site_used(site_num):
            return
        self.cur_stage_selected.stage.add(site_num)
        self._verify_ping_pong()
        self._generate_ping_pong_stages_items()
        self._update_parallelism_view()

    def _parallelism_view_right_clicked_handler(self, point):
        self.parallelism_view.clearSelection()
        if self.cur_stage_selected is None:
            return
        item = self.parallelism_view.itemAt(point)
        if item is None:
            return
        site_num = int(item.text())
        if site_num not in self.cur_stage_selected.stage:
            return
        self.cur_stage_selected.stage.remove(site_num)
        self._verify_ping_pong()
        self._generate_ping_pong_stages_items()
        self._update_parallelism_view()

    def _update_parallelism_view(self):
        if self.cur_parallelism is None:
            self.parallelism_view.clear()
            return
        if self.cur_ping_pong_config is None:
            return
        for site_num, coord in self.cur_parallelism.cells.items():
            item = self.parallelism_view.item(coord[1], coord[0])
            if item is None:
                continue
            if self.cur_ping_pong_config.is_site_used(site_num):
                if self.cur_stage_selected and site_num in self.cur_stage_selected.stage:
                    if self.parallelism_view.isEnabled():
                        item.setBackground(QtCore.Qt.darkGray)
                    else:
                        item.setBackground(QtCore.Qt.lightGray)
                else:
                    item.setBackground(self.default_brush)
            else:
                item.setBackground(QtCore.Qt.red)

    def _verify_ping_pong(self) -> bool:
        """This methode has the side effect to also call _verify() from TestProgramWizard"""
        self.tp_wizard.OKButton.setEnabled(False)
        self.parallelism_edit.setEnabled(False)
        for parallelism_config in self.parallelism_store.get_all().values():
            ok, msg = parallelism_config.are_all_configs_correct()
            if not ok:
                if msg:
                    self.tp_wizard.Feedback.setText(msg)
                else:
                    self.tp_wizard.Feedback.setText('There is an invalid PingPong Configuration')
                return False
        if self._ui_enabled:
            self.parallelism_edit.setEnabled(True)
        self.tp_wizard._verify()
        return True
