import sys
from ATE.data.STDF import STDR
from ATE.data.STDF import STDFError


class FTR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = "FTR"
        self.local_debug = False
        if version == None or version == "V4":
            self.version = "V4"
            self.info = """
Functional Test Record
----------------------

Function:
    Contains the results of the single execution of a functional test in the test program. The
    first occurrence of this record also establishes the default values for all semi-static
    information about the test. The FTR is related to the Test Synopsis Record (TSR) by test
    number, head number, and site number.

Frequency:
    * Obligatory, one or more for each execution of a functional test.

Location:
    Anywhere in the data stream after the corresponding Part Information Record (PIR)
    and before the corresponding Part Result Record (PRR).
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
                    "Value": 15,
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
                "TEST_NUM": {
                    "#": 3,
                    "Type": "U*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Test number                           ",
                    "Missing": None,
                },  # Obligatory!
                "HEAD_NUM": {
                    "#": 4,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Test head number                      ",
                    "Missing": 1,
                },
                "SITE_NUM": {
                    "#": 5,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Test site number                      ",
                    "Missing": 1,
                },
                "TEST_FLG": {
                    "#": 6,
                    "Type": "B*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Test flags (fail, alarm, etc.)        ",
                    "Missing": ["0"] * 8,
                },
                "OPT_FLAG": {
                    "#": 7,
                    "Type": "B*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Optional data flag                    ",
                    "Missing": ["1"] * 8,
                },
                "CYCL_CNT": {
                    "#": 8,
                    "Type": "U*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Cycle count of vector                 ",
                    "Missing": 0,
                },  # OPT_FLAG bit0 = 1
                "REL_VADR": {
                    "#": 9,
                    "Type": "U*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Relative vector address               ",
                    "Missing": 0,
                },  # OPT_FLAG bit1 = 1
                "REPT_CNT": {
                    "#": 10,
                    "Type": "U*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Repeat count of vector                ",
                    "Missing": 0,
                },  # OPT_FLAG bit2 = 1
                "NUM_FAIL": {
                    "#": 11,
                    "Type": "U*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Number of pins with 1 or more failures",
                    "Missing": 0,
                },  # OPT_FLAG bit3 = 1
                "XFAIL_AD": {
                    "#": 12,
                    "Type": "I*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "X logical device failure address      ",
                    "Missing": 0,
                },  # OPT_FLAG bit4 = 1
                "YFAIL_AD": {
                    "#": 13,
                    "Type": "I*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Y logical device failure address      ",
                    "Missing": 0,
                },  # OPT_FLAG bit4 = 1
                "VECT_OFF": {
                    "#": 14,
                    "Type": "I*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "Offset from vector of interest        ",
                    "Missing": 0,
                },  # OPT_FLAG bit5 = 1
                "RTN_ICNT": {
                    "#": 15,
                    "Type": "U*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "Count (j) of return data PMR indexes  ",
                    "Missing": 0,
                },
                "PGM_ICNT": {
                    "#": 16,
                    "Type": "U*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "Count (k) of programmed state indexes ",
                    "Missing": 0,
                },
                "RTN_INDX": {
                    "#": 17,
                    "Type": "xU*2",
                    "Ref": "RTN_ICNT",
                    "Value": None,
                    "Text": "Array of j return data PMR indexes    ",
                    "Missing": [],
                },  # RTN_ICNT = 0
                "RTN_STAT": {
                    "#": 18,
                    "Type": "xN*1",
                    "Ref": "RTN_ICNT",
                    "Value": None,
                    "Text": "Array of j returned states            ",
                    "Missing": [],
                },  # RTN_ICNT = 0
                "PGM_INDX": {
                    "#": 19,
                    "Type": "xU*2",
                    "Ref": "PGM_ICNT",
                    "Value": None,
                    "Text": "Array of k programmed state indexes   ",
                    "Missing": [],
                },  # PGM_ICNT = 0
                "PGM_STAT": {
                    "#": 20,
                    "Type": "xN*1",
                    "Ref": "PGM_ICNT",
                    "Value": None,
                    "Text": "Array of k programmed states          ",
                    "Missing": [],
                },  # PGM_ICNT = 0
                "FAIL_PIN": {
                    "#": 21,
                    "Type": "D*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Failing pin bitfield                  ",
                    "Missing": [],
                },
                "VECT_NAM": {
                    "#": 22,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Vector module pattern name            ",
                    "Missing": "",
                },
                "TIME_SET": {
                    "#": 23,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Time set name                         ",
                    "Missing": "",
                },
                "OP_CODE": {
                    "#": 24,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Vector Op Code                        ",
                    "Missing": "",
                },
                "TEST_TXT": {
                    "#": 25,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Descriptive text or label             ",
                    "Missing": "",
                },
                "ALARM_ID": {
                    "#": 26,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Name of alarm                         ",
                    "Missing": "",
                },
                "PROG_TXT": {
                    "#": 27,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Additional programmed information     ",
                    "Missing": "",
                },
                "RSLT_TXT": {
                    "#": 28,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Additional result information         ",
                    "Missing": "",
                },
                "PATG_NUM": {
                    "#": 29,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Pattern generator number              ",
                    "Missing": 0xFF,
                },
                "SPIN_MAP": {
                    "#": 30,
                    "Type": "D*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Bit map of enabled comparators        ",
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
        """
        Method that writes A(SCII)TDF version of the STDF file.
        """
        sequence = {}
        header = ""
        body = ""

        header = self.id + ":"

        #    The order of fields is different in STDF and ATDF for FTR record

        #    STDF page 57| ATDF page 51

        #     3 TEST_NUM    =  3 TEST_NUM
        #     4 HEAD_NUM    =  4 HEAD_NUM
        #     5 SITE_NUM    =  5 SITE_NUM
        #     6 TEST_FLG    -> 6 TEST_FLG bits 6 & 7
        #                   -> 6 TEST_FLG bits 0, 2, 3, 4, & 5
        #     7 OPT_FLAG    -> missing
        #     8 CYCL_CNT
        #     9 REL_VADR
        #    10 REPT_CNT
        #    11 NUM_FAIL
        #    12 XFAIL_AD
        #    13 YFAIL_AD
        #    14 VECT_OFF
        #    15 RTN_ICNT    -> missing
        #    16 PGM_ICNT    -> missing
        #    17 RTN_INDX
        #    18 RTN_STAT
        #    19 PGM_INDX
        #    20 PGM_STAT
        #    21 FAIL_PIN
        #    22 VECT_NAM    = 22 VECT_NAM
        #    23 TIME_SET    = 23 TIME_SET
        #    24 OP_CODE
        #    25 TEST_TXT
        #    26 ALARM_ID
        #    27 PROG_TXT
        #    28 RSLT_TXT
        #    29 PATG_NUM
        #    30 SPIN_MAP
        #                   =  8 CYCL_CNT
        #                   =  9 REL_VADR
        #                   = 10 REPT_CNT
        #                   = 11 NUM_FAIL
        #                   = 12 XFAIL_AD
        #                   = 13 YFAIL_AD
        #                   = 14 VECT_OFF
        #                   = 17 RTN_INDX
        #                   = 18 RTN_STAT
        #                   = 19 PGM_INDX
        #                   = 20 PGM_STAT
        #                   = 21 FAIL_PIN
        #                   = 24 OP_CODE
        #                   = 25 TEST_TXT
        #                   = 26 ALARM_ID
        #                   = 27 PROG_TXT
        #                   = 28 RSLT_TXT
        #                   = 29 PATG_NUM
        #                   = 30 SPIN_MAP

        #       3 TEST_NUM
        body += self.gen_atdf(3)
        #       4 HEAD_NUM
        body += self.gen_atdf(4)
        #       5 SITE_NUM
        body += self.gen_atdf(5)

        #       6 TEST_FLG bits 6 & 7
        #           bit 6: Pass/fail flag (bit 7) is valid
        v = self.get_fields(6)[3]
        if v != None and v[6] == "0":
            #           bit 7:
            #           0 = Part passed
            if self.get_fields(6)[3][7] == "0":
                body += "P|"
            #           1 = Part failed
            elif self.get_fields(6)[3][7] == "1":
                body += "F|"
            #                             6 TEST_FLG bits 0, 2, 3, 4, & 5
            #           bit 0:
            #           0 = No alarm
            if self.get_fields(6)[3][0] == "0":
                body += ""
            #           1 = Alarm detected during testing
            elif self.get_fields(6)[3][0] == "1":
                body += "A"
            #           bit 2:
            #           0= Test result is reliable
            if self.get_fields(6)[3][2] == "0":
                body += ""
            #           1 = Test result is unreliable
            elif self.get_fields(6)[3][2] == "1":
                body += "U"
            #           bit 3:
            #           0 = No timeout
            if self.get_fields(6)[3][3] == "0":
                body += ""
            #           1 = Timeout occurred
            elif self.get_fields(6)[3][3] == "1":
                body += "T"
            #           bit 4:
            #           0 = Test was executed
            if self.get_fields(6)[3][4] == "0":
                body += ""
            #           1= Testnotexecuted
            elif self.get_fields(6)[3][4] == "1":
                body += "N"
            #           bit 5:
            #           0 = No abort
            if self.get_fields(6)[3][5] == "0":
                body += "|"
            #           1= Testaborted
            elif self.get_fields(6)[3][5] == "1":
                body += "X|"
        else:
            body += "|"

        #       22 VECT_NAM
        body += self.gen_atdf(22)
        #       23 TIME_SET
        body += self.gen_atdf(23)
        #        8 CYCL_CNT
        body += self.gen_atdf(8)
        #        9 REL_VADR
        body += self.gen_atdf(9)
        #       10 REPT_CNT
        body += self.gen_atdf(10)
        #       11 NUM_FAIL
        body += self.gen_atdf(11)
        #       12 XFAIL_AD
        body += self.gen_atdf(12)
        #       13 YFAIL_AD
        body += self.gen_atdf(13)
        #       14 VECT_OFF
        body += self.gen_atdf(14)
        #       17 RTN_INDX
        body += self.gen_atdf(17)
        #       18 RTN_STAT
        body += self.gen_atdf(18)
        #       19 PGM_INDX
        body += self.gen_atdf(19)
        #       20 PGM_STAT
        body += self.gen_atdf(20)
        #       22 FAIL_PIN
        body += self.gen_atdf(21)
        #       24 OP_CODE
        body += self.gen_atdf(24)
        #       25 TEST_TXT
        body += self.gen_atdf(25)
        #       26 ALARM_ID
        body += self.gen_atdf(26)
        #       27 PROG_TXT
        body += self.gen_atdf(27)
        #       28 RSLT_TXT
        body += self.gen_atdf(28)
        #       29 PATG_NUM
        body += self.gen_atdf(29)
        #       30 SPIN_MAP
        body += self.gen_atdf(30)
        body = body[:-1]

        # assemble the record
        retval = header + body

        if self.local_debug:
            print("%s._to_atdf()\n   '%s'\n" % (self.id, retval))
        return retval
