from ate_spyder.widgets.actions_on.model.FileItem import FileItem
from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes


class WaveItem(FileItem):
    def __init__(self, name, path, project_info, parent=None):
        super().__init__(name, path, project_info, parent=parent)

    @staticmethod
    def _get_menu_items():
        return [MenuActionTypes.ImportFile(),
                MenuActionTypes.CloneFrom()]

    @staticmethod
    def is_valid_functionality(functionality):
        return not functionality == MenuActionTypes.CloneFrom()
