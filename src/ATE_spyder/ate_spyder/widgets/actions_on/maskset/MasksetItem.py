from ate_projectdatabase.Types import Types
from ate_spyder.widgets.actions_on.maskset.EditMasksetWizard import edit_maskset_dialog
from ate_spyder.widgets.actions_on.maskset.NewMasksetWizard import new_maskset_dialog
from ate_spyder.widgets.actions_on.maskset.ViewMasksetSettings import display_maskset_settings_dialog
from ate_spyder.widgets.actions_on.model.BaseItem import BaseItem
from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes
from ate_spyder.widgets.actions_on.utils.StateItem import StateItem

from ate_spyder.widgets.actions_on.utils.ExceptionHandler import (handle_excpetions,
                                                                  ExceptionTypes)


class MasksetItem(BaseItem):
    def __init__(self, project_info, name, parent=None):
        super().__init__(project_info, name, parent=parent)
        self.child_set = self._get_children_names()

    def _get_children_names(self):
        return self.project_info.get_maskset_names()

    def _create_child(self, name, parent):
        return MasksetItemChild(self.project_info, name, parent)

    def new_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: new_maskset_dialog(self.project_info),
                          ExceptionTypes.Maskset())

    def _get_menu_items(self):
        return [MenuActionTypes.Add()]


class MasksetItemChild(StateItem):
    def __init__(self, project_info, maskset, parent=None):
        super().__init__(project_info, maskset.name, parent=parent)

    @property
    def type(self):
        return Types.Maskset()

    @property
    def dependency_list(self):
        return self.project_info.get_dependant_objects_for_maskset(self.text())

    def edit_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: edit_maskset_dialog(self.project_info, self.text()),
                          ExceptionTypes.Maskset())

    def display_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: display_maskset_settings_dialog(self.project_info, self.text()),
                          ExceptionTypes.Maskset())

    def is_enabled(self):
        return self.project_info.get_maskset_state(self.text())

    def _update_item_state(self, enabled):
        self.project_info.update_maskset_state(self.text(), enabled)
        return enabled
