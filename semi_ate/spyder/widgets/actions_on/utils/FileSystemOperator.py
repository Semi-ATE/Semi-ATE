from ATE.org.actions_on.utils.MenuDialog import DeleteFileDialog, DeleteDirDialog, RenameDialog, AddDirectoryDialog
from PyQt5 import QtWidgets

import os
import shutil


class FileSystemOperator(QtWidgets.QFileDialog):
    def __init__(self, path):
        super().__init__()
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
        add_dir = AddDirectoryDialog(self.path, "Folder name")
        add_dir.show()

    def import_file(self):
        selected, _ = self.getSaveFileName(self, "Save File", self.path, "", options=self.options())
        if not selected:
            return

        file_name = os.path.basename(selected)
        desired_location = os.path.join(self.path, file_name)
        try:
            shutil.copyfile(selected, desired_location)
        except Exception as e:
            print(e)
            print("file exists already")

    def import_dir(self):
        selected = self.getExistingDirectory(self, "Select directory", self.path, options=self.options())
        if not selected:
            return

        try:
            shutil.copytree(selected, os.path.join(self.path, os.path.basename(selected)))
        except Exception as e:
            print(e)

    def move(self):
        selected = self.getExistingDirectory(self, "Select directory", self.path, options=self.options())
        if not selected:
            return
        try:
            shutil.move(self.path, selected)
        except Exception as e:
            print("file exists already", e)

    def delete_file(self):
        delete = DeleteFileDialog(self.path, "Remove")
        return delete.show()

    def delete_dir(self):
        delete = DeleteDirDialog(self.path, "Remove")
        delete.show()

    def rename(self):
        rename = RenameDialog(self.path, "Rename")
        rename.show()
