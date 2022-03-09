from PyQt5 import QtCore

from ate_spyder.widgets.actions_on.model.BaseItem import BaseItem
from ate_spyder.widgets.actions_on.model.Constants import MenuActionTypes


class StateItem(BaseItem):
    def __init__(self, project_info, name, parent=None):
        super().__init__(project_info, name, parent)

        self._set_current_state()
        self._set_tree_state(self.is_enabled())

    def _set_current_state(self):
        if len(self._are_dependencies_fulfilled()) == 0:
            return

        self._update_db_state(False)

    def _set_tree_state(self, is_enabled):
        if is_enabled:
            self._menu = self._enabled_item_menu()
            self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        else:
            self._menu = self._disabled_item_menu()
            self.setFlags(QtCore.Qt.ItemIsSelectable)

    def _set_state(self, enabled):
        flag = self._update_item_state(enabled)
        self.model().set_tree_items_state(self.text(), self.dependency_list, flag)
        self._set_tree_state(flag)

    def disable_item(self):
        self._set_state(False)

    def enable_item(self):
        dependencies = self._are_dependencies_fulfilled()
        enabled = len(dependencies) == 0
        self._set_state(enabled)
        if not enabled:
            from ate_spyder.widgets.actions_on.utils.ItemTrace import ItemTrace
            ItemTrace(dependencies, self.text(), self.project_info.parent, message='item depends on the elemnt(s) \nabove which is(are) disabled').exec_()

    def trace_item(self):
        from ate_spyder.widgets.actions_on.utils.ItemTrace import ItemTrace
        ItemTrace(self.dependency_list, self.text(), self.project_info.parent).exec_()

    def _are_dependencies_fulfilled(self):
        return {}

    def _disabled_item_menu(self):
        return [MenuActionTypes.Enable()]

    def _get_menu_items(self):
        return self._menu

    def _update_item_state(self, is_enabled):
        enabled = False
        if is_enabled:
            if len(self._are_dependencies_fulfilled()) == 0:
                enabled = True

        self._update_db_state(enabled)
        return enabled

    def _enabled_item_menu(self):
        return [MenuActionTypes.Edit(),
                MenuActionTypes.View(),
                MenuActionTypes.Trace(),
                None,
                self._dependant_menu_type()]

    def _dependant_menu_type(self):
        if not len(self.dependency_list):
            return MenuActionTypes.Delete()
        else:
            return MenuActionTypes.Obsolete()

    def delete_item(self):
        self.project_info.delete_item(self.type, self.text())
