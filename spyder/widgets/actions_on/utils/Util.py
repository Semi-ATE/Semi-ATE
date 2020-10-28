import os


def get_changed_dir_item(section_root, path, base_path):
    diff_path = os.path.relpath(path, base_path)
    items = diff_path.split(os.sep)
    parent_item = section_root

    for index in range(len(items) - 1):
        item = parent_item.get_child(items[index])
        parent_item = item

    return parent_item
    # kursiv Fall
    # name = items[len(items) - 2]
    # return self._get_parent(parent_item, items, 0, name)


def _get_parent(self, item, items, index, name):
    parent = item.get_child(items[index])
    if parent.name == name:
        return parent

    index += 1
    if index == len(items) - 1:
        return None

    return self._get_parent(parent, items, index, name)
