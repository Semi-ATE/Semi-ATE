from enum import Enum, IntEnum


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
    Grade = 1
    Result = 2
    Context = 3

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
    SbinInvalid = 'sbin is invalid'
    TestInvalid = 'test(s) is(are) invalid'
    TestDescriptionNotUnique = 'test description must be unique'
    ParameterNotValid = 'parameter are not valid'

    def __call__(self):
        return self.value


class ResolverTypes(Enum):
    Static = 'static'
    Local = 'local'

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
    Name = 0
    Lsl = 1
    Ltl = 2
    Utl = 3
    Usl = 4
    Unit = 5
    Format = 6

    def __call__(self):
        return self.value
