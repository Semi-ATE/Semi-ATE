import sys
from ATE.data.STDF import STDR


class PGR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = "PGR"
        self.local_debug = False
        if version == None or version == "V4":
            self.version = "V4"
            self.info = """
Pin Group Record
----------------

Function:
    Associates a name with a group of pins.

Frequency:
    * Optional
    * One per pin group defined in the test program.

Location:
    After all the PMRs whose PMR index values are listed in the PMR_INDX array of this
    record; and before the first PLR that uses this record's GRP_INDX value.
"""
            self.fields = {
                "REC_LEN": {
                    "#": 0,
                    "Type": "U*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "Bytes of data following header        ",
                    "Missing": None,
                },
                "REC_TYP": {
                    "#": 1,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": 1,
                    "Text": "Record type                           ",
                    "Missing": None,
                },
                "REC_SUB": {
                    "#": 2,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": 62,
                    "Text": "Record sub-type                       ",
                    "Missing": None,
                },
                "GRP_INDX": {
                    "#": 3,
                    "Type": "U*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "Unique index associated with pin group",
                    "Missing": 0,
                },
                "GRP_NAM": {
                    "#": 4,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Name of pin group                     ",
                    "Missing": "",
                },
                "INDX_CNT": {
                    "#": 5,
                    "Type": "U*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "Count (k) of PMR indexes              ",
                    "Missing": 0,
                },
                "PMR_INDX": {
                    "#": 6,
                    "Type": "xU*2",
                    "Ref": "INDX_CNT",
                    "Value": None,
                    "Text": "Array of indexes for pins in the group",
                    "Missing": [],
                },
            }
        else:
            raise STDFError(
                "%s object creation error: unsupported version '%s'"
                % (self.id, version)
            )
        self._default_init(endian, record)
