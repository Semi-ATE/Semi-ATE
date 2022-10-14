import os
from typing import Callable, List, Optional, Tuple

from PyQt5 import QtGui
from PyQt5 import QtWidgets

from ate_spyder.widgets.actions_on.model.Actions import ACTIONS
from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes
from ate_spyder.widgets.actions_on.model.BaseFolderItem import BaseFolderItem
from ate_spyder.widgets.actions_on.utils.FileSystemOperator import FileSystemOperator
from ate_spyder.widgets.navigation import ProjectNavigation


class BaseFolderStructureItem(BaseFolderItem):
    def __init__(self, name: str, path: str, project_info: ProjectNavigation, parent: object=None, is_editable: bool=True, is_parent_node: bool=False):
        super().__init__(name, path, project_info, parent=parent)

        self._is_editable = is_editable
        self._set_icon(is_parent_node)

    def update_item(self, path: str):
        self.path = path
        self.setText(os.path.basename(path))
        self.file_system_operator(path)

    def _do_not_edit_list(self) -> List[str]:
        return []

    def add_dir_item(self, name: str, path: str, index: int=0):
        if self._does_item_already_exist(name):
            return

        is_editable = True
        if name in self._do_not_edit_list() or not self._do_not_edit_list():
            is_editable = False

        item = BaseFolderStructureItem(name, path, self.project_info, parent=self, is_editable=is_editable)
        self.insertRow(index, item)

    def add_file_item(self, name: str, path: str, index: int=0):
        if self._does_item_already_exist(name):
            return

        item = BaseFolderStructureItemChild(name, path, self, self.project_info)
        self.insertRow(index, item)

    # copying directories recursively (import) does fire _on_file_created and _on_dir_created event multiple times
    # using this function we prevent creating same item multiple times
    def _does_item_already_exist(self, name: str) -> bool:
        for index in range(self.rowCount()):
            if self.child(index).text() == name:
                return True

        return False

    def _set_icon(self, is_parent_node: bool):
        if is_parent_node:
            return

        from ate_spyder.widgets.actions_on.documentation.FileIcon import FileIcons
        from ate_spyder.widgets.actions_on.documentation.Constants import FileIconTypes
        self.setIcon(FileIcons[FileIconTypes.FOLDER.name])

    def _get_menu_items(self):
        return [MenuActionTypes.Rename(),
                MenuActionTypes.Move(),
                None,
                MenuActionTypes.DeleteFile()]

    def exec_context_menu(self):
        self.menu = QtWidgets.QMenu(self.project_info.parent)
        self.add_menu_actions()

        if self._is_editable:
            from ate_spyder.widgets.actions_on.model.Actions import ACTIONS

            for action_type in self._get_menu_items():
                if not action_type:
                    self.menu.addSeparator()
                    continue

                action = ACTIONS[action_type]
                action = self.menu.addAction(action[0], action[1])
                action.triggered.connect(getattr(self, action_type))

        self.menu.exec_(QtGui.QCursor.pos())

    def add_menu_actions(self):
        self.menu.addMenu(self._generate_new_menu_actions(self.menu))
        self.menu.addMenu(self._generate_import_menu_actions(self.menu))

    def _generate_new_menu_actions(self, parent: object):
        new_menu = QtWidgets.QMenu('New', parent)
        import qtawesome as qta
        new_menu.setIcon(qta.icon('mdi.plus', color='orange'))
        self.add_new_menu_options(new_menu)
        return new_menu

    def add_new_menu_options(self, new_menu: QtWidgets.QMenu):
        self.add_action(new_menu, MenuActionTypes.AddFile(), MenuActionTypes.AddFile(), self.add_file__item)
        self.add_action(new_menu, MenuActionTypes.AddFolder(), MenuActionTypes.AddFolder(), self.add_folder_item)

    def _generate_import_menu_actions(self, parent: object) -> QtWidgets.QMenu:
        menu_action = QtWidgets.QMenu('Import', parent)
        import qtawesome as qta
        menu_action.setIcon(qta.icon('mdi.application-import', color='orange'))
        self.add_import_menu_options(menu_action)

        return menu_action

    def add_import_menu_options(self, menu_action: QtWidgets.QMenu):
        self.add_action(menu_action, MenuActionTypes.AddFile(), MenuActionTypes.ImportFile(), lambda: self.import_file_item('Stil files (*.stil *.wav)'))
        self.add_action(menu_action, MenuActionTypes.AddFolder(), MenuActionTypes.ImportFolder(), self.import_folder_item)

    def add_action(self, menu_action: QtWidgets.QMenu, action_type: MenuActionTypes, icon_type: MenuActionTypes, callback: Callable):
        action = QtWidgets.QAction(ACTIONS[action_type][1], menu_action)
        action.setIcon(ACTIONS[icon_type][0])
        action.triggered.connect(callback)

        menu_action.addAction(action)


class BaseFolderStructureItemChild(BaseFolderItem):
    def __init__(self, name: str, path: str, parent: object, project_info: ProjectNavigation):
        super().__init__(name, path, project_info, parent=parent)
        _, extension = os.path.splitext(name)
        self._set_icon(extension)
        self.file_system_operator = FileSystemOperator(self.path, project_info.parent)

    def update_item(self, path: str):
        self.path = path
        self.setText(os.path.basename(path))
        self.file_system_operator(path)

    def rename_item(self, available_names: list = []) -> Optional[Tuple[str, str]]:
        rename_view = self.file_system_operator.rename(available_names)
        return None if rename_view is None else (rename_view.path, rename_view.new_path)

    def delete_item(self):
        self.file_system_operator.delete_file()

    def move_item(self):
        self.file_system_operator.move()

    def _get_menu_items(self) -> List[MenuActionTypes]:
        return [MenuActionTypes.Rename(),
                MenuActionTypes.Move(),
                None,
                MenuActionTypes.Delete()]
