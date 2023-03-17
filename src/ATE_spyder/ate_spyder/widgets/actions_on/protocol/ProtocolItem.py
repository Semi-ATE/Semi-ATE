from ate_spyder.widgets.actions_on.model.BaseItem import BaseItem
from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes

from ate_spyder.widgets.actions_on.utils.ExceptionHandler import (handle_exceptions,
                                                                  ExceptionTypes)
from ate_spyder.widgets.actions_on.protocol.NewProtocolWizard import new_protocol_dialog


class ProtocolItem(BaseItem):
    def __init__(self, name, project_info):
        super().__init__(project_info, name, project_info.parent)

    def new_item(self):
        handle_exceptions(self.project_info.parent,
                          lambda: new_protocol_dialog(self.project_info),
                          ExceptionTypes.Protocol())

    def clone_from_item(self):
        pass
    
    def compile_protocols_files(self):
        self.project_info.compile_protocols(self.text())

    def _get_menu_items(self):
        menu = [MenuActionTypes.Add(),
                MenuActionTypes.CloneFrom()]
        
        # the stil file compilation option should be only enabled
        # if the protocols stil files available
        if self.project_info.get_protocols(self.text()):
            menu.insert(len(menu), MenuActionTypes.CompileProtocols())
        
        return menu

    @staticmethod
    def is_valid_functionality(functionality):
        return functionality not in (MenuActionTypes.Add(), MenuActionTypes.CloneFrom())


class ProtocolItemChild(BaseItem):
    def __init__(self, name, path, project_info, parent=None):
        super().__init__(name, path, project_info, parent=parent)

    def delete_item(self):
        pass

    @staticmethod
    def _get_menu_items():
        return [MenuActionTypes.DeleteFile()]
