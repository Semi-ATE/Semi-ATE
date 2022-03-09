from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes
from ate_spyder.widgets.actions_on.model.BaseFolderItem import BaseFolderItem
from PyQt5 import QtCore

import os


class FileItem(BaseFolderItem):
    def __init__(self, name, path, project_info, parent=None):
        super().__init__(name, path, project_info, parent=parent)
        self.path = path
        self.name = name
        self.hide()

    def set_pattern_directory(self, hardware, base):
        self._show()
        path = os.path.join(self.path, hardware, base, self.name)
        self.file_system_operator.path = path
        self._create_folder_if_needed(path)
        self._append_files(path)

    def _append_files(self, path):
        for name in os.listdir(path):
            self.add_file_item(os.path.join(path, name))

    def _show(self):
        self.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        self._is_hidden = False

    def hide(self):
        self._is_hidden = True
        self.setFlags(QtCore.Qt.NoItemFlags)
        self.set_children_hidden(self._is_hidden)

    @staticmethod
    def _does_folder_exist(path):
        return os.path.exists(path)

    def _create_folder_if_needed(self, path):
        if self._does_folder_exist(path):
            return

        os.makedirs(path)

    def add_file_item(self, path):
        name = os.path.basename(path)
        if self.get_child(name):
            return

        child = FileItemChild(name, path, self, self.project_info)
        self.appendRow(child)

    def remove_file_item(self, path):
        name = os.path.basename(path)
        self.remove_child(name)

    @staticmethod
    def _set_icon():
        pass

    @staticmethod
    def _get_menu_items():
        raise "implement me !!"

    def is_hidden(self):
        return self._is_hidden


class FileItemChild(BaseFolderItem):
    def __init__(self, name, path, parent, project_info):
        super().__init__(name, path, project_info, parent=parent)
        self.path = path
        self._set_icon(os.path.splitext(name)[1])

    def delete_item(self):
        self.file_system_operator.delete_file(path=self.path)

    @staticmethod
    def _get_menu_items():
        return [MenuActionTypes.DeleteFile()]
