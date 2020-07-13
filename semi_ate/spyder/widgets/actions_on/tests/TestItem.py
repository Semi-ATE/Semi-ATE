from ATE.org.actions_on.model.BaseItem import BaseItem
from ATE.org.actions_on.utils.StateItem import StateItem
from ATE.org.actions_on.model.Constants import MenuActionTypes
from ATE.org.actions_on.tests.NewStandardTestWizard import new_standard_test_dialog
from ATE.org.actions_on.tests.TestWizard import new_test_dialog
from ATE.org.actions_on.tests.TestWizard import edit_test_dialog
from ATE.org.actions_on.utils.FileSystemOperator import FileSystemOperator
from ATE.org.actions_on.tests.TestsObserver import TestsObserver

from PyQt5 import QtCore
import os


class TestItem(BaseItem):
    def __init__(self, project_info, name, path, parent=None):
        self.observer = None
        super().__init__(project_info, name, parent)
        self._is_enabled = False
        self.set_children_hidden(True)
        self.file_system_operator = FileSystemOperator(path)

    def _append_children(self):
        active_hardware = self.project_info.active_hardware
        active_base = self.project_info.active_base
        if not active_base or not active_hardware:
            return

        test_list, path = self._get_available_tests(active_hardware, active_base)
        for test_entry in test_list:
            self.add_file_item(test_entry, path)

        if self.observer is None:
            self.observer = TestsObserver(path, self)
            self.observer.start_observer()

    def add_file_item(self, name, path):
        child = TestItemChild(os.path.splitext(name)[0], path, self, self.project_info)
        self.appendRow(child)

    def new_item(self):
        new_test_dialog(self.project_info)

    # TODO: implement me !
    def import_item(self):
        pass

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

    def _get_available_tests(self, active_hardware, active_base):
        from os import walk, path

        test_directory = path.join(self.project_info.project_directory, 'src',
                                   active_hardware, active_base)

        file_names = []
        for _, directories, _ in walk(test_directory):
            file_names = [x for x in directories if '_' not in x]
            break

        return file_names, test_directory

    def add_standard_test_item(self):
        new_standard_test_dialog(self.project_info)

    def _get_menu_items(self):
        return [MenuActionTypes.Add(),
                MenuActionTypes.AddStandardTest(),
                MenuActionTypes.Import()]


class TestBaseItem(StateItem):
    def __init__(self, project_info, name, parent):
        super().__init__(project_info, name, parent)

    def _set_icon(self, is_virtual):
        from ATE.org.actions_on.documentation.FileIcon import FileIcons
        from ATE.org.actions_on.documentation.Constants import FileIconTypes

        if not is_virtual:
            icon = FileIcons[FileIconTypes.PY.name]
        else:
            icon = FileIcons[FileIconTypes.VIRTUAL.name]

        if icon is None:
            return

        self.setIcon(icon)


