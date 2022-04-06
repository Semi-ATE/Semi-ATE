from ate_spyder.widgets.actions_on.die.DieWizard import new_die_dialog
from ate_spyder.widgets.actions_on.die.EditDieWizard import edit_die_dialog
from ate_spyder.widgets.actions_on.die.ViewDieWizard import display_die_settings_dialog
from ate_spyder.widgets.actions_on.model.BaseItem import BaseItem
from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes
from ate_spyder.widgets.actions_on.utils.StateItem import StateItem

from ate_spyder.widgets.actions_on.utils.ExceptionHandler import (handle_excpetions,
                                                                  ExceptionTypes)


class DieItem(BaseItem):
    def __init__(self, project_info, name, parent=None):
        super().__init__(project_info, name, parent=parent)
        self.child_set = self._get_children_names()

    def _get_children_names(self):
        return self.project_info.get_dies()

    def _create_child(self, name, parent):
        return DieItemChild(self.project_info, name.name, parent)

    def _get_menu_items(self):
        return [MenuActionTypes.Add()]

    def new_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: new_die_dialog(self.project_info),
                          ExceptionTypes.Die())


class DieItemChild(StateItem):
    def __init__(self, project_info, name, parent=None):
        super().__init__(project_info, name, parent=parent)

    def edit_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: edit_die_dialog(self.project_info, self.text()),
                          ExceptionTypes.Die())

    def display_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: display_die_settings_dialog(self.text(), self.project_info),
                          ExceptionTypes.Die())

    @property
    def type(self):
        return 'dies'

    @property
    def dependency_list(self):
        return self.project_info.get_dependant_objects_for_die(self.text())

    def is_enabled(self):
        return self.project_info.get_die_state(self.text())

    def _update_db_state(self, enabled):
        self._update_item_state(enabled)

    def _update_item_state(self, enabled):
        self.project_info.update_die_state(self.text(), enabled)
        return enabled

    def _are_dependencies_fulfilled(self):
        dependency_list = {}
        hw = self.project_info.get_die_hardware(self.text())
        maskset = self.project_info.get_die_maskset(self.text())
        hw_enabled = self.project_info.get_hardware_state(hw)
        maskset_enabled = self.project_info.get_maskset_state(maskset)

        if not hw_enabled:
            dependency_list.update({'hardwares': [hw]})
        if not maskset_enabled:
            dependency_list.update({'maskset': [maskset]})

        return dependency_list

    def delete_item(self):
        self.project_info.remove_die(self.text())
