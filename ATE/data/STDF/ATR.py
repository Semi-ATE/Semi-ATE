from ATE.data.STDF import STDR
from ATE.data.STDF import STDFError


class ATR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = "ATR"
        self.local_debug = False
        # Version
        if version == None or version == "V4":
            self.version = "V4"
            self.info = """
Audit Trail Record
------------------

Function:
    Used to record any operation that alters the contents of the STDF file. The name of the
    program and all its parameters should be recorded in the ASCII field provided in this
    record. Typically, this record will be used to track filter programs that have been
    applied to the data.

Frequency:
    * Optional
    * One for each filter or other data transformation program applied to the STDF data.

Location:
    Between the File Attributes Record (FAR) and the Master Information Record (MIR).
    The filter program that writes the altered STDF file must write its ATR immediately
    after the FAR (and hence before any other ATRs that may be in the file). In this way,
    multiple ATRs will be in reverse chronological order.
"""
            self.fields = {
                "REC_LEN": {
                    "#": 0,
                    "Type": "U*2",
                    "Ref": None,
                    "Value": None,
                    "Text": "Bytes of data following header        ",
                    "Missing": None,
                    "Note": "",
                },
                "REC_TYP": {
                    "#": 1,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": 0,
                    "Text": "Record type                           ",
                    "Missing": None,
                    "Note": "",
                },
                "REC_SUB": {
                    "#": 2,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": 20,
                    "Text": "Record sub-type                       ",
                    "Missing": None,
                    "Note": "",
                },
                "MOD_TIM": {
                    "#": 3,
                    "Type": "U*4",
                    "Ref": None,
                    "Value": None,
                    "Text": "Date & time of STDF file modification ",
                    "Missing": 0,
                    "Note": "",
                },
                "CMD_LINE": {
                    "#": 4,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Command line of program               ",
                    "Missing": "",
                    "Note": "",
                },
            }
        else:
            raise STDFError(
                "%s object creation error: unsupported version '%s'"
                % (self.id, version)
            )
        self._default_init(endian, record)
