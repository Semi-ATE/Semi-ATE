from pathlib import Path
from typing import List, Callable
from PyQt5 import QtWidgets
import os
from functools import partial
import subprocess

from ate_spyder.widgets.actions_on.model.Actions import ACTIONS
from ate_spyder.widgets.actions_on.documentation.BaseFolderStructureItem import BaseFolderStructureItem, BaseFolderStructureItemChild
from ate_spyder.widgets.actions_on.utils.MenuDialog import new_pattern
from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes
from ate_projectdatabase.Utils import DB_KEYS


class PatternItem(BaseFolderStructureItem):
    def __init__(self, name: str, path: str, project_info: ProjectNavigation, parent=None, is_editable: bool = False, is_parent_node: bool = True):
        super().__init__(name, path, project_info, parent=parent, is_editable=is_editable, is_parent_node=is_parent_node)
        self.root = path

    @property
    def pattern_root_dir(self) -> Path:
        return self.project_info.project_directory.joinpath('pattern')

    def add_dir_item(self, name: str, path: str, index: int=0):
        diff_path = Path(path).relative_to(Path(self.pattern_root_dir))
        items = str(diff_path).split(os.sep)

        def is_hardware_active():
            if items[0] != self.project_info.active_hardware: return False
            return True

        def is_base_active():
            if items[1] != self.project_info.active_base: return False
            return True

        def is_target_active():
            if items[2] != self.project_info.active_target: return False
            return True

        def is_hidden():
            if len(items) == 1: return is_hardware_active()
            if len(items) == 2: return is_hardware_active() and is_base_active()
            if len(items) > 2: return is_hardware_active() and is_base_active() and is_target_active()

        if not is_hidden():
            return

        if self._does_item_already_exist(name):
            return

        is_editable = True
        if name in self._do_not_edit_list() or not self._do_not_edit_list():
            is_editable = False

        item = PatternItem(name, path, self.project_info, parent=self, is_editable=is_editable, is_parent_node=False)
        self.insertRow(index, item)

    def add_file_item(self, name: str, path: str, index: int=0):
        if Path(path).suffix not in self.supported_file_extension():
            return

        if self._does_item_already_exist(name):
            return

        # switching between projects doesn't update the file observer
        # this will make sure that older project path are ignored
        if not Path(path).is_relative_to(Path(self.root)):
            return

        diff_path = Path(path).relative_to(Path(self.root))
        items = str(diff_path).split(os.sep)

        if len(items) > 1:
            return

        item = PatternItemChild(name, path, self, self.project_info)
        self.insertRow(index, item)

    def add_new_menu_options(self, new_menu: QtWidgets.QMenu):
        items = 'STIL files (*.stil);;WAV files (*.wav)'
        for extension in self._get_import_pattern_extensions()[0]:
            items += f';;{extension[1:].upper()} files (*{extension})'
        self.add_action(new_menu, MenuActionTypes.AddFile(), MenuActionTypes.AddFile(), lambda: self.add_file__item(items))

    def add_import_menu_options(self, menu_action: QtWidgets.QMenu):
        for extension in self.supported_file_extension():
            item = f'{extension[1:].upper()} files (*{extension})'
            self._add_action_import_file(menu_action, item, MenuActionTypes.ImportFile(), partial(self.import_file_item, item))

    def supported_file_extension(self) -> List[str]:
        extensions = self._get_import_pattern_extensions()[0].copy()
        if '.stil' not in extensions:
            extensions += ['.stil']
        if '.wav' not in extensions:
            extensions += ['.wav']
        return extensions

    def add_file__item(self, file_types: str = ''):
        pattern_res = new_pattern(self.project_info, self.project_info.get_available_patterns(self.root))
        if not pattern_res:
            return

        open(Path(self.root).joinpath(pattern_res), 'w').close()

    def _get_import_pattern_extensions(self):
        if self.project_info is None:
            return [[''], [''], ['']]
        return self.project_info.get_hardware_definition(self.project_info.active_hardware)[DB_KEYS.HARDWARE.DEFINITION.PATTERN_IMPORT.KEY()]

    def _add_action_import_file(self, menu_action: QtWidgets.QMenu, action_type: str, icon_type: MenuActionTypes, callback: Callable):
        action = QtWidgets.QAction(action_type, menu_action)
        action.setIcon(ACTIONS[icon_type][0])
        action.triggered.connect(callback)

        menu_action.addAction(action)

    def import_file_item(self, file_types: str = ''):
        extensions = self._get_import_pattern_extensions()
        filetyp = file_types[file_types.find('.'):-1]
        if filetyp in extensions[0]:
            index = extensions[0].index(filetyp)
            filelocation = extensions[2][index]
            cmd = extensions[1][index]
        else:
            filelocation = None
            cmd = ''
        file_types = f'{filetyp[1:].upper()}.gz files (*{filetyp}.gz);;' + file_types
        file_name = self.file_system_operator.import_file(file_types, filelocation)

        if file_name is not None and cmd != '':
            relativ = cmd.find('..\\')
            if relativ > 0:
                cmd = f'{cmd[:relativ]} {str(self.project_info.project_directory)}\\{cmd[relativ:]} '
            cmd += file_name
            print(f'run converting call from Pattern import: {cmd})')
            output = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE).stdout.read()


class PatternItemChild(BaseFolderStructureItemChild):
    def __init__(self, name: str, path: str, parent: PatternItem, project_info: ProjectNavigation):
        super().__init__(name, path, parent, project_info)

    def _get_menu_items(self) -> List[MenuActionTypes]:
        options = [MenuActionTypes.OpenFile(),
                   MenuActionTypes.Rename(),
                   MenuActionTypes.Trace()]
        if not self.project_info.is_pattern_used(self.text()):
            options.extend([None, MenuActionTypes.Delete()])

        return options

    def open_file_item(self):
        self.model().edit_file.emit(str(self.path))

    def trace_item(self):
        from ate_spyder.widgets.actions_on.utils.ItemTrace import ItemTrace
        ItemTrace(self.dependency_list, self.text(), self.project_info.parent).exec_()

    def rename_item(self):
        rename_res = super().rename_item(self.project_info.get_available_patterns(Path(self.path).parent))
        if not rename_res:
            return
        old, new = rename_res
        self.project_info.update_pattern_names_for_programs(old, new)

    @property
    def dependency_list(self):
        return self.project_info.get_dependant_program_for_pattern(self.text())
