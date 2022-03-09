from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog
from ate_common.program_utils import (ALARM_BIN_MAX, ALARM_BIN_MIN, BinningColumns, GRADES, BINGROUPS)
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLineEdit, QTableWidget, QTableWidgetItem
from ate_common.program_utils import BinTableFieldName


class BinningHandler:
    def __init__(self, bin_table: QTableWidget, bin_container: dict, parent: BaseDialog):
        self.binning_table = bin_table
        self._bin_container = bin_container
        self.parent = parent

    def _update_binning_table(self):
        self.binning_table.clear()
        self.binning_table.setRowCount(self._bin_container.get_bin_table_size())
        for row, (sb_name, value) in enumerate(self._bin_container.get_bin_table().items()):
            self._add_bin_to_table(row, sb_name, value[BinTableFieldName.SBinNum()],
                                   value[BinTableFieldName.SBinGroup()], value[BinTableFieldName.SBinDescription()])

    def _create_input_cell(self, table: QTableWidget, item: QTableWidgetItem):
        column = item.column()
        row = item.row()
        checkable_widget = QLineEdit()
        checkable_widget.setText(item.text())

        table.setCellWidget(row, column, checkable_widget)
        checkable_widget.editingFinished.connect(lambda: self._edit_input_cell_done(item, checkable_widget, table))

    def _edit_input_cell_done(self, item: QTableWidgetItem, checkable_widget: QLineEdit, table: QTableWidget):
        old_value = item.text()
        new_value = checkable_widget.text()
        table.removeCellWidget(item.row(), item.column())

        if item.column() == BinningColumns.SBinName():
            if not self._bin_container.does_bin_exist(new_value):
                self.parent._update_feedback('bin is already defined')
                return

            self._bin_container.update_bin_name(old_value, new_value)
            item.setText(new_value)
            self.parent._update_binning_tree_items()
            return

        elif item.column() == BinningColumns.SBin():
            if self._bin_container.does_bin_num_exist(new_value):
                self.parent._update_feedback('bin number is already occupied')
                return

            try:
                sbin = int(new_value)

                if sbin in range(ALARM_BIN_MIN, ALARM_BIN_MAX):
                    self.parent._update_feedback(f'range {(ALARM_BIN_MIN, ALARM_BIN_MAX)} is reserved for internal use')
                    item.setText(old_value)

                group_item = self.binning_table.item(item.row(), BinningColumns.SBinGroup())
                if sbin in range(1, 10):
                    group_item.setText(BINGROUPS[0])
                else:
                    group_item.setText(BINGROUPS[1])

                self.parent._verify()

            except Exception:
                self._update_feedback('soft bin must be of type integral')
                item.setText(old_value)
                return

        elif item.column() == BinningColumns.SBinGroup():
            BINGROUPS.append(new_value)

        item.setText(new_value)
        self._update_row_content_binning_table(item)
        self.parent._verify()

    def context_menu_handler(self, point):
        item = self.binning_table.selectedItems()[0]
        column = item.column()
        if column not in (BinningColumns.SBin(), BinningColumns.SBinGroup()):
            return

        elements = self._get_actions(item.column())
        menu = self._generate_menu(elements)
        action = menu.exec_(self.binning_table.mapToGlobal(point))

        if action is None:
            return None

        text = action.text()
        if column == BinningColumns.SBin():
            for grade in GRADES:
                if grade[0] == text:
                    text = str(grade[1])
                    break

        item.setText(text)
        self._update_row_content_binning_table(item)
        self.parent._verify()

    def _generate_menu(self, elements: list):
        menu = QtWidgets.QMenu(self.parent.project_info.parent)
        for action in elements:
            menu.addAction(action)

        return menu

    @staticmethod
    def _get_actions(column: int) -> list:
        if column == BinningColumns.SBinGroup():
            return BINGROUPS

        if column == BinningColumns.SBin():
            return [grade[0] for grade in GRADES]

        return []

    def add_bin(self, row: int, sb_name: str, sb_num: str, sb_group: str, sb_description: str):
        self.binning_table.blockSignals(True)
        bin_name_item = QTableWidgetItem()
        bin_name_item.setText(sb_name)
        bin_num_item = QTableWidgetItem()
        bin_num_item.setText(sb_num)
        bin_group_item = QTableWidgetItem()
        bin_group_item.setText(sb_group)
        bin_desc_item = QTableWidgetItem()
        bin_desc_item.setText(sb_description)
        self.binning_table.setItem(row, 0, bin_name_item)
        self.binning_table.setItem(row, 1, bin_num_item)
        self.binning_table.setItem(row, 2, bin_group_item)
        self.binning_table.setItem(row, 3, bin_desc_item)

        self._bin_container.add_bin(bin_name_item.text(), bin_num_item.text(), bin_group_item.text(), bin_desc_item.text())
        self.binning_table.blockSignals(False)

    def _update_row_content_binning_table(self, item):
        sb_name = self.binning_table.item(item.row(), 0).text()
        sb_num = self.binning_table.item(item.row(), 1).text()
        sb_group = self.binning_table.item(item.row(), 2).text()
        sb_description = self.binning_table.item(item.row(), 3).text()

        self._bin_container.update_bin_info(sb_name, sb_num, sb_group, sb_description)

    def update(self):
        self.binning_table.clear()
        self.binning_table.setRowCount(self._bin_container.get_bin_table_size())
        for row, (sb_name, value) in enumerate(self._bin_container.get_bin_table().items()):
            self.add_bin(row, sb_name, str(value[BinTableFieldName.SBinNum()]),
                         value[BinTableFieldName.SBinGroup()], value[BinTableFieldName.SBinDescription()])

    def verify(self) -> bool:
        for row in range(self.binning_table.rowCount()):
            for col in range(self.binning_table.columnCount() - 1):
                item = self.binning_table.item(row, col)
                if not item:
                    continue

                if not self.binning_table.item(row, col).text():
                    return False

        return True
