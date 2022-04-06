import os

from ate_spyder.widgets.actions_on.utils.ObserverBase import EventHandlerBase
from ate_spyder.widgets.actions_on.utils.ObserverBase import ObserverBase


class EventHandler(EventHandlerBase):
    def __init__(self, section_root, path):
        super().__init__()
        self.path = path
        self.section_root = section_root

    def _on_file_created(self, path, modify=False):
        if not self._is_python_file(path):
            return

        base_name = os.path.basename(path)
        if '_' in os.path.basename(base_name):
            # is test_program
            return

        if '.py' not in base_name:
            # we only care if it's a python file
            return

        # TODO: workaround
        # if self.section_root.get_child(os.path.splitext(base_name)[0]) is None:
        #     if not modify:
        #         self.section_root.add_file_item(base_name, os.path.dirname(path))
        #     else:
        #         self.section_root.add_file_item(base_name, os.path.dirname(os.path.dirname(path)))

    def _on_deleted(self, path):
        if not self._is_python_file(path):
            return

        file_name = os.path.basename(path)
        self.section_root.remove_child(os.path.splitext(file_name)[0])

    def _on_moved(self, path, dest_path):
        # TODO: workaround
        self._on_file_created(dest_path, modify=True)

    def _is_python_file(self, path):
        # tree contains only python files
        if not os.path.splitext(os.path.basename(path))[1] == '.py':
            return False

        return True


class TestsObserver(ObserverBase):
    def __init__(self, path, section_root):
        event_handler = EventHandler(section_root, path)
        super().__init__(event_handler)
