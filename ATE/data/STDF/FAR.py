import sys
from ATE.data.STDF import STDR

class FAR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = 'FAR'
        self.local_debug = False
        if version==None or version=='V4' or version=='V3':
            if version==None: self.version = 'V4'
            else: self.version = version
            self.info = '''
File Attributes Record
----------------------

Function:
    Contains the information necessary to determine how to decode the STDF data contained in the file.

Frequency:
    * Obligatory
    * One per datastream

Location:
    First record of the STDF file
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' :         None},
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1', 'Ref' : None, 'Value' :    0, 'Text' : 'Record type                           ', 'Missing' :         None},
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1', 'Ref' : None, 'Value' :   10, 'Text' : 'Record sub-type                       ', 'Missing' :         None},
                'CPU_TYPE' : {'#' :  3, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'CPU type that wrote this file         ', 'Missing' :    self.sys_cpu()},
                'STDF_VER' : {'#' :  4, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'STDF version number                   ', 'Missing' : int(self.version[1])}
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)

