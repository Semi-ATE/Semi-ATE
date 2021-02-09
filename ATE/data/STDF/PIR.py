import sys
from ATE.data.STDF import STDR


class PIR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = "PIR"
        self.local_debug = False
        if version == None or version == "V4":
            self.version = "V4"
            self.info = """
Part Information Record
-----------------------

Function:
    Acts as a marker to indicate where testing of a particular part begins for each part
    tested by the test program. The PIR and the Part Results Record (PRR) bracket all the
    stored information pertaining to one tested part.

Frequency:
    * Obligatory
    * One per part tested.

Location:
    Anywhere in the data stream after the initial sequence "FAR-(ATRs)-MIR-(RDR)-(SDRs)", and before the corresponding PRR.
    Sent before testing each part.
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
                    "Value": 5,
                    "Text": "Record type                           ",
                    "Missing": None,
                },
                "REC_SUB": {
                    "#": 2,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": 10,
                    "Text": "Record sub-type                       ",
                    "Missing": None,
                },
                "HEAD_NUM": {
                    "#": 3,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Test head number                      ",
                    "Missing": 1,
                },
                "SITE_NUM": {
                    "#": 4,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Test site number                      ",
                    "Missing": 1,
                },
            }

        else:
            raise STDFError(
                "%s object creation error: unsupported version '%s'"
                % (self.id, version)
            )
        self._default_init(endian, record)
