from ate_spyder.widgets.navigation import ProjectNavigation
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


class BaseItem(QtGui.QStandardItem):
    def __init__(self, project_info: ProjectNavigation, name, parent=None):
        super().__init__(name)
        self.parent = parent
        self.project_info = project_info

        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.setToolTip(self._get_tooltip())

        self.hidden_children = []
        self._is_hidden = False

        self._append_children()

    def exec_context_menu(self):
        self.menu = QtWidgets.QMenu(self.project_info.parent)
        from ate_spyder.widgets.actions_on.model.Actions import ACTIONS

        menu_items = self._get_menu_items()

        if len(menu_items) == 0:
            return

        for action_type in menu_items:
            if not action_type:
                self.menu.addSeparator()
                continue

            action = ACTIONS[action_type]
            action = self.menu.addAction(action[0], action[1])

            if not self.is_valid_functionality(action_type):
                action.setEnabled(False)

            action.triggered.connect(getattr(self, action_type))

        if self.is_hidden():
            return

        self.menu.exec_(QtGui.QCursor.pos())

    @staticmethod
    def is_valid_functionality(functionality):
        return True

    def update(self):
        self.removeRows(0, self.rowCount())
        self._append_children()

    def row_count(self):
        return self.rowCount()

    def new_item(self):
        pass

    def trace_item(self):
        pass

    def edit_item(self):
        pass

    def delete_item(self):
        pass

    def display_item(self):
        pass

    def import_item(self):
        pass

    def clone_from_item(self):
        pass

    def clone_to_item(self):
        pass

    def tace_usage_item(self):
        pass

    def add_standard_test_item(self):
        pass

    def add_testprogram(self):
        pass

    def export_item(self):
        pass

    def _get_tooltip(self):
        return ''

    def _get_menu_items(self):
        return []

    def _get_children_names(self):
        return []

    def set_children_hidden(self, hide: bool):
        self._is_hidden = hide
        if hide:
            self._hide_children()
        else:
            self._show_children()

    def _hide_children(self):
        for index in range(self.rowCount()):
            self.hidden_children.append(self.takeChild(index))

        while self.rowCount():
            self.removeRow(0)

        self.setFlags(QtCore.Qt.NoItemFlags)

    def _show_children(self):
        for index, item in enumerate(self.hidden_children):
            self.insertRow(index, item)

        self.hidden_children = []
        self.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)

    def has_children(self):
        # ToDo: _get_children_names queries all items
        # of a given type resulting in the fact, that
        # we actually have to use a nameproperty of
        # the culd here -> fix this. Also:
        # check if _get_children_names ever returns
        # none objects.
        return len(self._get_children_names()) > 0
        # for child in self._get_children_names():
        #     item = self.get_child(child.name)
        #     if item is not None:
        #         return True
        # return False

    def is_hidden(self):
        return self._is_hidden

    def get_child(self, name):
        for index in range(self.rowCount()):
            item = self.child(index)
            if item.text() == name:
                return item

        return None

    def remove_child(self, name):
        child_item = self.get_child(name)
        if child_item is None:
            return

        self.removeRow(child_item.row())

    def _set_node_state(self, dependency_list, enabled):
        for index in range(self.rowCount()):
            item = self.child(index)
            if item.text() not in dependency_list:
                continue

            item._set_state(enabled)

    def _append_children(self):
        children = self._get_children_names()
        for child in children:
            child_item = self._create_child(child, self)
            self.appendRow(child_item)
