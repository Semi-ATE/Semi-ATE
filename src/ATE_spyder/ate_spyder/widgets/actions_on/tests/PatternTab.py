from typing import List
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui


class PatternTab(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QTabWidget):
        super().__init__(parent=parent)
        self.parent = parent

    def setup(self, patterns: List[str]):
        self.pattern_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self._fill_pattern_list(patterns)

        self._connect_event_handler()

    def _fill_pattern_list(self, patterns: List[str]):
        for pattern in patterns:
            self.pattern_list.insertRow(self.pattern_list.rowCount())
            self.pattern_list.setItem(self.pattern_list.rowCount() - 1, 0, self._generate_item(pattern))

    def _connect_event_handler(self):
        self.add_button.clicked.connect(self._add_pattern)
        self.remove_button.clicked.connect(self._remove_pattern)

        self.pattern_list.itemDoubleClicked.connect(self._pattern_double_clicked)

    def _generate_item(self, content: str = '') -> QtWidgets.QTableWidgetItem:
        item = QtWidgets.QTableWidgetItem()
        item.setText(content)
        return item

    def _add_pattern(self):
        self.pattern_list.insertRow(self.pattern_list.rowCount())
        self.pattern_list.setItem(self.pattern_list.rowCount() - 1, 0, self._generate_item(''))

    def _remove_pattern(self):
        if self.pattern_list.rowCount() == 0:
            self.feedback.setText('no patterns available')
            return

        empty_row = None
        for row in range(self.pattern_list.rowCount()):
            item = self.pattern_list.item(row, 0)
            if not item:
                empty_row = row

        selected_items = self.pattern_list.selectedItems()
        if not selected_items:
            if empty_row is None:
                self.feedback.setText('no item is selected')
                return

            self.pattern_list.removeRow(empty_row)
            return

        for selected_item in selected_items:
            self.pattern_list.removeRow(selected_item.row())

    def _pattern_double_clicked(self, item: QtWidgets.QTableWidgetItem):
        self.feedback.setText('')

        from ate_spyder.widgets.validation import valid_name_regex
        regx = QtCore.QRegExp(valid_name_regex)
        name_validator = QtGui.QRegExpValidator(regx, self)

        checkable_widget = QtWidgets.QLineEdit()
        checkable_widget.setText(item.text())
        checkable_widget.setValidator(name_validator)

        self.pattern_list.setCellWidget(item.row(), item.column(), checkable_widget)
        checkable_widget.editingFinished.connect(
            lambda: self._edit_cell_done(item.row(), item.column(), checkable_widget)
        )

    def _edit_cell_done(self, row: int, column: int, checkable_widget: QtWidgets.QLineEdit):
        item = self.pattern_list.item(row, column)
        if not self._validate_pattern_name(checkable_widget):
            self.feedback.setText('pattern name is already used')
            self.pattern_list.removeCellWidget(row, column)
            return

        item.setText(checkable_widget.text())
        self.pattern_list.removeCellWidget(row, column)

    def _validate_pattern_name(self, checkable_widget: QtWidgets.QLineEdit):
        if checkable_widget is None:
            return

        for row in range(self.pattern_list.rowCount()):
            item = self.pattern_list.item(row, 0)
            if item is None:
                return

            if item.text() == checkable_widget.text():
                return False

        return True

    def collect_pattern_names(self) -> List[str]:
        pattern_list = []
        for row in range(self.pattern_list.rowCount()):
            item = self.pattern_list.item(row, 0)
            if item is None:
                continue

            if not item.text():
                continue

            pattern_list.append(item.text())

        return pattern_list

    def is_updated(self, default_patterns: List[str]):
        none_empty_pattern_names_count = 0
        for index in range(self.pattern_list.rowCount()):
            item = self.pattern_list.item(index, 0)
            if not item.text():
                continue

            none_empty_pattern_names_count += 1
        if len(default_patterns) != none_empty_pattern_names_count:
            return True

        for default_pattern in default_patterns:
            if not self.pattern_list.findItems(default_pattern, QtCore.Qt.MatchFlag.MatchExactly):
                return True

        return False

    @property
    def add_button(self) -> QtWidgets.QPushButton:
        return self.parent.addPattern

    @property
    def remove_button(self) -> QtWidgets.QPushButton:
        return self.parent.removePattern

    @property
    def pattern_list(self) -> QtWidgets.QTableWidget:
        return self.parent.patternList

    @property
    def feedback(self) -> QtWidgets.QLineEdit:
        return self.parent.Feedback
