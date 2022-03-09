import os
import shutil

from PyQt5 import QtWidgets

from ate_spyder.widgets.actions_on.utils.MenuDialog import AddDirectoryDialog
from ate_spyder.widgets.actions_on.utils.MenuDialog import DeleteDirDialog
from ate_spyder.widgets.actions_on.utils.MenuDialog import DeleteFileDialog
from ate_spyder.widgets.actions_on.utils.MenuDialog import RenameDialog
from ate_spyder.widgets.actions_on.utils.MenuDialog import ExceptionFoundDialog


class FileSystemOperator(QtWidgets.QFileDialog):
    def __init__(self, path, parent):
        super().__init__()
        self.parent = parent
        self.path = path

    def __call__(self, path):
        self.path = path

    def add_file(self):
        selected, _ = self.getSaveFileName(self, "Save File", self.path, "", options=self.options())
        if not selected:
            return

        # TODO: what if file exists already !??
        open(selected, 'w').close()

    def add_dir(self):
        add_dir = AddDirectoryDialog(self.path, "Folder name", self.parent)
        add_dir.show()

    def import_file(self):
        selected, _ = self.getOpenFileName(self, "Import File", self.path, '', options=self.options())
        if not selected:
            return

        file_name = os.path.basename(selected)
        location = os.path.join(self.path, file_name)

        try:
            shutil.copyfile(selected, location)
        except Exception:
            exception = ExceptionFoundDialog(selected, "File not found", self.parent, "file exists already: ")
            exception.show()

    def get_file(self, file_filter: str = ''):
        selected, _ = self.getOpenFileName(self, "Select File", self.path, file_filter, options=self.options())
        if not selected:
            return

        return selected

    def import_dir(self):
        selected = self.getExistingDirectory(self, "Select directory", self.path, options=self.options())
        if not selected:
            return

        try:
            shutil.copytree(selected, os.path.join(self.path, os.path.basename(selected)))
        except Exception:
            exception = ExceptionFoundDialog(selected, "Import Exception", self.parent, f"cannot copy directory {selected}")
            exception.show()

    def export_file(self, name: str = ''):
        file_path, _ = self.getSaveFileName(self, "Save File", name)
        if not file_path:
            return None

        return file_path

    def move(self):
        selected = self.getExistingDirectory(self, "Select directory", self.path, options=self.options())
        if not selected:
            return
        try:
            shutil.move(self.path, selected)
        except Exception:
            exception = ExceptionFoundDialog(selected, "Move Exception", self.parent, f"cannot move directory {selected}")
            exception.show()

    def delete_file(self, path=None):
        delete = DeleteFileDialog(path if path is not None else self.path, "Remove", self.parent)
        return delete.show()

    def delete_dir(self):
        delete = DeleteDirDialog(self.path, "Remove", self.parent)
        delete.show()

    def rename(self):
        rename = RenameDialog(self.path, "Rename", self.parent)
        rename.show()

    def get_path(self):
        selected, _ = self.getOpenFileName(self, "Import File", self.path, options=self.options(), filter='JSON(*.json)')

        if not selected:
            return None

        return selected
