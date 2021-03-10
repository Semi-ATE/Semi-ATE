import sys
from ATE.data.STDF import STDR
from ATE.data.STDF import STDFError


class GDR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = "GDR"
        self.local_debug = False
        if version == None or version == "V4" or version == "V3":
            if version == None:
                self.version = "V4"
            else:
                self.version = version
            self.info = """
Generic Data Record
-------------------

Function:
    Contains information that does not conform to any other record type defined by the
    STDF specification. Such records are intended to be written under the control of job
    plans executing on the tester. This data may be used for any purpose that the user
    desires.

Frequency:
    * Optional, a test data file may contain any number of GDRs.

Location:
    Anywhere in the data stream after the initial "FAR-(ATRs)-MIR-(RDR)-(SDRs)" sequence.
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
                    "Value": 50,
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
                "FLD_CNT": {
                    "#": 3,
                    "Type": "U*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "Count of data fields in record        ",
                    "Missing": 0,
                },
                "GEN_DATA": {
                    "#": 4,
                    "Type": "xV*n",
                    "Ref": "FLD_CNT",
                    "Value": None,
                    "Text": "Data type code and data for one field ",
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

        atdf_code = ["", "U", "M", "B", "I", "S", "L", "F", "D", "", "T", "X", "Y", "N"]
        pair = self.get_fields(4)[3]
        for i in range(len(pair)):
            code = pair[i][0][0]
            value = pair[i][0][1]
            body += atdf_code[code]
            if code == 11:
                body += self.hexify(value).replace("0x", "")
            elif code == 12:
                # HEX representation of bits
                bits_to_pack = len(value)
                bytes_to_pack = int(bits_to_pack) // 8
                if (bits_to_pack % 8) != 0:
                    bytes_to_pack += 1
                for Byte in range(bytes_to_pack):
                    byte = 0
                    for Bit in range(8):
                        if (Byte * 8) + Bit < len(value):
                            if value[(Byte * 8) + Bit] == "1":
                                byte += pow(2, Bit)
                    body += "%02X" % byte
            elif code == 13:
                # One nubble
                # ATDF is not clear if we can write only one nubble or two
                # so here we will output 2 nubbles seprated by comma
                for i in range(len(value)):
                    body += str(value[i]) + ","
                body = body[:-1]

            else:
                body += str(value)
            body += "|"
        body = body[:-1]

        # assemble the record
        retval = header + body

        if self.local_debug:
            print("%s._to_atdf()\n   '%s'\n" % (self.id, retval))
        return retval
