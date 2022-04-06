from enum import IntEnum
import os
import shutil

import qtawesome as qta
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from pathlib import Path

from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog
from ate_spyder.widgets.navigation import ProjectNavigation


STANDARD_DIALOG = 'Standard.ui'
DELETE_DIALOG = 'Delete.ui'
RENAME_DIALOG = 'Rename.ui'
ORANGE_LABEL = 'color: orange'


class MenuDialog(BaseDialog):
    def __init__(self, ui_name, action, parent):
        ui_file = os.path.join(os.path.dirname(__file__), ui_name)
        super().__init__(ui_file, parent)
        self.action = action
        for _ in self._steps():
            pass

    def _steps(self):
        self._setup()
        yield
        self._connect_action_handler()

    def show(self):
        return self.exec_()

    def _setup(self):
        self.setWindowTitle(self.action)
        self.setFixedSize(self.size())
        self.ok_button = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        self.cancel_button = self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)

    def _connect_action_handler(self):
        self.ok_button.clicked.connect(self._accept)
        self.cancel_button.clicked.connect(self._cancel)

    def _accept(self):
        self.accept()

    def _cancel(self):
        self.reject()


class DeleteFileDialog(MenuDialog):
    def __init__(self, path, action, parent):
        super().__init__(DELETE_DIALOG, action, parent)
        self.path = path
        self.icon_label.setPixmap(qta.icon('mdi.alert-outline', color='orange').pixmap(50, 50))
        font = QtGui.QFont()
        font.setBold(True)
        self.file_name_label.setFont(font)
        self.file_name_label.setText(os.path.basename(self.path))
        self.label.setText("Are you sure you want to delete")

    def _accept(self):
        os.remove(self.path)
        self.accept()


class DeleteDirDialog(DeleteFileDialog):
    def __init__(self, path, action, parent):
        super().__init__(path, action, parent)

    def _accept(self):
        shutil.rmtree(self.path)
        self.accept()


class RenameDialog(MenuDialog):
    def __init__(self, path, action, parent):
        super().__init__(RENAME_DIALOG, action, parent)
        self.path = path
        self.fileName.setText(os.path.basename(self.path))
        self.fileName.textChanged.connect(self.validate)
        self.fileName.setFocus(QtCore.Qt.MouseFocusReason)

    def validate(self, text):
        if not text:
            self.feedback.setText("name field is empty")
            self.feedback.setStyleSheet("color: orange")
            self.ok_button.setDisabled(True)
            return

        self.feedback.setText("")
        self.ok_button.setDisabled(False)

    def _accept(self):
        shutil.move(self.path, os.path.join(os.path.dirname(self.path), self.fileName.text()))
        self.accept()


class NewGroupDialog(MenuDialog):
    def __init__(self, path: str, action: str, parent, project_info: ProjectNavigation, group_parent: str):
        super().__init__(RENAME_DIALOG, action, parent)
        self.path = path
        from ate_spyder.widgets.validation import valid_name_regex
        name_validator = QtGui.QRegExpValidator(QtCore.QRegExp(valid_name_regex), self)
        self.fileName.setValidator(name_validator)
        self.fileName.setText(os.path.basename(self.path))
        self.fileName.textChanged.connect(self.validate)
        self.fileName.setFocus(QtCore.Qt.MouseFocusReason)
        self.project_info = project_info
        self.groups = project_info.get_groups()
        self.group_parent = group_parent
        self.group_name = None

    def validate(self, text):
        if not text or text in [group.name for group in self.groups]:
            self.feedback.setText("name is not valid or already used")
            self.feedback.setStyleSheet("color: orange")
            self.ok_button.setDisabled(True)
            return

        self.feedback.setText("")
        self.ok_button.setDisabled(False)

    def _accept(self):
        self.group_name = self.fileName.text()
        self.accept()


def new_group(project_info: ProjectNavigation, group_parent: str):
    new_dialog = NewGroupDialog('', 'New Group', project_info.parent, project_info, group_parent)
    if not new_dialog.exec_():
        return None
    name = new_dialog.group_name
    del(new_dialog)
    return name


class AddDirectoryDialog(RenameDialog):
    def __init__(self, path, action, parent):
        super().__init__(RENAME_DIALOG, action, parent)
        self.path = path
        self.fileName.setText('')

    def _accept(self):
        try:
            os.mkdir(os.path.join(self.path, self.fileName.text()))
        except Exception as e:
            print(e)

        self.accept()


class ExceptionFoundDialog(DeleteFileDialog):
    def __init__(self, path, action, parent, message):
        super().__init__(path, action, parent)
        self.label.setText(f"{message}")

    def _accept(self):
        self.accept()


class Action(IntEnum):
    Rename = 0
    Overwrite = 1


class ImportDialog(BaseDialog):
    def __init__(self, parent):
        ui_file = Path(__file__).parent.joinpath('ImportDialog.ui')
        super().__init__(str(ui_file), parent)
        self._connect_action_handler()

    def _connect_action_handler(self):
        from ate_spyder.widgets.validation import valid_name_regex
        test_name_validator = QtGui.QRegExpValidator(QtCore.QRegExp(valid_name_regex), self)
        self.fileName.setValidator(test_name_validator)
        self.rename.clicked.connect(self._rename)
        self.overwrite.clicked.connect(self._overwrite)
        self.cancel.clicked.connect(self._cancel)
        self.feedback.setText('')
        self.feedback.setStyleSheet(ORANGE_LABEL)

    def _cancel(self):
        self.reject()

    def _rename(self):
        name = self.fileName.text()
        if not name:
            self.feedback.setText('make sure to insert a name')
            return

        self.action = {'type': Action.Rename, 'data': {'name': name}}
        self.accept()

    def _overwrite(self):
        self.action = {'type': Action.Overwrite, 'data': {}}
        self.accept()


class StandardDialog(MenuDialog):
    def __init__(self, parent, message):
        super().__init__(STANDARD_DIALOG, 'Version Mismatch', parent)
        self.label.setText(f"{message}")
        self.icon_label.setPixmap(qta.icon('mdi.alert-outline', color='orange').pixmap(50, 50))
        self.ok_button = self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok)
        self.cancel_button = self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel)
