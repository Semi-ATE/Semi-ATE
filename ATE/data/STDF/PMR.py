import sys
from ATE.data.STDF import STDR
from ATE.data.STDF import STDFError


class PMR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = "PMR"
        self.local_debug = False
        if version == None or version == "V4":
            self.version = "V4"
            self.info = """
Pin Map Record
--------------

Function:
    Provides indexing of tester channel names, and maps them to physical and logical pin
    names. Each PMR defines the information for a single channel/pin combination.

Frequency:
    * Optional
    * One per channel/pin combination used in the test program.
    * Reuse of a PMR index number is not permitted.

Location:
    After the initial "FAR-(ATRs)-MIR-(RDR)-(SDRs)" sequence and before the first PGR, PLR,
    FTR, or MPR that uses this record's PMR_INDX value.
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
                    "Value": 60,
                    "Text": "Record sub-type                       ",
                    "Missing": None,
                },
                "PMR_INDX": {
                    "#": 3,
                    "Type": "U*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "Unique index associated with pin      ",
                    "Missing": 0,
                },
                "CHAN_TYP": {
                    "#": 4,
                    "Type": "U*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "Channel type                          ",
                    "Missing": 0,
                },
                "CHAN_NAM": {
                    "#": 5,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Channel name                          ",
                    "Missing": "",
                },
                "PHY_NAM": {
                    "#": 6,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Physical name of pin                  ",
                    "Missing": "",
                },
                "LOG_NAM": {
                    "#": 7,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Logical name of pin                   ",
                    "Missing": "",
                },
                "HEAD_NUM": {
                    "#": 8,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Head number associated with channel   ",
                    "Missing": 1,
                },
                "SITE_NUM": {
                    "#": 9,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Site number associated with channel   ",
                    "Missing": 1,
                },
            }
        else:
            raise STDFError(
                "%s object creation error: unsupported version '%s'"
                % (self.id, version)
            )
        self._default_init(endian, record)
