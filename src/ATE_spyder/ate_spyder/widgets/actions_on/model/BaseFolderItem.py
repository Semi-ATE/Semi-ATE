from ate_spyder.widgets.actions_on.model.BaseItem import BaseItem
from ate_spyder.widgets.actions_on.utils.FileSystemOperator import FileSystemOperator


class BaseFolderItem(BaseItem):
    def __init__(self, name, path, project_info, parent=None):
        super().__init__(project_info, name, parent)
        self.path = path
        self.file_system_operator = FileSystemOperator(self.path, self.project_info.parent)

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

    def _set_icon(self, extension):
        icon = self._get_icon(extension)
        if icon is None:
            return

        self.setIcon(icon)

    @staticmethod
    def _get_icon(extension):
        from ate_spyder.widgets.actions_on.documentation.FileIcon import FileIcons
        from ate_spyder.widgets.actions_on.documentation.Constants import FileIconTypes
        for name, member in FileIconTypes.__members__.items():
            if extension in member():
                return FileIcons[name]

        return None
