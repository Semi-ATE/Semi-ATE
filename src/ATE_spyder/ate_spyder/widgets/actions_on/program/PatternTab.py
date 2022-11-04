from os import walk
from pathlib import Path
from typing import List
from PyQt5 import QtWidgets
from PyQt5 import QtCore

from ate_spyder.widgets.navigation import ProjectNavigation


class PatternTab(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QTabWidget, project_navigation: ProjectNavigation, read_only: bool = False):
        super().__init__(parent=parent)
        self.parent = parent
        self.project_navigation = project_navigation
        self.read_only = read_only

    def setup(self):
        self.pattern_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.pattern_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.pattern_table.horizontalHeader().setStretchLastSection(True)

    def fill_pattern_table(self, test_names: List[str], assinged_patterns: dict):
        self.pattern_table.setRowCount(0)
        for test_name in test_names:
            self.add_pattern_items(test_name)

        current_test_name = ''
        for index in range(self.pattern_table.rowCount()):
            test_item = self.pattern_table.item(index, 0)
            if test_item.text():
                current_test_name = test_item.text()

            pattern_name = self.pattern_table.item(index, 1).text()
            assigned_tuples = assinged_patterns.get(current_test_name)
            if assigned_tuples is None:
                continue

            for tuple in assigned_tuples:
                if tuple[0] == f'{current_test_name}_{pattern_name}':
                    combo = self.pattern_table.cellWidget(index, 2)
                    index = combo.findText(tuple[1])
                    combo.setCurrentIndex(index)

    def update_table(self, test_names: List[str]):
        self.pattern_table.setRowCount(0)
        for test_name in test_names:
            self.add_pattern_items(test_name)

    def add_pattern_items(self, test_name: str):
        if not test_name:
            return

        if self._is_assigned(test_name):
            return

        patterns = self.project_navigation.get_pattern_list_for_test(
            test_name,
            self.parent.hardware.currentText(),
            self.parent.base.currentText(),
        )

        title_set = False
        for pattern in patterns:
            self.pattern_table.insertRow(self.pattern_table.rowCount())
            if not title_set:
                test_name_item = self._generate_item(test_name)
                title_set = True
            else:
                test_name_item = self._generate_item('')

            flags = QtCore.Qt.NoItemFlags
            test_name_item.setFlags(flags)
            self.pattern_table.setItem(self.pattern_table.rowCount() - 1, 0, test_name_item)

            pattern_item = self._generate_item(pattern)
            pattern_item.setFlags(flags)
            self.pattern_table.setItem(self.pattern_table.rowCount() - 1, 1, pattern_item)

            dropdown = self._generate_dropdown_item()
            if self.read_only:
                dropdown.setEnabled(flags)
            self.pattern_table.setCellWidget(self.pattern_table.rowCount() - 1, 2, dropdown)

    def _generate_dropdown_item(self):
        combo = QtWidgets.QComboBox()
        combo.currentIndexChanged.connect(self._table_changed)
        files = self._collect_patterns_from_file_structure()
        combo.addItems(files)
        return combo

    def _table_changed(self, _index: int):
        self.parent._verify()

    def _collect_patterns_from_file_structure(self):
        project_root: Path = self.project_navigation.project_directory
        pattern_files = []
        pattern_root = project_root.joinpath('pattern')
        hw_path = pattern_root.joinpath(self.project_navigation.active_hardware)
        base_path = hw_path.joinpath(self.project_navigation.active_base)
        target_path = base_path.joinpath(self.project_navigation.active_target)
        pattern_files.extend(self._get_pattern_files(pattern_root))
        pattern_files.extend(self._get_pattern_files(hw_path))
        pattern_files.extend(self._get_pattern_files(base_path))
        pattern_files.extend(self._get_pattern_files(target_path))

        return pattern_files

    def _get_pattern_files(self, path: Path) -> List[str]:
        for dir_path, _, files in walk(path):
            return [str(Path(dir_path, file).relative_to(self.project_navigation.project_directory)) for file in files if file.endswith('.stil') or file.endswith('.wav')]

        return []

    def _generate_item(self, content: str = '') -> QtWidgets.QTableWidgetItem:
        item = QtWidgets.QTableWidgetItem()
        item.setText(content)
        return item

    def _is_assigned(self, test_name: str) -> bool:
        for index in range(self.pattern_table.rowCount()):
            item = self.pattern_table.item(index, 0)

            if item.text() == test_name:
                return True

        return False

    def validate_pattern_table(self) -> bool:
        for index in range(self.pattern_table.rowCount()):
            pattern = self.pattern_table.item(index, 1)
            combo = self.pattern_table.cellWidget(index, 2)
            if combo is None:
                continue
            text = combo.currentText()
            if not text:
                self.feedback.setText(f'pattern: \'{pattern.text()}\' is not assigned yet')
                return False

        return True

    def collect_pattern(self) -> dict:
        patterns = {}
        current_test_name = ''
        for index in range(self.pattern_table.rowCount()):
            test_item = self.pattern_table.item(index, 0)
            if test_item.text():
                current_test_name = test_item.text()

            pattern_name = self.pattern_table.item(index, 1).text()

            pattern_path = self.pattern_table.cellWidget(index, 2).currentText()
            if not pattern_path:
                continue

            patterns.setdefault(current_test_name, []).append((f'{current_test_name}_{pattern_name}', pattern_path))

        return patterns

    @property
    def pattern_table(self) -> QtWidgets.QTableWidget:
        return self.parent.pattern_table

    @property
    def feedback(self) -> QtWidgets.QTableWidget:
        return self.parent.Feedback
