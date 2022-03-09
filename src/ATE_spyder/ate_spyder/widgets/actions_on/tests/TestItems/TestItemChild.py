import os
from pathlib import Path
from qtpy import QtCore
from ate_spyder.widgets.actions_on.tests.TestItems.TestBaseItem import TestBaseItem
from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes
from ate_spyder.widgets.actions_on.utils.FileSystemOperator import FileSystemOperator
from ate_spyder.widgets.actions_on.tests.TestWizard import edit_test_dialog
from ate_spyder.widgets.actions_on.utils.ExceptionHandler import (handle_excpetions,
                                                                  ExceptionTypes)
from ate_spyder.widgets.actions_on.tests.TestItems.utils import export_content
from ate_spyder.widgets.constants import TEST_SECTION


class TestItemChild(TestBaseItem):
    def __init__(self, name, path, parent, project_info, groups=['']):
        super().__init__(project_info, name, parent)
        self.path = os.path.join(path, name, name + '.py')
        self.groups = groups
        self.file_system_operator = FileSystemOperator(self.path, self.project_info.parent)
        self._set_icon(False)

        self.add_target_items()

    def update_item(self, path):
        name = os.path.basename(os.path.splitext(path)[0])
        self.path = path
        self.setText(name)
        self.file_system_operator = FileSystemOperator(self.path, self.project_info.parent)

    def edit_item(self):
        self.model().edit_test_params.emit(self.path)
        test_content = self._get_test_content()
        handle_excpetions(self.project_info.parent,
                          lambda: edit_test_dialog(self.project_info, test_content),
                          ExceptionTypes.Maskset())

    def _get_test_content(self):
        return self.project_info.get_test_table_content(self.text(), self.project_info.active_hardware, self.project_info.active_base)

    def open_file_item(self):
        path = os.path.dirname(self.path)
        filename = os.path.basename(self.path)
        path = os.path.join(path, filename)

        self.model().edit_file.emit(path)

    def delete_item(self):
        from ate_spyder.widgets.actions_on.utils.ItemTrace import ItemTrace
        if not ItemTrace(self.dependency_list, self.text(), self.project_info.parent, message="Are you sure you want to delete ?").exec_():
            return

        # emit event to update tab view
        self.model().delete_file.emit(self.path)

        import shutil
        shutil.rmtree(os.path.dirname(self.path))
        self.project_info.remove_test(self.text(), self.project_info.active_hardware, self.project_info.active_base, self.parent.text())

        self._remove_item()

    def _remove_item(self):
        self.parent.removeRow(self.row())

    def export_item(self):
        selected_dir = self.file_system_operator.export_file(f'{self.text()}.ate')

        if not selected_dir:
            return

        self._export_data(selected_dir)

    def _export_data(self, path: str):
        export_content(Path(path), self._get_test_content(), Path(self.path), self.project_info, self.text())

    @property
    def dependency_list(self):
        return self.project_info.get_dependant_objects_for_test(self.text())

    def is_enabled(self):
        return True

    def _update_db_state(self, enabled):
        pass

    def _are_dependencies_fulfilled(self):
        dependency_list = {}
        active_hardware = self.project_info.active_hardware
        hw_enabled = self.project_info.get_hardware_state(active_hardware)

        if not hw_enabled:
            dependency_list.update({'hardwares': active_hardware})

        return dependency_list

    def _enabled_item_menu(self):
        menu = [MenuActionTypes.OpenFile(),
                MenuActionTypes.Edit(),
                MenuActionTypes.Trace(),
                MenuActionTypes.Export()]

        delete_menu_option = [None,
                              MenuActionTypes.Delete()]

        if not self.dependency_list:
            menu += delete_menu_option

        return menu

    def add_target_items(self):
        for target in self.get_available_test_targets():
            is_default = self.project_info.is_test_target_set_to_default(target, self.project_info.active_hardware, self.project_info.active_base, self.text())
            self.add_target_item(target, is_default)

    def _is_valid_test_target_group(self, target):
        group_name = self.parent.text()
        return group_name in target or group_name == TEST_SECTION

    def add_target_item(self, target_name, is_default=True):
        if not self._is_valid_test_target_group(target_name):
            return

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

    def get_path(self):
        if self._is_default:
            filename = os.path.join(self.path, self.parent.text() + '.py')
        else:
            filename = os.path.join(self.path, self.text() + '.py')

        return filename

    def open_file_item(self):
        path = os.path.join(self.path, self.get_path())

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
        self.project_info.parent.select_target.emit(self.text().split('_')[0])

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
