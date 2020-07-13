from ATE.org.actions_on.maskset.NewMasksetWizard import new_maskset_dialog
from ATE.org.actions_on.maskset.EditMasksetWizard import edit_maskset_dialog
from ATE.org.actions_on.maskset.ViewMasksetSettings import display_maskset_settings_dialog

from ATE.org.actions_on.model.Constants import MenuActionTypes
from ATE.org.actions_on.model.BaseItem import BaseItem
from ATE.org.actions_on.utils.StateItem import StateItem


class MasksetItem(BaseItem):
    def __init__(self, project_info, name, parent=None):
        super().__init__(project_info, name, parent=parent)
        self.child_set = self._get_children_names()

    def _get_children_names(self):
        return self.project_info.get_maskset_names()

    def _create_child(self, name, parent):
        return MasksetItemChild(self.project_info, name, parent)

    def new_item(self):
        new_maskset_dialog(self.project_info)

    def _get_menu_items(self):
        return [MenuActionTypes.Add()]


class MasksetItemChild(StateItem):
    def __init__(self, project_info, maskset, parent=None):
        super().__init__(project_info, maskset.name, parent=parent)
        self.definition = self._get_definition()

    @property
    def type(self):
        return "masksets"

    @property
    def dependency_list(self):
        return self.project_info.get_dependant_objects_for_maskset(self.text())

    def edit_item(self):
        edit_maskset_dialog(self.project_info, self.text())

    def display_item(self):
        configuration = self._get_definition()
        display_maskset_settings_dialog(self.project_info, configuration, self.text())

    def is_enabled(self):
        return self.project_info.get_maskset_state(self.text())

    def _get_definition(self):
        return self.project_info.get_maskset_definition(self.text())

    def _update_item_state(self, enabled):
        self.project_info.update_maskset_state(self.text(), enabled)
        return enabled
