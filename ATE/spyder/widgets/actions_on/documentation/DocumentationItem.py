import os

from PyQt5 import QtGui
from PyQt5 import QtWidgets

from ATE.spyder.widgets.actions_on.documentation.BaseDocumentationItem import BaseDocumentationItem
from ATE.spyder.widgets.actions_on.model.Actions import ACTIONS
from ATE.spyder.widgets.actions_on.model.Constants import MenuActionTypes
from ATE.spyder.widgets.actions_on.utils.FileSystemOperator import FileSystemOperator


class DocumentationItem(BaseDocumentationItem):
    '''
    DocumentationItem is the presentation of a folder
    '''
    def __init__(self, name, path, project_info, parent=None, is_editable=True):
        self._is_editable = is_editable
        super().__init__(name, path, parent, project_info=project_info)
        self._set_icon()
        self.file_system_operator = FileSystemOperator(self.path, self.project_info.parent)

    def update_item(self, path):
        self.path = path
        self.setText(os.path.basename(path))
        self.file_system_operator(path)

    def add_dir_item(self, name, path, index=0):
        if self._does_item_already_exist(name):
            return

        is_editable = True
        if name in ('audits', 'exports'):
            is_editable = False

        item = DocumentationItem(name, path, self.project_info, parent=self, is_editable=is_editable)
        self.insertRow(index, item)

    def add_file_item(self, name, path, index=0):
        if self._does_item_already_exist(name):
            return

        item = DocumentationItemChild(name, path, self, self.project_info)
        self.insertRow(index, item)

    # copying directories recursively (import) does fire _on_file_created and _on_dir_created event multiple times
    # using this function we prevent creating same item multiple times
    def _does_item_already_exist(self, name):
        for index in range(self.rowCount()):
            if self.child(index).text() == name:
                return True

        return False

    def import_folder_item(self):
        self.file_system_operator.import_dir()

    def import_file_item(self):
        self.file_system_operator.import_file()

    def delete_item(self):
        self.file_system_operator.delete_dir()

    def rename_item(self):
        self.file_system_operator.rename()

    def move_item(self):
        self.file_system_operator.move()

    def add_file__item(self):
        self.file_system_operator.add_file()

    def add_folder_item(self):
        self.file_system_operator.add_dir()

    def _set_icon(self):
        if self.text() == 'documentation':
            return

        from ATE.spyder.widgets.actions_on.documentation.FileIcon import FileIcons
        from ATE.spyder.widgets.actions_on.documentation.Constants import FileIconTypes
        self.setIcon(FileIcons[FileIconTypes.FOLDER.name])

    def _get_menu_items(self):
        return [MenuActionTypes.Rename(),
                MenuActionTypes.Move(),
                None,
                MenuActionTypes.DeleteFile()]

    def exec_context_menu(self):
        self.menu = QtWidgets.QMenu(self.project_info.parent)
        self.menu.addMenu(self._generate_new_menu_actions(self.menu))
        self.menu.addMenu(self._generate_import_menu_actions(self.menu))

        if self._is_editable:
            from ATE.spyder.widgets.actions_on.model.Actions import ACTIONS

            for action_type in self._get_menu_items():
                if not action_type:
                    self.menu.addSeparator()
                    continue

                action = ACTIONS[action_type]
                action = self.menu.addAction(action[0], action[1])
                action.triggered.connect(getattr(self, action_type))

        self.menu.exec_(QtGui.QCursor.pos())

    def _generate_new_menu_actions(self, parent):
        new_menu = QtWidgets.QMenu('New', parent)
        import qtawesome as qta
        new_menu.setIcon(qta.icon('mdi.plus', color='orange'))

        new_file = QtWidgets.QAction(ACTIONS[MenuActionTypes.AddFile()][1], new_menu)
        new_file.setIcon(ACTIONS[MenuActionTypes.AddFile()][0])
        new_file.triggered.connect(self.add_file__item)

        new_folder = QtWidgets.QAction(ACTIONS[MenuActionTypes.AddFolder()][1], new_menu)
        new_folder.setIcon(ACTIONS[MenuActionTypes.AddFolder()][0])
        new_folder.triggered.connect(self.add_folder_item)

        new_menu.addAction(new_file)
        new_menu.addAction(new_folder)

        return new_menu

    def _generate_import_menu_actions(self, parent):
        menu_action = QtWidgets.QMenu('Import', parent)
        import qtawesome as qta
        menu_action.setIcon(qta.icon('mdi.application-import', color='orange'))

        import_file = QtWidgets.QAction(ACTIONS[MenuActionTypes.AddFile()][1], parent)
        import_file.setIcon(ACTIONS[MenuActionTypes.ImportFile()][0])
        import_file.triggered.connect(self.import_file_item)

        import_folder = QtWidgets.QAction(ACTIONS[MenuActionTypes.AddFolder()][1], parent)
        import_folder.setIcon(ACTIONS[MenuActionTypes.ImportFolder()][0])
        import_folder.triggered.connect(self.import_folder_item)

        menu_action.addAction(import_file)
        menu_action.addAction(import_folder)

        return menu_action


class DocumentationItemChild(BaseDocumentationItem):
    '''
    DocumentationItemChild is the presentation of a file
    '''
    def __init__(self, name, path, parent, project_info, is_editable=True):
        super().__init__(name, path, parent)
        _, extension = os.path.splitext(name)
        self._set_icon(extension)
        self.file_system_operator = FileSystemOperator(self.path, project_info.parent)

    def update_item(self, path):
        self.path = path
        self.setText(os.path.basename(path))
        self.file_system_operator(path)

    def rename_item(self):
        self.file_system_operator.rename()

    def delete_item(self):
        self.file_system_operator.delete_file()

    def move_item(self):
        self.file_system_operator.move()

    def _set_icon(self, extension):
        icon = self._get_icon(extension)
        if icon is None:
            return

        self.setIcon(icon)

    def _get_icon(self, extension):
        from ATE.spyder.widgets.actions_on.documentation.FileIcon import FileIcons
        from ATE.spyder.widgets.actions_on.documentation.Constants import FileIconTypes
        for name, member in FileIconTypes.__members__.items():
            if extension in member():
                return FileIcons[name]

        return None

    def _get_menu_items(self):
        return [MenuActionTypes.Rename(),
                MenuActionTypes.Move(),
                None,
                MenuActionTypes.Delete()]
