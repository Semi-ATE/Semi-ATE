from ate_spyder.widgets.actions_on.utils.ObserverBase import ObserverBase
from ate_spyder.widgets.actions_on.utils.FileEventHandler import FileEventHandler


class FileObserver(ObserverBase):
    def __init__(self, path):
        event_handler = FileEventHandler(path)
        super().__init__(event_handler)

    def append_section(self, section):
        self.event_handler.append_section(section)
