from typing import Dict, List, Optional, TYPE_CHECKING

from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QDialog, QListWidgetItem, QTableWidgetItem, QWidget

from ate_projectdatabase.Hardware.ParallelismStore import ParallelismStore
from ate_projectdatabase.Hardware.ParallelismConfig import ParallelismConfig
from ate_projectdatabase.Utils import BaseType
from ate_spyder.widgets.actions_on.utils.ItemTrace import ItemTrace

if TYPE_CHECKING:
    from ate_spyder.widgets.actions_on.hardwaresetup.HardwareWizard import HardwareWizard


class ParallelismWidget(QWidget):
    def __init__(self, parent: Optional['QWidget'], parallelism_count: int):
        super().__init__(parent=parent)
        self.hardware_wizard: HardwareWizard = parent
        uic.loadUi(__file__.replace(".py", ".ui"), self)
        self._selected_site_num = None
        self.parallelism_count = parallelism_count
        self.current_item: QListWidgetItem = None
        self.current_table: ParallelismConfig = None
        self._parallelism_store: ParallelismStore = ParallelismStore()
        self._setup_ui()
        self._setup_handlers()
        self._parallelism_add_list: Dict[str, int] = {}
        self._parallelism_remove_list: List[str] = []

    @property
    def parallelism_store(self):
        return self._parallelism_store

    @parallelism_store.setter
    def parallelism_store(self, store_from_db: ParallelismStore):
        self._parallelism_store = store_from_db
        self.testconfig_store.blockSignals(True)
        self.testconfig_store.clear()
        self.testconfig_store.addItems(list(self.parallelism_store.get_all().keys()))
        self.testconfig_store.blockSignals(False)

    def set_ui_enabled(self, value: bool = True):
        self.testsites.setEnabled(value)
        self.testconfig.setEnabled(value)
        self.reset_button.setEnabled(value)
        self.type_box.setEnabled(value)
        self.sites_count_select.setEnabled(value)
        self.add_testconfig.setEnabled(value)
        self.remove_testconfig.setEnabled(value)

    @property
    def parallelism_count(self):
        return self._parallelism_count

    @parallelism_count.setter
    def parallelism_count(self, value):
        self._parallelism_count = value
        self.sites_count_select.blockSignals(True)
        self.sites_count_select.clear()
        self.sites_count_select.addItems([str(num) for num in range(1, self.parallelism_count + 1)])
        self.sites_count_select.blockSignals(False)
        self.sites_count_select.setCurrentIndex(self.parallelism_count - 1)

    @property
    def selected_site_num(self):
        if (self._selected_site_num is not None
                and not 0 <= self._selected_site_num < self.current_table.sites_count):
            self.selected_site_num = 0
        return self._selected_site_num

    @selected_site_num.setter
    def selected_site_num(self, value: int):
        self._selected_site_num = value
        if value is None:
            self.testsites.clearSelection()
        else:
            self.testsites.setCurrentRow(value - 1)

    def _setup_ui(self):
        self.default_brush = QListWidgetItem('').background()
        self.add_testconfig.setToolTip("Add Configuration to available list with selected type and sites count.")

    def _setup_handlers(self):
        self.testconfig_store.currentItemChanged.connect(self._current_config_item_changed)
        self.add_testconfig.clicked.connect(self._add_testconfig_handler)
        self.remove_testconfig.clicked.connect(self._remove_testconfig_handler)

        self.testsites.clicked.connect(self._testsites_clicked)
        self.testconfig.cellClicked.connect(self._table_cell_clicked)
        self.testconfig.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.testconfig.customContextMenuRequested.connect(self._table_cell_clear)

        self.reset_button.clicked.connect(self._reset_button_handler)

    def _add_testconfig_handler(self):
        cur_selected_pattern = BaseType.PR if self.probing_button.isChecked() else BaseType.FT
        cur_sites_count = int(self.sites_count_select.currentText())
        new_name = self.parallelism_store.generate_next_config_name(cur_selected_pattern, cur_sites_count)
        new_config_item = ParallelismConfig.new(new_name, cur_selected_pattern, cur_sites_count)
        self.parallelism_store.add(new_config_item)
        self._parallelism_add_list[new_config_item.name] = new_config_item.get_default_first_ping_pong().id

        new_ui_item = QListWidgetItem(new_name)
        new_ui_item.setBackground(QtCore.Qt.red)
        self.testconfig_store.addItem(new_ui_item)
        self.testconfig_store.setCurrentItem(new_ui_item)
        self._verify_parallelism()

    def _remove_testconfig_handler(self):
        row = self.testconfig_store.currentRow()
        if row < 0:
            return
        item_text = self.testconfig_store.item(row).text()
        remove_parallelism = self.parallelism_store.get(item_text)
        remove_parallelism_id = remove_parallelism.get_default_first_ping_pong().id
        all_executions = self.hardware_wizard.project_info.get_programs_executions_matching_hardware(
            self.hardware_wizard.project_info.active_hardware)
        where = []
        # List only TestPrograms using a non default PingPong
        for prog_name, layout_list in all_executions.items():
            if item_text in layout_list:
                if any([check_id != remove_parallelism_id for check_id in layout_list[item_text]]):
                    where.append(prog_name)

        dependency_list = {
            "Non default ping pong used in following test programs": where
        }
        warn_user = ItemTrace(
            dependency_list,
            f'Remove parallelism "{item_text}"',
            self,
            message='''
This parallelism and all corresponding ping pong configurations are removed from all test programs!
Warning the above listed programs use a non default ping pong configuration!
            '''
        )
        ok_cancle = warn_user.exec_()
        if ok_cancle == QDialog.Accepted:
            self.parallelism_store.remove(item_text)
            self.current_item = None
            self.current_table = None
            self._parallelism_remove_list.append(item_text)
            self.testconfig_store.takeItem(row)
        elif ok_cancle == QDialog.Rejected:
            return
        else:
            raise Exception("Unreachable Code")

    def _current_config_item_changed(self, cur_item, old_item):
        if cur_item:
            item_text = cur_item.text()
            self.current_item = cur_item
            self.current_table = self.parallelism_store.get(item_text)
        self._verify_parallelism()

        self._init_sites_table_ui()
        self._update_sites_ui()
        self._update_table_ui()

    def _clear_sites_table_ui(self):
        self.testsites.clear()
        self.testconfig.clear()
        self.testconfig.setRowCount(0)
        self.testconfig.setColumnCount(0)

    def _init_sites_table_ui(self):
        self._clear_sites_table_ui()
        if not self.current_table:
            return
        # sites
        self.testsites.addItems([str(num) for num in range(self.current_table.sites_count)])
        self.selected_site_num = None
        # table
        row_count = self.current_table.sites_count
        column_count = self.current_table.sites_count
        if self.current_table.base_type == BaseType.FT:
            row_count = 1
        self.testconfig.setRowCount(row_count)
        self.testconfig.setColumnCount(column_count)

        for row in range(row_count):
            for col in range(column_count):
                item = QTableWidgetItem('')
                item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                self.testconfig.setItem(row, col, item)

    def _update_sites_ui(self):
        first_enabled_item_flag = True
        if not self.current_table:
            return
        for index in range(self.testsites.count()):
            item = self.testsites.item(index)
            item_text = item.text()
            if not item_text:
                return
            if int(item_text) in self.current_table.cells:
                item.setFlags(QtCore.Qt.ItemIsSelectable)
            else:
                item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
                if first_enabled_item_flag:
                    self.selected_site_num = int(item_text)
                    self.testsites.setCurrentItem(item)
                    first_enabled_item_flag = False

    def _update_table_ui(self):
        if not self.current_table:
            return
        for row in range(self.testconfig.rowCount()):
            for column in range(self.testconfig.columnCount()):
                item = self.testconfig.item(row, column)
                if item and item.text():
                    num = int(item.text())
                    if num not in self.current_table.cells or self.current_table.cells[num] != (column, row):
                        item.setText('')

        for cell_key, cell_coord in self.current_table.cells.items():
            self.testconfig.item(cell_coord[1], cell_coord[0]).setText(str(cell_key))
        self.testconfig.clearSelection()

    def _testsites_clicked(self, index):
        item = self.testsites.itemFromIndex(index)
        if item and item.text():
            self.selected_site_num = int(item.text())

    def _table_cell_clicked(self, row, column):
        clicked_cell = self.testconfig.item(row, column)

        if clicked_cell.text():
            clicked_cell_num = int(clicked_cell.text())
            if clicked_cell_num in self.current_table.cells:
                self.selected_site_num = clicked_cell_num
                return

        if self.selected_site_num is None:
            self.hardware_wizard.feedback.setText('No site for placement selected')
            return

        self.current_table.cells[self.selected_site_num] = (column, row)
        self._verify_parallelism()

        self._update_sites_ui()
        self._update_table_ui()

    def _table_cell_clear(self, point):
        item = self.testconfig.itemAt(point)
        if not item:
            return
        item_content = item.text()
        if not item_content:
            self.selected_site_num = None
            return
        item_num = int(item_content)
        self.current_table.cells.pop(item_num)
        self._verify_parallelism()
        self.selected_site_num = item_num

        self._update_sites_ui()
        self._update_table_ui()

    def _reset_button_handler(self):
        if not self.current_table:
            return
        self.current_table.cells.clear()
        self._verify_parallelism()
        self._update_sites_ui()
        self._update_table_ui()

    def _verify_parallelism(self):
        self.hardware_wizard.OKButton.setEnabled(False)
        self.hardware_wizard.feedback.setStyleSheet('color: orange')
        if not self.current_table:
            pass
        elif self.current_table.are_all_sites_used():
            self.current_item.setBackground(self.default_brush)
        else:
            self.hardware_wizard.feedback.setText(f'use all sites in config {self.current_table.name}')
            self.current_item.setBackground(QtCore.Qt.red)
            return

        if not self.parallelism_store.all_tables_filled():
            self.hardware_wizard.feedback.setText('There is an invalid configuration')
            return

        has_dup, dup1, dup2 = self.parallelism_store.find_duplicate()
        if has_dup:
            self.hardware_wizard.feedback.setText(f'found duplicate config pattern: {dup1} = {dup2}')
            return

        self.hardware_wizard.feedback.setText('')
        self.hardware_wizard._verify()

    def save_execution_sequence_changes(self):
        for parallelism_name, ping_pong_id in self._parallelism_add_list.items():
            if parallelism_name in self._parallelism_remove_list:
                continue
            self.hardware_wizard.project_info.add_parallelism_to_execution_sequence(parallelism_name, ping_pong_id)

        for parallelism_name in self._parallelism_remove_list:
            if parallelism_name in self._parallelism_add_list.keys():
                continue
            self.hardware_wizard.project_info.remove_parallelism_from_execution_sequence(parallelism_name)
