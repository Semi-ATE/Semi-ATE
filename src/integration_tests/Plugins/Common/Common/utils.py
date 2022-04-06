from enum import IntEnum

class GPIOState(IntEnum):
    OFF = 0
    ON = 1
    NONE = 2

    def __call__(self):
        return self.value
