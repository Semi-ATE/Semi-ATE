from ATE.spyder.widgets.actions_on.model.BaseItem import BaseItem


class BaseDocumentationItem(BaseItem):
    def __init__(self, name, path, parent=None, project_info=None):
        super().__init__(project_info, name, parent)
        self.path = path

    def add_file__item(self):
        pass

    def add_folder_item(self):
        pass

    def import_folder_item(self):
        pass

    def import_file_item(self):
        pass

    def rename_item(self):
        pass
