from pathlib import Path
from typing import Dict
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic
import yaml


class SignalToChannelTab(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget, read_only: bool = False):
        super().__init__(parent=parent)
        uic.loadUi(__file__.replace('.py', '.ui'), self)

        self.parent = parent
        self.read_only = read_only

    def setup(self):
        self.signal_to_channel_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.generate_button.setVisible(False)
        if not self.read_only:
            self._connect_event_handler()

    def load_table(self, path: Path):
        self.signal_to_channel_table.setRowCount(0)
        flags = QtCore.Qt.NoItemFlags
        with open(path) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            if not data:
                self.num_channels.setValue(0)
                return
            num_channels = max(data.values())

            self.num_channels.setValue(num_channels)
            for key, value in data.items():
                row_count = self.signal_to_channel_table.rowCount()
                self.signal_to_channel_table.insertRow(row_count)
                self.signal_to_channel_table.setItem(row_count, 0, self._generate_item(key))
                self.signal_to_channel_table.setCellWidget(row_count, 1, self._generate_dropdown_item())
                combo = self.signal_to_channel_table.cellWidget(row_count, 1)
                combo.setCurrentIndex(value)
                if self.read_only:
                    self.signal_to_channel_table.item(row_count, 0).setFlags(flags)
                    combo.setEnabled(False)
                    self.num_channels.setEnabled(False)

    def _connect_event_handler(self):
        self.add_button.clicked.connect(self._add_row)
        self.remove_button.clicked.connect(self._remove_row)
        self.num_channels.valueChanged.connect(self._update_channel_selection)

        self.signal_to_channel_table.itemDoubleClicked.connect(self._pattern_double_clicked)

    def _update_channel_selection(self, value):
        for row in range(self.signal_to_channel_table.rowCount()):
            combo = self.signal_to_channel_table.cellWidget(row, 1)
            channels = [f'{channel_idx}' for channel_idx in range(0, value + 1)]
            index = combo.currentIndex()
            combo.clear()
            combo.addItems(channels)
            if combo.count() - 1 < index:
                combo.setCurrentIndex(0)
            else:
                combo.setCurrentIndex(index)

    def _generate_item(self, content: str = '') -> QtWidgets.QTableWidgetItem:
        item = QtWidgets.QTableWidgetItem()
        item.setText(content)
        return item

    def _add_row(self):
        self.feedback.setText('')
        self.signal_to_channel_table.insertRow(self.signal_to_channel_table.rowCount())
        self.signal_to_channel_table.setItem(self.signal_to_channel_table.rowCount() - 1, 0, self._generate_item(''))
        self.signal_to_channel_table.setCellWidget(self.signal_to_channel_table.rowCount() - 1, 1, self._generate_dropdown_item())

    def _generate_dropdown_item(self):
        combo = QtWidgets.QComboBox()
        # combobox items are designed by default to have rounded corners
        # the following will set reshape the combobox with 90° angle
        combo.setStyleSheet("QComboBox {" "border:0px solid;" "border-radius: 0px;" "combobox-popup: 0;" "background: transparent;" "}")
        combo.view().setStyleSheet("QListView{" "border:0px solid;" "border-radius: 0px;" "}")
        num_channels = self.num_channels.value()
        combo.addItems([f'{channel_idx}' for channel_idx in range(0, num_channels + 1)])
        return combo

    def _remove_row(self):
        self.feedback.setText('')
        if self.signal_to_channel_table.rowCount() == 0:
            self.feedback.setText('no patterns available')
            return

        empty_row = None
        for row in range(self.signal_to_channel_table.rowCount()):
            item = self.signal_to_channel_table.item(row, 0)
            if not item:
                empty_row = row

        selected_items = self.signal_to_channel_table.selectedItems()
        if not selected_items:
            if empty_row is None:
                self.feedback.setText('no item is selected')
                return

            self.signal_to_channel_table.removeRow(empty_row)
            return

        for selected_item in selected_items:
            self.signal_to_channel_table.removeRow(selected_item.row())

    def _pattern_double_clicked(self, item: QtWidgets.QTableWidgetItem):
        self.feedback.setText('')

        from ate_spyder.widgets.validation import valid_name_regex
        regx = QtCore.QRegExp(valid_name_regex)
        name_validator = QtGui.QRegExpValidator(regx, self)

        checkable_widget = QtWidgets.QLineEdit()
        checkable_widget.setText(item.text())
        checkable_widget.setValidator(name_validator)

        self.signal_to_channel_table.setCellWidget(item.row(), item.column(), checkable_widget)
        checkable_widget.editingFinished.connect(
            lambda: self._edit_cell_done(item.row(), item.column(), checkable_widget)
        )

    def _edit_cell_done(self, row: int, column: int, checkable_widget: QtWidgets.QLineEdit):
        item = self.signal_to_channel_table.item(row, column)
        if not self._validate_signal_name(checkable_widget, row):
            self.feedback.setText('Signal name is already used')
            self.signal_to_channel_table.removeCellWidget(row, column)
            return

        item.setText(checkable_widget.text())
        self.signal_to_channel_table.removeCellWidget(row, column)

    def _validate_signal_name(self, checkable_widget: QtWidgets.QLineEdit, current_row: int) -> bool:
        if checkable_widget is None:
            return

        for row in range(self.signal_to_channel_table.rowCount()):
            if current_row == row:
                continue
            item = self.signal_to_channel_table.item(row, 0)
            if item is None:
                return

            if item.text() == checkable_widget.text():
                return False

        return True

    def _collect_signal_to_channel_info(self) -> Dict[str, int]:
        signal_to_channel_table = {}
        for row in range(self.signal_to_channel_table.rowCount()):
            sig_name = self.signal_to_channel_table.item(row, 0)
            ch_num = self.signal_to_channel_table.cellWidget(row, 1)
            if sig_name is None:
                continue

            if not sig_name.text():
                continue

            signal_to_channel_table[sig_name.text()] = int(ch_num.currentText())

        return signal_to_channel_table

    def generate_yml_file(self, path: Path):
        with open(path, 'w') as f:
            data = yaml.dump(self._collect_signal_to_channel_info(), sort_keys=True)
            f.write(data)

    @property
    def feedback(self) -> QtWidgets.QLineEdit:
        return self.parent.feedback
