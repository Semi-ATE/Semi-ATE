import sys
from ATE.data.STDF import STDR
from ATE.data.STDF import STDFError


class MRR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = "MRR"
        self.local_debug = False
        if version == None or version == "V4":
            self.version = "V4"
            self.info = """
Master Results Record
---------------------

Function:
    The Master Results Record (MRR) is a logical extension of the Master Information
    Record (MIR). The data can be thought of as belonging with the MIR, but it is not
    available when the tester writes the MIR information. Each data stream must have
    exactly one MRR as the last record in the data stream.

Frequency:
    * Obligatory
    * One per data stream

Location:
    Must be the last record in the data stream.
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
                    "Value": 20,
                    "Text": "Record sub-type                       ",
                    "Missing": None,
                },
                "FINISH_T": {
                    "#": 3,
                    "Type": "U*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Date and time last part tested        ",
                    "Missing": self._missing_stdf_time_field_value(),
                },
                "DISP_COD": {
                    "#": 4,
                    "Type": "C*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Lot disposition code                  ",
                    "Missing": " ",
                },
                "USR_DESC": {
                    "#": 5,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Lot description supplied by user      ",
                    "Missing": "",
                },
                "EXC_DESC": {
                    "#": 6,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Lot description supplied by exec      ",
                    "Missing": "",
                },
            }

        else:
            raise STDFError(
                "%s object creation error: unsupported version '%s'"
                % (self.id, version)
            )
        self._default_init(endian, record)
