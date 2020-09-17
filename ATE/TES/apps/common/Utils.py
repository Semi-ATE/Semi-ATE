from enum import Enum


class LogLevel(Enum):
    Info = 'info'
    Warning = 'warning'
    Debug = 'debug'
    Error = 'error'

    def __call__(self):
        return self.value
