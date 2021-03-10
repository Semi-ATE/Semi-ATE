from enum import Enum, IntEnum


class TableIds(Enum):
    Flow = 1
    Definition = 2
    Hardware = 3
    Maskset = 4
    Device = 5
    Product = 6
    Package = 7
    Die = 8
    Test = 9
    Program = 10
    TestItem = 11
    NewTest = 12
    RemoveTest = 13

    def __call__(self):
        return self.value


class UpdateOptions(IntEnum):
    DB_Update = 0
    Group_Update = 1
    Code_Update = 2

    def __call__(self):
        return self.value


TEST_SECTION = 'tests'
QUALIFICATION = 'qualification'

FLOWS = ['checker', 'maintenance', 'production', 'engineering', 'validation', 'quality', 'qualification']
SUBFLOWS_QUALIFICATION = ['ZHM', 'ABSMAX', 'EC', 'HTOL', 'HTSL', 'DR', 'AC', 'HAST', 'ELFR', 'LU', 'TC', 'THB', 'ESD', 'RSJ']