from ate_spyder.widgets.actions_on.documentation.DocumentationItem import DocumentationItem
from ate_spyder.widgets.actions_on.utils.Util import get_changed_dir_item
from ate_spyder.widgets.actions_on.utils.ObserverBase import ObserverBase
from ate_spyder.widgets.actions_on.utils.ObserverBase import EventHandlerBase

import os


class EventHandler(EventHandlerBase):
    def __init__(self, section_root, path):
        super().__init__()
        self.path = path
        self.section_root = section_root

    def _on_file_created(self, path):
        file_name = os.path.basename(path)
        parent_item = get_changed_dir_item(self.section_root, path, self.path)
        parent_item.add_file_item(file_name, path, parent_item.rowCount())

    def _on_dir_created(self, path):
        dir_name = os.path.basename(path)
        parent_item = get_changed_dir_item(self.section_root, path, self.path)
        parent_item.add_dir_item(dir_name, path, parent_item.rowCount())

    def _on_deleted(self, path):
        file_name = os.path.basename(path)
        parent_item = get_changed_dir_item(self.section_root, path, self.path)
        parent_item.remove_child(file_name)

    def _on_file_modified(self, event):
        # ignored for now
        pass

    def _on_dir_modified(self, event):
        # event is generated each time we do change the content of folder
        # ignore it for now
        pass

    def _on_moved(self, path, dest_path):
        file_name = os.path.basename(path)
        parent_item = get_changed_dir_item(self.section_root, path, self.path)

        # to prevent emiting an event, child will be token from the tree and modified
        child_item = self._get_changed_file_item(parent_item, file_name)

        row = child_item.row()
        item = parent_item.takeChild(row)
        item.update_item(dest_path)

        # remove invalid row and append the child again
        parent_item.removeRow(row)
        parent_item.insertRow(row, item)

    def _get_changed_file_item(self, parent_item, file_name):
        return parent_item.get_child(file_name)


class DocumentationObserver(ObserverBase):
    '''
    create doc content observer
    '''
    def __init__(self, path, section_root):
        self.section_root = section_root
        event_handler = EventHandler(self.section_root, path)
        super().__init__(event_handler)

    def _generate_dir_item(self, name, path, parent):
        return DocumentationItem(name, path, parent)

    def _init_section(self):
        tree_elements = []
        for root, _, files in os.walk(self.path):
            root_basename = os.path.basename(os.path.normpath(root))
            parent = os.path.basename(os.path.abspath(os.path.join(root, os.pardir)))
            level = root.replace(self.path, '').count(os.sep)
            node = (root_basename, files, parent, level, root)
            tree_elements.append(node)

        # pop all file inside root at the end
        tree_elements.insert(len(tree_elements) - 1, tree_elements.pop(0))
        self._create_items(tree_elements)

    def _create_items(self, tree_elements):
        for element in tree_elements:
            item = self.section_root
            root_file = element[0]  # str
            files = element[1]  # list
            level = element[3]  # int
            path = element[4]  # str

            if level == 1:
                self.section_root.add_dir_item(root_file, path, self.section_root.rowCount())
                item = self.section_root.get_child(root_file)
            elif level > 1:  # skip the case were level == 0
                parent_item = get_changed_dir_item(self.section_root, path, self.path)
                parent_item.add_dir_item(root_file, path)
                item = parent_item.get_child(root_file)

            for f in files:
                item.add_file_item(f, os.path.join(path, f), item.rowCount())
