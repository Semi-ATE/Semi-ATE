from PyQt5 import QtCore
from watchdog.events import DirCreatedEvent
from watchdog.events import DirDeletedEvent
from watchdog.events import DirModifiedEvent
from watchdog.events import DirMovedEvent
from watchdog.events import FileCreatedEvent
from watchdog.events import FileDeletedEvent
from watchdog.events import FileModifiedEvent
from watchdog.events import FileMovedEvent
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


class EventHandlerBase(PatternMatchingEventHandler, QtCore.QObject):
    file_created = QtCore.pyqtSignal(str)
    dir_created = QtCore.pyqtSignal(str)
    deleted = QtCore.pyqtSignal(str)
    moved = QtCore.pyqtSignal(str, str)
    file_modified = QtCore.pyqtSignal(str)
    dir_modified = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._connect_event_handler()
        self.file_created.connect(self._on_file_created)
        self.dir_created.connect(self._on_dir_created)
        self.deleted.connect(self._on_deleted)
        self.moved.connect(self._on_moved)
        self.file_modified.connect(self._on_file_modified)
        self.dir_modified.connect(self._on_file_modified)

    def _connect_event_handler(self):
        self.on_any_event = self._on_any_event

    def _on_any_event(self, event):
        if isinstance(event, (FileCreatedEvent, DirCreatedEvent)):
            if event.is_directory:
                self.dir_created.emit(event.src_path)
            else:
                self.file_created.emit(event.src_path)

        elif isinstance(event, (FileModifiedEvent, DirModifiedEvent)):
            if event.is_directory:
                self.dir_modified.emit(event.src_path)
            else:
                self.file_modified.emit(event.src_path)

        elif isinstance(event, (FileMovedEvent, DirMovedEvent)):
            self.moved.emit(event.src_path, event.dest_path)

        elif isinstance(event, (FileDeletedEvent, DirDeletedEvent)):
            self.deleted.emit(event.src_path)

    def _on_file_created(self, path):
        pass

    def _on_dir_created(self, path):
        pass

    def _on_deleted(self, path):
        pass

    def _on_file_modified(self, event):
        pass

    def _on_dir_modified(self, event):
        # event is generated each time we do change the content of folder
        # ignore it for now
        pass

    def _on_moved(self, path, dest_path):
        pass

    def _get_changed_file_item(self, parent_item, file_name):
        return parent_item.get_child(file_name)


class ObserverBase:
    '''
    create doc content observer
    '''
    def __init__(self, event_handler):
        self.event_handler = event_handler
        self.path = event_handler.path

        self._init_observer()
        self._init_section()

    def _init_section(self):
        pass

    def _create_items(self, tree_elements):
        pass

    def _init_observer(self):
        self.go_recursively = True
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=self.go_recursively)

    def start_observer(self):
        try:
            self.observer.start()
        except OSError:
            print("Observer error")

    def stop_observer(self):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
