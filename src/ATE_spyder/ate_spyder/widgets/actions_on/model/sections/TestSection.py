from ate_spyder.widgets.actions_on.tests.TestItem import GroupItem, TestItem
from ate_spyder.widgets.navigation import ProjectNavigation
from qtpy.QtGui import QStandardItemModel, QStandardItem


class TestSection(TestItem):
    def __init__(self, project_nav: ProjectNavigation, label: str, path: str, parent: QStandardItemModel) -> None:
        super().__init__(project_nav, label, path, parent)

    def remove_test_target_item(self, target_name: str, test_name: str):
        for index in range(self.rowCount()):
            test_item = self.child(index)
            if isinstance(test_item, GroupItem):
                for index in range(test_item.rowCount()):
                    group_item = test_item.child(index)
                    self._remove_test_target(group_item, test_name, target_name)
                continue

            self._remove_test_target(test_item, test_name, target_name)

    @staticmethod
    def _remove_test_target(test_item: QStandardItem, test_name: str, target_name: str):
        if (test_item is None) or (test_item.text() != test_name):
            return

        for test_target_index in range(test_item.rowCount()):
            test_target_item = test_item.child(test_target_index)
            if test_target_item is None or target_name != test_target_item.text():
                continue

            test_target_item.clean_up()
            test_item.removeRow(test_target_index)

    def update_test_items(self, text):
        for index in range(self.rowCount()):
            item = self.child(index)

            if isinstance(item, GroupItem):
                for index in range(item.rowCount()):
                    test_item = item.child(index)
                    self._update_test_item(test_item, text)
                continue

            self._update_test_item(item, text)

    @staticmethod
    def _update_test_item(item: QStandardItem, text: str):
        item._set_tree_state(True)

        available_test_targets_for_current_test_item = item.get_available_test_targets()
        actual_test_targets_for_current_test_item = item.get_children()
        new_items = list(set(available_test_targets_for_current_test_item) - set(actual_test_targets_for_current_test_item))

        for new_item in new_items:
            item.add_target_item(new_item)

        for test_target_index in range(item.rowCount()):
            test_target_item = item.child(test_target_index)
            if test_target_item is None:
                continue

            test_target_item.update_state(text)

    def update_test_items_hw_changed(self, _hardware):
        for index in range(self.rowCount()):
            self.takeChild(index)

        self.update()

    def update_group_items(self, test_name: str, groups: list):
        for index in range(self.rowCount()):
            tree_item = self.child(index)
            if isinstance(tree_item, GroupItem):
                self._update_group_items(tree_item, test_name, groups)

        self._update_test_section_items(test_name, groups)

    def _update_test_section_items(self, test_name: str, groups: list):
        if self.text() not in groups:
            for index in range(self.rowCount()):
                tree_item = self.child(index)
                if isinstance(tree_item, GroupItem):
                    continue

                if tree_item.text() != test_name:
                    continue

                self.removeRow(index)
                break
        else:
            for index in range(self.rowCount()):
                tree_item = self.child(index)
                if isinstance(tree_item, GroupItem):
                    continue

                if tree_item.text() == test_name:
                    return

            self.add_child(test_name)

    def _update_group_items(self, group_item: QStandardItem, test_name: str, groups: list):
        if (group_item is None):
            return

        group_name = group_item.text()
        if group_name in groups:
            group_item.update_child_items(test_name, True)
        else:
            group_item.update_child_items(test_name)
