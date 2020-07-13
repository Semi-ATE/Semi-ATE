from ATE.org.actions_on.utils.ObserverBase import ObserverBase
from ATE.org.actions_on.utils.ObserverBase import EventHandlerBase

import os


class EventHandler(EventHandlerBase):
    def __init__(self, section_root):
        super().__init__(section_root)

    def _on_file_created(self, path):
        if not self._is_python_file(path):
            return

        # is test_program
        if '_' in os.path.basename(path):
            return

        base_name = os.path.basename(os.path.dirname(path))
        if self.section_root.get_child(base_name) is None:
            self.section_root.add_file_item(base_name, os.path.dirname(path))

    def _on_deleted(self, path):
        if not self._is_python_file(path):
            return

        file_name = os.path.basename(path)

        self.section_root.remove_child(os.path.splitext(file_name)[0])

    def _on_moved(self, path, dest_path):
        if not self._is_python_file(dest_path) and \
           not self._is_python_file(path):
            return

        file_name = os.path.basename(os.path.splitext(path)[0])
        if '_' in file_name and '_BC' not in file_name:
            child = self.section_root.get_child(file_name.split('_')[0]).get_child(file_name)
        else:
            child = self.section_root.get_child(file_name)

        row = child.row()
        cloned_child = self.section_root.takeChild(row)
        self.section_root.removeRow(row)

        cloned_child.update_item(dest_path)
        self.section_root.insertRow(row, cloned_child)

    def _is_python_file(self, path):
        # tree contains only python files
        if not os.path.splitext(os.path.basename(path))[1] == '.py':
            return False

        return True


class TestsObserver(ObserverBase):
    def __init__(self, path, section_root):
        self.event_handler = EventHandler(section_root)
        super().__init__(path, section_root)
