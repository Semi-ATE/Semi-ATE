from ate_spyder.widgets.actions_on.hardwaresetup.EditHardwaresetupWizard import edit_hardwaresetup_dialog
from ate_spyder.widgets.actions_on.hardwaresetup.HardwareWizard import new_hardwaresetup_dialog
from ate_spyder.widgets.actions_on.hardwaresetup.ViewHardwaresetupSettings import display_hardware_settings_dialog
from ate_spyder.widgets.actions_on.model.BaseItem import BaseItem
from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes
from ate_spyder.widgets.actions_on.utils.StateItem import StateItem

from ate_spyder.widgets.actions_on.utils.ExceptionHandler import (handle_excpetions,
                                                                  ExceptionTypes)


class HardwaresetupItem(BaseItem):
    def __init__(self, project_info, name, parent=None):
        super().__init__(project_info, name, parent=parent)
        self.child_set = self._get_children_names()

        self.hidden_children = []

    def _get_children_names(self):
        return self.project_info.get_hardware_names()

    def _create_child(self, name, parent):
        return HardwaresetupItemChild(self.project_info, name, parent)

    def new_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: new_hardwaresetup_dialog(self.project_info),
                          ExceptionTypes.Hardware())

    def _get_menu_items(self):
        return [MenuActionTypes.Add()]


class HardwaresetupItemChild(StateItem):
    def __init__(self, project_info, hwrecord, parent):
        super().__init__(project_info, hwrecord, parent=parent)

    @property
    def type(self):
        return 'hardwares'

    @property
    def dependency_list(self):
        return self.project_info.get_dependant_objects_for_hardware(self.text())

    def activate_item(self):
        self.project_info.update_active_hardware(self.text())

    def edit_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: edit_hardwaresetup_dialog(self.project_info, self.text()),
                          ExceptionTypes.Hardware())

    def display_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: display_hardware_settings_dialog(self.text(), self.project_info),
                          ExceptionTypes.Hardware())

    def is_enabled(self):
        return self.project_info.get_hardware_state(self.text())

    def _update_item_state(self, enabled):
        self.project_info.update_hardware_state(self.text(), enabled)
        return enabled

    def _enabled_item_menu(self):
        menu = super()._enabled_item_menu()
        menu.insert(0, MenuActionTypes.Activate())
        return menu

    def delete_item(self):
        self.project_info.remove_hardware(self.text())
