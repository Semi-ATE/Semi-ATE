import sys
from ATE.data.STDF import STDR
from ATE.data.STDF import STDFError


class SDR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = "SDR"
        self.local_debug = False
        if version == None or version == "V4":
            self.version = "V4"
            self.info = """
Site Description Record
-----------------------

Function:
    Contains the configuration information for one or more test sites, connected to one test
    head, that compose a site group.

Frequency:
    * Optional
    * One for each site or group of sites that is differently configured.

Location:
    Immediately after the MIR and RDR (if an RDR is used).
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
                    "Value": 80,
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
                "SITE_GRP": {
                    "#": 4,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Site group number                     ",
                    "Missing": 1,
                },
                "SITE_CNT": {
                    "#": 5,
                    "Type": "U*1",
                    "Ref": None,
                    "Value": None,
                    "Text": "Number (k) of test sites in site group",
                    "Missing": 1,
                },
                "SITE_NUM": {
                    "#": 6,
                    "Type": "xU*1",
                    "Ref": "SITE_CNT",
                    "Value": None,
                    "Text": "Array of k test site numbers          ",
                    "Missing": [1],
                },
                "HAND_TYP": {
                    "#": 7,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Handler or prober type                ",
                    "Missing": "",
                },
                "HAND_ID": {
                    "#": 8,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Handler or prober ID                  ",
                    "Missing": "",
                },
                "CARD_TYP": {
                    "#": 9,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Probe card type                       ",
                    "Missing": "",
                },
                "CARD_ID": {
                    "#": 10,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Probe card ID                         ",
                    "Missing": "",
                },
                "LOAD_TYP": {
                    "#": 11,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Load board type                       ",
                    "Missing": "",
                },
                "LOAD_ID": {
                    "#": 12,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Load board ID                         ",
                    "Missing": "",
                },
                "DIB_TYP": {
                    "#": 13,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "DIB (aka load-) board type            ",
                    "Missing": "",
                },
                "DIB_ID": {
                    "#": 14,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "DIB (aka load-) board ID              ",
                    "Missing": "",
                },
                "CABL_TYP": {
                    "#": 15,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Interface cable type                  ",
                    "Missing": "",
                },
                "CABL_ID": {
                    "#": 16,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Interface cable ID                    ",
                    "Missing": "",
                },
                "CONT_TYP": {
                    "#": 17,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Handler contactor type                ",
                    "Missing": "",
                },
                "CONT_ID": {
                    "#": 18,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Handler contactor ID                  ",
                    "Missing": "",
                },
                "LASR_TYP": {
                    "#": 19,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Laser type                            ",
                    "Missing": "",
                },
                "LASR_ID": {
                    "#": 20,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Laser ID                              ",
                    "Missing": "",
                },
                "EXTR_TYP": {
                    "#": 21,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Extra equipment type                  ",
                    "Missing": "",
                },
                "EXTR_ID": {
                    "#": 22,
                    "Type": "C*n",
                    "Ref": None,
                    "Value": None,
                    "Text": "Extra equipment ID                    ",
                    "Missing": "",
                },
            }
        else:
            raise STDFError(
                "%s object creation error: unsupported version '%s'"
                % (self.id, version)
            )
        self._default_init(endian, record)
