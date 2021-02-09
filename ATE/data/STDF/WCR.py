import sys
from ATE.data.STDF import STDR
from ATE.data.STDF import STDFError


class WCR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = "WCR"
        self.local_debug = False
        if version == None or version == "V4":
            if version == None:
                self.version = "V4"
            else:
                self.version = version
            self.info = """
Wafer Configuration Record
--------------------------

Function:
    Contains the configuration information for the wafers tested by the job plan. The
    WCR provides the dimensions and orientation information for all wafers and dice
    in the lot. This record is used only when testing at wafer probe time.

Frequency:
    * Obligatory for Wafer sort
    * One per STDF file

Location:
    Anywhere in the data stream after the initial "FAR-(ATRs)-MIR-(RDR)-(SDRs)" sequence, and before the MRR.
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
                    "Value": 2,
                    "Text": "Record type                           ",
                    "Missing": None,
                },
                "REC_SUB": {
                    "#": 2,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": 30,
                    "Text": "Record sub-type                       ",
                    "Missing": None,
                },
                "WAFR_SIZ": {
                    "#": 3,
                    "Type": "R*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Diameter of wafer in WF_UNITS         ",
                    "Missing": 0.0,
                },
                "DIE_HT": {
                    "#": 4,
                    "Type": "R*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Height of die in WF_UNITS             ",
                    "Missing": 0.0,
                },
                "DIE_WID": {
                    "#": 5,
                    "Type": "R*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Width of die in WF_UNITS              ",
                    "Missing": 0.0,
                },
                "WF_UNITS": {
                    "#": 6,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Units for wafer and die dimensions    ",
                    "Missing": 0,
                },  # 0=?/1=Inch/2=cm/3=mm/4=mils
                "WF_FLAT": {
                    "#": 7,
                    "Type": "C*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Orientation of wafer flat (U/D/L/R)   ",
                    "Missing": " ",
                },
                "CENTER_X": {
                    "#": 8,
                    "Type": "I*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "X coordinate of center die on wafer   ",
                    "Missing": -32768,
                },
                "CENTER_Y": {
                    "#": 9,
                    "Type": "I*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "Y coordinate of center die on wafer   ",
                    "Missing": -32768,
                },
                "POS_X": {
                    "#": 10,
                    "Type": "C*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Positive X direction of wafer (L/R)   ",
                    "Missing": " ",
                },
                "POS_Y": {
                    "#": 11,
                    "Type": "C*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Positive Y direction of wafer (U/D)   ",
                    "Missing": " ",
                },
            }
        else:
            raise STDFError(
                "%s object creation error: unsupported version '%s'"
                % (self.id, version)
            )
        self._default_init(endian, record)

    def to_atdf(self):

        sequence = {}
        header = ""
        body = ""

        header = self.id + ":"

        #        The order of fields is different in STDF and ATDF for WCR record
        #
        #        STDF page 40| ATDF page 36
        #
        #        3  WAFR_SIZ
        #        4  DIE_HT
        #        5  DIE_WID
        #        6  WF_UNITS
        #        7  WF_FLAT     = 7 WF_FLAT
        #        8  CENTER_X
        #        9  CENTER_Y
        #        10 POS_X       = 10 POS_X
        #        11 POS_Y       = 11 POS_Y
        #                          3 WAFR_SIZ
        #                          4 DIE_HT
        #                          5 DIE_WID
        #                          6 WF_UNITS
        #                          8 CENTER_X
        #                          9 CENTER_Y

        #       7 WF_FLAT
        body += self.gen_atdf(7)
        #       10 POS_X
        body += self.gen_atdf(10)
        #       11 POS_Y
        body += self.gen_atdf(11)
        #       3 WAFR_SIZ
        body += self.gen_atdf(3)
        #       4 DIE_HT
        body += self.gen_atdf(4)
        #       5 DIE_WID
        body += self.gen_atdf(5)
        #       6 WF_UNITS
        body += self.gen_atdf(6)
        #       8 CENTER_X
        body += self.gen_atdf(8)
        #       9 CENTER_Y
        body += self.gen_atdf(9)

        body = body[:-1]

        # assemble the record
        retval = header + body

        if self.local_debug:
            print("%s._to_atdf()\n   '%s'\n" % (self.id, retval))
        return retval
