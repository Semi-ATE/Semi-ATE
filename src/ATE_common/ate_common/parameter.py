from enum import Enum, unique


@unique
class InputColumnKey(Enum):
    SHMOO = 'shmoo'
    NAME = 'name'
    MIN = 'min'
    DEFAULT = 'default'
    MAX = 'max'
    POWER = 'exp10'
    UNIT = 'unit'
    FMT = 'fmt'

    def __call__(self):
        return self.value


@unique
class OutputColumnKey(Enum):
    NAME = 'name'
    LSL = 'lsl'
    LTL = 'ltl'
    NOM = 'nom'
    UTL = 'utl'
    USL = 'usl'
    POWER = 'exp10'
    UNIT = 'unit'
    MPR = 'mpr'
    FMT = 'fmt'

    def __call__(self):
        return self.value

@unique
class OutputColumnLabel(Enum):
    NAME = 'Name'
    LSL = 'LSL'
    LTL = '(LTL)'
    NOM = 'Nom'
    UTL = '(UTL)'
    USL = 'USL'
    POWER = '10ᵡ'
    UNIT = 'Unit'
    MPR = 'MPR'
    FMT = 'fmt'

    def __call__(self):
        return self.value

@unique
class InputColumnLabel(Enum):
    SHMOO = 'Shmoo'
    NAME = 'Name'
    MIN = 'Min'
    DEFAULT = 'Default'
    MAX = 'Max'
    POWER = '10ᵡ'
    UNIT = 'Unit'
    FMT = 'fmt'

    def __call__(self):
        return self.value
