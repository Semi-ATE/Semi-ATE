from os import walk
from pathlib import Path
from typing import List
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

from ate_spyder.widgets.navigation import ProjectNavigation


class PatternTab(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QTabWidget, project_navigation: ProjectNavigation):
        super().__init__(parent=parent)
        self.parent = parent
        self.project_navigation = project_navigation

    def setup(self):
        self.pattern_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

    def fill_table(self):
        pass

    def add_pattern_item(self, test_name: str):
        if self._does_exist(test_name):
            return

        patterns = self.project_navigation.get_pattern_list_for_test(
            test_name,
            self.project_navigation.active_hardware,
            self.project_navigation.active_base
        )
        self.pattern_table.insertRow(self.pattern_table.rowCount())

        title_set = False
        for pattern in patterns:
            if not title_set:
                test_name_item = self._generate_item(test_name)
                title_set = True
            else:
                test_name_item = self._generate_item(test_name)

            # make item not editable
            # test_name_item.
            self.pattern_list.setItem(self.pattern_list.rowCount() - 1, 0, test_name_item)


            pattern_item = self._generate_item(pattern)
            self.pattern_list.setItem(self.pattern_list.rowCount() - 1, 1, pattern_item)

            self.pattern_list.setItem(self.pattern_list.rowCount() - 1, 2, pattern)

    def _generate_dropdown_item(self):
        combo = QtWidgets.QComboBox()
        combo.addItem()

    def _collect_patterns_from_file_structure(self):
        project_root = self.project_navigation.project_directory
        pattern_files = []
        pattern_files.extend(self._get_pattern_files(project_root.joinpath('pattern', self.project_navigation.active_hardware)))
        pattern_files.extend(self._get_pattern_files(project_root.joinpath('pattern', self.project_navigation.active_hardware, self.project_navigation.active_base)))
        pattern_files.extend(self._get_pattern_files(project_root.joinpath('pattern', self.project_navigation.active_hardware, self.project_navigation.active_base, self.project_navigation.active_target)))

        return pattern_files

    def _get_pattern_files(self, path: Path):
        for _, _, files in walk(path):
            return [file for file in files if Path(file).suffix not in ['.stil', '.wav']]


    def _generate_item(self, content: str = '') -> QtWidgets.QTableWidgetItem:
        item = QtWidgets.QTableWidgetItem()
        item.setText(content)
        return item

    def _does_exist(self, test_name: str) -> bool:
        for index in range(self.pattern_table.rowCount()):
            item = self.pattern_table.item(index, 0)

            if item.text() == test_name:
                return True

        return False

    @property
    def pattern_table(self) -> QtWidgets.QTableWidget:
        return self.parent.pattern_table
