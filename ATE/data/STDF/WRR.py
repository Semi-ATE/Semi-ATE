import sys
import time

from ATE.data.STDF import STDR
from ATE.data.STDF import STDFError


class WRR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = "WRR"
        self.local_debug = False
        if version == None or version == "V4":
            self.version = "V4"
            self.info = """
Wafer Results Record
--------------------

Function:
    Contains the result information relating to each wafer tested by the job plan. The WRR
    and the Wafer Information Record (WIR) bracket all the stored information pertaining
    to one tested wafer. This record is used only when testing at wafer probe time. A
    WIR/WRR pair will have the same HEAD_NUM and SITE_GRP values.

Frequency:
    * Obligatory for Wafer sort
    * One per wafer tested.

Location:
    Anywhere in the data stream after the corresponding WIR.
    Sent after testing each wafer.
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
                    "Value": 20,
                    "Text": "Record sub-type                       ",
                    "Missing": None,
                },
                "HEAD_NUM": {
                    "#": 3,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Test head number                      ",
                    "Missing": 255,
                },
                "SITE_GRP": {
                    "#": 4,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Site group number                     ",
                    "Missing": 255,
                },
                "FINISH_T": {
                    "#": 5,
                    "Type": "U*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Date and time last part tested        ",
                    "Missing": 0,
                },
                "PART_CNT": {
                    "#": 6,
                    "Type": "U*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Number of parts tested                ",
                    "Missing": 0,
                },
                "RTST_CNT": {
                    "#": 7,
                    "Type": "U*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Number of parts retested              ",
                    "Missing": 4294967295,
                },
                "ABRT_CNT": {
                    "#": 8,
                    "Type": "U*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Number of aborts during testing       ",
                    "Missing": 4294967295,
                },
                "GOOD_CNT": {
                    "#": 9,
                    "Type": "U*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Number of good (passed) parts tested  ",
                    "Missing": 4294967295,
                },
                "FUNC_CNT": {
                    "#": 10,
                    "Type": "U*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Number of functional parts tested     ",
                    "Missing": 4294967295,
                },
                "WAFER_ID": {
                    "#": 11,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Wafer ID                              ",
                    "Missing": "",
                },
                "FABWF_ID": {
                    "#": 12,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Fab wafer ID                          ",
                    "Missing": "",
                },
                "FRAME_ID": {
                    "#": 13,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Wafer frame ID                        ",
                    "Missing": "",
                },
                "MASK_ID": {
                    "#": 14,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Wafer mask ID                         ",
                    "Missing": "",
                },
                "USR_DESC": {
                    "#": 15,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Wafer description supplied by user    ",
                    "Missing": "",
                },
                "EXC_DESC": {
                    "#": 16,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Wafer description supplied by exec    ",
                    "Missing": "",
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

        #        The order of fields is different in STDF and ATDF for WRR record
        #
        #        STDF page 38| ATDF page 34
        #
        #        3  HEAD_NUM    =  3  HEAD_NUM
        #        4  SITE_GRP
        #        5  FINISH_T    =  5  FINISH_T
        #        6  PART_CNT    =  6  PART_CNT
        #                        |11  WAFER_ID
        #                        | 4  SITE_GRP
        #        7  RTST_CNT    =  7  RTST_CNT
        #        8  ABRT_CNT    =  8  ABRT_CNT
        #        9  GOOD_CNT    =  9  GOOD_CNT
        #        10 FUNC_CNT    = 10  FUNC_CNT
        #        11 WAFER_ID
        #        12 FABWF_ID    = 12  FABWF_ID
        #        13 FRAME_ID    = 13  FRAME_ID
        #        14 MASK_ID     = 14  MASK_ID
        #        15 USR_DESC    = 15  USR_DESC
        #        16 EXC_DESC    = 16  EXC_DESC

        #       3 HEAD_NUM
        body += self.gen_atdf(3)

        #       5 FINISH_T
        v = self.get_fields(5)[3]
        if v != None:
            t = time.strftime("%-H:%-M:%-S %-d-%b-%Y", time.gmtime(v))
            body += "%s|" % (t.upper())

        #       6 PART_CNT
        body += self.gen_atdf(6)

        #       11 PART_CNT
        body += self.gen_atdf(11)

        #       4 SITE_GRP
        body += self.gen_atdf(4)

        #       7 RTST_CNT
        body += self.gen_atdf(7)

        #       8 ABRT_CNT
        body += self.gen_atdf(8)

        #       9 ABRT_CNT
        body += self.gen_atdf(9)

        #       10 FUNC_CNT
        body += self.gen_atdf(10)

        #       12 FABWF_ID
        body += self.gen_atdf(12)

        #       13 FRAME_ID
        body += self.gen_atdf(13)

        #       14 MASK_ID
        body += self.gen_atdf(14)

        #       15 USR_DESC
        body += self.gen_atdf(15)

        #       16 EXC_DESC
        body += self.gen_atdf(16)

        body = body[:-1]

        # assemble the record
        retval = header + body

        if self.local_debug:
            print("%s._to_atdf()\n   '%s'\n" % (self.id, retval))
        return retval
