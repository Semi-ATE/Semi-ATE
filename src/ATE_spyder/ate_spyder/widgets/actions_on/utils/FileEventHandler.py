from ate_spyder.widgets.actions_on.utils.ObserverBase import EventHandlerBase
import os


class FileEventHandler(EventHandlerBase):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.sections = []

    def _on_file_created(self, path):
        if not self.sections:
            return

        dir_name = os.path.dirname(path)
        for section in self.sections:
            if not section.is_hidden() and section.name in dir_name:
                section.add_file_item(path)

    def _on_deleted(self, path):
        if not self.sections:
            return

        dir_name = os.path.dirname(path)
        for section in self.sections:
            if not section.is_hidden() and section.name in dir_name:
                section.remove_file_item(path)

    def append_section(self, section):
        self.sections.append(section)
