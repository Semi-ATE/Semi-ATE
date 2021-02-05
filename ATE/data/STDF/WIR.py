import sys
import time

from ATE.data.STDF import STDR

class WIR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = 'WIR'
        self.local_debug = False
        if version==None or version=='V4':
            self.version = 'V4'
            self.info = '''
Wafer Information Record
------------------------

Function:
    Acts mainly as a marker to indicate where testing of a particular wafer begins for each
    wafer tested by the job plan. The WIR and the Wafer Results Record (WRR) bracket all
    the stored information pertaining to one tested wafer. This record is used only when
    testing at wafer probe. A WIR/WRR pair will have the same HEAD_NUM and SITE_GRP values.

Frequency:
    * Obligatory for Wafer sort
    * One per wafer tested.

Location:
    Anywhere in the data stream after the initial sequence (see page 14) and before the MRR.
    Sent before testing each wafer.
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' : None},
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1', 'Ref' : None, 'Value' :    2, 'Text' : 'Record type                           ', 'Missing' : None},
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1', 'Ref' : None, 'Value' :   10, 'Text' : 'Record sub-type                       ', 'Missing' : None},
                'HEAD_NUM' : {'#' :  3, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'Test head number                      ', 'Missing' : 1   },
                'SITE_GRP' : {'#' :  4, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'Site group number                     ', 'Missing' : 255 },
                'START_T'  : {'#' :  5, 'Type' : 'U*4', 'Ref' : None, 'Value' : None, 'Text' : 'Date and time first part tested       ', 'Missing' : 0   },
                'WAFER_ID' : {'#' :  6, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Wafer ID                              ', 'Missing' : ''  }
            }

        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)

    def to_atdf(self):

        sequence = {}
        header = ''
        body = ''
        
        header = self.id + ':'

#        The order of fields is different in STDF and ATDF for WIR record
#        STDF page 37, the order is HEAD_NUM, SITE_GRP, START_T,  WAFER_ID
#        ATDF page 33, the order is HEAD_NUM, START_T,  SITE_GRP, WAFER_ID

#       3 HEAD_NUM
        body += self.gen_atdf(3)

#       5 START_T
        v = self.get_fields(5)[3]
        if v != None:
            t = time.strftime("%-H:%-M:%-S %-d-%b-%Y", time.gmtime(v))
            body += "%s|" % (t.upper())

#       4 SITE_GRP
        body += self.gen_atdf(4)
#       6 WAFER_ID
        body += self.gen_atdf(6)

        body = body[:-1]

        # assemble the record
        retval = header + body

        if self.local_debug: print("%s._to_atdf()\n   '%s'\n" % (self.id, retval))
        return retval