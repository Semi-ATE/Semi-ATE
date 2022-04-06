from ate_spyder.widgets.actions_on.device.EditDeviceWizard import edit_device_dialog
from ate_spyder.widgets.actions_on.device.NewDeviceWizard import new_device_dialog
from ate_spyder.widgets.actions_on.device.ViewDeviceWizard import display_device_settings_dialog
from ate_spyder.widgets.actions_on.model.BaseItem import BaseItem
from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes
from ate_spyder.widgets.actions_on.utils.StateItem import StateItem

from ate_spyder.widgets.actions_on.utils.ExceptionHandler import (handle_excpetions,
                                                                  ExceptionTypes)


class DeviceItem(BaseItem):
    def __init__(self, project_info, name, parent=None):
        super().__init__(project_info, name, parent=parent)
        self.child_set = self._get_children_names()

    def _get_children_names(self):
        return self.project_info.get_device_names()

    def _create_child(self, name, parent):
        return DeviceItemChild(self.project_info, name, parent)

    def _get_menu_items(self):
        return [MenuActionTypes.Add()]

    def new_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: new_device_dialog(self.project_info),
                          ExceptionTypes.Device())


class DeviceItemChild(StateItem):
    def __init__(self, project_info, name, parent=None):
        super().__init__(project_info, name, parent=parent)

    def edit_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: edit_device_dialog(self.project_info, self.text()),
                          ExceptionTypes.Device())

    def display_item(self):
        handle_excpetions(self.project_info.parent,
                          lambda: display_device_settings_dialog(self.text(), self.project_info),
                          ExceptionTypes.Device())

    def is_enabled(self):
        return self.project_info.get_device_state(self.text())

    def _update_db_state(self, enabled):
        return self.project_info.update_device_state(self.text(), enabled)

    @property
    def type(self):
        return 'devices'

    @property
    def dependency_list(self):
        return self.project_info.get_dependant_objects_for_device(self.text())

    def _are_dependencies_fulfilled(self):
        dependency_list = {}
        hw = self.project_info.get_device_hardware(self.text())
        dies = self.project_info.get_device_dies(self.text())
        package = self.project_info.get_device_package(self.text())
        hw_enabled = self.project_info.get_hardware_state(hw)
        package_enabled = self.project_info.get_package_state(package)

        dies_enabled = []
        for die in dies:
            die_flag = self.project_info.get_die_state(die.split('_')[0])
            t = (die, die_flag)
            dies_enabled.append(t)

        used_dies = []
        if not hw_enabled:
            dependency_list.update({'hardwares': [hw]})
        for die_flag in dies_enabled:
            if not die_flag[1]:
                used_dies.append(die_flag[0])

        if len(used_dies):
            dependency_list.update({'dies': used_dies})
        if not package_enabled:
            dependency_list.update({'packages': [package]})

        return dependency_list

    def delete_item(self):
        self.project_info.remove_device(self.text())
