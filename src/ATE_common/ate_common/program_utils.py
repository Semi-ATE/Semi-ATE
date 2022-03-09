from enum import Enum, IntEnum

ALARM_BIN_MIN = 60000
ALARM_BIN_MAX = 65535
GOOD_BIN_MIN = 1
GOOD_BIN_MAX = 9
BINGROUPS = ['Good', 'Contact Fail', 'Electric Fail', 'Alarm']
GRADES = [("Grade_B", 2),
          ("Grade_C", 3),
          ("Grade_D", 4),
          ("Grade_E", 5),
          ("Grade_F", 6),
          ("Grade_G", 7),
          ("Grade_H", 8),
          ("Grade_I", 9)]

class ParameterEditability(IntEnum):
    NotEditable = 0
    Editable = 1
    Selectable = 2

    def __call__(self):
        return self.value


class ParameterState(IntEnum):
    Invalid = 0
    Valid = 1
    Changed = 2
    New = 3
    PartValid = 4
    Removed = 5

    def __call__(self):
        return self.value


class BinningColumns(Enum):
    SBinName = 0
    SBin = 1
    SBinGroup = 2
    SBinDescription = 3

    def __call__(self):
        return self.value


class Result(Enum):
    Fail = ('FAIL', 2)
    Pass = ('PASS', 1)

    def __call__(self):
        return self.value


class Tabs(Enum):
    Sequence = 'Sequence'
    Binning = 'Binning'
    PingPong = 'Ping_Pong'
    Execution = 'Execution'

    def __call__(self):
        return self.value


class Action(Enum):
    Up = 'Up'
    Down = 'Down'
    Left = 'Left'
    Right = 'Right'

    def __call__(self):
        return self.value


class Range(Enum):
    In_Range = 0
    Out_Of_Range = 1
    Limited_Range = 2

    def __call__(self):
        return self.value


# ToDo: Add numeric type! These strings are display values that
# are bound to change, which would break all projects.
class Sequencer(Enum):
    Static = 'Fixed Temperature'  # 'Static'
    Dynamic = 'Variable Temperature'  # 'Dynamic'

    def __call__(self):
        return self.value


class ErrorMessage(Enum):
    NotSelected = 'no test is selected'
    InvalidInput = 'invalid input'
    InvalidTemperature = 'invalid temperature value(s)'
    OutOfRange = 'value out of range'
    TargetMissed = 'target is missing'
    UsertextMissed = 'usertext is missing'
    TemperatureMissed = 'temperature is missing'
    NoTestSelected = 'no test was selected'
    MultipleTestSelection = 'multiple tests are selected'
    EmtpyTestList = 'no test was chosen'
    NoValidTestRange = 'test range is not valid'
    TemperatureNotValidated = 'temperature(s) could not be validated'
    SbinInvalidOrMissing = 'soft bins are invalid or still missing'
    TestInvalid = 'test(s) is(are) invalid'
    TestDescriptionNotUnique = 'test description must be unique'
    ParameterNotValid = 'parameter are not valid'
    BinTableNotfilled = 'make sure to fill bin table'
    UserNameMissing = 'user naming is missing'
    UserNameUsed = 'user name used already'

    def __call__(self):
        return self.value


class ResolverTypes(Enum):
    Static = 'static'
    Local = 'local'
    Remote = 'remote'

    def __call__(self):
        return self.value


class ValidatorTypes(Enum):
    NoValidation = 'novalidation'
    FloatValidation = 'float'
    IntValidation = 'int'

    def __call__(self):
        return self.value


class InputFieldsPosition(IntEnum):
    Name = 0
    Min = 1
    Value = 2
    Max = 3
    Unit = 4
    Format = 5
    Type = 6

    def __call__(self):
        return self.value


class OutputFieldsPosition(IntEnum):
    No = 0
    Name = 1
    Lsl = 2
    Ltl = 3
    Utl = 4
    Usl = 5
    Unit = 6
    Format = 7

    def __call__(self):
        return self.value

class BinTableFieldName(Enum):
    SBinName = 'SBINNAME'
    SBinNum = 'SBIN'
    SBinGroup = 'GROUP'
    SBinDescription = 'DESCRIPTION'
    HBin = 'HBIN'

    def __call__(self):
        return self.value