class TestItemChild(TestBaseItem):
    def __init__(self, name, path, parent, project_info):
        super().__init__(project_info, name, parent)
        self.path = os.path.join(path, name, name + '.py')
        self.file_system_operator = FileSystemOperator(self.path)
        self._set_icon(False)

        self.add_target_items()

    def update_item(self, path):
        name = os.path.basename(os.path.splitext(path)[0])
        self.path = path
        self.setText(name)
        self.file_system_operator = FileSystemOperator(self.path)

    def edit_item(self):
        test_content = self.project_info.get_test_table_content(self.text(), self.project_info.active_hardware, self.project_info.active_base)
        edit_test_dialog(self.project_info, test_content)

    def open_file_item(self):
        path = os.path.dirname(self.path)
        dirname, _ = os.path.splitext(os.path.basename(self.path))
        filename = os.path.basename(self.path)
        path = os.path.join(path, filename)

        self.model().edit_file.emit(path)

    def delete_item(self):
        from ATE.org.actions_on.utils.ItemTrace import ItemTrace
        if not ItemTrace(self.dependency_list, self.text(), message=f"Are you sure you want to delete ?").exec_():
            return

        # emit event to update tab view
        self.model().delete_file.emit(self.path)

        import shutil
        shutil.rmtree(os.path.dirname(self.path))
        self.project_info.remove_test(self.text())

    @property
    def dependency_list(self):
        # hack each used test must start with a 1 as index
        return self.project_info.get_dependant_objects_for_test(self.text())

    def is_enabled(self):
        return self.project_info.get_test_state(self.text(), self.project_info.active_hardware, self.project_info.active_base)

    def _update_db_state(self, enabled):
        self.project_info.update_test_state(self.text(), enabled)

    def _are_dependencies_fulfilled(self):
        dependency_list = {}
        active_hardware = self.project_info.active_hardware
        # active_base = self.project_info.active_base

        # hw = self.project_info.get_test_hardware(self.text(), active_hardware, active_base)
        # if not hw:
        #     return dependency_list

        hw_enabled = self.project_info.get_hardware_state(active_hardware)

        if not hw_enabled:
            dependency_list.update({'hardwares': active_hardware})

        return dependency_list

    def _enabled_item_menu(self):
        return [MenuActionTypes.OpenFile(),
                MenuActionTypes.Edit(),
                MenuActionTypes.Trace(),
                None,
                MenuActionTypes.Delete()]

    def add_target_items(self):
        for target in self.get_available_test_targets():
            is_default = self.project_info.is_test_target_set_to_default(target, self.project_info.active_hardware, self.project_info.active_base, self.text())
            self.add_target_item(target, is_default)

    def add_target_item(self, target_name, is_default=True):
        child = TestItemChildTarget(self.project_info, target_name, self, is_default, self.path)
        self.appendRow(child)

    def get_children(self):
        children = []
        for index in range(self.rowCount()):
            children.append(self.child(index).text())

        return children

    def get_available_test_targets(self):
        return self.project_info.get_available_test_targets(self.project_info.active_hardware, self.project_info.active_base, self.text())


class TestItemChildTarget(TestBaseItem):
    def __init__(self, project_info, name, parent, is_default, path):
        self._is_default = is_default
        self._is_enabled = project_info.active_target == name.split('_')[0]
        super().__init__(project_info, name, parent)
        self.base = project_info.active_hardware
        self.hardware = project_info.active_base
        self.target_name = name
        self.path = os.path.dirname(path)
        self._set_icon(self._is_default)

    def is_enabled(self):
        return self._is_enabled

    def open_file_item(self):
        if self._is_default:
            filename = os.path.join(self.path, self.parent.text() + '.py')
        else:
            filename = os.path.join(self.path, self.text() + '.py')

        path = os.path.join(self.path, filename)

        self.model().edit_file.emit(path)

    def _enabled_item_menu(self):
        menu = [MenuActionTypes.OpenFile()]
        if self._is_default:
            menu.append(MenuActionTypes.UseCustomImplementation())
        else:
            menu.append(MenuActionTypes.UseDefaultImplementation())

        return menu

    def use_custom_implementation(self):
        self._set_default_state(False)
        self._set_icon(False)

    def use_default_implementation(self):
        self._set_icon(True)
        self.clean_up()
        self._set_default_state(True)

    def clean_up(self):
        if not self._is_default:
            filename = os.path.join(self.path, self.text() + '.py')
            if not os.path.exists(filename):
                return

            os.remove(filename)
            self.model().delete_file.emit(filename)

    def _set_default_state(self, is_default):
        self.project_info.set_test_target_default_state(self.target_name,
                                                        self.project_info.active_hardware,
                                                        self.project_info.active_base,
                                                        self.parent.text(),
                                                        is_default)

        self._is_default = is_default

    def _update_db_state(self, is_enabled):
        pass

    def select_target_item(self):
        self.project_info.select_target.emit(self.text().split('_')[0])

    def _disabled_item_menu(self):
        return [MenuActionTypes.Select()]

    def _get_menu_items(self):
        if self.is_enabled():
            return self._enabled_item_menu()
        else:
            return self._disabled_item_menu()

    def update_state(self, target_name):
        if target_name == self.target_name.split('_')[0]:
            self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            self._is_enabled = True
        else:
            self.setFlags(QtCore.Qt.ItemIsSelectable)
            self._is_enabled = False


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
