from ATE.data.STDF import STDR
from ATE.data.STDF import STDFError


class EPS(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = "EPS"
        self.local_debug = False
        # Version
        if version == None or version == "V4" or version == "V3":
            self.version = version
            self.info = """
End Program Section Record
--------------------------

Function:
    Marks the end of the current program section (or sequencer) in the job plan.

Frequency:
    * Optional on each exit from the program segment.

Location:
    Following the corresponding BPS and before the PRR in the data stream.
"""
            #           Changed by seimit : to pass serialization test, set None value for 'Ref' instead the old ''
            self.fields = {
                "REC_LEN": {
                    "#": 0,
                    "Type": "U*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "Bytes of data following header        ",
                    "Missing": "N/A                    ",
                },
                "REC_TYP": {
                    "#": 1,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": 20,
                    "Text": "Record type                           ",
                    "Missing": "20                     ",
                },
                "REC_SUB": {
                    "#": 2,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": 20,
                    "Text": "Record sub-type                       ",
                    "Missing": "10                     ",
                },
            }
        else:
            raise STDFError(
                "%s object creation error: unsupported version '%s'"
                % (self.id, version)
            )
        self._default_init(endian, record)
