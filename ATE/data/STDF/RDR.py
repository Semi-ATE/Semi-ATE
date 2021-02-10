import sys
from ATE.data.STDF import STDR
from ATE.data.STDF import STDFError


class RDR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = "RDR"
        self.local_debug = False
        if version == None or version == "V4":
            self.version = "V4"
            self.info = """
Retest Data Record
------------------

Function:
    Signals that the data in this STDF file is for retested parts. The data in this record,
    combined with information in the MIR, tells data filtering programs what data to
    replace when processing retest data.

Frequency:
    * Obligatory if a lot is retested. (not if a device is binned in the reteset bin)
    * One per data stream.

Location:
    If this record is used, it must appear immediately after theMaster Information Record (MIR).
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
                    "Value": 70,
                    "Text": "Record sub-type                       ",
                    "Missing": None,
                },
                "NUM_BINS": {
                    "#": 3,
                    "Type": "U*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "Number (k) of bins being retested     ",
                    "Missing": 0,
                },
                "RTST_BIN": {
                    "#": 4,
                    "Type": "xU*2",
                    "Ref": "NUM_BINS",
                    "Value": None,
                    "Text": "Array of retest bin numbers           ",
                    "Missing": [],
                },
            }
        else:
            raise STDFError(
                "%s object creation error: unsupported version '%s'"
                % (self.id, version)
            )
        self._default_init(endian, record)
