import sys
from ATE.data.STDF import STDR
from ATE.data.STDF import STDFError


class PLR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = "PLR"
        self.local_debug = False
        if version == None or version == "V4":
            self.version = "V4"
            self.info = """
Pin List Record
---------------

Function:
    Defines the current display radix and operating mode for a pin or pin group.

Frequency:
    * Optional
    * One or more whenever the usage of a pin or pin group changes in the test program.

Location:
    After all the PMRs and PGRs whose PMR index values and pin group index values are
    listed in the GRP_INDX array of this record; and before the first FTR that references pins
    or pin groups whose modes are defined in this record.
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
                    "Value": 63,
                    "Text": "Record sub-type                       ",
                    "Missing": None,
                },
                "GRP_CNT": {
                    "#": 3,
                    "Type": "U*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "Count (k) of pins or pin groups       ",
                    "Missing": 0,
                },
                "GRP_INDX": {
                    "#": 4,
                    "Type": "xU*2",
                    "Ref": "GRP_CNT",
                    "Value": None,
                    "Text": "Array of pin or pin group indexes     ",
                    "Missing": [],
                },
                "GRP_MODE": {
                    "#": 5,
                    "Type": "xU*2",
                    "Ref": "GRP_CNT",
                    "Value": None,
                    "Text": "Operating mode of pin group           ",
                    "Missing": [],
                },
                "GRP_RADX": {
                    "#": 6,
                    "Type": "xU*1",
                    "Ref": "GRP_CNT",
                    "Value": None,
                    "Text": "Display radix of pin group            ",
                    "Missing": [],
                },
                "PGM_CHAR": {
                    "#": 7,
                    "Type": "xC*n",
                    "Ref": "GRP_CNT",
                    "Value": None,
                    "Text": "Program state encoding characters     ",
                    "Missing": [],
                },
                "RTN_CHAR": {
                    "#": 8,
                    "Type": "xC*n",
                    "Ref": "GRP_CNT",
                    "Value": None,
                    "Text": "Return state encoding characters      ",
                    "Missing": [],
                },
                "PGM_CHAL": {
                    "#": 9,
                    "Type": "xC*n",
                    "Ref": "GRP_CNT",
                    "Value": None,
                    "Text": "Program state encoding characters     ",
                    "Missing": [],
                },
                "RTN_CHAL": {
                    "#": 10,
                    "Type": "xC*n",
                    "Ref": "GRP_CNT",
                    "Value": None,
                    "Text": "Return state encoding characters      ",
                    "Missing": [],
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

        #        The order of fields is different in STDF and ATDF for PLR record
        #
        #        STDF page 32| ATDF page 27
        #
        #          3 GRP_CNT    -> missing
        #          4 GRP_INDX   = 4 GRP_INDX
        #          5 GRP_MODE   = 5 GRP_MODE
        #          6 GRP_RADX   = 6 GRP_RADX
        #          7 PGM_CHAR
        #          8 RTN_CHAR
        #          9 PGM_CHAL
        #         10 RTN_CHAL
        #                       = 9 PGM_CHAL , 7 PGM_CHAR
        #                       = 10 RTN_CHAL, 8 RTN_CHAR

        #       4 GRP_INDX
        body += self.gen_atdf(4)
        #       5 GRP_MODE
        body += self.gen_atdf(5)
        #       6 GRP_RADX
        body += self.gen_atdf(6)

        pgm_right = self.get_fields(7)[3]
        pgm_left = self.get_fields(9)[3]

        if pgm_right == None and pgm_left == None:
            body += "|"
            pass
        else:
            if len(pgm_left) == 0:
                #               7 PGM_CHAR
                body += self.gen_atdf(7)
            else:
                for right, left in zip(pgm_right, pgm_left):
                    body += right + "," + left + "/"
                body = body[:-1]
                body += "|"

        rtn_right = self.get_fields(8)[3]
        rtn_left = self.get_fields(10)[3]

        if rtn_right == None and rtn_left == None:
            body += "|"
            pass
        else:
            if len(rtn_left) == 0:
                #           8 RTN_CHAR
                body += self.gen_atdf(8)
            else:
                for right, left in zip(rtn_right, rtn_left):
                    body += right + "," + left + "/"
        body = body[:-1]

        # assemble the record
        retval = header + body

        if self.local_debug:
            print("%s._to_atdf()\n   '%s'\n" % (self.id, retval))
        return retval
