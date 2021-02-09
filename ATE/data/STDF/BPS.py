from ATE.data.STDF import STDR
from ATE.data.STDF import STDFError


class BPS(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = "BPS"
        self.local_debug = False
        # Version
        if version == None or version == "V4" or version == "V3":
            if version == None:
                self.verson = "V4"
            else:
                self.version = version
            self.info = """
Begin Program Section Record
----------------------------

Function:
    Marks the beginning of a new program section (or sequencer) in the job plan.

Frequency:
    * Optional on each entry into the program segment.

Location:
    Anywhere after the PIR and before the PRR.
"""
            self.fields = {
                "REC_LEN": {
                    "#": 0,
                    "Type": "U*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "Bytes of data following header        ",
                    "Missing": None,
                    "Note": "",
                },
                "REC_TYP": {
                    "#": 1,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": 20,
                    "Text": "Record type                           ",
                    "Missing": None,
                    "Note": "",
                },
                "REC_SUB": {
                    "#": 2,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": 10,
                    "Text": "Record sub-type                       ",
                    "Missing": None,
                    "Note": "",
                },
                "SEQ_NAME": {
                    "#": 3,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Sequence name                         ",
                    "Missing": "",
                    "Note": "",
                },
            }
        else:
            raise STDFError(
                "%s object creation error: unsupported version '%s'"
                % (self.id, version)
            )
        self._default_init(endian, record)
