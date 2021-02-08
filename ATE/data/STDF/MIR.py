import sys
from ATE.data.STDF import STDR

class MIR(STDR):
    def __init__(self, version=None, endian=None, record = None):
        self.id = 'MIR'
        self.local_debug = False
        if version==None or version=='V4':
            self.version ='V4'
            self.info = '''
Master Information Record
-------------------------

Function:
    The MIR and the MRR (Master Results Record) contain all the global information that
    is to be stored for a tested lot of parts. Each data stream must have exactly one MIR,
    immediately after the FAR (and the ATRs, if they are used). This will allow any data
    reporting or analysis programs access to this information in the shortest possible
    amount of time.

Frequency:
    * Obligatory
    * One per data stream.

Location:
    Immediately after the File Attributes Record (FAR) and the Audit Trail Records (ATR),
    if ATRs are used.
'''
            initial_timestamp_value = self._missing_stdf_time_field_value()
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2', 'Ref' : None, 'Value' :    0, 'Text' : 'Bytes of data following header        ', 'Missing' :       None},
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1', 'Ref' : None, 'Value' :    1, 'Text' : 'Record type                           ', 'Missing' :       None},
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1', 'Ref' : None, 'Value' :   10, 'Text' : 'Record sub-type                       ', 'Missing' :       None},
                'SETUP_T'  : {'#' :  3, 'Type' : 'U*4', 'Ref' : None, 'Value' : None, 'Text' : 'Date and time of job setup            ', 'Missing' :       initial_timestamp_value},
                'START_T'  : {'#' :  4, 'Type' : 'U*4', 'Ref' : None, 'Value' : None, 'Text' : 'Date and time first part tested       ', 'Missing' :       initial_timestamp_value},
                'STAT_NUM' : {'#' :  5, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'Tester station number                 ', 'Missing' :          0},
                'MODE_COD' : {'#' :  6, 'Type' : 'C*1', 'Ref' : None, 'Value' : None, 'Text' : 'Test mode code : A/M/P/E/M/P/Q/space  ', 'Missing' :        ' '},
                'RTST_COD' : {'#' :  7, 'Type' : 'C*1', 'Ref' : None, 'Value' : None, 'Text' : 'Lot retest code : Y/N/0..9/space      ', 'Missing' :        ' '},
                'PROT_COD' : {'#' :  8, 'Type' : 'C*1', 'Ref' : None, 'Value' : None, 'Text' : 'Data protection code 0..9/A..Z/space  ', 'Missing' :        ' '},
                'BURN_TIM' : {'#' :  9, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Burn-in time (in minutes)             ', 'Missing' :      65535},
                'CMOD_COD' : {'#' : 10, 'Type' : 'C*1', 'Ref' : None, 'Value' : None, 'Text' : 'Command mode code                     ', 'Missing' :        ' '},
                'LOT_ID'   : {'#' : 11, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Lot ID (customer specified)           ', 'Missing' :         ''},
                'PART_TYP' : {'#' : 12, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Part Type (or product ID)             ', 'Missing' :         ''},
                'NODE_NAM' : {'#' : 13, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Name of node that generated data      ', 'Missing' :         ''},
                'TSTR_TYP' : {'#' : 14, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Tester type                           ', 'Missing' :         ''},
                'JOB_NAM'  : {'#' : 15, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Job name (test program name)          ', 'Missing' :         ''},
                'JOB_REV'  : {'#' : 16, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Job (test program) revision number    ', 'Missing' :         ''},
                'SBLOT_ID' : {'#' : 17, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Sublot ID                             ', 'Missing' :         ''},
                'OPER_NAM' : {'#' : 18, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Operator name or ID (at setup time)   ', 'Missing' :         ''},
                'EXEC_TYP' : {'#' : 19, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Tester executive software type        ', 'Missing' :         ''},
                'EXEC_VER' : {'#' : 20, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Tester exec software version number   ', 'Missing' :         ''},
                'TEST_COD' : {'#' : 21, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Test phase or step code               ', 'Missing' :         ''},
                'TST_TEMP' : {'#' : 22, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Test temperature                      ', 'Missing' :         ''},
                'USER_TXT' : {'#' : 23, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Generic user text                     ', 'Missing' :         ''},
                'AUX_FILE' : {'#' : 24, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Name of auxiliary data file           ', 'Missing' :         ''},
                'PKG_TYP'  : {'#' : 25, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Package type                          ', 'Missing' :         ''},
                'FAMLY_ID' : {'#' : 26, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Product family ID                     ', 'Missing' :         ''},
                'DATE_COD' : {'#' : 27, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Date code                             ', 'Missing' :         ''},
                'FACIL_ID' : {'#' : 28, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Test facility ID                      ', 'Missing' :         ''},
                'FLOOR_ID' : {'#' : 29, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Test floor ID                         ', 'Missing' :         ''},
                'PROC_ID'  : {'#' : 30, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Fabrication process ID                ', 'Missing' :         ''},
                'OPER_FRQ' : {'#' : 31, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Operation frequency or step           ', 'Missing' :         ''},
                'SPEC_NAM' : {'#' : 32, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Test specification name               ', 'Missing' :         ''},
                'SPEC_VER' : {'#' : 33, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Test specification version number     ', 'Missing' :         ''},
                'FLOW_ID'  : {'#' : 34, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Test flow ID                          ', 'Missing' :         ''},
                'SETUP_ID' : {'#' : 35, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Test setup ID                         ', 'Missing' :         ''},
                'DSGN_REV' : {'#' : 36, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Device design revision                ', 'Missing' :         ''},
                'ENG_ID'   : {'#' : 37, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Engineering lot ID                    ', 'Missing' :         ''},
                'ROM_COD'  : {'#' : 38, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'ROM code ID                           ', 'Missing' :         ''},
                'SERL_NUM' : {'#' : 39, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Tester serial number                  ', 'Missing' :         ''},
                'SUPR_NAM' : {'#' : 40, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Supervisor name or ID                 ', 'Missing' :         ''}
            }

        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)