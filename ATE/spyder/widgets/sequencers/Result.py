

from enum import Enum


# The enummembers are numbered by "severity". A given test
# can never decrease a result for the complete program, i.e.
# once we have a fail it will stay a fail regardless of what
# others say.
class Result(Enum):
    Fail = 2
    Pass = 1
    Inconclusive = 0

    def __call__(self):
        return self.value
