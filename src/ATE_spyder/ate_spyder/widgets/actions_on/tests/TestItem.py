from pathlib import Path
from ate_spyder.widgets.actions_on.model.BaseItem import BaseItem
from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes
from ate_spyder.widgets.actions_on.tests.NewStandardTestWizard import new_standard_test_dialog
from ate_spyder.widgets.actions_on.tests.TestWizard import new_test_dialog
from ate_spyder.widgets.actions_on.utils.FileSystemOperator import FileSystemOperator
from ate_spyder.widgets.actions_on.tests.TestsObserver import TestsObserver
from ate_spyder.widgets.actions_on.tests.TestItems.TestItemChild import TestItemChild
from ate_spyder.widgets.actions_on.tests.TestItems.utils import import_content
from ate_spyder.widgets.constants import TEST_SECTION, QUALIFICATION

from ate_spyder.widgets.actions_on.utils.MenuDialog import new_group
from ate_spyder.widgets.actions_on.utils.ExceptionHandler import (handle_excpetions,
                                                                  ExceptionTypes)
import os

FILE_FILTER = '*.ate'


class TestContainerBase(BaseItem):
    def __init__(self, project_info, name, parent):
        super().__init__(project_info, name, parent=parent)

    def add_file_item(self, name, path):
        child = TestItemChild(os.path.splitext(name)[0], path, self, self.project_info)
        self.appendRow(child)

    def _get_path(self):
        active_hardware = self.project_info.active_hardware
        active_base = self.project_info.active_base
        from os import path, fspath
        from pathlib import Path

        test_directory = path.join(self.project_info.project_directory, 'src',
                                   active_hardware, active_base)
        return fspath(Path(test_directory))

    def add_child(self, name: str):
        self.add_file_item(name, self._get_path())


class TestItem(TestContainerBase):
    def __init__(self, project_info, name, path, parent=None):
        self.observer = None
        super().__init__(project_info, name, parent)
        self._is_enabled = False
        self.set_children_hidden(True)
        self.file_system_operator = FileSystemOperator(path, project_info.parent)

    def _append_children(self):
        active_hardware = self.project_info.active_hardware
        active_base = self.project_info.active_base
        if not active_base or not active_hardware:
            return

        path = self._get_path()
        groups = self._get_available_groups()
        for group in groups:
            if group == TEST_SECTION:
                continue

            if (group == QUALIFICATION) and (self.project_info.active_base == 'PR'):
                continue

            self.add_group_to_tree(group)

        if self.observer is None:
            self.observer = TestsObserver(path, self)
            self.observer.start_observer()

    def add_test_group(self):
        group = new_group(self.project_info, self)
        if not group:
            return

        self.project_info.add_test_group(group)
        self.add_group_to_tree(group)

    def add_group_to_tree(self, name: str):
        child = GroupItem(self.project_info, name, "", self)
        self.appendRow(child)

    def new_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: new_test_dialog(self.project_info),
                          ExceptionTypes.Test())

    def import_item(self):
        selected_file = self.file_system_operator.get_file(FILE_FILTER)

        if not selected_file:
            return

        self._import_test(selected_file)

    def _import_test(self, path: str):
        current_version = self.project_info.get_version()
        import_content(Path(path), self.project_info, self.parent.parent, current_version)

    def update(self):
        active_hardware = self.project_info.active_hardware
        active_base = self.project_info.active_base

        if not active_hardware or \
           not active_base:
            self._is_enabled = False
            self.set_children_hidden(True)
            if self.observer is not None:
                self.observer.stop_observer()
                self.observer = None
            return
        else:
            self._is_enabled = True
            self.set_children_hidden(False)

        super().update()

    def is_enabled(self):
        return self._is_enabled

    def _get_available_groups(self):
        return [group.name for group in self.project_info.get_groups() if group.is_selected]

    def add_standard_test_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: new_standard_test_dialog(self.project_info),
                          ExceptionTypes.Test())

    @staticmethod
    def _get_menu_items():
        return [MenuActionTypes.Add(),
                MenuActionTypes.AddStandardTest(),
                MenuActionTypes.Import(),
                MenuActionTypes.AddGroup()]

    @staticmethod
    def is_valid_functionality(functionality):
        if functionality in (MenuActionTypes.AddStandardTest()):
            return False

        return True


class GroupItem(TestContainerBase):
    def __init__(self, project_info, name, path, parent):
        super().__init__(project_info, name, parent)
        self._set_icon()
        self._is_enabled = True

    def _get_available_tests(self):
        active_hardware = self.project_info.active_hardware
        active_base = self.project_info.active_base
        tests_from_db = set([test.name for test in self.project_info.get_tests_from_db(active_hardware, active_base)])
        tests = self.project_info.get_tests_for_group(self.text())
        test_list = [test for test in tests_from_db if test in tests]

        return test_list

    def _append_children(self):
        test_list = self._get_available_tests()
        path = self._get_path()
        for test_entry in test_list:
            self.add_file_item(test_entry, path)

    def _set_icon(self):
        from ate_spyder.widgets.actions_on.documentation.FileIcon import FileIcons
        from ate_spyder.widgets.actions_on.documentation.Constants import FileIconTypes

        icon = FileIcons[FileIconTypes.FOLDER.name]
        if icon is None:
            return

        self.setIcon(icon)

    def is_enabled(self):
        return self._is_enabled

    def _get_menu_items(self):
        if (self.project_info.is_standard_group(self.text())) or (not self.is_empty()):
            return []

        return [MenuActionTypes.Delete()]

    def delete_item(self):
        if not self.is_empty():
            return

        self.project_info.remove_group(self.text())
        self.parent.removeRow(self.row())

    def is_empty(self):
        return self.rowCount() == 0

    def update_child_items(self, child_name: str, is_new: bool = False):
        if is_new:
            for index in range(self.rowCount()):
                test_item = self.child(index)
                test_item_name = test_item.text()

                if test_item_name == child_name:
                    return

            self.add_child(child_name)
        else:
            for index in range(self.rowCount()):
                test_item = self.child(index)
                test_item_name = test_item.text()

                if test_item_name != child_name:
                    continue

                self.remove_row(index)
                return

    def remove_row(self, row: int):
        self.removeRow(row)


def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts
