from ate_spyder.widgets.actions_on.model.BaseItem import BaseItem


class TreeNode:
    def __init__(self, name: str, item: BaseItem, root,
                 parent=None, prev=None, next=None):
        self.parent: TreeNode = parent
        self.prev: TreeNode = prev
        self.next: TreeNode = next
        self.name = name
        self.item = item
        self.root = root

    def get_parent(self):
        return self.parent

    def get_name(self):
        return self.name

    def is_root(self) -> bool:
        return self.parent is None


class TestElementTree:
    def __init__(self, root_name: str, tree_item: BaseItem):
        self._root = TreeNode(root_name, tree_item, self)
        self._last_element = self._root

    def add_item(self, name: str, tree_item: BaseItem):
        item = TreeNode(name, tree_item, self._root, parent=self._last_element, prev=self._last_element, next=self._last_element)
        item.next = self._last_element.next if self._last_element.next is not None else self._last_element
        self._last_element.next = item
        self._last_element = item

    @staticmethod
    def remove_item(item_name: TreeNode):
        next: TreeNode = item_name.next
        prev: TreeNode = item_name.prev

        next.prev = prev
        prev.next = next

        del(item_name)

    def find_element(self, name: str):
        item: TreeNode = self._root.next
        while not item.is_root():

            if item.get_name() == name:
                return item
            item = item.next

        return None

    def get_root(self):
        return self._root


class TestElementTreeHandler:
    def __init__(self, section_name, tree_item):
        self._trees: TestElementTree = {}
        self.main_node = TestElementTree(section_name, tree_item)

    def add_tree(self, root_name: str, tree_item: BaseItem):
        self._trees[root_name] = TestElementTree(root_name, tree_item)

    def add_element(self, node_name: str, tree_item: BaseItem):
        self._trees[node_name] = TreeNode(node_name, tree_item, self.main_node)

    def add_element_to_node(self, root_name: str, node_name: str, tree_item: BaseItem):
        self._trees[root_name].add_item(node_name, tree_item)

    def get_tree(self, root_name):
        return self._trees[root_name]
