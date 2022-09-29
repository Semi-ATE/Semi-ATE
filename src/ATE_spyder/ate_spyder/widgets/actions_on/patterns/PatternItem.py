from pathlib import Path
from typing import List
from PyQt5 import QtWidgets
import os

from ate_spyder.widgets.actions_on.documentation.BaseFolderStructureItem import BaseFolderStructureItem, BaseFolderStructureItemChild
from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes


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
        # TODO: what extension shall we support
        if Path(path).suffix not in self.supported_file_extension():
            return

        if self._does_item_already_exist(name):
            return

        diff_path = Path(path).relative_to(Path(self.root))
        items = str(diff_path).split(os.sep)

        if len(items) > 1:
            return

        item = PatternItemChild(name, path, self, self.project_info)
        self.insertRow(index, item)

    def add_new_menu_options(self, new_menu: QtWidgets.QMenu):
        self.add_action(new_menu, MenuActionTypes.AddFile(), MenuActionTypes.AddFile(), lambda: self.add_file__item('STIL files (*.stil);;WAV files (*.wav)'))

    def add_import_menu_options(self, menu_action: QtWidgets.QMenu):
        self.add_action(menu_action, MenuActionTypes.AddFile(), MenuActionTypes.ImportFile(), lambda: self.import_file_item('Stil files (*.stil *.wav)'))

    def supported_file_extension(self) -> List[str]:
        return ['.stil', '.wav']


class PatternItemChild(BaseFolderStructureItemChild):
    def __init__(self, name: str, path: str, parent: PatternItem, project_info: ProjectNavigation):
        super().__init__(name, path, parent, project_info)

    def _get_menu_items(self) -> List[MenuActionTypes]:
        return [MenuActionTypes.OpenFile(),
                MenuActionTypes.Rename(),
                MenuActionTypes.Move(),
                None,
                MenuActionTypes.Delete()]
    
    def open_file_item(self):
        self.model().edit_file.emit(str(self.path))