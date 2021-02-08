import sys
from ATE.data.STDF import STDR

class PCR(STDR):
    def __init__(self, version=None, endian=None, record = None):
        self.id = 'PCR'
        self.local_debug = False
        if version==None or version=='V4':
            self.version = 'V4'
            self.info =     '''
Part Count Record
-----------------

Function:
    Contains the part count totals for one or all test sites. Each data stream must have at
    least one PCR to show the part count.

Frequency:
    * Obligatory.
    * At least one PCR in the file: either one summary PCR for all test sites
      (HEAD_NUM = 255), or one PCR for each head/site combination, or both.

Location:
    Anywhere in the data stream after the initial "FAR-(ATRs)-MIR-(RDR)-(SDRs)" sequence and before the MRR.
    When data is being recorded in real time, this record will usually appear near the end of the data stream.
'''
            self.fields = {
                'REC_LEN'  : {'#' : 0, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' :        None},
                'REC_TYP'  : {'#' : 1, 'Type' : 'U*1', 'Ref' : None, 'Value' :    1, 'Text' : 'Record type                           ', 'Missing' :        None},
                'REC_SUB'  : {'#' : 2, 'Type' : 'U*1', 'Ref' : None, 'Value' :   30, 'Text' : 'Record sub-type                       ', 'Missing' :        None},
                'HEAD_NUM' : {'#' : 3, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'Test head number                      ', 'Missing' :           0},
                'SITE_NUM' : {'#' : 4, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'Test site number                      ', 'Missing' :           0},
                'PART_CNT' : {'#' : 5, 'Type' : 'U*4', 'Ref' : None, 'Value' : None, 'Text' : 'Number of parts tested                ', 'Missing' :           0},
                'RTST_CNT' : {'#' : 6, 'Type' : 'U*4', 'Ref' : None, 'Value' : None, 'Text' : 'Number of parts retested              ', 'Missing' : 4294967295},
                'ABRT_CNT' : {'#' : 7, 'Type' : 'U*4', 'Ref' : None, 'Value' : None, 'Text' : 'Number of aborts during testing       ', 'Missing' : 4294967295},
                'GOOD_CNT' : {'#' : 8, 'Type' : 'U*4', 'Ref' : None, 'Value' : None, 'Text' : 'Number of good (passed) parts tested  ', 'Missing' : 4294967295},
                'FUNC_CNT' : {'#' : 9, 'Type' : 'U*4', 'Ref' : None, 'Value' : None, 'Text' : 'Number of functional parts tested     ', 'Missing' : 4294967295}
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)

