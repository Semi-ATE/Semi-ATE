import os

from ATE.spyder.widgets.actions_on.utils.ObserverBase import EventHandlerBase
from ATE.spyder.widgets.actions_on.utils.ObserverBase import ObserverBase


class EventHandler(EventHandlerBase):
    def __init__(self, section_root):
        super().__init__(section_root)

    def _on_file_created(self, path, modify=False):
        if not self._is_python_file(path):
            return

        # is test_program
        if '_' in os.path.basename(path):
            return

        base_name = os.path.basename(os.path.dirname(path))

        # TODO: workaround
        if self.section_root.get_child(base_name) is None:
            if not modify:
                self.section_root.add_file_item(base_name, os.path.dirname(path))
            else:
                self.section_root.add_file_item(base_name, os.path.dirname(os.path.dirname(path)))

    def _on_deleted(self, path):
        if not self._is_python_file(path):
            return

        file_name = os.path.basename(path)

        self.section_root.remove_child(os.path.splitext(file_name)[0])

    def _on_moved(self, path, dest_path):
        # TODO: wordaround

        self._on_file_created(dest_path, modify=True)

    def _is_python_file(self, path):
        # tree contains only python files
        if not os.path.splitext(os.path.basename(path))[1] == '.py':
            return False

        return True


class TestsObserver(ObserverBase):
    def __init__(self, path, section_root):
        self.event_handler = EventHandler(section_root)
        super().__init__(path, section_root)
