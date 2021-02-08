'''
Created on Jan 6, 2016

@author: $Author: horen.tom@gmail.com$

This module is part of the ATE.org (meta) package.
--------------------------------------------------
This library implements the STDF standard to the full extend (meaning including optional field presence) to read/modify/write STDF files.

Support:
    Endians: Little & Big
    Versions & Extensions:
        V3 : standard, +
        V4 : standard, V4-2007, Memory:2010.1
    Modes: read & write
    compressions: gzip (read & write)

Disclaimer:
    Although all aspects of the library are tested extensively with unit tests, the library could only be tested in real life using standard STDF V4 files.
    It has not been used with STDF V4 extensions (lack of sample files) or STDF V3 (lack of sample files and specification)

License : GPL
'''
import bz2
import datetime
import io
import os
import pickle
import struct
import sys
import math
import time
from abc import ABC
from mimetypes import guess_type


if sys.version_info[0] < 3:
    raise Exception("The STDF library is made for Python 3")


__version__ = '$Revision: 0.51 $'
__author__ = '$Author: tho $'

__latest_STDF_version__ = 'V4'

FileNameDefinitions = {
    'V4' : r'[a-zA-Z][a-zA-Z0-9_]{0,38}\.[sS][tT][dD][a-zA-Z0-9_\.]{0,36}'
}

RecordDefinitions = {
    # Information about the STDF file
    (0,10)   : {'V3' : ['FAR', 'File Attributes Record', [('', False)]],                        'V4' : ['FAR', 'File Attributes Record', [('', True)]]                               },
    (0,20)   : {                                                                                'V4' : ['ATR', 'Audit Trail Record', [('', False)]]                                  },
    (0,30)   : {                                                                                'V4' : ['VUR', 'Version Update Record', [('V4-2007', True), ('Memory:2010.1', True)]]},
    # Data collected on a per lot basis
    (1,10)   : {'V3' : ['MIR', 'Master Information Record', [('', True)]],                      'V4' : ['MIR', 'Master Information Record', [('', True)]]                            },
    (1,20)   : {'V3' : ['MRR', 'Master Results Record', [('', True)]],                          'V4' : ['MRR', 'Master Results Record', [('', True)]]                                },
    (1,30)   : {                                                                                'V4' : ['PCR', 'Part Count Record', [('', True)]]                                    },
    (1,40)   : {'V3' : ['HBR', 'Hardware Bin Record', [('', False)]],                           'V4' : ['HBR', 'Hardware Bin Record', [('', False)]]                                 },
    (1,50)   : {'V3' : ['SBR', 'Software Bin Record', [('', False)]],                           'V4' : ['SBR', 'Software Bin Record', [('', False)]]                                 },
    (1,60)   : {'V3' : ['PMR', 'Pin Map Record', [('', False)]],                                'V4' : ['PMR', 'Pin Map Record', [('', False)]]                                      },
    (1,62)   : {                                                                                'V4' : ['PGR', 'Pin Group Record', [('', False)]]                                    },
    (1,63)   : {                                                                                'V4' : ['PLR', 'Pin List Record', [('', False)]]                                     },
    (1,70)   : {                                                                                'V4' : ['RDR', 'Re-test Data Record', [('', False)]]                                 },
    (1,80)   : {                                                                                'V4' : ['SDR', 'Site Description Record', [('', False)]]                             },
    (1,90)   : {                                                                                'V4' : ['PSR', 'Pattern Sequence Record', [('V4-2007', False)]]                      },
    (1,91)   : {                                                                                'V4' : ['NMR', 'Name Map Record', [('V4-2007', False)]]                              },
    (1,92)   : {                                                                                'V4' : ['CNR', 'Cell Name Record', [('V4-2007', False)]]                             },
    (1,93)   : {                                                                                'V4' : ['SSR', 'Scan Structure Record', [('V4-2007', False)]]                        },
    (1,94)   : {                                                                                'V4' : ['CDR', 'Chain Description Record', [('V4-2007', False)]]                     },
    (1,95)   : {                                                                                'V4' : ['ASR', 'Algorithm Specification Record', [('Memory:2010.1', False)]]         },
    (1,96)   : {                                                                                'V4' : ['FSR', 'Frame Specification Record', [('Memory:2010.1', False)]]             },
    (1,97)   : {                                                                                'V4' : ['BSR', 'Bit stream Specification Record', [('Memory:2010.1', False)]]        },
    (1,99)   : {                                                                                'V4' : ['MSR', 'Memory Structure Record', [('Memory:2010.1', False)]]                },
    (1,100)  : {                                                                                'V4' : ['MCR', 'Memory Controller Record', [('Memory:2010.1', False)]]               },
    (1,101)  : {                                                                                'V4' : ['IDR', 'Instance Description Record', [('Memory:2010.1', False)]]            },
    (1,102)  : {                                                                                'V4' : ['MMR', 'Memory Model Record', [('Memory:2010.1', False)]]                    },
    # Data collected per wafer
    (2,10)   : {'V3' : ['WIR', 'Wafer Information Record', [('', False)]],                      'V4' : ['WIR', 'Wafer Information Record', [('', False)]]                            },
    (2,20)   : {'V3' : ['WRR', 'Wafer Results Record', [('', False)]],                          'V4' : ['WRR', 'Wafer Results Record', [('', False)]]                                },
    (2,30)   : {'V3' : ['WCR', 'Wafer Configuration Record', [('', False)]],                    'V4' : ['WCR', 'Wafer Configuration Record', [('', False)]]                          },
    # Data collected on a per part basis
    (5,10)   : {'V3' : ['PIR', 'Part Information Record', [('', False)]],                       'V4' : ['PIR', 'Part Information Record', [('', False)]]                             },
    (5,20)   : {'V3' : ['PRR', 'Part Results Record', [('', False)]],                           'V4' : ['PRR', 'Part Results Record', [('', False)]]                                 },
    # Data collected per test in the test program
    (10,30)  : {'V3' : ['TSR', 'Test Synopsis Record', [('', False)]],                          'V4' : ['TSR', 'Test Synopsis Record', [('', False)]]                                },
    # Data collected per test execution
    (15,10)  : {'V3' : ['PTR', 'Parametric Test Record', [('', False)]],                        'V4' : ['PTR', 'Parametric Test Record', [('', False)]]                              },
    (15,15)  : {                                                                                'V4' : ['MPR', 'Multiple-Result Parametric Record', [('', False)]]                   },
    (15,20)  : {'V3' : ['FTR', 'Functional Test Record', [('', False)]],                        'V4' : ['FTR', 'Functional Test Record', [('', False)]]                              },
    (15,30)  : {                                                                                'V4' : ['STR', 'Scan Test Record', [('V4-2007', False)]]                             },
    (15,40)  : {                                                                                'V4' : ['MTR', 'Memory Test Record', [('Memory:2010.1', False)]]                     },
    # Data collected per program segment
    (20,10)  : {'V3' : ['BPS', 'Begin Program Section Record', [('', False)]],                  'V4' : ['BPS', 'Begin Program Section Record', [('', False)]]                        },
    (20,20)  : {'V3' : ['EPS', 'End Program Section Record', [('', False)]],                    'V4' : ['EPS', 'End Program Section Record', [('', False)]]                          },
    # Generic Data
    (50,10)  : {'V3' : ['GDR', 'Generic Data Record', [('', False)]],                           'V4' : ['GDR', 'Generic Data Record', [('', False)]]                                 },
    (50,30)  : {'V3' : ['DTR', 'Datalog Text Record', [('', False)]],                           'V4' : ['DTR', 'Datalog Text Record', [('', False)]]                                 },
    # Teradyne extensions
    (180,-1) : {                                                                                'V4' : ['RR1', 'Records Reserved for use by Image software', [('', False)]]          },
    (181,-1) : {                                                                                'V4' : ['RR2', 'Records Reserved for use by IG900 software', [('', False)]]          },
}

class STDFError(Exception):
    pass

# Removal of dependency on ATE.utils.macignumber:
# The original implementation in ATE.utils.magicnumber.extension_from_magic_number_in_file(filename)
# returns '.stdf' if the two bytes at offset 2 of the given file are equal to b'\x00\x0A'.
# This checks that the data in the file looks a FAR record (REC_TYP is 0, REC_SUB is 10).
# Note that the REC_LEN field (first two bytes of the file) is probably ignored because it
# depends on the endianness, defined by CPU_TYPE (fifth byte).
def is_file_with_stdf_magicnumber(filename):
    try:
        with open(filename, 'rb') as f:
            f.seek(2)
            return f.read(2) == b'\x00\x0A'
    except OSError:
        # if it cannot be read it's not an stdf file
        return False


# date and time format according to the STDF spec V4:
# number of seconds since midnight on January 1st, 1970, in the local time zone (32bit unsigned int)
# Note that DT() has a more detailed format but that is not relevant for now (e.g. we dont need Quarter)
def _stdf_time_field_value_to_string(seconds_since_1970_in_local_time: int):
    return datetime.datetime.fromtimestamp(seconds_since_1970_in_local_time).strftime('%Y-%m-%d %H:%M:%S')


def ts_to_id(Version=__latest_STDF_version__, Extensions=None):
    '''
    This function returns a dictionary of TS -> ID for the given STDF version and Extension(s)
    If Extensions==None, then all available extensions are used
    '''
    retval = {}
    if Version in supported().versions():
        if Extensions==None:
            Extensions = supported().extensions_for_version(Version) + ['']
        else:
            exts = ['']
            for Extension in Extensions:
                if Extension in supported().extensions(Version):
                    if Extension not in exts:
                        exts.append(Extension)
            Extensions = exts
        for (REC_TYP, REC_SUB) in RecordDefinitions:
            if Version in RecordDefinitions[(REC_TYP, REC_SUB)]:
                for ext, _obligatory_flag in RecordDefinitions[(REC_TYP, REC_SUB)][Version][2]:
                    if ext in Extensions:
                        retval[(REC_TYP, REC_SUB)] = RecordDefinitions[(REC_TYP, REC_SUB)][Version][0]
    return retval

def id_to_ts(Version=__latest_STDF_version__, Extensions=None):
    '''
    This function returns a dictionary ID -> TS for the given STDF version and Extension(s)
    If Extensions==None, then all available extensions are used
    '''
    retval = {}
    temp = ts_to_id(Version, Extensions)
    for item in temp:
        retval[temp[item]]= item
    return retval

class supported(object):

    def __init__(self):
        pass

    def versions(self):
        '''
        This method will return a list of all versions that are supported.
        '''
        retval = []
        for (REC_TYP, REC_SUB) in RecordDefinitions:
            for Version in RecordDefinitions[(REC_TYP, REC_SUB)]:
                if Version not in retval:
                    retval.append(Version)
        return retval

    def extensions_for_version(self, Version=__latest_STDF_version__):
        '''
        This function will return a list of *ALL* Extensions that are supported for the given STDF Version.
        '''
        retval = []
        if Version in self.versions():
            for (Type, Sub) in RecordDefinitions:
                if Version in RecordDefinitions[(Type, Sub)]:
                    exts = RecordDefinitions[(Type, Sub)][Version][2]
                    for ext in exts:
                        if ext[0]!='' and ext[0] not in retval:
                            retval.append(ext[0])
        return retval

    def versions_and_extensions(self):
        '''
        This method returns a dictionary of all versions and the supported extensions for them
        '''
        retval = {}
        for version in self.supported_versions():
            retval[version] = self.extensions_for_version(version)

class STDR(ABC):
    '''
    This is the Abstract Base Class Record for all STDF records
    '''
    buffer = b''

    def __init__(self, endian=None, record=None):
        self.id = 'STDR'
        self.missing_fields = 0
        self.local_debug = True
        self.buffer = ''
        self.fields = {
            'REC_LEN'  : {'#' :  0, 'Type' :  'U*2', 'Ref' : None, 'Value' :      0, 'Text' : 'Bytes of data following header        ', 'Missing' : None},
            'REC_TYP'  : {'#' :  1, 'Type' :  'U*1', 'Ref' : None, 'Value' :      0, 'Text' : 'Record type                           ', 'Missing' : None},
            'REC_SUB'  : {'#' :  2, 'Type' :  'U*1', 'Ref' : None, 'Value' :      0, 'Text' : 'Record sub-type                       ', 'Missing' : None},
            # Types for testing
            'K1'       : {'#' :  3, 'Type' :  'U*1', 'Ref' : None, 'Value' :   None, 'Text' : 'One byte unsigned integer reference   ', 'Missing' : 0},
            'K2'       : {'#' :  4, 'Type' :  'U*2', 'Ref' : None, 'Value' :   None, 'Text' : 'One byte unsigned integer reference   ', 'Missing' : 0},
            'U*1'      : {'#' :  5, 'Type' :  'U*1', 'Ref' : None, 'Value' :   None, 'Text' : 'One byte unsigned integer             ', 'Missing' : 0},
            'U*2'      : {'#' :  6, 'Type' :  'U*2', 'Ref' : None, 'Value' :   None, 'Text' : 'Two byte unsigned integer             ', 'Missing' : 0},
            'U*4'      : {'#' :  7, 'Type' :  'U*4', 'Ref' : None, 'Value' :   None, 'Text' : 'Four byte unsigned integer            ', 'Missing' : 0},
            'U*8'      : {'#' :  8, 'Type' :  'U*8', 'Ref' : None, 'Value' :   None, 'Text' : 'Eight byte unsigned integer           ', 'Missing' : 0},
            'U*?'      : {'#' :  9, 'Type' :  'U*1', 'Ref' : None, 'Value' :   None, 'Text' : 'Eight byte unsigned integer           ', 'Missing' : 0},
            'xU*1'     : {'#' :  9, 'Type' :  'U*1', 'Ref' : 'K1', 'Value' :   None, 'Text' : 'Eight byte unsigned integer           ', 'Missing' : 0},
            'xU*2'     : {'#' :  9, 'Type' :  'U*1', 'Ref' : 'K1', 'Value' :   None, 'Text' : 'Eight byte unsigned integer           ', 'Missing' : 0},
            'xU*4'     : {'#' :  9, 'Type' :  'U*1', 'Ref' : 'K1', 'Value' :   None, 'Text' : 'Eight byte unsigned integer           ', 'Missing' : 0},
            'xU*?'     : {'#' :  9, 'Type' :  'U*1', 'Ref' : 'K1', 'Value' :   None, 'Text' : 'Eight byte unsigned integer           ', 'Missing' : 0},
            'I*1'      : {'#' : 10, 'Type' :  'I*1', 'Ref' : None, 'Value' :   None, 'Text' : 'One byte signed integer               ', 'Missing' : 0},
            'I*2'      : {'#' : 11, 'Type' :  'I*2', 'Ref' : None, 'Value' :   None, 'Text' : 'Two byte signed integer               ', 'Missing' : 0},
            'I*4'      : {'#' : 12, 'Type' :  'I*4', 'Ref' : None, 'Value' :   None, 'Text' : 'Four byte signed integer              ', 'Missing' : 0},
            'I*8'      : {'#' : 13, 'Type' :  'I*8', 'Ref' : None, 'Value' :   None, 'Text' : 'Eight byte signed integer             ', 'Missing' : 0},
            'R*4'      : {'#' : 14, 'Type' :  'R*4', 'Ref' : None, 'Value' :   None, 'Text' : 'Four byte floating point number       ', 'Missing' : 0.0},
            'R*8'      : {'#' : 15, 'Type' :  'R*8', 'Ref' : None, 'Value' :   None, 'Text' : 'Eight byte floating point number      ', 'Missing' : 0.0},
            'C*1'      : {'#' : 16, 'Type' :  'R*8', 'Ref' : None, 'Value' :   None, 'Text' : 'One byte fixed length string          ', 'Missing' : '1'},
            'C*2'      : {'#' : 17, 'Type' :  'R*8', 'Ref' : None, 'Value' :   None, 'Text' : 'Two byte fixed length string          ', 'Missing' : '12'},
            'C*3'      : {'#' : 18, 'Type' :  'R*8', 'Ref' : None, 'Value' :   None, 'Text' : 'Three byte fixed length string        ', 'Missing' : '123'},
            'R*9'      : {'#' : 19, 'Type' :  'R*8', 'Ref' : None, 'Value' :   None, 'Text' : 'Nine byte fixed length string         ', 'Missing' : '123456789'},
            'C*10'     : {'#' : 20, 'Type' :  'R*8', 'Ref' : None, 'Value' :   None, 'Text' : 'Ten byte (2-digit) fixed length string', 'Missing' : '1234567890'}

# C*12 Fixed length character string:
# C*n Variable length character string
# C*f Variable length character string

# B*6 Fixed length bit-encoded data
# V*n Variable data type field:
# B*n Variable length bit-encoded field.
# D*n Variable length bit-encoded field.
# N*1 Unsigned integer data stored in a nibble.
# kxTYPE Array of data of the type specified.

        }
        self._default_init(endian, record)

    def _default_init(self, endian=None, record=None):
        # missing fields
        self.missing_fields = 0
        # Buffer
        self.buffer = ''
        # Endian
        if endian == None:
            self.endian = self.sys_endian()
        elif ((endian == '<') or (endian == '>')):
            self.endian = endian
        else:
            raise STDFError("%s object creation error : unsupported endian '%s'" % (self.id, endian))
        # Record
        if record != None:
            if self.local_debug: print("len(%s) = %s" % (self.id, len(record)))
            self._unpack(record)

    def __call__(self, endian = None, record = None):
        '''
        Method to change contents of an already created object. (eg : Change endian)
        '''
        if endian != None:
            if ((endian == '<') or (endian == '>')):
                self.endian = endian
            else:
                raise STDFError("%s object creation error : unsupported endian '%s'" % (self.id, endian))
        if record != None:
            self._unpack(record)

    def get_fields(self, FieldID = None):
        '''
        Getter, returns a 7 element tuple (#, Type, Ref, Value, Text, Missing, Note)
        if FieldID is provided either in a string or numerical way.
        If it is not provided, it returns a (IN ORDER) list of (string) keys.
        '''
        if FieldID == None:
            retval = [None] * len(self.fields)
            for field in self.fields:
                retval[self.fields[field]['#']] = field
            return retval
        else:
            if isinstance(FieldID, str):
                if FieldID in self.fields:
                    return(self.fields[FieldID]['#'],
                           self.fields[FieldID]['Type'],
                           self.fields[FieldID]['Ref'],
                           self.fields[FieldID]['Value'],
                           self.fields[FieldID]['Text'],
                           self.fields[FieldID]['Missing'])
                else:
                    return (None, None, None, None, None)
            elif isinstance(FieldID, int):
                if FieldID in range(len(self.fields)):
                    for field in self.fields:
                        if self.fields[field]['#'] == FieldID:
                            return(self.fields[field]['#'],
                                   self.fields[field]['Type'],
                                   self.fields[field]['Ref'],
                                   self.fields[field]['Value'],
                                   self.fields[field]['Text'],
                                   self.fields[field]['Missing'])
                else:
                    return (None, None, None, None, None)
            else:
                raise STDFError("%s.get_fields(%s) Error : '%s' is not a string or integer" % (self.id, FieldID, FieldID))

    def get_value(self, FieldID):
        _, _, Ref, Value, _, Missing = self.get_fields(FieldID)
        # TODO: ref value handling is missing here: for arrays (kxTYPE etc.) this returns the size of the array instead of its value for now
        if Ref is not None:
            return self.get_value(ref)
        return Missing if Value is None else Value

    def set_value(self, FieldID, Value):
        '''
        Setter, sets the Value of the FieldID
        '''
        FieldKey = ''
        if isinstance(FieldID, int):
            for field in self.fields:
                if self.fields[field]['#'] == FieldID:
                    FieldKey = field
            if FieldKey == '':
                raise STDFError("%s.set_value(%s, %s) Error : '%s' is not a valid key" % (self.id, FieldID, Value, FieldID))
        elif isinstance(FieldID, str):
            if FieldID not in self.fields:
                raise STDFError("%s.set_value(%s, %s) Error : '%s' is not a valid key" % (self.id, FieldID, Value, FieldID))
            else:
                FieldKey = FieldID
        else:
            raise STDFError("%s.set_value(%s, %s) : Error : '%s' is not a string or integer." % (self.id, FieldID, Value, FieldID))

        Type, Ref = self.get_fields(FieldKey)[1:3]
        K = None
        # TODO: the following condition should most likely be "Ref is not None", since this one is always true but initialized K to the field with '#' == 3 in case of Ref == None
#	Changed by semit
#	Old code:
#        if Ref != '':
#	New code:
        if Ref != None:
            K = self.get_fields(Ref)[3]
        Type, Bytes = Type.split("*")

        if Type.startswith('x'):
            if not isinstance(Value, list):
                raise STDFError("%s.set_value(%s, %s) Error : '%s' does not references a list." % (self.id, FieldKey, Value, "*".join((str(K), Type, Bytes))))
            length_type = self.fields[Ref]['Type']
            if not length_type.startswith('U*'):
                raise STDFError("%s.set_value(%s, %s) Error : '%s' references a non unsigned integer." % (self.id, FieldKey, Value, "*".join((str(K), Type, Bytes))))
            if not length_type in ['U*1', 'U*2', 'U*4', 'U*8']:
                raise STDFError("%s.set_value(%s, %s) Error : '%s' references an unsupported unsigned integer." % (self.id, FieldKey, Value, "*".join((str(K), Type, Bytes))))

            if Type == 'xU': # list of unsigned integers
                temp = [0] * len(Value)
                if Bytes == '1':
                    for index in range(len(Value)):
                        if isinstance(Value[index], int):
                            if ((Value[index]>=0) and (Value[index]<=255)): temp[index]=Value[index]
                            else: raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]=%s' can not be casted into U*1." % (self.id, FieldKey, Value, index, Value[index]))
                        else:
                            raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]' is not an integer." % (self.id, FieldKey, Value, index))
                elif Bytes == '2':
                    for index in range(len(Value)):
                        if isinstance(Value[index], int):
                            if ((Value[index]>=0) and (Value[index]<=65535)): temp[index]=Value[index]
                            else: raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]=%s' can not be casted into U*2" % (self.id, FieldKey, Value, index, Value[index]))
                        else:
                            raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]' is not an integer." % (self.id, FieldKey, Value, index))
                elif Bytes == '4':
                    for index in range(len(Value)):
                        if isinstance(Value[index], int):
                            if ((Value[index]>=0) and (Value[index]<=4294967295)): temp[index]=Value[index]
                            else: raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]=%s' can not be casted into U*4" % (self.id, FieldKey, Value, index, Value[index]))
                        else:
                            raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]' is not an integer." % (self.id, FieldKey, Value, index))
                elif Bytes == '8':
                    for index in range(len(Value)):
                        if isinstance(Value[index], int):
                            if ((Value[index]>=0) and (Value[index]<=18446744073709551615)): temp[index]=Value[index]
                            else: raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]=%s' can not be casted into U*8" % (self.id, FieldKey, Value, index, Value[index]))
                        else:
                            raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]' is not an integer." % (self.id, FieldKey, Value, index))
                else:
                    raise STDFError("%s.set_value(%s, %s) Error : '%s' is an unsupported Type" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                self.fields[FieldKey]['Value'] = temp
                self.fields[Ref]['Value'] = len(temp)
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s, Reference '%s' = %s" % (self.id, FieldKey, Value, temp, Ref, len(temp)))

            elif Type == 'xI': # list of signed integers
                temp = [0] * len(Value)
                if Bytes == '1':
                    for index in range(len(Value)):
                        if isinstance(Value[index], int):
                            if ((Value[index]>=-128) and (Value[index]<=128)): temp[index]=Value[index]
                            else: raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]=%s' can not be casted into I*1" % (self.id, FieldKey, Value, index, Value[index]))
                        else:
                            raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]' is not an integer." % (self.id, FieldKey, Value, index))
                elif Bytes == '2':
                    for index in range(len(Value)):
                        if isinstance(Value[index], int):
                            if ((Value[index]>=-32768) and (Value[index]<=32767)): temp[index]=Value[index]
                            else: raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]=%s' can not be casted into I*2" % (self.id, FieldKey, Value, index, Value[index]))
                        else:
                            raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]' is not an integer." % (self.id, FieldKey, Value, index))
                elif Bytes == '4':
                    for index in range(len(Value)):
                        if isinstance(Value[index], int):
                            if ((Value[index]>=-2147483648) and (Value[index]<=2147483647)): temp[index]=Value[index]
                            else: raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]=%s' can not be casted into I*4" % (self.id, FieldKey, Value, index, Value[index]))
                        else:
                            raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]' is not an integer." % (self.id, FieldKey, Value, index))
                elif Bytes == '8':
                    for index in range(len(Value)):
                        if isinstance(Value[index], int):
                            if ((Value[index]>=-36028797018963968) and (Value[index]<=36028797018963967)): temp[index]=Value[index]
                            else: raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]=%s' can not be casted into I*8" % (self.id, FieldKey, Value, index, Value[index]))
                        else:
                            raise STDFError("%s.set_value(%s, %s) Error : 'index[%s]' is not an integer." % (self.id, FieldKey, Value, index))
                else:
                    raise STDFError("%s.set_value(%s, %s) Error : '%s' is an unsupported Type" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                self.fields[FieldKey]['Value'] = temp
                self.fields[Ref]['Value'] = len(temp)
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s, Reference '%s' = %s" % (self.id, FieldKey, Value, temp, Ref, len(temp)))

            elif Type == 'xR': # list of floats
                temp = [0.0] * len(Value)
                if ((Bytes == '4') or (Bytes == '8')):
                    for index in range(len(Value)):
                        temp[index] = float(Value[index]) # no checking for float & double, pack will cast with appropriate precision, cast integers.
                else:
                    raise STDFError("%s.set_value(%s, %s) Error : '%s' is an unsupported Type" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                self.fields[FieldKey]['Value'] = temp
                self.fields[Ref]['Value'] = len(temp)
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s, Reference '%s' = %s" % (self.id, FieldKey, Value, temp, Ref, len(temp)))

            elif Type == 'xC': # list of strings
                temp = [''] * len(Value)
                if Bytes.isdigit():
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                elif Bytes == 'n':
                    for i in range(len(Value)):
                        temp[i] = Value[i]
                elif Bytes == 'f':
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                self.fields[FieldKey]['Value'] = temp
                self.fields[Ref]['Value'] = len(temp)
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s, Reference '%s' = %s" % (self.id, FieldKey, Value, temp, Ref, len(temp)))

            elif Type == 'xB': # list of list of single character strings being '0' or '1' (max length = 255*8 = 2040 bits)
                if Bytes.isdigit():
                    temp = [['0'] * (int(Bytes) * 8)] * len(Value)
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                elif Bytes == 'n':
                    temp = [['0'] * (int() * 8)] * len(Value) #TODO: Fill in the int() statement
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                elif Bytes == 'f':
                    temp = [['0'] * (int() * 8)] * len(Value) #TODO: Fill in the int() statement
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                self.fields[FieldKey]['Value'] = temp
                self.fields[Ref]['Value'] = len(temp)
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s, Reference '%s' = %s" % (self.id, FieldKey, Value, temp, Ref, len(temp)))

            elif Type == 'xD': # list of list of single character strings being '0' and '1'(max length = 65535 bits)
                if Bytes.isdigit():
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                elif Bytes == 'n':
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                elif Bytes == 'f':
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                # assign from temp to field
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s, Reference '%s' = %s" % (self.id, FieldKey, Value, temp, Ref, len(temp)))

            elif Type == 'xN': # list of list of nibble integers
                if not isinstance(Value, list):
                    raise STDFError("%s.set_value(%s, %s) : %s should be a list" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                for nibble_list in Value:
                    if not isinstance(nibble_list, int):
                        raise STDFError("%s.set_value(%s, %s) Error : %s should be a list of nibble(s)" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                if Bytes.isdigit():
                    temp = Value
                elif Bytes == 'n':
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                elif Bytes == 'f':
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                self.fields[FieldKey]['Value'] = temp
                self.fields[Ref]['Value'] = len(temp)
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s, Reference '%s' = %s" % (self.id, FieldKey, Value, temp, Ref, len(temp)))

            elif Type == 'xV': # list of tuple (type, value) where type is defined in spec page 62tuples
                '''
                 0 = B*0 Special pad field
                 1 = U*1 One byte unsigned integer
                 2 = U*2 Two byte unsigned integer
                 3 = U*4 Four byte unsigned integer
                 4 = I*1 One byte signed integer
                 5 = I*2 Two byte signed integer
                 6 = I*4 Four byte signed integer
                 7 = R*4 Four byte floating point number
                 8 = R*8 Eight byte floating point number
                10 = C*n Variable length ASCII character string (first byte is string length in bytes)
                11 = B*n Variable length binary data string (first byte is string length in bytes)
                12 = D*n Bit encoded data (first two bytes of string are length in bits)
                13 = N*1 Unsigned nibble
                '''
                if Bytes.isdigit():
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                elif Bytes == 'n':
                    temp = Value
                    if self.fields[FieldKey]['Value'] == None:
                        self.fields[FieldKey]['Value'] = []

                    code = temp[0][0]

                    if code < 0 or code == 9 or code > 13 :
                        raise STDFError(f"{self.id}.set_value({FieldKey}, {temp}) Error : valid data type codes are from 0 to 8 and from 9 to 13 ")

                    self.fields[FieldKey]['Value'].append(temp)
                    if self.local_debug: print(f"{self.id}._set_value({FieldKey}, {Value}) -> added at position {len(self.fields[FieldKey]['Value'])} ")

                elif Bytes == 'f':
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldKey, Value, str(K) + '*'.join((Type, Bytes))))
                # assign from temp to field
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s, Reference '%s' = %s" % (self.id, FieldKey, Value, temp, Ref, len(temp)))

            else:
                raise STDFError("%s.set_value(%s, %s) Error : '%s' is an unsupported Type" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
        else:
            temp = ''
            if Type == 'U': # unsigned integer
                if type(Value) not in [int, int]:
                    raise STDFError("%s.set_value(%s, %s) Error : '%s' is not a an integer" % (self.id, FieldKey, Value, Value))
                if Bytes == '1':
                    if ((Value>=0) and (Value<=255)): temp = Value
                    else: raise STDFError("%s.set_value(%s, %s) Error : '%s' can not be casted into U*1" % (self.id, FieldKey, Value, Value))
                elif Bytes == '2':
                    if ((Value>=0) and (Value<=65535)): temp = Value
                    else: raise STDFError("%s.set_value(%s, %s) Error : '%s' can not be casted into U*2" % (self.id, FieldKey, Value, Value))
                elif Bytes == '4':
                    if ((Value>=0) and (Value<=4294967295)): temp = Value
                    else: raise STDFError("%s.set_value(%s, %s) Error : '%s' can not be casted into U*4" % (self.id, FieldKey, Value, Value))
                elif Bytes == '8':
                    if ((Value>=0) and (Value<=18446744073709551615)): temp = Value
                    else: raise STDFError("%s.set_value(%s, %s) Error : '%s' can not be casted into U*8" % (self.id, FieldKey, Value, Value))
                else:
                    raise STDFError("%s.set_value(%s, %s) Error : '%s' is an unsupported Type" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                self.fields[FieldKey]['Value'] = temp
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s" % (self.id, FieldKey, Value, temp))

            elif Type == 'I': # signed integer
                if type(Value) not in [int, int]:
                    raise STDFError("%s.set_value(%s, %s) : '%s' is not an integer" % (self.id, FieldKey, Value, Value))
                if Bytes == '1':
                    if ((Value>=-128) and (Value<=127)): temp = Value
                    else: raise STDFError("%s.set_value(%s, %s) : '%s' can not be casted into I*1" % (self.id, FieldKey, Value, Value))
                elif Bytes == '2':
                    if ((Value>=-32768) and (Value<=32767)): temp = Value
                    else: raise STDFError("%s.set_value(%s, %s) : '%s' can not be casted into I*2" % (self.id, FieldKey, Value, Value))
                elif Bytes == '4':
                    if ((Value>=-2147483648) and (Value<=2147483647)): temp = Value
                    else: raise STDFError("%s.set_value(%s, %s) : '%s' can not be casted into I*4" % (self.id, FieldKey, Value, Value))
                elif Bytes == '8':
                    if ((Value>=-36028797018963968) and (Value<=36028797018963967)): temp = Value
                    else: raise STDFError("%s.set_value(%s, %s) : '%s' can not be casted into I*8" % (self.id, FieldKey, Value, Value))
                else:
                    raise STDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                self.fields[FieldKey]['Value'] = temp
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s" % (self.id, FieldKey, Value, temp))

            elif Type == 'R': # float
                if type(Value) not in [float, int, int]:
                    raise STDFError("%s.set_value(%s, %s) : '%s' is not a float" % (self.id, FieldKey, Value, Value))
                if ((Bytes == '4') or (Bytes == '8')): temp = float(Value) # no checking for float & double, pack will cast with appropriate precision
                else: raise STDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                self.fields[FieldKey]['Value'] = temp
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s" % (self.id, FieldKey, Value, temp))

            elif Type == 'C': # string
                if not isinstance(Value, str):
                    raise STDFError("%s.set_value(%s, %s) Error : '%s' is not a python-string" % (self.id, FieldKey, Value, Value))
                if Bytes.isdigit():
                    temp = Value.strip()[:int(Bytes)]
                    #TODO: pad with spaces if the length doesn't match !!!
                    # TODO: OK, but why strip first, just to pad again? common value for "C*1" is a single space ' ', but "C*n" is usually not filled with spaces, is it?
                    temp = temp.ljust(int(Bytes), ' ')
                elif Bytes == 'n':
                    temp = Value.strip()[:255]
                elif Bytes == 'f':
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                self.fields[FieldKey]['Value'] = temp
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s" % (self.id, FieldKey, Value, temp))

            elif Type == 'B': # list of single character strings being '0' or '1' (max length = 255*8 = 2040 bits)
                if Bytes.isdigit():
                    if Bytes == '1': # can be a list of '1' and '0' or can be an unsigned 1 character byte
                        temp = ['0'] * 8
                        if isinstance(Value, int):
                            if (Value < 0) or (Value > 255):
                                raise STDFError("%s.set_value(%s, %s) : '%s' does contain an non-8-bit integer." % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                            for Bit in range(8):
                                mask = pow(2, 7-Bit)
                                if (Value & mask) == mask:
                                    temp[Bit] = '1'
                        elif isinstance(Value, list):
                            if len(Value) != 8:
                                raise STDFError("%s.set_value(%s, %s) : '%s' does contain a list of 8 elements." % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                            for Bit in range(8):
                                if not isinstance(Value[Bit], str):
                                    raise STDFError("%s.set_value(%s, %s) : '%s' does contain a list of 8 elements but there are non-string elements inside." % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                                if Value[Bit] not in ['0', '1']:
                                    raise STDFError("%s.set_value(%s, %s) : '%s' does contain a list of 8 elements, all string, but none '0' or '1'." % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                            temp = Value
                        else:
                            raise STDFError("%s.set_value(%s, %s) : assignment to 'B*1' is not an integer or list" % (self.id, FieldKey, Value))
                    else:
                        raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                elif Bytes == 'n':
                    if not isinstance(Value, list):
                        raise STDFError("%s.set_value(%s, %s) : assignment to '%s' is not a list" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                    # Determine how long the end result will be
                    result_length = 0
                    for index in range(len(Value)):
                        if isinstance(Value[index], str):
                            if Value[index] in ['0', '1']:
                                result_length += 1
                            else:
                                raise STDFError("%s.set_value(%s, %s) : '%s' list does contain a string element that is not '1' or '0'." % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                        elif isinstance(Value[index], int):
                            if (Value[index] >= 0) and (Value[index] <= 255):
                                result_length += 8
                            else:
                                raise STDFError("%s.set_value(%s, %s) : '%s' list does contain an non-8-bit integer." % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                        else:
                            raise STDFError("%s.set_value(%s, %s) : '%s' list does contain an element that is not of type int or string." % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                    if result_length % 8 != 0:
                        raise STDFError("%s.set_value(%s, %s) : '%s' list does not constitute a multiple of 8 bits." % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                    temp = ['0'] * result_length
                    temp_index = 0
                    for value_index in range(len(Value)):
                        if isinstance(Value[value_index], str):
                            temp[temp_index] = Value[value_index]
                            temp_index += 1
                        elif isinstance(Value[value_index], int):
                            for Bit in range(8):
                                mask = pow(2, 7-Bit)
                                if (Value[value_index] & mask) == mask:
                                    temp[temp_index] = '1'
                                temp_index += 1
                        else:
                            raise STDFError("%s.set_value(%s, %s) : '%s' list does contain an element that is not of type int or string." % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                elif Bytes == 'f':
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                self.fields[FieldKey]['Value'] = temp
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s" % (self.id, FieldKey, Value, temp))

            elif Type == 'D': # list of single character strings being '0' and '1'(max length = 65535 bits)
                if not isinstance(Value, list):
                    raise STDFError("%s.set_value(%s, %s) Error : '%s' is not a list" % (self.id, FieldKey, Value, Value))
                if Bytes.isdigit():
                    if int(Bytes) > 65535:
                        raise STDFError("%s.set_value(%s, %s) Error : type '%s' can't be bigger than 65535 bits" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                    temp = ['0'] * int(Bytes) # set all bits to '0'
                    if len(Value) > len(temp):
                        raise STDFError("%s.set_value(%s, %s) Error : too many elements in Value" % (self.id, FieldKey, Value))
                    for i in range(len(Value)):
                        temp[i] = Value[i]
                elif Bytes == 'n':
                    temp = Value
                elif Bytes == 'f':
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                self.fields[FieldKey]['Value'] = temp
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s" % (self.id, FieldKey, Value, temp))

            elif Type == 'N': # list of integers
                if not isinstance(Value, list):
                    raise STDFError("%s.set_value(%s, %s) Error : '%s' is not a list" % (self.id, FieldKey, Value, Value))
                for nibble in Value:
                    if ((nibble<0) or (nibble>15)):
                        raise STDFError("%s.set_value(%s, %s) Error : a non-nibble value is present in the list." % (self.id, FieldKey, Value))
                if Bytes.isdigit():
                    if int(Bytes) > 510:
                        raise STDFError("%s.set_value(%s, %s) Error : type '%s' can't be bigger than 510 nibbles" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                    temp = [0] * int(Bytes)
                    if len(Value) > len(temp):
                        raise STDFError("%s.set_value(%s, %s) Error : too many elements in Value" % (self.id, FieldKey, Value))
                    for i in range(len(Value)):
                        temp[i] = Value[i]
                elif Bytes == 'n':
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                elif Bytes == 'f':
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                self.fields[FieldKey]['Value'] = temp
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s" % (self.id, FieldKey, Value, temp))

            elif Type == 'V': # tuple (type, value) where type is defined in spec page 62
                '''
                 0 = B*0 Special pad field
                 1 = U*1 One byte unsigned integer
                 2 = U*2 Two byte unsigned integer
                 3 = U*4 Four byte unsigned integer
                 4 = I*1 One byte signed integer
                 5 = I*2 Two byte signed integer
                 6 = I*4 Four byte signed integer
                 7 = R*4 Four byte floating point number
                 8 = R*8 Eight byte floating point number
                10 = C*n Variable length ASCII character string (first byte is string length in bytes)
                11 = B*n Variable length binary data string (first byte is string length in bytes)
                12 = D*n Bit encoded data (first two bytes of string are length in bits)
                13 = N*1 Unsigned nibble
                '''
                if not isinstance(Value, tuple):
                    raise STDFError("%s.set_value(%s, %s) : '%s' is not a tuple", (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                if len(Value) != 2:
                    raise STDFError("%s.set_value(%s, %s) : '%s' is not a 2-element tuple", (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                if Value[0] not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 'B*0', 'U*1', 'U*2', 'U*4', 'I*1', 'I*2', 'I*4', 'R*4', 'R*8', 'C*n', 'B*n', 'D*n', 'N*1']:
                    raise STDFError("%s.set_value(%s, %s) : '%s' first element of the tuple is not a recognized", (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                if Bytes.isdigit():
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                elif Bytes == 'n':
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                elif Bytes == 'f':
                    raise STDFError("%s.set_value(%s, %s) : Unimplemented type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))
                self.fields[FieldKey]['Value'] = temp
                if self.local_debug: print("%s._set_value(%s, %s) -> Value = %s" % (self.id, FieldKey, Value, temp))

            else:
                raise STDFError("%s.set_value(%s, %s) Error : '%s' is an unsupported Type" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))

    def _type_size(self, FieldID):
        '''
        support function to determine the type size
        '''
        FieldKey = ''
        if isinstance(FieldID, int):
            for field in self.fields:
                if self.fields[field]['#'] == FieldID:
                    FieldKey = field
            if FieldKey == '':
                raise STDFError("%s._type_size(%s) : '%s' is not a valid key" % (self.id, FieldID, FieldID))
        elif isinstance(FieldID, str):
            if FieldID not in self.fields:
                raise STDFError("%s._type_size(%s) : '%s' is not a valid key" % (self.id, FieldID, FieldID))
            else:
                FieldKey = FieldID
        else:
            raise STDFError("%s._type_size(%s) : '%s' is not a string or integer." % (self.id, FieldID,FieldID))

        Type, Ref, Value = self.get_fields(FieldKey)[1:4]
        if Value==None: Value=self.get_fields(FieldKey)[5] # get the 'missing' default
        # TODO: the reference handling and/or array ("kxTYPE") handling here is most probably
        # broken and need to be tested: (e.g. Ref !='' seems wrong, missing/default value of
        # referenced field should be used, None check before use of K below etc.)
        K = None
        if Ref != None:
            K = self.get_fields(Ref)[3]
        Type, Bytes = Type.split("*")
        if Type.startswith('x'):
            if ((Type == 'xU') or (Type == 'xI')):
                if Bytes in ['1', '2', '4', '8']:
                    retval = int(Bytes) * K
                    if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, str(K) + '*'.join((Type, Bytes))))
                    return retval
                else:
                    raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
            elif Type == 'xR':
                if Bytes in ['4', '8']:
                    retval = int(Bytes) * K
                    if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, str(K) + '*'.join((Type, Bytes))))
                    return retval
                else:
                    raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
            elif Type == 'xC':
                if Bytes.isdigit():
                    retval = int(Bytes) * K
                    if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, str(K) + '*'.join((Type, Bytes))))
                    return retval
                elif Bytes == 'n':
                    retval = 0
                    list_values = self.fields[FieldID]['Value'] 
                    for i in range(len(list_values)):
                        retval += len(list_values[i]) + 1
                    return retval
                elif Bytes == 'f':
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
            elif Type == 'xB':
                if Bytes.isdigit():
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                elif Bytes == 'n':
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                elif Bytes == 'f':
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
            elif Type == 'xD':
                if Bytes.isdigit():
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                elif Bytes == 'n':
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                elif Bytes == 'f':
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
            elif Type == 'xN':
                if Bytes.isdigit():
                    retval = math.ceil(K/2)
                    if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, str(K) + '*'.join((Type, Bytes))))
                    return retval
                elif Bytes == 'n':
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                elif Bytes == 'f':
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
            elif Type == 'xV':
                if Bytes.isdigit():
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                elif Bytes == 'n':
                    retval = 0
                    l = self.fields[FieldKey]['Value']
                    size = len(l)
                    pad_for_code = [2,4,5,6,7,8]
                    # index of the length_for_code list is the data type code mention in page 64 for GEN_DATA field
                    # first 8 elements are size in bytes for B*0, U*1, U*2, U*4, I*1, I*2, I*4, R*4, R*8 
                    # rest of the elements are length size in bytes for C*n, B*n, D*n, N*1
                    length_for_code = [1, 1, 2, 4, 1, 2, 4, 4, 8, 0, 1, 1, 2, 1]
                    for i in range(size):
                        code = l[i][0][0]
                        # The data type code is the first unsigned byte of the field.
                        retval += 1
                        if code < 9:
                            # Adding size for the numeric data
                            retval += length_for_code[code]
                        elif code == 10 or code == 11:
                            # Adding size of the arrays
                            value = l[i][0][1]
                            retval += length_for_code[code]
                            retval += len(value)
                        elif code == 12:
                            value = l[i][0][1]
                            retval += length_for_code[code]
                            retval += math.ceil(len(value) / 8)
                        elif code == 13:
                            retval += length_for_code[code]
                                            
                        if code in pad_for_code:
                            retval += 1
                    if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, '*'.join((Type, Bytes))))
                    return retval    
                elif Bytes == 'f':
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
            else:
                raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
        else:
            if ((Type == 'U') or (Type == 'I')):
                if Bytes in ['1', '2', '4', '8']:
                    retval = int(Bytes)
                    if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, '*'.join((Type, Bytes))))
                    return retval
                else:
                    raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
            elif Type == 'R':
                if Bytes in ['4', '8']:
                    retval = int(Bytes)
                    if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, '*'.join((Type, Bytes))))
                    return retval
                else:
                    raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
            elif Type == 'C':
                if Bytes.isdigit():
                    retval = int(Bytes)
                    if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, '*'.join((Type, Bytes))))
                    return retval
                elif Bytes == 'n':
                    retval = len(Value) + 1
                    if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, '*'.join((Type, Bytes))))
                    return retval
                elif Bytes == 'f':
                    retval = len(Value)
                    if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, '*'.join((Type, Bytes))))
                    return retval
                else:
                    raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
            elif Type == 'B':
                if Bytes.isdigit():
                    retval = int(Bytes)
                    if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, '*'.join((Type, Bytes))))
                    return retval
                elif Bytes == 'n':
                    bits_to_pack = len(Value)
                    bytes_to_pack = bits_to_pack // 8
                    if (bits_to_pack % 8) != 0:
                        bytes_to_pack += 1
                    if bytes_to_pack <= 255:
                        retval = bytes_to_pack + 1
                        if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, '*'.join((Type, Bytes))))
                        return retval
                    else:
                        raise STDFError("%s._type_size(%s) : '%s' can not hold more than 255 bytes" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                elif Bytes == 'f':
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
            elif Type == 'D':
                if Bytes.isdigit():
                    bytes_to_pack = int(Bytes) // 8
                    if (int(Bytes) % 8) != 0:
                        bytes_to_pack += 1
                    retval = bytes_to_pack
                    if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, '*'.join((Type, Bytes))))
                    return retval
                elif Bytes == 'n':
                    bits_to_pack = len(Value)
                    bytes_to_pack = bits_to_pack // 8
                    if (bits_to_pack % 8) != 0:
                        bytes_to_pack += 1
                    if bytes_to_pack <= 8192:
                        retval = bytes_to_pack + 2
                        if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, '*'.join((Type, Bytes))))
                        return retval
                    else:
                        raise STDFError("%s._type_size(%s) : '%s' can not hold more than 8192 bytes (=65535 bits)" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                elif Bytes == 'f':
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
            elif Type == 'N':
                if Bytes.isdigit():
                    bytes_to_pack = int(Bytes) // 2
                    if (int(Bytes) % 2) != 0:
                        bytes_to_pack += 1
                    retval = bytes_to_pack
                    if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, '*'.join((Type, Bytes))))
                    return retval
                elif Bytes == 'n':
                    nibbles_to_pack = len(Value)
                    bytes_to_pack = nibbles_to_pack // 2
                    if (nibbles_to_pack % 2) != 0:
                        bytes_to_pack += 1
                    retval = bytes_to_pack + 1
                    if self.local_debug: print("%s._type_size(%s) = %s [%s]" % (self.id, FieldKey, retval, '*'.join((Type, Bytes))))
                    return retval
                elif Bytes == 'f':
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
            elif Type == 'V':
                if Bytes.isdigit():
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                elif Bytes == 'n':
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                elif Bytes == 'f':
                    raise STDFError("%s._type_size(%s) : Unimplemented type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                else:
                    raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
            else:
                raise STDFError("%s_type_size(%s) : Unsupported type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))

    def _update_rec_len(self):
        '''
        Private method that updates the "bytes following the header" in the 'REC_LEN' field
        '''
        reclen = 0
        is_optional_flag = False
        
        for field in self.fields:
            if field == 'REC_LEN' : continue
            if field == 'REC_TYP' : continue
            if field == 'REC_SUB' : continue
#            When a record contains the OPT_FLAG, the fields after OPT_FLAG are 
#            not mandatory always. They have to be set in the first instance of 
#            the record as "default values" and after that if there are no changes
#            they can be skipped (including the OPT_FLAG field)
            if field == 'OPT_FLAG':
                is_optional_flag = True
                if self.fields[field]['Value'] != None:
                    reclen += self._type_size(field)
                continue
            if is_optional_flag:
                if self.fields[field]['Value'] != None:
                    reclen += self._type_size(field)
            else:
                reclen += self._type_size(field)

        if self.local_debug: print("%s._update_rec_len() = %s" % (self.id, reclen))
        self.fields['REC_LEN']['Value'] = reclen

    def _pack_item(self, FieldID):
        '''
        Private method that packs a field from the record and returns the packed version.


            'KxT*S'
                K = reference in other field
                T = Type (U, I, R, C, B, D, N, V)
                    U = Unsigned integer
                    I = Signed integer
                    R = Floating point
                    C = String
                    S = Long string
                    B = list of bytes
                    D = list of bits
                    N = list of nibbles
                    V = variable type
                S = Size (#, n, f)
                    # = size is given by the number
                    n = size is in the first byte (255=max)
                    f = size is in another field.
        '''
        FieldKey = ''
        if isinstance(FieldID, int):
            for field in self.fields:
                if self.fields[field]['#'] == FieldID:
                    FieldKey = field
            if FieldKey == '':
                raise STDFError("%s._pack_item(%s) Error : not a valid integer key" % (self.id, FieldID))
        elif isinstance(FieldID, str):
            if FieldID not in self.fields:
                raise STDFError("%s._pack_item(%s) Error : not a valid string key" % (self.id, FieldID))
            else:
                FieldKey = FieldID
        else:
            raise STDFError("%s._pack_item(%s) Error : not a string or integer key." % (self.id, FieldID))

        TypeFormat, Ref, Value = self.get_fields(FieldKey)[1:4] # get Type, Reference and Value
        if Value==None: Value=self.get_fields(FieldKey)[5] # get the 'missing' default

        if Value is None:
            # changed behavior to consistently require explicit initialization of non-optional
            # fields (instead of crashing somewhere below when None is accessed).
            # we could introdce a non-strict mode where we store valid data for the current
            # type here if this is not desired.
            raise STDFError("%s._pack_item(%s) : Error : cannot pack uninitialized value (None) of non-optional field" % (self.id, FieldKey))

        Type, Size = TypeFormat.split("*")
        if Type.startswith('x'):
            Type = Type[1:]
            TypeMultiplier = True
        else:
            TypeMultiplier = False
        if Ref!=None:
            if isinstance(Ref, str) and TypeMultiplier:
                K = self.get_fields(Ref)[3]
            elif isinstance(Ref, tuple):
                if (len(Ref)==1 and not TypeMultiplier) or (len(Ref)==2 and TypeMultiplier):
                    K = self.get_fields(Ref[0])[3]
                else:
                    raise STDFError("%s._pack_item(%s) : Unsupported Reference '%s' vs '%s'" % (self.id, FieldKey, Ref, TypeFormat))
            else:
                raise STDFError("%s._pack_item(%s) : Unsupported Reference '%s' vs '%s'" % (self.id, FieldKey, Ref, TypeFormat))
        else:
            K = 1
        fmt = ''
        pkg = b''

        if Type == 'U': # (list of) Unsigned integer(s)
            if TypeMultiplier: ValueMask = Value
            else: ValueMask = [Value]
            if Size.isdigit():
                if Size == '1': fmt = '%sB' % self.endian   # 1 byte unsigned integer(s) 0 .. 255
                elif Size == '2': fmt = '%sH' % self.endian # 2 byte unsigned integer(s) 0 .. 65.535
                elif Size == '4': fmt = '%sI' % self.endian # 4 byte unsigned integer(s) 0 .. 4.294.967.295
                elif Size == '8': fmt = '%sQ' % self.endian # 8 byte unsigned integer(s) 0 .. 18446744073709551615
                else:
                    if TypeMultiplier: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, str(K) + TypeFormat))
                    else: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, TypeFormat))
            else:
                if TypeMultiplier: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, str(K) + TypeFormat))
                else: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, TypeFormat))
            for i in range(K):
                pkg+=struct.pack(fmt, ValueMask[i])
            if self.local_debug:
                if TypeMultiplier: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), str(K) + TypeFormat, len(pkg)))
                else: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), TypeFormat, len(pkg)))
        elif Type == 'I': # (list of) Signed integer(s)
            if TypeMultiplier: ValueMask = Value
            else: ValueMask = [Value]
            if Size.isdigit():
                if Size == '1': fmt = '%sb' % self.endian   # 1 byte signed integer(s) -128 .. +127
                elif Size == '2': fmt = '%sh' % self.endian # 2 byte signed integer(s) -32.768 .. +32.767
                elif Size == '4': fmt = '%si' % self.endian # 4 byte signed integer(s) -2.147.483.648 .. +2.147.483.647
                elif Size == '8': fmt = '%sq' % self.endian # 8 byte signed integer(s) -9.223.372.036.854.775.808 .. +9.223.372.036.854.775.807
                else:
                    if TypeMultiplier: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, str(K) + TypeFormat))
                    else: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, TypeFormat))
            else:
                if TypeMultiplier: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, str(K) + TypeFormat))
                else: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, TypeFormat))
            for i in range(K):
                pkg+=struct.pack(fmt, ValueMask[i])
            if self.local_debug:
                if TypeMultiplier: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), str(K) + TypeFormat, len(pkg)))
                else: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), TypeFormat, len(pkg)))
        elif Type == 'R': # (list of) floating point number(s)
            if TypeMultiplier: ValueMask = Value
            else: ValueMask = [Value]
            if Size.isdigit():
                if Size == '4': fmt = '%sf' % self.endian # (list of) 4 byte floating point number(s) [float]
                elif Size == '8': fmt = '%sd' % self.endian # (list of) 8 byte floating point number(s) [double]
                else:
                    if TypeMultiplier: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, str(K) + TypeFormat))
                    else: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, TypeFormat))
            else:
                if TypeMultiplier: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, str(K) + TypeFormat))
                else: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, TypeFormat))
            for i in range(K):
                pkg+=struct.pack(fmt, ValueMask[i])
            if self.local_debug:
                if TypeMultiplier: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), str(K) + TypeFormat, len(pkg)))
                else: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), TypeFormat, len(pkg)))
        elif Type == 'C': # (list of) string(s)
            if TypeMultiplier: ValueMask = Value
            else: ValueMask = [Value]
            if Size.isdigit() or Size=='f' or Size == 'n':
                for i in range(K):
                    if Size == 'n':
                        pkg += struct.pack('B', len(ValueMask[i]))
                    pkg += ValueMask[i].encode()
            else:
                if TypeMultiplier: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, str(K) + TypeFormat))
                else: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, TypeFormat))
            if self.local_debug:
                if TypeMultiplier: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), str(K) + TypeFormat, len(pkg)))
                else: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), TypeFormat, len(pkg)))
        elif Type == 'S': # (list of) long string(s)
            if TypeMultiplier: ValueMask = Value
            else: ValueMask = [Value]
            if Size=='f' or Size == 'n':
                for i in range(K):
                    if Size == 'n':
                        pkg += struct.pack('%sH' % self.endian, len(ValueMask[i]))
                    pkg += ValueMask[i]
            else:
                if TypeMultiplier: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, str(K) + TypeFormat))
                else: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, TypeFormat))
            if self.local_debug:
                if TypeMultiplier: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), str(K) + TypeFormat, len(pkg)))
                else: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), TypeFormat, len(pkg)))
        elif Type == 'B': # (list of) list of n*8 times '0' or '1'
            if TypeMultiplier: ValueMask = Value
            else: ValueMask = [Value]
            if Size.isdigit() or Size=='f' or Size == 'n':
                for i in range(K):
                    bits_to_pack = len(ValueMask[i])
                    bytes_to_pack = bits_to_pack // 8 # Bits to pack should always be a multiple of 8, guaranteed by set_value
                    if Size == 'n':
                        pkg += struct.pack('B', bytes_to_pack)
                    for Byte in range(bytes_to_pack):
                        byte = 0
                        for Bit in range(8):
                            if ValueMask[i][(Byte * 8) + Bit] == '1':
                                byte+= pow(2, 7-Bit)
                        pkg += struct.pack('B', byte)
            else:
                if TypeMultiplier: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, str(K) + TypeFormat))
                else: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, TypeFormat))
            if self.local_debug:
                if TypeMultiplier: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), str(K) + TypeFormat, len(pkg)))
                else: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), TypeFormat, len(pkg)))

        elif Type == 'D': # (list of) list of bits being '0' or '1'

            if TypeMultiplier: ValueMask = Value
            else: ValueMask = [Value]
            if Size.isdigit() or Size == 'f' or Size == 'n':
                for i in range(K):
                    temp_value = ValueMask[i]
                    bits_to_pack = len(temp_value)
                    bytes_to_pack = int(bits_to_pack) // 8
                    if Size == 'n':
                        pkg += struct.pack('%sH' % self.endian, bits_to_pack)
                    if (bits_to_pack % 8) != 0:
                        bytes_to_pack += 1
                    for Byte in range(bytes_to_pack):
                        byte = 0
                        for Bit in range(8):
                            if (Byte * 8) + Bit < len(temp_value):
                                if temp_value[(Byte * 8) + Bit] == '1':
                                    byte += pow(2, Bit)
                        pkg += struct.pack('B', byte)
            else:
                if TypeMultiplier: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, str(K) + TypeFormat))
                else: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, TypeFormat))
            if self.local_debug:
                if TypeMultiplier: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), str(K) + TypeFormat, len(pkg)))
                else: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), TypeFormat, len(pkg)))

        elif Type == 'N': # a list of nibbles
            if TypeMultiplier: ValueMask = Value
            else: ValueMask = [Value]
            if Size.isdigit() or Size == 'f' or Size == 'n':
                indx = 0
                bytes_pack = []
                for i in range(K): # number of nibble-lists
                    bytes_pack.append(ValueMask[i])
                    if len(bytes_pack) == 2:
                        N_odd = bytes_pack[0] & 0x0F
                        N_even = ( bytes_pack[1] & 0x0F ) << 4
                        byte = N_even | N_odd
                        pkg += struct.pack('B', byte)
                        indx = 0
                        bytes_pack.clear()
                if len(bytes_pack) == 1:
                    byte = bytes_pack[0] & 0x0F
                    pkg += struct.pack('B', byte)

            else:
                if TypeMultiplier: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, str(K) + TypeFormat))
                else: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, TypeFormat))
            if self.local_debug:
                if TypeMultiplier: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), str(K) + TypeFormat, len(pkg)))
                else: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), TypeFormat, len(pkg)))
        elif Type == 'V': # (list of) variable types
            if TypeMultiplier: ValueMask = Value
            else: ValueMask = [Value]
            if Size == 'n':
                v = self.fields[FieldKey]['Value']
                if v == None:
                    raise STDFError("{self.id}._pack_item({FieldKey}) : There is no value set")

                size = len(v)
                # The following codes need a pad value
                pad_for_code = [2,3,5,6,7,8]
                # first 8 elements are size in bytes for B*0, U*1, U*2, U*4, I*1, I*2, I*4, R*4, R*8 
                # rest of the elements are length size in bytes for C*n, B*n, D*n, N*1
                length_for_code = [1, 1, 2, 4, 1, 2, 4, 4, 8, 1, 1, 2, 1]
                
                format_for_code = ['', '%sB', '%sH', '%sI', '%sb', '%sh', '%si', '%sf', '%sd']
                
                bytes_pack = []
                retval = 0

                for i in range(size):

                    code = v[i][0][0]
                    value = v[i][0][1]

                    if code in pad_for_code:
                        pkg += struct.pack('B', 0)
                        
                    pkg += struct.pack('B', code)

                    if code < 9:
                        pkg+=struct.pack(format_for_code[code] % self.endian, value)
                    elif code == 10 or code == 11:    
                        pkg += struct.pack('B', len(value))
                        if code == 10 or code == 11:
                            pkg += value.encode()
                    elif code == 12:
                        temp_value = value
                        bits_to_pack = len(temp_value)
                        bytes_to_pack = int(bits_to_pack) // 8
                        if Size == 'n':
                            pkg += struct.pack('%sH' % self.endian, bits_to_pack)
                        if (bits_to_pack % 8) != 0:
                            bytes_to_pack += 1
                        for Byte in range(bytes_to_pack):
                            byte = 0
                            for Bit in range(8):
                                if (Byte * 8) + Bit < len(temp_value):
                                    if temp_value[(Byte * 8) + Bit] == '1':
                                        byte += pow(2, Bit)
                            pkg += struct.pack('B', byte)
                    elif code == 13:
                        if len(value) == 1:
                            pkg += struct.pack('B', value[0])
                        elif len(value) == 2:
                            N_odd = value[0] & 0x0F
                            N_even = ( value[1] & 0x0F ) << 4
                            byte = N_even | N_odd
                            pkg += struct.pack('B', byte)
                        else:
                            raise STDFError("%s._pack_item(%s) : Only 2 nibbles are supported for code 13 type '%s'" % (self.id, FieldKey, TypeFormat))
                            
            else:
                if TypeMultiplier: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, str(K) + TypeFormat))
                else: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, TypeFormat))
            if self.local_debug:
                if TypeMultiplier: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), str(K) + TypeFormat, len(pkg)))
                else: print("%s._pack_item(%s)\n   '%s' [%s]\n   %s bytes" % (self.id, FieldKey, hexify(pkg), TypeFormat, len(pkg)))
        else:
            if TypeMultiplier: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, str(K) + TypeFormat))
            else: raise STDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldKey, TypeFormat))
        return pkg

    def _unpack_item(self, FieldID):
        if len(self.buffer) == 0:
            self.set_value(FieldID, self.fields[FieldID]['Missing'])
            self.missing_fields += 1
        else:
            FieldKey = ''
            if isinstance(FieldID, int):
                for field in self.fields:
                    if self.fields[field]['#'] == FieldID:
                        FieldKey = field
                if FieldKey == '':
                    raise STDFError("%s._unpack_item(%s) : not a valid integer key" % (self.id, FieldID))
            elif isinstance(FieldID, str):
                if FieldID not in self.fields:
                    raise STDFError("%s._unpack_item(%s) : not a valid string key" % (self.id, FieldID))
                else:
                    FieldKey = FieldID
            else:
                raise STDFError("%s._unpack_item(%s) : not a string or integer key." % (self.id, FieldID))

            Type, Ref, Value = self.get_fields(FieldKey)[1:4]
            if Ref != None:
                K = self.get_fields(Ref)[3]
            Type, Bytes = Type.split("*")
            fmt = ''
            pkg = self.buffer

            if Type.startswith('x'):
                result = []

                if Type == 'xU': # list of unsigned integers
                    if Bytes.isdigit():
                        if Bytes == '1': fmt = self.endian + 'B'   # list of one byte unsigned integers 0..255
                        elif Bytes == '2': fmt = self.endian + 'H' # list of 2 byte unsigned integers 0..65535
                        elif Bytes == '4': fmt = self.endian + 'I' # list of 4 byte unsigned integers 0..4294967295
                        elif Bytes == '8': fmt = self.endian + 'Q' # list of 8 byte unsigned integers 0..18446744073709551615
                        else:
                            raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    else:
                        raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    for _ in range(K):
                        working_buffer = self.buffer[0:int(Bytes)]
                        self.buffer = self.buffer[int(Bytes):]
                        result.append(struct.unpack(fmt, working_buffer)[0])
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), str(K) + '*'.join((Type, Bytes)), result))
                    self.set_value(FieldKey, result)

                elif Type == 'xI': # list of signed integers
                    if Bytes.isdigit():
                        if Bytes == '1': fmt = self.endian + 'b'   # list of one byte signed integers -127..127
                        elif Bytes == '2': fmt = self.endian + 'h' # list of 2 byte signed integers
                        elif Bytes == '4': fmt = self.endian + 'i' # list of 4 byte signed integers
                        elif Bytes == '8': fmt = self.endian + 'q' # list of 8 byte signed integers
                        else:
                            raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    else:
                        raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    for _ in range(K):
                        working_buffer = self.buffer[0:int(Bytes)]
                        self.buffer = self.buffer[int(Bytes):]
                        result.append(struct.unpack(fmt, working_buffer)[0])
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), str(K) + '*'.join((Type, Bytes)), result))
                    self.set_value(FieldKey, result)

                elif Type == 'xR': # list of floating point numbers
                    if Bytes.isdigit():
                        if Bytes == '4': fmt = self.endian + 'f'   # list of 4 byte floating point numbers (float)
                        elif Bytes == '8': fmt = self.endian + 'd' # list of 8 byte floating point numbers (double)
                        else:
                            raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    else:
                        raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    for _ in range(K):
                        working_buffer = self.buffer[0:int(Bytes)]
                        self.buffer = self.buffer[int(Bytes):]
                        result.append(struct.unpack(fmt, working_buffer)[0])
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), str(K) + '*'.join((Type, Bytes)), result))
                    self.set_value(FieldKey, result)

                elif Type == 'xC': # list of strings
                    if Bytes.isdigit():
                        if int(Bytes) <= 255:
                            raise STDFError("%s._unpack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                        else:
                            raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    elif Bytes == 'n':
                        for i in range(K):
                            working_buffer = self.buffer[0:1]
                            self.buffer = self.buffer[1:]
                            n_bytes = struct.unpack('B', working_buffer)[0]
                            if len(self.buffer) < n_bytes:
                                raise STDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldKey, n_bytes, len(self.buffer)))
                            working_buffer = self.buffer[0:n_bytes]
                            self.buffer = self.buffer[n_bytes:]
                            s = working_buffer.decode('utf-8')
                            result.append(s)
                        self.set_value(FieldKey, result)
                        return
                    elif Bytes == 'f':
                        raise STDFError("%s._unpack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    else:
                        raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    for _ in range(K):
                        working_buffer = self.buffer[0:int(Bytes)]
                        self.buffer = self.buffer[int(Bytes):]
                        result.append(struct.unpack(fmt, working_buffer)[0])
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), str(K) + '*'.join((Type, Bytes)), result))
                    self.set_value(FieldKey, result)

                elif Type == 'xB': # list of list of '0' or '1'
                    if Bytes.isdigit():
                        raise STDFError("%s._unpack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    elif Bytes == 'n':
                        raise STDFError("%s._unpack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    elif Bytes == 'f':
                        raise STDFError("%s._unpack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    else:
                        raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), str(K) + '*'.join((Type, Bytes)), result))
                    self.set_value(FieldKey, result)

                elif Type == 'xD': # list of list of '0' or '1'
                    if Bytes.isdigit():
                        raise STDFError("%s._unpack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    elif Bytes == 'n':
                        raise STDFError("%s._unpack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    elif Bytes == 'f':
                        raise STDFError("%s._unpack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    else:
                        raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), str(K) + '*'.join((Type, Bytes)), result))
                    self.set_value(FieldKey, result)

                elif Type == 'xN': # list of a list of nibbles
                    if Bytes.isdigit():
                        result = []
                        bytesCount = math.ceil(K/2)                        
                        working_buffer = self.buffer[0:bytesCount]
                        self.buffer = self.buffer[bytesCount:]
                        for i in range(bytesCount):
                            B = working_buffer[i]
                            N1 = B & 0x0F
                            N2 = (B & 0xF0) >> 4
                            result.append(N1)
                            result.append(N2)
                        if is_odd(K):
                            result = result[:-1]
                            
                    elif Bytes == 'n':
                        raise STDFError("%s._unpack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    elif Bytes == 'f':
                        raise STDFError("%s._unpack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    else:
                        raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), '*'.join((Type, Bytes)), result))
                    self.set_value(FieldKey, result)

                elif Type == 'xV': # list of 2-element tuples
                    if Bytes.isdigit():
                        raise STDFError("%s._unpack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    elif Bytes == 'n':
                        # index of the length_for_code list is the data type code mention in page 64 for GEN_DATA field
                        # first 8 elements are size in bytes for B*0, U*1, U*2, U*4, I*1, I*2, I*4, R*4, R*8 
                        # rest of the elements are length size in bytes for C*n, B*n, D*n, N*1
                        length_for_code = [1, 1, 2, 4, 1, 2, 4, 4, 8, 0, 1, 1, 2, 0]
                        format_for_code = ['', 'B', 'H', 'I', 'b', 'h', 'i', 'f', 'd', '']

                        for i in range(K):
                            code = self.buffer[0]
                            if code == 0:
                                # removing padding byte
                                self.buffer = self.buffer[1:]
                                code = self.buffer[0]
                            self.buffer = self.buffer[1:]
                            
                            value_size = length_for_code[code]

                            working_buffer = self.buffer[0:value_size]
                            self.buffer = self.buffer[value_size:]

                            if code < 9:
                                fmt = self.endian + format_for_code[code] 
                                v = struct.unpack(fmt, working_buffer)[0]
                                
                                if code == 7:
                                    leading = round(v,0)
                                    len_lead = len(str(leading))
                                    v = round(v, 9 - len_lead)

                                sv = [ (code, v) ]
                                self.set_value(FieldKey, sv)

                            elif code == 10 or code == 11:
                                bytes_to_read = struct.unpack('B', working_buffer)[0]
                                working_buffer = self.buffer[0:bytes_to_read]
                                self.buffer = self.buffer[bytes_to_read:]
                                if code == 10 or code == 11:
                                    v = working_buffer.decode('ASCII')
                                    cv = [ (code, v) ]
                                    self.set_value(FieldKey, cv)
                            elif code == 12:
                                n_bits = struct.unpack('%sH' % self.endian, working_buffer)[0]
                                n_bytes = int(n_bits/8)
                                if n_bits % 8 != 0:
                                    n_bytes += 1
                                if len(self.buffer) < n_bytes:
                                    raise STDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldKey, n_bytes, len(self.buffer)))
                                working_buffer = self.buffer[0:n_bytes]
                                self.buffer = self.buffer[n_bytes:]
                                result = ['0'] * n_bits
                                for Byte in range(n_bytes):
                                    B = working_buffer[Byte]
                                    for Bit in range(8):
                                        if ((B >> Bit) & 1) == 1:
                                            result[(Byte * 8) + Bit] = '1'
                                
                                cv = [ (code, result) ]
                                self.set_value(FieldKey, cv)
                            elif code == 13:
                                result = []
                                working_buffer = self.buffer[0:1]
                                self.buffer = self.buffer[1:]
                                B = working_buffer[0]
                                N1 = B & 0x0F
                                N2 = (B & 0xF0) >> 4
                                result.append(N1)
                                result.append(N2)
                                cv = [ (code, result) ]
                                self.set_value(FieldKey, cv)
                                   
                        return        
                    elif Bytes == 'f':
                        raise STDFError("%s._unpack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    else:
                        raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), str(K) + '*'.join((Type, Bytes)), result))
                    self.set_value(FieldKey, result)
                else:
                    raise STDFError("%s._pack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, str(K) + '*'.join((Type, Bytes))))
            else:
                if Type == 'U': # unsigned integer
                    if Bytes.isdigit():
                        if Bytes == '1': fmt = "%sB" % self.endian   # unsigned char
                        elif Bytes == '2': fmt = "%sH" % self.endian # unsigned short
                        elif Bytes == '4': fmt = "%sL" % self.endian # unsigned long
                        elif Bytes == '8': fmt = "%sQ" % self.endian # unsigned long long
                        else:
                            raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                        if len(self.buffer) < int(Bytes):
                            raise STDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldKey, Bytes, len(self.buffer)))
                        working_buffer = self.buffer[0:int(Bytes)]
                        self.buffer = self.buffer[int(Bytes):]
                        result = struct.unpack(fmt, working_buffer)[0]
                    else:
                        raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'." % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), '*'.join((Type, Bytes)), result))
                    self.set_value(FieldID, result)

                elif Type == 'I': # signed integer
                    if Bytes.isdigit():
                        if Bytes == '1': fmt = "%sb" % self.endian   # signed char
                        elif Bytes == '2': fmt = "%sh" % self.endian # signed short
                        elif Bytes == '4': fmt = "%sl" % self.endian # signed long
                        elif Bytes == '8': fmt = "%sq" % self.endian # signed long long
                        else:
                            raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                        if len(self.buffer) < int(Bytes):
                            raise STDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldKey, Bytes, len(self.buffer)))
                        working_buffer = self.buffer[0:int(Bytes)]
                        self.buffer = self.buffer[int(Bytes):]
                        result = struct.unpack(fmt, working_buffer)[0]
                    else:
                        raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'." % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), '*'.join((Type, Bytes)), result))
                    self.set_value(FieldID, result)

                elif Type == 'R': # float
                    if Bytes.isdigit():
                        if Bytes == '4': fmt = "%sf" % self.endian # float
                        elif Bytes == '8': fmt = "%sd" % self.endian # double
                        else:
                            raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                        if len(self.buffer) < int(Bytes):
                            raise STDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldKey, Bytes, len(self.buffer)))
                        working_buffer = self.buffer[0:int(Bytes)]
                        self.buffer = self.buffer[int(Bytes):]
                        result = struct.unpack(fmt, working_buffer)[0]
                    else:
                        raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'." % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), '*'.join((Type, Bytes)), result))
                    leading = round(result,0)
                    len_lead = len(str(leading))
                    result = round(result, 9 - len_lead)
                    self.set_value(FieldID, result)

                elif Type == 'C': # string
                    if Bytes.isdigit(): # C*1 C*2 ...
                        if len(self.buffer) < int(Bytes):
                            raise STDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldKey, Bytes, len(self.buffer)))
                        working_buffer = self.buffer[0:int(Bytes)]
                        self.buffer = self.buffer[int(Bytes):]
                        result = working_buffer.decode()
                    elif Bytes == 'n': # C*n
                        working_buffer = self.buffer[0:1]
                        self.buffer = self.buffer[1:]
                        n_bytes = struct.unpack('B', working_buffer)[0]
                        if len(self.buffer) < n_bytes:
                            raise STDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldKey, n_bytes, len(self.buffer)))
                        working_buffer = self.buffer[0:n_bytes]
                        self.buffer = self.buffer[n_bytes:]
                        result = working_buffer.decode('utf-8')
                    elif Bytes == 'f': # C*f
                        n_bytes = self.get_fields(Ref)[3]
                        if len(self.buffer) < n_bytes:
                            raise STDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldKey, n_bytes, len(self.buffer)))
                        working_buffer = self.buffer[0:n_bytes]
                        self.buffer = self.buffer[n_bytes:]
                        result = working_buffer.decode()
                    else:
                        raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'." % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), '*'.join((Type, Bytes)), result))
                    self.set_value(FieldID, result)

                elif Type == 'B': # list of single character strings being '0' or '1' (max length = 255*8 = 2040 bits)
                    if Bytes.isdigit(): # B*1 B*2 ...
                        if len(self.buffer) < int(Bytes):
                            raise STDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldKey, Bytes, len(self.buffer)))
                        working_buffer = self.buffer[0:int(Bytes)]
                        self.buffer = self.buffer[int(Bytes):]
                        temp = struct.unpack('B' * int(Bytes), working_buffer) # temp is a list (tuple) of 'Bytes' unsigned 1 byte bytes
                        result = ['0'] * (int(Bytes) * 8)
                        for Byte in range(len(temp)):
                            for Bit in range(8):
                                mask = pow(2, 7 - Bit)
                                if (temp[Byte] & mask) == mask :
                                    result[(Byte * 8) + Bit] = '1'
                    elif Bytes == 'n': # B*n
                        working_buffer = self.buffer[0:1]
                        self.buffer = self.buffer[1:]
                        n_bytes = struct.unpack('B', working_buffer)[0]
                        if len(self.buffer) < n_bytes:
                            raise STDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldKey, n_bytes, len(self.buffer)))
                        working_buffer = self.buffer[0:n_bytes]
                        self.buffer = self.buffer[n_bytes:]
                        temp = struct.unpack('B' * n_bytes, working_buffer)
                        result = ['0'] * (n_bytes * 8)
                        for Byte in range(len(temp)):
                            for Bit in range(8):
                                b = (temp[Byte] >> Bit) & 1
                                result[(Byte * 8) + Bit] = str(b)
                    elif Bytes == 'f': # B*f
                        raise STDFError("%s._pack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    else:
                        raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'." % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), '*'.join((Type, Bytes)), result))
                    self.set_value(FieldID, result)

                elif Type == 'D': # list of single character strings being '0' and '1'(max length = 65535 bits)
                    if Bytes.isdigit():
                        raise STDFError("%s._pack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    elif Bytes == 'n':
                        working_buffer = self.buffer[0:2]
                        self.buffer = self.buffer[2:]
                        n_bits = struct.unpack('%sH' % self.endian, working_buffer)[0]
                        n_bytes = int(n_bits/8)
                        if n_bits % 8 != 0:
                            n_bytes += 1
                        if len(self.buffer) < n_bytes:
                            raise STDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldKey, n_bytes, len(self.buffer)))
                        working_buffer = self.buffer[0:n_bytes]
                        self.buffer = self.buffer[n_bytes:]
                        result = ['0'] * n_bits
                        for Byte in range(n_bytes):
                            B = working_buffer[Byte]
                            for Bit in range(8):
                                if ((B >> Bit) & 1) == 1:
                                    result[(Byte * 8) + Bit] = '1'
                    elif Bytes == 'f':
                        raise STDFError("%s._pack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    else:
                        raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'." % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), '*'.join((Type, Bytes)), result))
                    self.set_value(FieldID, result)

                elif Type == 'N': # list of integers
                    if Bytes.isdigit():
                        if len(self.buffer) < int(Bytes):
                            raise STDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldKey, Bytes, len(self.buffer)))
                        working_buffer = self.buffer[0:int(Bytes)]
                        self.buffer = self.buffer[int(Bytes):]
                        brol = []
                        for index in range(len(working_buffer)):
                            B = struct.unpack("%sB" % self.endian, working_buffer[index])[0]
                            N1 = B & 0x0F
                            N2 = (B & 0xF0) >> 4
                            brol.append(N1)
                            brol.append(N2)
                        brol = brol[:int(Bytes)]
                        self.set_value(FieldID, brol)
                    elif Bytes == 'n':
                        raise STDFError("%s._pack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    elif Bytes == 'f':
                        raise STDFError("%s._pack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    else:
                        raise STDFError("%s._unpack_item(%s) : Unsupported type '%s'." % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), '*'.join((Type, Bytes)), result))
                    self.set_value(FieldID, result)

                elif Type == 'V': # tuple (type, value) where type is defined in spec page 62
                    '''
                     0 = B*0 Special pad field
                     1 = U*1 One byte unsigned integer
                     2 = U*2 Two byte unsigned integer
                     3 = U*4 Four byte unsigned integer
                     4 = I*1 One byte signed integer
                     5 = I*2 Two byte signed integer
                     6 = I*4 Four byte signed integer
                     7 = R*4 Four byte floating point number
                     8 = R*8 Eight byte floating point number
                    10 = C*n Variable length ASCII character string (first byte is string length in bytes)
                    11 = B*n Variable length binary data string (first byte is string length in bytes)
                    12 = D*n Bit encoded data (first two bytes of string are length in bits)
                    13 = N*1 Unsigned nibble
                    '''
                    if Bytes.isdigit():
                        raise STDFError("%s._pack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    elif Bytes == 'n':
                        raise STDFError("%s._pack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    elif Bytes == 'f':
                        raise STDFError("%s._pack_item(%s) : Unimplemented type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    else:
                        raise STDFError("%s._pack_item(%s) : Unsupported type '%s'" % (self.id, FieldKey, '*'.join((Type, Bytes))))
                    if self.local_debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldKey, hexify(pkg), '*'.join((Type, Bytes)), result))
                    self.set_value(FieldID, result)

                else:
                    raise STDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldKey, Value, '*'.join((Type, Bytes))))

    def _unpack(self, record):
        '''
        Private method to unpack a record (including header -to-check-record-type-) and set the appropriate values in fields.
        '''
        self.buffer = record

        if self.local_debug: print("%s._unpack(%s) with buffer length = %s" % (self.id, hexify(record), len(record)))

        if record[2] != self.fields['REC_TYP']['Value']:
            raise STDFError("%s_unpack(%s) : REC_TYP doesn't match record" % hexify(record))

        if record[3] != self.fields['REC_SUB']['Value']:
            raise STDFError("%s_unpack(%s) : REC_SUB doesn't match record" % (self.id, hexify(record)))

        items = {}
        for index in self.fields:
            items[self.fields[index]['#']]=index
        for index in range(len(items)):
            self._unpack_item(items[index])

    def Vn_decode(self, BUFF, endian):
        '''
        This method unpacks a V*n field
        '''
        buffer_remainer = BUFF
        buffer_endian = endian
        retval = {}
        index = 1

        if buffer_endian not in ['<', '>']:
            raise STDFError("Vn_decode() : unsupported endian '%s'" % buffer_endian)

        return buffer_remainer #TODO: implement the tests for decoding of the V*n type and remove this bypass return statement

        while len(buffer_remainer) != 0:
            working_buffer = buffer_remainer[0:1]
            buffer_remainer = buffer_remainer[1:]
            local_type, = struct.unpack('b', working_buffer) # type identifier
            if local_type == 0: # B*0 Special pad field, of length 0
                pass
            elif local_type == 1: # U*1 One byte unsigned integer
                working_buffer = buffer_remainer[0:1]
                buffer_remainer = buffer_remainer[1:]
                retval[index]['Type'] = 'U*1'
                retval[index]['Value'], = struct.unpack("%sB" % buffer_endian, working_buffer)
                index += 1
            elif local_type == 2: # U*2 Two byte unsigned integer
                working_buffer = buffer_remainer[0:2]
                buffer_remainer = buffer_remainer[2:]
                retval[index]['Type'] = 'U*2'
                retval[index]['Value'], = struct.unpack("%sH" % buffer_endian, working_buffer)
                index += 1
            elif local_type == 3: # U*4 Four byte unsigned integer
                working_buffer = buffer_remainer[0:4]
                buffer_remainer = buffer_remainer[4:]
                retval[index]['Type'] = 'U*4'
                retval[index]['Value'], = struct.unpack("%sI" % buffer_endian, working_buffer)
                index += 1
            elif local_type == 4: # I*1 One byte signed integer
                working_buffer = buffer_remainer[0:1]
                buffer_remainer = buffer_remainer[1:]
                retval[index]['Type'] = 'I*1'
                retval[index]['Value'], = struct.unpack("%sb" % buffer_endian, working_buffer)
                index += 1
            elif local_type == 5: # I*2 Two byte signed integer
                working_buffer = buffer_remainer[0:2]
                buffer_remainer = buffer_remainer[2:]
                retval[index]['Type'] = 'I*2'
                retval[index]['Value'], = struct.unpack("%sh" % buffer_endian, working_buffer)
                index += 1
            elif local_type == 6: # I*4 Four byte signed integer
                working_buffer = buffer_remainer[0:4]
                buffer_remainer = buffer_remainer[4:]
                retval[index]['Type'] = 'I*4'
                retval[index]['Value'], = struct.unpack("%si" % buffer_endian, working_buffer)
                index += 1
            elif local_type == 7: # R*4 Four byte floating point number
                working_buffer = buffer_remainer[0:4]
                buffer_remainer = buffer_remainer[4:]
                retval[index]['Type'] = 'R*4'
                retval[index]['Value'], = struct.unpack("%sf" % buffer_endian, working_buffer)
                index += 1
            elif local_type == 8: # R*8 Eight byte floating point number
                working_buffer = buffer_remainer[0:8]
                buffer_remainer = buffer_remainer[8:]
                retval[index]['Type'] = 'R*8'
                retval[index]['Value'], = struct.unpack("%sd" % buffer_endian, working_buffer)
                index += 1
            elif local_type == 10: # C*n Variable length ASCII character string (first byte is string length in bytes)
                working_buffer = buffer_remainer[0:1]
                buffer_remainer = buffer_remainer[1:]
                Cn_length, = struct.unpack("%sB" % buffer_endian, working_buffer)
                working_buffer = buffer_remainer[0:Cn_length]
                buffer_remainer = buffer_remainer[Cn_length:]
                retval[index]['Type'] = 'C*n'
                retval[index]['Value'] = working_buffer
                index += 1
            elif local_type == 11: # B*n Variable length binary data string (first byte is string length in bytes)
                working_buffer = buffer_remainer[0:1]
                buffer_remainer = buffer_remainer[1:]
                Bn_length, = struct.unpack("%sB" % buffer_endian, working_buffer)
                working_buffer = buffer_remainer[0:Bn_length]
                buffer_remainer = buffer_remainer[Bn_length:]
                retval[index]['Type'] = 'B*n'
                retval[index]['Value'] = working_buffer
                index += 1
            elif local_type == 12: # D*n Bit encoded data (first two bytes of string are length in bits)
                working_buffer = buffer_remainer[0:2]
                buffer_remainer = buffer_remainer[2:]
                Dn_length = struct.unpack("%sH" % buffer_endian, working_buffer)
                working_buffer = buffer_remainer[0:Dn_length]
                buffer_remainer = buffer_remainer[Dn_length:]
                retval[index]['Type'] = 'D*n'
                retval[index]['Value'] = working_buffer
                index += 1
            elif local_type == 13: # N*1 Unsigned nibble
                working_buffer = buffer_remainer[0:1]
                buffer_remainer = buffer_remainer[1:]
                retval[index]['Type'] = 'N*1'
                retval[index]['Value'], = struct.unpack("%sB" % buffer_endian, working_buffer) & 0x0F
                index += 1
            else:
                raise STDFError("Vn_decode() : unsupported type '%d' in V*n" % local_type)
        return retval

    def __len__(self):
        retval = 0
        for field in self.fields:
            retval += self._type_size(field)
        return retval


    def __repr__(self):
        '''
        Method that packs the whole record and returns the packed version.
        '''
        sequence = {}
        sequence_wo_opt_data = {}
        use_optional_data = False
        is_optional_flag = False
        header = b''
        body = b''

        # When a record contains the OPT_FLAG, the fields after OPT_FLAG are 
        # not mandatory always. They have to be set in the first instance of 
        # the record as "default values" and after that if there are no changes
        # they can be skipped (including the OPT_FLAG field)
        for field in self.fields:
            sequence[self.fields[field]['#']] = field
            if field == 'OPT_FLAG':
                is_optional_flag = True
                if self.fields[field]['Value'] != None:
                    sequence_wo_opt_data[self.fields[field]['#']] = field                
                continue
            if is_optional_flag and self.fields[field]['Value'] != None:
                use_optional_data = True
            if is_optional_flag == False and use_optional_data == False:
                sequence_wo_opt_data[self.fields[field]['#']] = field                
        
        if is_optional_flag and use_optional_data == False:
            sequence = sequence_wo_opt_data
            
        # pack the body
        for item in range(3, len(sequence)):
            body += self._pack_item(sequence[item])
        self._update_rec_len()

        # check the body length against the REC_LEN
        if self.get_fields('REC_LEN')[3] != len(body):
            raise STDFError("%s.pack() length error %s != %s" % (self.id, self.get_fields('REC_LEN')[3], len(body)))

        # pack the header
        for item in range(0, 3):
            header += self._pack_item(sequence[item])

        # assemble the record
        retval = header + body

        if self.local_debug: print("%s.pack()\n   '%s'\n   %s bytes" % (self.id, hexify(retval), len(retval)))
        return retval


    def __str__(self):
        '''
        Method used by print to print the STDF record.
        '''
        time_fields = ['MOD_TIM', 'SETUP_T', 'START_T', 'FINISH_T']
        sequence = {}
        for field in self.fields:
            sequence[self.fields[field]['#']] = field
        retval = "   %s (%d,%d) @ %s\n" % (self.id, self.get_value('REC_TYP'), self.get_value('REC_SUB'), self.version)
        for field in sorted(sequence):
            retval += "      %s = '%s'" % (sequence[field], self.fields[sequence[field]]['Value'])
            retval += " [%s] (%s)" %  (self.fields[sequence[field]]['Type'], self.fields[sequence[field]]['Text'].strip())
            if self.fields[sequence[field]]['Ref'] != None:
                retval += " -> %s" % self.fields[sequence[field]]['Ref']
            if sequence[field] in time_fields:
                local_unix_time_stamp = float(self.fields[sequence[field]]['Value'])
                retval += " = %s" % _stdf_time_field_value_to_string(float(self.fields[sequence[field]]['Value']))
            retval += "\n"
        return retval

    def to_dict(self, include_missing_values=False):
        '''
        Method used by convert the record to dict
        '''
        time_fields = ['MOD_TIM', 'SETUP_T', 'START_T', 'FINISH_T']
        sequence = {}
        for field in self.fields:
            sequence[self.fields[field]['#']] = field
        return {sequence[field]: self.fields[sequence[field]]['Value']
                for field in sequence}

    def to_atdf(self):

        sequence = {}
        header = ''
        body = ''

        header = self.id + ':'
        
        time_fields = ['MOD_TIM', 'SETUP_T', 'START_T', 'FINISH_T']

        if self.id == 'RDR':
            skip_fields = ['NUM_BINS']
        else:            
            skip_fields = ['INDX_CNT', 'SITE_CNT']
            
        if self.id == 'FAR':
            body = 'A|4|2|U'
        else:
            sequence = {}
            for field in self.fields:
                sequence[self.fields[field]['#']] = field
            for field in sorted(sequence)[3:]:
#                Skip the first 3 fields : REC_LEN, REC_TYPE, REC_SUB.
#                They are not applicable for the ASCII based ATDF file format
                if sequence[field] in time_fields:
                    
                    timestamp = self.fields[sequence[field]]['Value']
#                    ATDF spec page 9:
#                    Insignificant leading zeroes in all numbers are optional.
                    t = time.strftime("%-H:%-M:%-S %-d-%b-%Y", time.gmtime(timestamp))
                    body += "%s|" % (t.upper())
                        
                elif sequence[field] in skip_fields:
#                    Some fields must be skipped like number of elements in array:
#                    like INDX_CNT in PGR reconrd
                    pass
                else:
                    value = self.fields[sequence[field]]['Value']
                    if type(value) == list:
                        
                        Type = self.fields[sequence[field]]['Type']
                        Type, Bytes = Type.split("*")
                        if Type == 'B':
                            # converting bits into HEX values
                            vals = []
                            val = 0
                            x = 0
                            bit = 7
                            for i in range(len(value)):
                                el = value[i]
                                val = val | ( int(el)<<bit)
                                bit -= 1
                                if i != 0 and i % 7 == 0:
                                    vals.append(val)
                                    bit = 7
                            for elem in vals:
                                body += hex(elem)
                            body += "|"
                        else:
                            # For the following fields which in some recoreds are
                            # single value and for some are lists :
                            # PMR_INDX from PMR as value, but list in PGR
                            for elem in value:
                                body += "%s," % elem
                            body = body[:-1] 
                            body += "|"
                    else:
                        body += "%s|" % (value)
            body = body[:-1] 

        # assemble the record
        retval = header + body

        if self.local_debug: print("%s._to_atdf()\n   '%s'\n" % (self.id, retval))
        return retval

    def reset(self):
        '''
        Reset all fields with None value
        '''
        for field in self.fields:
            if field == 'REC_TYP' or field == 'REC_SUB': continue
            self.fields[field]['Value'] = None

    '''
    This function returns the hexified version of input
    the input can be a byte array or a string, but the output is always a string.
    '''
    def hexify(self, input):
        retval = ''
        if isinstance(input, bytes):
            for b in range(len(input)):
                retval += hex(input[b]).upper().replace('0X', '0x')
        elif isinstance(input, str):
            for i in input:
                retval += hex(ord(i)).upper().replace('0X', '0x')
        else:
            raise Exception("input type needs to be bytes or str.")
        return retval

    def sys_endian(self):
        '''
        This function determines the endian of the running system.
        '''
        if sys.byteorder == 'little':
            return '<'
        return '>'
    
    def sys_cpu(self):
        if self.sys_endian()=='<':
            return 2
        return 1
    
    # Removal of dependency on ATE.utils.DT: DT().epoch and DT.__repr__
    def _missing_stdf_time_field_value(self) -> int:
        return int(time.time()) # used to be DT().epoch, which returned time.time(). note that we need an 32bit unsigned integer to allow de-/serialization without data loss
        
class ASR(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = ''
        self.local_debug = False
        # Version
        if version==None or version=='V4':
            self.version = 'V4'
            self.info=    '''
Algorithm Specification Record (V4, Memory:2010.1)
--------------------------------------------------

Function:
    This record is used to store the algorithms that are applied during a memory test. Table 11 Algorithm Specification Record (ASR) Record

Frequency:
    * Once per unique memory test specification.

Location:
    It can occur after all the Memory Model Records(MMRs) and before any Test specific records
    e.g. Parametric Test Record (PTR), Functional Test Record (FTRs), Scan Test Record (STR) and Memory Test Record (MTRs).
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2'  , 'Ref' :       None, 'Value' : None, 'Text' : 'Bytes of data following header                      ', 'Missing' : None, 'Note' : ''},
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1'  , 'Ref' :       None, 'Value' :    0, 'Text' : 'Record type                                         ', 'Missing' : None, 'Note' : ''},
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1'  , 'Ref' :       None, 'Value' :   20, 'Text' : 'Record sub-type                                     ', 'Missing' : None, 'Note' : ''},
                'ASR_IDX'  : {'#' :  3, 'Type' : 'U*2'  , 'Ref' :       None, 'Value' : None, 'Text' : 'Unique identifier for this ASR record               ', 'Missing' :    0, 'Note' : ''},
                'STRT_IDX' : {'#' :  4, 'Type' : 'U*1'  , 'Ref' :       None, 'Value' : None, 'Text' : 'Cycle Start index flag                              ', 'Missing' :    0, 'Note' : ''},
                'ALGO_CNT' : {'#' :  5, 'Type' : 'U*1'  , 'Ref' :       None, 'Value' : None, 'Text' : 'count (k) of Algorithms descriptions                ', 'Missing' :    0, 'Note' : ''},
                'ALGO_NAM' : {'#' :  6, 'Type' : 'xC*n' , 'Ref' : 'ALGO_CNT', 'Value' : None, 'Text' : 'Array of Names of the Algorithms                    ', 'Missing' :   [], 'Note' : ''},
                'ALGO_LEN' : {'#' :  7, 'Type' : 'xC*n' , 'Ref' : 'ALGO_CNT', 'Value' : None, 'Text' : 'Array of Complexity of algorithm  (e.g., 13N)       ', 'Missing' :   [], 'Note' : ''},
                'FILE_ID'  : {'#' :  8, 'Type' : 'xC*n' , 'Ref' : 'ALGO_CNT', 'Value' : None, 'Text' : 'Array of Name of the file with algorithm description', 'Missing' :   [], 'Note' : ''},
                'CYC_BGN'  : {'#' :  9, 'Type' : 'xU*8' , 'Ref' : 'ALGO_CNT', 'Value' : None, 'Text' : 'Array of Starting cycle number for the Algorithms   ', 'Missing' :   [], 'Note' : ''},
                'CYC_END'  : {'#' : 10, 'Type' : 'xU*8' , 'Ref' : 'ALGO_CNT', 'Value' : None, 'Text' : 'Array of End Cycle number for the algorithm         ', 'Missing' :   [], 'Note' : ''}
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)

class BSR(STDR):
    def __init__(self, version=None, endian=None, record = None):
        self.id = 'BSR'
        self.local_debug = False
        if version==None or version=='V4':
            self.version = 'V4'
            self.info=    '''
Bit stream Specification Record (V4, Memory:2010.1)
---------------------------------------------------

Function:
    This record is used to enable string bit stream data from the memories.
    This record defines the format of the bit stream in which the data can be recorded in Memory Test Record (MTR).
    The bit streams are stored as stream of clusters for compaction. i.e. only the data words that have meaningful
    information are stored in the stream. Each cluster is defined as the starting address where the meaningful
    information starts followed by the count of words with meaningful information followed by the words themselves.

Frequency:
    Once per memory Algorithm.

Location:
    It can occur after all the Memory Model Records(MMRs) and before any Test specific records e.g.
    Parametric Test Record (PTR), Functional Test Record (FTRs), Scan Test Record (STR) and Memory Test Record (MTRs).
'''
            self.fields = {
                'REC_LEN'  : {'#' : 0, 'Type' : 'U*2' , 'Ref' : None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' : None},
                'REC_TYP'  : {'#' : 1, 'Type' : 'U*1' , 'Ref' : None, 'Value' :    1, 'Text' : 'Record type                           ', 'Missing' : None},
                'REC_SUB'  : {'#' : 2, 'Type' : 'U*1' , 'Ref' : None, 'Value' :   97, 'Text' : 'Record sub-type                       ', 'Missing' : None},
                'BSR_IDX'  : {'#' : 3, 'Type' : 'U*2' , 'Ref' : None, 'Value' : None, 'Text' : 'Unique ID for this Bit stream         ', 'Missing' :    0},
                'BIT_TYP'  : {'#' : 4, 'Type' : 'U*1' , 'Ref' : None, 'Value' : None, 'Text' : 'Meaning of bits in the stream         ', 'Missing' :    0},
                'ADDR_SIZ' : {'#' : 5, 'Type' : 'U*1' , 'Ref' : None, 'Value' : None, 'Text' : 'Address field size [1,2,4 or 8]       ', 'Missing' :    0},
                'WC_SIZ'   : {'#' : 6, 'Type' : 'U*1' , 'Ref' : None, 'Value' : None, 'Text' : 'Word Count Field Size [1,2,4 or 8]    ', 'Missing' :    0},
                'WRD_SIZ'  : {'#' : 7, 'Type' : 'U*2' , 'Ref' : None, 'Value' : None, 'Text' : 'Number of bits used in the word field ', 'Missing' :    0}
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)

class CDR(STDR):
    def __init__(self, version=None, endian=None, record = None):
        self.id = 'CDR'
        self.local_debug = False
        if version==None or version=='V4':
            self.version = 'V4'
            self.info=    '''
Chain Description Record (V4-2007)
----------------------------------

Function:
    This record contains the description of a scan chain in terms of its input, output, number of cell and clocks.
    Each CDR record contains description of exactly one scan chain. Each CDR is uniquely identified by an index.

Frequency:
    ?!?

Location:
    ?!?
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2',  'Ref' : None,       'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' : None},
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1',  'Ref' : None,       'Value' :    1, 'Text' : 'Record type                           ', 'Missing' : None},
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1',  'Ref' : None,       'Value' :   94, 'Text' : 'Record sub-type                       ', 'Missing' : None},
                'CONT_FLG' : {'#' :  3, 'Type' : 'B*1',  'Ref' : None,       'Value' : None, 'Text' : 'Continuation CDR record follow (if!=0)', 'Missing' : 0},
                'CDR_INDX' : {'#' :  4, 'Type' : 'U*2',  'Ref' : None,       'Value' : None, 'Text' : 'SCR Index                             ', 'Missing' : 0},
                'CHN_NAM'  : {'#' :  5, 'Type' : 'C*n',  'Ref' : None,       'Value' : None, 'Text' : 'Chain Name                            ', 'Missing' : None},
                'CHN_LEN'  : {'#' :  6, 'Type' : 'U*4',  'Ref' : None,       'Value' : None, 'Text' : 'Chain Length (cells in chain)         ', 'Missing' : 0},
                'SIN_PIN'  : {'#' :  7, 'Type' : 'U*2',  'Ref' : None,       'Value' : None, 'Text' : "PMR index of the chain's Scan In Sig  ", 'Missing' : 0},
                'SOUT_PIN' : {'#' :  8, 'Type' : 'U*2',  'Ref' : None,       'Value' : None, 'Text' : "PMR index of the chain's Scan Out Sig ", 'Missing' : 0},
                'MSTR_CNT' : {'#' :  9, 'Type' : 'U*1',  'Ref' : None,       'Value' : None, 'Text' : 'Count (m) of master clock pins        ', 'Missing' : 0},
                'M_CLKS'   : {'#' : 10, 'Type' : 'xU*2', 'Ref' : 'MSTR_CNT', 'Value' : None, 'Text' : 'Arr of PMR indses for the master clks ', 'Missing' : []},
                'SLAV_CNT' : {'#' : 11, 'Type' : 'U*1',  'Ref' : None,       'Value' : None, 'Text' : 'Count (n) of slave clock pins         ', 'Missing' : 0},
                'S_CLKS'   : {'#' : 12, 'Type' : 'xU*2', 'Ref' : 'SLAV_CNT', 'Value' : None, 'Text' : 'Arr of PMR indxes for the slave clks  ', 'Missing' : []},
                'INV_VAL'  : {'#' : 13, 'Type' : 'U*1',  'Ref' : None,       'Value' : None, 'Text' : '0: No Inversion, 1: Inversion         ', 'Missing' : 0},
                'LST_CNT'  : {'#' : 14, 'Type' : 'U*2',  'Ref' : None,       'Value' : None, 'Text' : 'Count (k) of scan cells               ', 'Missing' : 0},
                'CELL_LST' : {'#' : 15, 'Type' : 'xS*n', 'Ref' : 'LST_CNT',  'Value' : None, 'Text' : 'Array of Scan Cell Names              ', 'Missing' : []},
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)

class CNR(STDR):
    def __init__(self, version=None, endian=None, record = None):
        self.id = 'CNR'
        self.local_debug = False
        if version==None or version=='V4':
            self.version = 'V4'
            self.info=    '''
Cell Name Record (V4-2007)
--------------------------

Function:
    This record is used to store the mapping from Chain and Bit position to the Cell/FlipFlop name.
    A CNR record should be created for each Cell for which a name mapping is required.
    Typical usage would be to create a record for each failing cell/FlipFlop.
    A CNR with new mapping for a chain and bit position would override the previous mapping.

Frequency:

Location:
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2' , 'Ref' : None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' : None},
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1' , 'Ref' : None, 'Value' :    1, 'Text' : 'Record type                           ', 'Missing' : None},
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1' , 'Ref' : None, 'Value' :   92, 'Text' : 'Record sub-type                       ', 'Missing' : None},
                'CHN_NUM'  : {'#' :  2, 'Type' : 'U*2' , 'Ref' : None, 'Value' : None, 'Text' : 'Chain number. (cfr STR:CHN_NUM)       ', 'Missing' :    0},
                'BIT_POS'  : {'#' :  2, 'Type' : 'U*4' , 'Ref' : None, 'Value' : None, 'Text' : 'Bit position in the chain             ', 'Missing' :    0},
                'CELL_NAM' : {'#' :  2, 'Type' : 'S*n' , 'Ref' : None, 'Value' : None, 'Text' : 'Scan Cell Name                        ', 'Missing' :   ''}
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)


class FSR(STDR):
    def __init__(self, version=None, endian=None, record = None):
        self.id = 'FSR'
        self.local_debug = False
        if version==None or version == 'V4':
            self.version = 'V4'
            self.info=    '''
Frame Specification Record (V4, Memory:2010.1)
----------------------------------------------

Function:
    Frame Specification Record (FSR) is used to define a frame structure that can be used to store the fail data in a frame format.
    In most of the embedded memory test architecture available in the industry, the data is communicated from the BIST controllers
    to ATE in a serial frame format. Each vendor has its own frame format. So to deal with different frame format from various vendors
    the FSR allows encapsulating one or more specific frame definitions used within the STDF file.

Frequency:
    * Once per memory Algorithm

Location:
    It can occur after all the Memory Model Records(MMRs) and before any Test specific records e.g. Parametric Test Record (PTR),
    Functional Test Record (FTRs), Scan Test Record (STR) and Memory Test Record (MTRs).
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' : None},
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1', 'Ref' : None, 'Value' :    0, 'Text' : 'Record type                           ', 'Missing' : None},
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1', 'Ref' : None, 'Value' :   20, 'Text' : 'Record sub-type                       ', 'Missing' : None},
                'BSR_IDX'  : {'#' :  2, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Unique ID this Bit stream spec.       ', 'Missing' :    0},
                'BIT_TYP'  : {'#' :  2, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'Meaning of bits in the stream         ', 'Missing' :    0},
                'ADDR_SIZ' : {'#' :  2, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'Address field size [1,2,4 & 8] are ok ', 'Missing' :    0},
                'WC_SIZ'   : {'#' :  2, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : 'Word Count Field Size [1,2,4 & 8]     ', 'Missing' :    0},
                'WRD_SIZ'  : {'#' :  2, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Number of bits in word field          ', 'Missing' :    0}
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)


class IDR(STDR):
    def __init__(self, version=None, endian=None, record = None):
        self.id = 'IDR'
        self.local_debug = False
        if version==None or version=='V4':
            self.version = 'V4'
            self.info=    '''
Instance Description Record (V4, Memory:2010.1)
-----------------------------------------------

Function:
    This record is used to store the information for a memory instance within a design. It contains a
    reference to the model records which define the design information for this specific memory instance.

Frequency:
    * Once per memory instance

Location:
    It can occur after all the Memory Controller Records(MCRs) and before Memory Model Records (MMRs)
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' : None},
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1', 'Ref' : None, 'Value' :    0, 'Text' : 'Record type                           ', 'Missing' : None},
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1', 'Ref' : None, 'Value' :   20, 'Text' : 'Record sub-type                       ', 'Missing' : None},
                'INST_IDX' : {'#' :  3, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Unique index of this IDR              ', 'Missing' : None}, # Obligatory
                'INST_NAM' : {'#' :  4, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Name of the Instance                  ', 'Missing' :   ''},
                'REF_COD'  : {'#' :  5, 'Type' : 'U*1', 'Ref' : None, 'Value' : None, 'Text' : '0=Wafer Notch based, 1=Pkg ref        ', 'Missing' : None},
                'ORNT_COD' : {'#' :  6, 'Type' : 'C*2', 'Ref' : None, 'Value' : None, 'Text' : 'Orientation of Instance               ', 'Missing' : '  '},
                'MDL_FILE' : {'#' :  7, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Pointer to file describing model      ', 'Missing' :   ''},
                'MDL_REF'  : {'#' :  8, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Reference to the model record         ', 'Missing' : None}
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)

class MCR(STDR):
    def __init__(self, version=None, endian=None, record = None):
        self.id = 'MCR'
        self.local_debug = False
        if version == 'V4':
            self.version = version
            self.info=    '''
Memory Controller Record (V4, Memory:2010.1)
--------------------------------------------

Function:
    This record is used to store information about an embedded memory controller in a design.
    There is one MCR record in an STDF file for each controller in a design.
    These records are referenced by the top level Memory Structure Record (MSR) through its CTRL_LST field.

Frequency:
    * Once per controller in the design.

Location:
    It can occur after all the Memory Structure Records(MSRs) and before Instance Description Records (IDRs)
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2' , 'Ref' :       None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' : None},
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1' , 'Ref' :       None, 'Value' :    1, 'Text' : 'Record type                           ', 'Missing' : None},
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1' , 'Ref' :       None, 'Value' :  100, 'Text' : 'Record sub-type                       ', 'Missing' : None},
                'CTRL_IDX' : {'#' :  3, 'Type' : 'U*2' , 'Ref' :       None, 'Value' : None, 'Text' : 'Index of this memory controller record', 'Missing' : None},
                'CTRL_NAM' : {'#' :  4, 'Type' : 'C*n' , 'Ref' :       None, 'Value' : None, 'Text' : 'Name of the controller                ', 'Missing' :   ''},
                'MDL_FILE' : {'#' :  5, 'Type' : 'C*n' , 'Ref' :       None, 'Value' : None, 'Text' : 'Pointer to the file describing model  ', 'Missing' :   ''},
                'INST_CNT' : {'#' :  6, 'Type' : 'U*2' , 'Ref' :       None, 'Value' : None, 'Text' : 'Count of INST_INDX array              ', 'Missing' :    0},
                'INST_LST' : {'#' :  7, 'Type' : 'xU*2', 'Ref' : 'INST_CNT', 'Value' : None, 'Text' : 'Array of memory instance indexes      ', 'Missing' :   []}
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)



class MMR(STDR):
    def __init__(self, version=None, endian=None, record = None):
        self.id = 'MMR'
        self.local_debug = False
        if version==None or version=='V4':
            self.version = 'V4'
            self.info=    '''
Memory Model Record (V4, Memory:2010.1)
---------------------------------------

Function:
    This record is used to store the memory model information in STDF.
    The record allows storing the logic level information of the model.
    It does not have any fields to store the physical information except height and width.
    The physical information can be optionally linked to the record through a reference to the file.

Frequency:
    Once per memory model.

Location:
    It can occur after all the Instance Description Records(IDRs) and before any Frame Specification Records (FSRs),
    Bit Stream Specification Records (BSRs) and any Test specific records e.g. Parametric Test Record (PTR),
    Functional Test Record (FTRs), Scan Test Record (STR) and Memory Test Record (MTRs).
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2',  'Ref' :       None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' : None},
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1',  'Ref' :       None, 'Value' :    1, 'Text' : 'Record type                           ', 'Missing' : None},
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1',  'Ref' :       None, 'Value' :   95, 'Text' : 'Record sub-type                       ', 'Missing' : None},
                'ASR_IDX'  : {'#' :  3, 'Type' : 'U*2',  'Ref' :       None, 'Value' : None, 'Text' : 'Unique identifier for this ASR record ', 'Missing' : None},
                'STRT_IDX' : {'#' :  4, 'Type' : 'U*1',  'Ref' :       None, 'Value' : None, 'Text' : 'Cycle Start index flag                ', 'Missing' : None},
                'ALGO_CNT' : {'#' :  5, 'Type' : 'U*1',  'Ref' :       None, 'Value' : None, 'Text' : 'count (k) of Algorithms descriptions  ', 'Missing' :    0},
                'ALGO_NAM' : {'#' :  6, 'Type' : 'xC*n', 'Ref' : 'ALGO_CNT', 'Value' : None, 'Text' : 'Array of Names Name of the Algorithm  ', 'Missing' :   []},
                'ALGO_LEN' : {'#' :  7, 'Type' : 'xC*n', 'Ref' : 'ALGO_CNT', 'Value' : None, 'Text' : 'Array of Complexity of algorithm      ', 'Missing' :   []},
                'FILE_ID'  : {'#' :  8, 'Type' : 'xC*n', 'Ref' : 'ALGO_CNT', 'Value' : None, 'Text' : 'Array of Name of the file with descr. ', 'Missing' :   []},
                'CYC_BGN'  : {'#' :  9, 'Type' : 'xU*8', 'Ref' : 'ALGO_CNT', 'Value' : None, 'Text' : 'Array of Starting cycle number        ', 'Missing' :   []},
                'CYC_END'  : {'#' : 10, 'Type' : 'xU*8', 'Ref' : 'ALGO_CNT', 'Value' : None, 'Text' : 'Array of End Cycle number             ', 'Missing' :   []}
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)




class MSR(STDR):
    def __init__(self, version=None, endian=None, record = None):
        self.id = 'MSR'
        self.local_debug = False
        if version == 'V4':
            self.version = 'V4'
            self.info=    '''
Memory Structure Record (V4, Memory:2010.1)
-------------------------------------------

Function:
    This record is the top level record for storing Memory design information.
    It supports both the direct access memories as well as the embedded memories controlled by
    embedded controllers. For embedded memories it contains the references to the controllers
    and for direct access memories it contains the references to the memory instances.

Frequency:
    * One for each STDF file for a design

Location:
    It can occur anytime after Retest Data Record (RDR) if no Site Description Record(s)
    are present, otherwise after all the SDRs. This record must occur before Memory Controller
    Records (MCRs) and Instance Description Records (IDRs)
'''
            self.fields = {
                'REC_LEN'  : {'#' : 0, 'Type' :  'U*2', 'Ref' :       None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' : None},
                'REC_TYP'  : {'#' : 1, 'Type' :  'U*1', 'Ref' :       None, 'Value' :    1, 'Text' : 'Record type                           ', 'Missing' : None},
                'REC_SUB'  : {'#' : 2, 'Type' :  'U*1', 'Ref' :       None, 'Value' :   99, 'Text' : 'Record sub-type                       ', 'Missing' : None},
                'NAME'     : {'#' : 3, 'Type' :  'C*n', 'Ref' :       None, 'Value' : None, 'Text' : 'Name of the design under test         ', 'Missing' :   ''},
                'FILE_NAM' : {'#' : 4, 'Type' :  'C*n', 'Ref' :       None, 'Value' : None, 'Text' : 'Filename containing design information', 'Missing' :   ''},
                'CTRL_CNT' : {'#' : 5, 'Type' :  'U*2', 'Ref' :       None, 'Value' : None, 'Text' : 'Count (k) of controllers in the design', 'Missing' :    0},
                'CTRL_LST' : {'#' : 6, 'Type' : 'xU*2', 'Ref' : 'CTRL_CNT', 'Value' : None, 'Text' : 'Array of controller record indexes    ', 'Missing' :   []},
                'INST_CNT' : {'#' : 7, 'Type' :  'U*2', 'Ref' :       None, 'Value' : None, 'Text' : 'Count(m) of Top level memory instances', 'Missing' :    0},
                'INST_LST' : {'#' : 8, 'Type' : 'xU*2', 'Ref' : 'INST_CNT', 'Value' : None, 'Text' : 'Array of Instance record indexes      ', 'Missing' :   []}
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)

class MTR(STDR):
    def __init__(self, version=None, endian=None, record=None,  BSR__ADDR_SIZ=None, BSR__WC_SIZ=None):
        self.id = 'MTR'
        self.local_debug = False
        if version == 'V4':
            self.version = version
            self.info=    '''
Memory Test Record (V4, Memory:2010.1)
--------------------------------------

Function:
    This is the record is used to store fail data along with capture test conditions and references to test test descriptions.
    It allows the fail data to be stored in various formats describe below using the field highlighting

Frequency:
    Number of memory tests times records required to log the fails for the test (counting continuation record)

Location:
    It can occur after all the memory design specific records i.e. any Memory Structure Record (MSR),
    any Memory Controller Records (MCRs), any Memory Instance Records (IDRs), any Memory Model Records(MMRs),
    any Algorithms Specification Records (ASRs), any Frame Specification Records (FSRs) and any Bitstream Specificaion Records (BSRs)
'''
            #TODO: Implement "Field Presense Expression" (see PTR record on how)
            self.fields = {
                'REC_LEN'   : {'#' :  0, 'Type' :  'U*2', 'Ref' :                     None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' :    None},
                'REC_TYP'   : {'#' :  1, 'Type' :  'U*1', 'Ref' :                     None, 'Value' :   15, 'Text' : 'Record type                           ', 'Missing' :    None},
                'REC_SUB'   : {'#' :  2, 'Type' :  'U*1', 'Ref' :                     None, 'Value' :   40, 'Text' : 'Record sub-type                       ', 'Missing' :    None},
                'CONT_FLG'  : {'#' :  3, 'Type' :  'B*1', 'Ref' :                     None, 'Value' : None, 'Text' : 'Continuation flag                     ', 'Missing' :    None},
                'TEST_NUM'  : {'#' :  4, 'Type' :  'U*4', 'Ref' :                     None, 'Value' : None, 'Text' : 'Test number                           ', 'Missing' :    None},
                'HEAD_NUM'  : {'#' :  5, 'Type' :  'U*1', 'Ref' :                     None, 'Value' : None, 'Text' : 'Test head number                      ', 'Missing' :       1},
                'SITE_NUM'  : {'#' :  6, 'Type' :  'U*1', 'Ref' :                     None, 'Value' : None, 'Text' : 'Test site number                      ', 'Missing' :       1},
                'ASR_REF'   : {'#' :  7, 'Type' :  'U*2', 'Ref' :                     None, 'Value' : None, 'Text' : 'ASR Index                             ', 'Missing' :    None},
                'TEST_FLG'  : {'#' :  8, 'Type' :  'B*1', 'Ref' :                     None, 'Value' : None, 'Text' : 'Test flags (fail, alarm, etc.)        ', 'Missing' : ['0']*8},
                'LOG_TYP'   : {'#' :  9, 'Type' :  'C*n', 'Ref' :                     None, 'Value' : None, 'Text' : 'User defined description of datalog   ', 'Missing' :      ''},
                'TEST_TXT'  : {'#' : 10, 'Type' :  'C*n', 'Ref' :                     None, 'Value' : None, 'Text' : 'Descriptive text or label             ', 'Missing' :      ''},
                'ALARM_ID'  : {'#' : 11, 'Type' :  'C*n', 'Ref' :                     None, 'Value' : None, 'Text' : 'Name of alarm                         ', 'Missing' :      ''},
                'PROG_TXT'  : {'#' : 12, 'Type' :  'C*n', 'Ref' :                     None, 'Value' : None, 'Text' : 'Additional Programmed information     ', 'Missing' :      ''},
                'RSLT_TXT'  : {'#' : 13, 'Type' :  'C*n', 'Ref' :                     None, 'Value' : None, 'Text' : 'Additional result information         ', 'Missing' :      ''},
                'COND_CNT'  : {'#' : 14, 'Type' :  'U*2', 'Ref' :                     None, 'Value' : None, 'Text' : 'Count (k) of conditions               ', 'Missing' :       0},
                'COND_LST'  : {'#' : 15, 'Type' : 'xC*n', 'Ref' :               'COND_CNT', 'Value' : None, 'Text' : 'Array of Conditions                   ', 'Missing' :      []},
                'CYC_CNT'   : {'#' : 16, 'Type' :  'U*8', 'Ref' :                     None, 'Value' : None, 'Text' : 'Total cycles executed during the test ', 'Missing' :       0},
                'TOTF_CNT'  : {'#' : 17, 'Type' :  'U*8', 'Ref' :                     None, 'Value' : None, 'Text' : 'Total fails during the test           ', 'Missing' :       0},
                'TOTL_CNT'  : {'#' : 18, 'Type' :  'U*8', 'Ref' :                     None, 'Value' : None, 'Text' : 'Total fails during the complete MTR   ', 'Missing' :       0},
                'OVFL_FLG'  : {'#' : 19, 'Type' :  'B*1', 'Ref' :                     None, 'Value' : None, 'Text' : 'Failure Flag                          ', 'Missing' : ['0']*8},
                'FILE_INC'  : {'#' : 20, 'Type' :  'B*1', 'Ref' :                     None, 'Value' : None, 'Text' : 'File incomplete                       ', 'Missing' : ['0']*8},
                'LOG_TYPE'  : {'#' : 21, 'Type' :  'B*1', 'Ref' :                     None, 'Value' : None, 'Text' : 'Type of datalog                       ', 'Missing' : ['0']*8},
                'FDIM_CNT'  : {'#' : 22, 'Type' :  'U*1', 'Ref' :                     None, 'Value' : None, 'Text' : 'Count (m) of FDIM_FNAM and FDIM_FCNT  ', 'Missing' :       0},
                'FDIM_NAM'  : {'#' : 23, 'Type' : 'xC*n', 'Ref' :               'FDIM_CNT', 'Value' : None, 'Text' : 'Array of logged Dim names             ', 'Missing' :      []},
                'FDIM_FCNT' : {'#' : 24, 'Type' : 'xU*8', 'Ref' :               'FDIM_CNT', 'Value' : None, 'Text' : 'Array of failure counts               ', 'Missing' :      []},
                'CYC_BASE'  : {'#' : 25, 'Type' :  'U*8', 'Ref' :                     None, 'Value' : None, 'Text' : 'Cycle offset to CYC_OFST array        ', 'Missing' :       0},
                'CYC_SIZE'  : {'#' : 26, 'Type' :  'U*1', 'Ref' :                     None, 'Value' : None, 'Text' : 'Size (f) of CYC_OFST [1,2,4 or 8 byes]', 'Missing' :       1},
                'PMR_SIZE'  : {'#' : 27, 'Type' :  'U*1', 'Ref' :                     None, 'Value' : None, 'Text' : 'Size (f) of PMR_ARR [1 or 2 bytes]    ', 'Missing' :       1},
                'ROW_SIZE'  : {'#' : 28, 'Type' :  'U*1', 'Ref' :                     None, 'Value' : None, 'Text' : 'Size (f) of ROW_ARR [1,2,4 or 8 bytes]', 'Missing' :       1},
                'COL_SIZE'  : {'#' : 29, 'Type' :  'U*1', 'Ref' :                     None, 'Value' : None, 'Text' : 'Size (f) of COL_ARR [1,2,4 or 8 bytes]', 'Missing' :       1},
                'DLOG_MSK'  : {'#' : 30, 'Type' :  'U*1', 'Ref' :                     None, 'Value' : None, 'Text' : 'Presence indication mask              ', 'Missing' :       0},
                'PMR_CNT'   : {'#' : 31, 'Type' :  'U*4', 'Ref' :                     None, 'Value' : None, 'Text' : 'Count (n) of pins in PMN_ARR          ', 'Missing' :       0},
                'PMR_ARR'   : {'#' : 32, 'Type' : 'xU*f', 'Ref' :  ('PMR_CNT', 'PMR_SIZE'), 'Value' : None, 'Text' : 'Array of PMR indexes for pins         ', 'Missing' :      []},
                'CYCO_CNT'  : {'#' : 33, 'Type' :  'U*4', 'Ref' :                     None, 'Value' : None, 'Text' : 'Count (n) of CYC_OFST array           ', 'Missing' :       0},
                'CYC_OFST'  : {'#' : 34, 'Type' : 'xU*f', 'Ref' : ('CYCO_CNT', 'CYC_SIZE'), 'Value' : None, 'Text' : 'Array of cycle indexes for each fail  ', 'Missing' :      []},
                'ROW_CNT'   : {'#' : 35, 'Type' :  'U*4', 'Ref' :                     None, 'Value' : None, 'Text' : 'Count (d) of ROW_ARR array            ', 'Missing' :       0},
                'ROW_ARR'   : {'#' : 36, 'Type' : 'xU*f', 'Ref' :  ('ROW_CNT', 'ROW_SIZE'), 'Value' : None, 'Text' : 'Array of row addresses for each fail  ', 'Missing' :      []},
                'COL_CNT'   : {'#' : 37, 'Type' :  'U*4', 'Ref' :                     None, 'Value' : None, 'Text' : 'Count (d) of COL_ARR array            ', 'Missing' :       0},
                'COL_ARR'   : {'#' : 38, 'Type' : 'xU*f', 'Ref' :  ('COL_CNT', 'COL_SIZE'), 'Value' : None, 'Text' : 'Array of col addresses for each fail  ', 'Missing' :      []},
                'STEP_CNT'  : {'#' : 39, 'Type' :  'U*4', 'Ref' :                     None, 'Value' : None, 'Text' : 'Count (d) STEP_ARR array              ', 'Missing' :       0},
                'STEP_ARR'  : {'#' : 40, 'Type' : 'xU*1', 'Ref' :               'STEP_CNT', 'Value' : None, 'Text' : 'Array of march steps for each fail    ', 'Missing' :      []},
                'DIM_CNT'   : {'#' : 41, 'Type' :  'U*1', 'Ref' :                     None, 'Value' : None, 'Text' : 'Number (k) of dimensions              ', 'Missing' :       0},
                'DIM_NAMS'  : {'#' : 42, 'Type' : 'xC*n', 'Ref' :                'DIM_CNT', 'Value' : None, 'Text' : 'Names of the dimensions               ', 'Missing' :      []},
                'DIM_DCNT'  : {'#' : 43, 'Type' :  'U*4', 'Ref' :                     None, 'Value' : None, 'Text' : 'Count (n) of DIM_VALS                 ', 'Missing' :       0},
                'DIM_DSIZ'  : {'#' : 44, 'Type' :  'U*1', 'Ref' :                     None, 'Value' : None, 'Text' : 'Size (f) of DIM_VALS [1,2,4or 8 bytes]', 'Missing' :       1},
                'DIM_VALS'  : {'#' : 45, 'Type' : 'xU*f', 'Ref' : ('DIM_DCNT', 'DIM_DSIZ'), 'Value' : None, 'Text' : 'Array of data values for a dimension  ', 'Missing' :      []},
                'TFRM_CNT'  : {'#' : 46, 'Type' :  'U*8', 'Ref' :                     None, 'Value' : None, 'Text' : 'Total frames in frame based logging   ', 'Missing' :       0},
                'TFSG_CNT'  : {'#' : 47, 'Type' :  'U*8', 'Ref' :                     None, 'Value' : None, 'Text' : 'Total segments across all records     ', 'Missing' :       0},
                'LFSG_CNT'  : {'#' : 48, 'Type' :  'U*2', 'Ref' :                     None, 'Value' : None, 'Text' : 'Local number of frame segments        ', 'Missing' :       0},
                'FRM_IDX'   : {'#' : 49, 'Type' :  'U*2', 'Ref' :                     None, 'Value' : None, 'Text' : 'Index of the frame record             ', 'Missing' :       0},
                'FRM_MASK'  : {'#' : 50, 'Type' :  'D*n', 'Ref' :                     None, 'Value' : None, 'Text' : 'Frame presence mask                   ', 'Missing' :      []},
                'FRM_CNT'   : {'#' : 51, 'Type' :  'U*4', 'Ref' :                     None, 'Value' : None, 'Text' : 'Count (q) of frame (curr frame & maks)', 'Missing' :       0},
                'LFBT_CNT'  : {'#' : 52, 'Type' :  'U*4', 'Ref' :                     None, 'Value' : None, 'Text' : 'Count(q) of bits stored in this record', 'Missing' :       0},
                'FRAMES'    : {'#' : 53, 'Type' :  'D*n', 'Ref' :                     None, 'Value' : None, 'Text' : 'Bit encoded data (curr FSR)           ', 'Missing' :      []},
                'TBSG_CNT'  : {'#' : 54, 'Type' :  'U*8', 'Ref' :                     None, 'Value' : None, 'Text' : 'Number of logged bit stream segments  ', 'Missing' :       0},
                'LBSG_CNT'  : {'#' : 55, 'Type' :  'U*2', 'Ref' :                     None, 'Value' : None, 'Text' : '# of bit stream segmnts in this record', 'Missing' :       0},
                'BSR_IDX'   : {'#' : 56, 'Type' :  'U*2', 'Ref' :                     None, 'Value' : None, 'Text' : 'Index of the bit stream record        ', 'Missing' :       0},
                'STRT_ADR'  : {'#' : 57, 'Type' :  'U*f', 'Ref' :            BSR__ADDR_SIZ, 'Value' : None, 'Text' : 'Start row addr in the current segment ', 'Missing' :       1},
                'WORD_CNT'  : {'#' : 58, 'Type' :  'U*f', 'Ref' :              BSR__WC_SIZ, 'Value' : None, 'Text' : 'Word count in current stream segment  ', 'Missing' :       1},
                'WORDS'     : {'#' : 59, 'Type' :  'D*n', 'Ref' :                     None, 'Value' : None, 'Text' : 'Bit encoded data for one or words     ', 'Missing' :      []},
                'TBMP_SIZE' : {'#' : 60, 'Type' :  'U*8', 'Ref' :                     None, 'Value' : None, 'Text' : 'count (k) of CBIT_MAP                 ', 'Missing' :       0},
                'LBMP_SIZE' : {'#' : 61, 'Type' :  'U*2', 'Ref' :                     None, 'Value' : None, 'Text' : 'Bytes from map in the current record  ', 'Missing' :       0},
                'CBIT_MAP'  : {'#' : 62, 'Type' : 'xU*1', 'Ref' :              'TBMP_SIZE', 'Value' : None, 'Text' : 'Compressed bit map                    ', 'Missing' :      []}
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)

class NMR(STDR):
    def __init__(self, version=None, endian=None, record = None):
        self.id = 'NMR'
        self.local_debug = False
        if version==None or version=='V4':
            self.version = 'V4'
            self.info=    '''
Name Map Record (V4-2007)
-------------------------

Function:
    This record contains a map of PMR indexes to ATPG signal names.
    This record is designed to allow preservation of ATPG signal names used in the ATPG files through the datalog output.
    This record is only required when the standard PMR records do not contain the ATPG signal name.

Frequency:
    ?!?

Location:
    ?!?

'''
            self.fields = {
                'REC_LEN'  : {'#' : 0, 'Type' :  'U*2', 'Ref' :       None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' : None},
                'REC_TYP'  : {'#' : 1, 'Type' :  'U*1', 'Ref' :       None, 'Value' :    1, 'Text' : 'Record type                           ', 'Missing' : None},
                'REC_SUB'  : {'#' : 2, 'Type' :  'U*1', 'Ref' :       None, 'Value' :   91, 'Text' : 'Record sub-type                       ', 'Missing' : None},
                'CONT_FLG' : {'#' : 3, 'Type' :  'B*1', 'Ref' :       None, 'Value' : None, 'Text' : 'NMR record(s) following if not 0      ', 'Missing' :    0},
                'TOTM_CNT' : {'#' : 4, 'Type' :  'U*2', 'Ref' :       None, 'Value' : None, 'Text' : 'Count of PMR indexes (=ATPG_NAMes)    ', 'Missing' :    0},
                'LOCM_CNT' : {'#' : 5, 'Type' :  'U*2', 'Ref' :       None, 'Value' : None, 'Text' : 'Count of (k) PMR indexes              ', 'Missing' :    0},
                'PMR_INDX' : {'#' : 6, 'Type' : 'xU*2', 'Ref' : 'LOCM_CNT', 'Value' : None, 'Text' : 'Array of PMR indexes                  ', 'Missing' :   []},
                'ATPG_NAM' : {'#' : 7, 'Type' : 'xC*n', 'Ref' : 'LOCM_CNT', 'Value' : None, 'Text' : 'Array of ATPG signal names            ', 'Missing' :   []}
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)





class PSR(STDR):
    def __init__(self, version=None, endian=None, record = None):
        self.id = 'PSR'
        self.local_debug = False
        if version==None or version=='V4':
            self.version = 'V4'
            self.info=    '''
Pattern Sequence Record (V4-2007)
---------------------------------

Function:
    PSR record contains the information on the pattern profile for a specific executed scan test
    as part of the Test Identification information. In particular it implements the Test Pattern
    Map data object in the data model. It specifies how the patterns for that test were constructed.
    There will be a PSR record for each scan test in a test program. A PSR is referenced by the STR
    (Scan Test Record) using its PSR_INDX field

Frequency:
    ?!?

Location:
    ?!?
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2', 'Ref' :       None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' :    None},
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1', 'Ref' :       None, 'Value' :    1, 'Text' : 'Record type                           ', 'Missing' :    None},
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1', 'Ref' :       None, 'Value' :   90, 'Text' : 'Record sub-type                       ', 'Missing' :    None},
                'CONT_FLG' : {'#' :  3, 'Type' : 'B*1', 'Ref' :       None, 'Value' : None, 'Text' : 'PSR record(s) to follow if not 0      ', 'Missing' : ['0']*8},
                'PSR_INDX' : {'#' :  4, 'Type' : 'U*2', 'Ref' :       None, 'Value' : None, 'Text' : 'PSR Record Index (used by STR records)', 'Missing' :    None},
                'PSR_NAM'  : {'#' :  5, 'Type' : 'C*n', 'Ref' :       None, 'Value' : None, 'Text' : 'Symbolic name of PSR record           ', 'Missing' :      ''},
                'OPT_FLG'  : {'#' :  6, 'Type' : 'B*1', 'Ref' :       None, 'Value' : None, 'Text' : 'Options Flag                          ', 'Missing' :    None},
                'TOTP_CNT' : {'#' :  7, 'Type' : 'U*2', 'Ref' :       None, 'Value' : None, 'Text' : 'Count of sets in the complete data set', 'Missing' :       1},
                'LOCP_CNT' : {'#' :  8, 'Type' : 'U*2', 'Ref' :       None, 'Value' : None, 'Text' : 'Count (k) of sets in this record      ', 'Missing' :       0},
                'PAT_BGN'  : {'#' :  9, 'Type' :'xU*8', 'Ref' : 'LOCP_CNT', 'Value' : None, 'Text' : "Array of Cycle #'s patterns begins on ", 'Missing' :      []},
                'PAT_END'  : {'#' : 10, 'Type' :'xU*8', 'Ref' : 'LOCP_CNT', 'Value' : None, 'Text' : "Array of Cycle #'s patterns stops at  ", 'Missing' :      []},
                'PAT_FILE' : {'#' : 11, 'Type' :'xC*n', 'Ref' : 'LOCP_CNT', 'Value' : None, 'Text' : 'Array of Pattern File Names           ', 'Missing' :      []},
                'PAT_LBL'  : {'#' : 12, 'Type' :'xC*n', 'Ref' : 'LOCP_CNT', 'Value' : None, 'Text' : 'Optional pattern symbolic name        ', 'Missing' :      []},
                'FILE_UID' : {'#' : 13, 'Type' :'xC*n', 'Ref' : 'LOCP_CNT', 'Value' : None, 'Text' : 'Optional array of file identifier code', 'Missing' :      []},
                'ATPG_DSC' : {'#' : 14, 'Type' :'xC*n', 'Ref' : 'LOCP_CNT', 'Value' : None, 'Text' : 'Optional array of ATPG information    ', 'Missing' :      []},
                'SRC_ID'   : {'#' : 15, 'Type' :'xC*n', 'Ref' : 'LOCP_CNT', 'Value' : None, 'Text' : 'Optional array of PatternInSrcFileID  ', 'Missing' :      []}
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)




class RR1(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = 'RR1'
        raise STDFError("%s object creation error : reserved object", self.id)

class RR2(STDR):
    def __init__(self, version=None, endian=None, record=None):
        self.id = 'RR2'
        raise STDFError("%s object creation error : reserved object", self.id)





class SSR(STDR):
    def __init__(self, version=None, endian=None, record = None):
        self.id = 'SSR'
        self.local_debug = False
        if version==None or version == 'V4':
            self.version = 'V4'
            self.info=    '''
Scan Structure Record
---------------------

Function:
    This record contains the Scan Structure information normally found in a STIL file.
    The SSR is a top level Scan Structure record that contains an array of indexes to CDR
    (Chain Description Record) records which contain the chain information.

Frequency:
    ?!?

Location:
    ?!?
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2',  'Ref' : None,      'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' : None},
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1',  'Ref' : None,      'Value' :    1, 'Text' : 'Record type                           ', 'Missing' : None},
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1',  'Ref' : None,      'Value' :   93, 'Text' : 'Record sub-type                       ', 'Missing' : None},
                'SSR_NAM'  : {'#' :  3, 'Type' : 'C*n',  'Ref' : None,      'Value' : None, 'Text' : 'Name of the STIL Scan Structure       ', 'Missing' : ''  },
                'CHN_CNT'  : {'#' :  4, 'Type' : 'U*2',  'Ref' : None,      'Value' : None, 'Text' : 'Count (k) of number of Chains         ', 'Missing' : 0   },
                'CHN_LIST' : {'#' :  5, 'Type' : 'xU*2', 'Ref' : 'CHN_CNT', 'Value' : None, 'Text' : 'Array of CDR Indexes                  ', 'Missing' : []  }
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)

class STR(STDR):
    def __init__(self, version=None, endian=None, record = None):
        self.id = 'STR'
        self.local_debug = False
        if version==None or version=='V4':
            self.version = 'V4'
            self.info=    '''
Record
------------------

Function:
    It contains all or some of the results of the single execution of a scan test in the test program.
    It is intended to contain all of the individual pin/cycle failures that are detected in a single test execution.
    If there are more failures than can be contained in a single record, then the record may be followed by additional continuation STR records.

Frequency:
    ?!?

Location:
    ?!?
'''
            self.fields = {
                'REC_LEN'  : {'#' :  0, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' : None   },
                'REC_TYP'  : {'#' :  1, 'Type' : 'U*1',  'Ref' : None,                     'Value' :   15, 'Text' : 'Record type                           ', 'Missing' : None   },
                'REC_SUB'  : {'#' :  2, 'Type' : 'U*1',  'Ref' : None,                     'Value' :   30, 'Text' : 'Record sub-type                       ', 'Missing' : None   },
                'CONT_FLG' : {'#' :  3, 'Type' : 'B*1',  'Ref' : None,                     'Value' : None, 'Text' : 'Continuation STRs follow (if not 0)   ', 'Missing' : 0      },
                'TEST_NUM' : {'#' :  4, 'Type' : 'U*4',  'Ref' : None,                     'Value' : None, 'Text' : 'Test number                           ', 'Missing' : None   },
                'HEAD_NUM' : {'#' :  5, 'Type' : 'U*1',  'Ref' : None,                     'Value' : None, 'Text' : 'Test head number                      ', 'Missing' : 1      },
                'SITE_NUM' : {'#' :  6, 'Type' : 'U*1',  'Ref' : None,                     'Value' : None, 'Text' : 'Test site number                      ', 'Missing' : 1      },
                'PSR_REF'  : {'#' :  7, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'PSR Index (Pattern Sequence Record)   ', 'Missing' : 0      },
                'TEST_FLG' : {'#' :  8, 'Type' : 'B*1',  'Ref' : None,                     'Value' : None, 'Text' : 'Test flags (fail, alarm, etc.)        ', 'Missing' : ['0']*8},
                'LOG_TYP'  : {'#' :  9, 'Type' : 'C*n',  'Ref' : None,                     'Value' : None, 'Text' : 'User defined description of datalog   ', 'Missing' : ''     },
                'TEST_TXT' : {'#' : 10, 'Type' : 'C*n',  'Ref' : None,                     'Value' : None, 'Text' : 'Descriptive text or label             ', 'Missing' : ''     },
                'ALARM_ID' : {'#' : 11, 'Type' : 'C*n',  'Ref' : None,                     'Value' : None, 'Text' : 'Name of alarm                         ', 'Missing' : ''     },
                'PROG_TXT' : {'#' : 12, 'Type' : 'C*n',  'Ref' : None,                     'Value' : None, 'Text' : 'Additional Programmed information     ', 'Missing' : ''     },
                'RSLT_TXT' : {'#' : 13, 'Type' : 'C*n',  'Ref' : None,                     'Value' : None, 'Text' : 'Additional result information         ', 'Missing' : ''     },
                'Z_VAL'    : {'#' : 14, 'Type' : 'U*1',  'Ref' : None,                     'Value' : None, 'Text' : 'Z Handling Flag                       ', 'Missing' : 0      },
                'FMU_FLG'  : {'#' : 15, 'Type' : 'B*1',  'Ref' : None,                     'Value' : None, 'Text' : 'MASK_MAP & FAL_MAP field status       ', 'Missing' : ['0']*8},
                'MASK_MAP' : {'#' : 16, 'Type' : 'D*n',  'Ref' : None,                     'Value' : None, 'Text' : 'Bit map of Globally Masked Pins       ', 'Missing' : []     },
                'FAL_MAP'  : {'#' : 17, 'Type' : 'D*n',  'Ref' : None,                     'Value' : None, 'Text' : 'Bit map of failures after buffer full ', 'Missing' : []     },
                'CYC_CNT'  : {'#' : 18, 'Type' : 'U*8',  'Ref' : None,                     'Value' : None, 'Text' : 'Total cycles executed in test         ', 'Missing' : 0      },
                'TOTF_CNT' : {'#' : 19, 'Type' : 'U*4',  'Ref' : None,                     'Value' : None, 'Text' : 'Total failures (pin x cycle) detected ', 'Missing' : 0      },
                'TOTL_CNT' : {'#' : 20, 'Type' : 'U*4',  'Ref' : None,                     'Value' : None, 'Text' : "Total fails logged across all STR's   ", 'Missing' : 0      },
                'CYC_BASE' : {'#' : 21, 'Type' : 'U*8',  'Ref' : None,                     'Value' : None, 'Text' : 'Cycle offset to apply to CYCL_NUM arr ', 'Missing' : 0      },
                'BIT_BASE' : {'#' : 22, 'Type' : 'U*4',  'Ref' : None,                     'Value' : None, 'Text' : 'Offset to apply to BIT_POS array      ', 'Missing' : 0      },
                'COND_CNT' : {'#' : 23, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Count (g) of Test Conditions+opt spec ', 'Missing' : 0      },
                'LIM_CNT'  : {'#' : 24, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Count (j) of LIM Arrays in cur. rec.  ', 'Missing' : 0      }, # 1 = global
                'CYC_SIZE' : {'#' : 25, 'Type' : 'U*1',  'Ref' : None,                     'Value' : None, 'Text' : 'Size (f) [1,2,4 or 8] of  CYC_OFST    ', 'Missing' : 1      },
                'PMR_SIZE' : {'#' : 26, 'Type' : 'U*1',  'Ref' : None,                     'Value' : None, 'Text' : 'Size (f) [1 or 2] of PMR_INDX         ', 'Missing' : 1      },
                'CHN_SIZE' : {'#' : 27, 'Type' : 'U*1',  'Ref' : None,                     'Value' : None, 'Text' : 'Size (f) [1, 2 or 4] of CHN_NUM       ', 'Missing' : 1      },
                'PAT_SIZE' : {'#' : 28, 'Type' : 'U*1',  'Ref' : None,                     'Value' : None, 'Text' : 'Size (f) [1,2, or 4] of PAT_NUM       ', 'Missing' : 1      },
                'BIT_SIZE' : {'#' : 29, 'Type' : 'U*1',  'Ref' : None,                     'Value' : None, 'Text' : 'Size (f) [1,2, or 4] of BIT_POS       ', 'Missing' : 1      },
                'U1_SIZE'  : {'#' : 30, 'Type' : 'U*1',  'Ref' : None,                     'Value' : None, 'Text' : 'Size (f) [1,2,4 or 8] of USR1         ', 'Missing' : 1      },
                'U2_SIZE'  : {'#' : 31, 'Type' : 'U*1',  'Ref' : None,                     'Value' : None, 'Text' : 'Size (f) [1,2,4 or 8] of USR2         ', 'Missing' : 1      },
                'U3_SIZE'  : {'#' : 32, 'Type' : 'U*1',  'Ref' : None,                     'Value' : None, 'Text' : 'Size (f) [1,2,4 or 8] of USR3         ', 'Missing' : 1      },
                'UTX_SIZE' : {'#' : 33, 'Type' : 'U*1',  'Ref' : None,                     'Value' : None, 'Text' : 'Size (f) of each string in USER_TXT   ', 'Missing' : 0      },
                'CAP_BGN'  : {'#' : 34, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Offset to BIT_POS to get capture cycls', 'Missing' : 0      },
                'LIM_INDX' : {'#' : 35, 'Type' : 'xU*2', 'Ref' : 'LIM_CNT',                'Value' : None, 'Text' : 'Array of PMR unique limit specs       ', 'Missing' : []     },
                'LIM_SPEC' : {'#' : 36, 'Type' : 'xU*4', 'Ref' : 'LIM_CNT',                'Value' : None, 'Text' : "Array of fail datalog limits for PMR's", 'Missing' : []     },
                'COND_LST' : {'#' : 37, 'Type' : 'xC*n', 'Ref' : 'COND_CNT',               'Value' : None, 'Text' : 'Array of test condition (Name=value)  ', 'Missing' : []     },
                'CYC_CNT'  : {'#' : 38, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Count (k) of entries in CYC_OFST array', 'Missing' : 0      },
                'CYC_OFST' : {'#' : 39, 'Type' : 'xU*f', 'Ref' : ('CYC_CNT', 'CYC_SIZE'),  'Value' : None, 'Text' : 'Array of cycle nrs relat to CYC_BASE  ', 'Missing' : []     },
                'PMR_CNT'  : {'#' : 40, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Count (k) of entries in the PMR_INDX  ', 'Missing' : 0      },
                'PMR_INDX' : {'#' : 41, 'Type' : 'xU*f', 'Ref' : ('PMR_CNT', 'PMR_SIZE'),  'Value' : None, 'Text' : 'Array of PMR Indexes (All Formats)    ', 'Missing' : []     },
                'CHN_CNT'  : {'#' : 42, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Count (k) of entries in the CHN_NUM   ', 'Missing' : 0      },
                'CHN_NUM'  : {'#' : 43, 'Type' : 'xU*f', 'Ref' : ('CHN_CNT', 'CHN_SIZE'),  'Value' : None, 'Text' : 'Array of Chain No for FF Name Mapping ', 'Missing' : []     },
                'EXP_CNT'  : {'#' : 44, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Count (k) of EXP_DATA array entries   ', 'Missing' : 0      },
                'EXP_DATA' : {'#' : 45, 'Type' : 'xU*1', 'Ref' : 'EXP_CNT',                'Value' : None, 'Text' : 'Array of expected vector data         ', 'Missing' : []     },
                'CAP_CNT'  : {'#' : 46, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Count (k) of CAP_DATA array entries   ', 'Missing' : 0      },
                'CAP_DATA' : {'#' : 47, 'Type' : 'xU*1', 'Ref' : 'CAP_CNT',                'Value' : None, 'Text' : 'Array of captured data                ', 'Missing' : []     },
                'NEW_CNT'  : {'#' : 48, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Count (k) of NEW_DATA array entries   ', 'Missing' : 0      },
                'NEW_DATA' : {'#' : 49, 'Type' : 'xU*1', 'Ref' : 'NEW_CNT',                'Value' : None, 'Text' : 'Array of new vector data              ', 'Missing' : []     },
                'PAT_CNT'  : {'#' : 50, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Count (k) of PAT_NUM array entries    ', 'Missing' : 0      },
                'PAT_NUM'  : {'#' : 51, 'Type' : 'xU*f', 'Ref' : ('PAT_CNT', 'PAT_SIZE'),  'Value' : None, 'Text' : 'Array of pattern # (Ptn/Chn/Bit fmt)  ', 'Missing' : []     },
                'BPOS_CNT' : {'#' : 52, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Count (k) of BIT_POS array entries    ', 'Missing' : 0      },
                'BIT_POS'  : {'#' : 53, 'Type' : 'xU*f', 'Ref' : ('BPOS_CNT', 'BIT_SIZE'), 'Value' : None, 'Text' : 'Array of chain bit (Ptn/Chn/Bit fmt)  ', 'Missing' : []     },
                'USR1_CNT' : {'#' : 54, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Count (k) of USR1 array entries       ', 'Missing' : 0      },
                'USR1'     : {'#' : 55, 'Type' : 'xU*f', 'Ref' : ('USR1_CNT', 'U1_SIZE'),  'Value' : None, 'Text' : 'Array of logged fail                  ', 'Missing' : []     },
                'USR2_CNT' : {'#' : 56, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Count (k) of USR2 array entries       ', 'Missing' : 0      },
                'USR2'     : {'#' : 57, 'Type' : 'xU*f', 'Ref' : ('USR2_CNT', 'U2_SIZE'),  'Value' : None, 'Text' : 'Array of logged fail                  ', 'Missing' : []     },
                'USR3_CNT' : {'#' : 58, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Count (k) of USR3 array entries       ', 'Missing' : 0      },
                'USR3'     : {'#' : 59, 'Type' : 'xU*f', 'Ref' : ('USR3_CNT', 'U3_SIZE'),  'Value' : None, 'Text' : 'Array of logged fail                  ', 'Missing' : []     },
                'TXT_CNT'  : {'#' : 60, 'Type' : 'U*2',  'Ref' : None,                     'Value' : None, 'Text' : 'Count (k) of USER_TXT array entries   ', 'Missing' : 0      },
                'USER_TXT' : {'#' : 61, 'Type' : 'xC*f', 'Ref' : ('TXT_CNT', 'UTX_SIZE'),  'Value' : None, 'Text' : 'Array of logged fail                  ', 'Missing' : []     }
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)



class VUR(STDR):
    def __init__(self, version=None, endian=None, record = None):
        self.id = 'VUR'
        self.local_debug = False
        if version==None or version=='V4':
            self.version = 'V4'
            self.info=    '''
Version Update Record
---------------------

Function:
    Version update Record is used to identify the updates over version V4.
    Presence of this record indicates that the file may contain records defined by the new standard.

Frequency:
    * One for each extension to STDF V4 used.

Location:
    Just before the MIR
'''
            self.fields = {
                'REC_LEN'  : {'#' : 0, 'Type' : 'U*2', 'Ref' : None, 'Value' : None, 'Text' : 'Bytes of data following header        ', 'Missing' : None},
                'REC_TYP'  : {'#' : 1, 'Type' : 'U*1', 'Ref' : None, 'Value' :    0, 'Text' : 'Record type                           ', 'Missing' : None},
                'REC_SUB'  : {'#' : 2, 'Type' : 'U*1', 'Ref' : None, 'Value' :   30, 'Text' : 'Record sub-type                       ', 'Missing' : None},
                'UPD_NAM'  : {'#' : 3, 'Type' : 'C*n', 'Ref' : None, 'Value' : None, 'Text' : 'Update Version Name                   ', 'Missing' : ''  }
            }
        else:
            raise STDFError("%s object creation error: unsupported version '%s'" % (self.id, version))
        self._default_init(endian, record)


def is_odd(Number):
    '''
    This function will return True if the Number is odd, False otherwise
    '''
    if ((Number % 2) == 1):
        return True
    return False

def is_even(Number):
    '''
    This function will return True if the Number is EVEN, False otherwise.
    '''
    if ((Number % 2) == 1):
        return False
    return True

def read_record(fd, RHF):
    '''
    This method will read one record from fd (at the current fp) with record header format RHF, and return the raw record
    '''
    header = fd.read(4)
    REC_LEN, REC_TYP, REC_SUB = struct.unpack(RHF, header)
    footer = fd.read(REC_LEN)
    return REC_LEN, REC_TYP, REC_SUB, header+footer

def read_indexed_record(fd, fp, RHF):
    fd.seek(fp)
    header = fd.read(4)
    REC_LEN, REC_TYP, REC_SUB = struct.unpack(RHF, header)
    footer = fd.read(REC_LEN)
    return REC_LEN, REC_TYP, REC_SUB, header+footer

class records_from_file(object):
    '''
    Generator class to run over the records in FileName.
    The return values are 4-fold : REC_LEN, REC_TYP, REC_SUB and REC
    REC is the complete record (including REC_LEN, REC_TYP & REC_SUB)
    if unpack indicates if REC is to be the raw record or the unpacked object.
    of_interest can be a list of records to return. By default of_interest is void
    meaning all records (of FileName's STDF Version) are used.
    '''
    debug = False

    def __init__(self, FileName, unpack=False, of_interest=None):
        if self.debug: print("initializing 'records_from_file")
        if isinstance(FileName, str):
            self.keep_open = False
            if not os.path.exists(FileName):
                raise STDFError("'%s' does not exist")
            self.endian = get_STDF_setup_from_file(FileName)[0]
            self.version = 'V%s' % struct.unpack('B', get_bytes_from_file(FileName, 5, 1))
            self.fd = open(FileName, 'rb')
        elif isinstance(FileName, io.IOBase):
            self.keep_open = True
            self.fd = FileName
            ptr = self.fd.tell()
            self.fd.seek(4)
            buff = self.fd.read(2)
            CPU_TYPE, STDF_VER = struct.unpack('BB', buff)
            if CPU_TYPE == 1: self.endian = '>'
            elif CPU_TYPE == 2: self.endian = '<'
            else: self.endian = '?'
            self.version = 'V%s' % STDF_VER
            self.fd.seek(ptr)
        else:
            raise STDFError("'%s' is not a string or an open file descriptor")
        self.unpack = unpack
        self.fmt = '%sHBB' % self.endian
        TS2ID = ts_to_id(self.version)
        if of_interest==None:
            self.records_of_interest = TS2ID
        elif isinstance(of_interest, list):
            ID2TS = id_to_ts(self.version)
            tmp_list = []
            for item in of_interest:
                if isinstance(item, str):
                    if item in ID2TS:
                        if ID2TS[item] not in tmp_list:
                            tmp_list.append(ID2TS[item])
                elif isinstance(item, tuple) and len(item)==2:
                    if item in TS2ID:
                        if item not in tmp_list:
                            tmp_list.append(item)
            self.records_of_interest = tmp_list
        else:
            raise STDFError("objects_from_file(%s, %s) : Unsupported of_interest" % (FileName, of_interest))

    def __del__(self):
        if not self.keep_open:
            self.fd.close()

    def __iter__(self):
        return self

    def __next__(self):
        while self.fd!=None:
            header = self.fd.read(4)
            if len(header)!=4:
                raise StopIteration
            else:
                REC_LEN, REC_TYP, REC_SUB = struct.unpack(self.fmt, header)
                footer = self.fd.read(REC_LEN)
                if (REC_TYP, REC_SUB) in self.records_of_interest:
                    if len(footer)!=REC_LEN:
                        raise StopIteration()
                    else:
                        if self.unpack:
                            return REC_LEN, REC_TYP, REC_SUB, create_record_object(self.version, self.endian, (REC_TYP, REC_SUB), header+footer)
                        else:
                            return REC_LEN, REC_TYP, REC_SUB, header+footer

def objects_from_indexed_file(FileName, index, records_of_interest=None):
    '''
     This is a Generator of records (not in order!)
    '''
    if not isinstance(FileName, str): raise STDFError("'%s' is not a string.")
    if not os.path.exists(FileName): raise STDFError("'%s' does not exist")
    endian = get_STDF_setup_from_file(FileName)[0]
    RLF = '%sH' % endian
    version = 'V%s' % struct.unpack('B', get_bytes_from_file(FileName, 5, 1))
    fd = open(FileName, 'rb')

    ALL = list(id_to_ts(version).keys())
    if records_of_interest==None:
        roi = ALL
    elif isinstance(records_of_interest, list):
        roi = []
        for item in records_of_interest:
            if isinstance(item, str):
                if (item in ALL) and (item not in roi):
                    roi.append(item)
    else:
        raise STDFError("objects_from_indexed_file(%s, index, records_of_interest) : Unsupported records_of_interest" % (FileName, records_of_interest))
    for REC_ID in roi:
        if REC_ID in index:
            for fp in index[REC_ID]:
                OBJ = create_record_object(version, endian, REC_ID, get_record_from_file_at_position(fd, fp, RLF))
                yield OBJ

# class xrecords_from_file(object):
#     '''
#     This is a *FAST* iterator class that returns the next record from an STDF file each time it is called.
#     It is fast because it doesn't check versions, extensions and it doesn't unpack the record and skips unknown records.
#     '''
#
#     def __init__(self, FileName, of_interest=None):
#         #TODO: add a record_list of records to return
#         if isinstance(FileName, str):
#             try:
#                 stdf_file = File(FileName)
#             except:
#                 raise StopIteration
#             self.fd = stdf_file.open()
#         elif isinstance(FileName, File):
#             stdf_file = FileName
#             self.fd = FileName.open()
#         else:
#             raise STDFError("records_from_file(%s) : Unsupported 'FileName'" % FileName)
#         self.endian = stdf_file.endian
#         self.version = stdf_file.version
#         TS2ID = ts_to_id(self.version)
#         if of_interest==None:
#             self.of_interest = list(TS2ID.keys())
#         elif isinstance(of_interest, list):
#             ID2TS = id_to_ts(self.version)
#             tmp_list = []
#             for item in of_interest:
#                 if isinstance(item, str):
#                     if item in ID2TS:
#                         if ID2TS[item] not in tmp_list:
#                             tmp_list.append(ID2TS[item])
#                 elif isinstance(item, tuple) and len(item)==2:
#                     if item in TS2ID:
#                         if item not in tmp_list:
#                             tmp_list.append(item)
#             self.of_interest = tmp_list
#         else:
#             raise STDFError("records_from_file(%s, %s) : Unsupported of_interest" % (FileName, of_interest))
#
#     def __del__(self):
#         self.fd.close()
#
#     def __iter__(self):
#         return self
#
#     def __next__(self):
#         while self.fd!=None:
#             while True:
#                 header = self.fd.read(4)
#                 if len(header)!=4:
#                     raise StopIteration
#                 REC_LEN, REC_TYP, REC_SUB = struct.unpack('HBB', header)
#                 footer = self.fd.read(REC_LEN)
#                 if len(footer)!=REC_LEN:
#                     raise StopIteration
#                 if (REC_TYP, REC_SUB) in self.of_interest:
#                     return REC_LEN, REC_TYP, REC_SUB, header+footer
#
# class xobjects_from_file(object):
#     '''
#     This is an iterator class that returns the next object (unpacked) from an STDF file.
#     It will take care of versions and extensions, and unrecognized records will simply be skipped.
#     '''
#     def __init__(self, FileName, of_interest=None):
#         if isinstance(FileName, str):
#             try:
#                 stdf_file = File(FileName)
#             except:
#                 raise STDFError("objects_from_file(%s, %s) : File doesn't exist" % (FileName, of_interest))
#             self.fd = stdf_file.open()
#         elif isinstance(FileName, File):
#             self.fd = FileName.open()
#         else:
#             raise STDFError("objects_from_file(%s) : Unsupported 'FileName'" % FileName)
#         self.endian = stdf_file.endian
#         self.version = stdf_file.version
#         TS2ID = ts_to_id(self.version)
#         if of_interest==None:
#             of_interest = TS2ID
#         elif isinstance(of_interest, list):
#             ID2TS = id_to_ts(self.version)
#             tmp_list = []
#             for item in of_interest:
#                 if isinstance(item, str):
#                     if item in ID2TS:
#                         if ID2TS[item] not in tmp_list:
#                             tmp_list.append(ID2TS[item])
#                 elif isinstance(item, tuple) and len(item)==2:
#                     if item in TS2ID:
#                         if item not in tmp_list:
#                             tmp_list.append(item)
#             of_interest = tmp_list
#         else:
#             raise STDFError("objects_from_file(%s, %s) : Unsupported of_interest" % (FileName, of_interest))
#         self.of_interest = of_interest
#         self.fmt = '%sHBB' % self.endian
#
#     def __del__(self):
#         self.fd.close()
#
#     def __iter__(self):
#         return self
#
#     def __next__(self):
#         while True:
#             header = self.fd.read(4)
#             if len(header)!=4:
#                 raise StopIteration
#             else:
#                 REC_LEN, REC_TYP, REC_SUB = struct.unpack(self.fmt, header)
#                 footer = self.fd.read(REC_LEN)
#                 if len(footer)!=REC_LEN:
#                     raise StopIteration
#                 else:
#                     record = header + footer
#                     if (REC_TYP, REC_SUB) in self.of_interest:
#                         recobj = create_record_object(self.version, self.endian, (REC_TYP, REC_SUB), record)
#                         return (recobj)


# class open(object):
#     '''
#     file opener that opens an STDF file transparently (gzipped or not)
#     '''
#     def __init__(self, fname):
#         f = open(fname)
#         # Read magic number (the first 2 bytes) and rewind.
#         magic_number = f.read(2)
#         f.seek(0)
#         # Encapsulated 'self.f' is a file or a GzipFile.
#         if magic_number == '\x1f\x8b':
#             self.f = gzip.GzipFile(fileobj=f)
#         else:
#             self.f = f
#
#         # Define '__enter__' and '__exit__' to use in 'with' blocks.
#         def __enter__(self):
#             return self
#         def __exit__(self, type, value, traceback):
#             try:
#                 self.f.fileobj.close()
#             except AttributeError:
#                 pass
#             finally:
#                 self.f.close()
#
#         # Reproduce the interface of an open file by encapsulation.
#         def __getattr__(self, name):
#             return getattr(self.f, name)
#         def __iter__(self):
#             return iter(self.f)
#         def next(self):
#             return next(self.f)



def create_record_object(Version, Endian, REC_ID, REC=None):
    '''
    This function will create and return the appropriate Object for REC
    based on REC_ID. REC_ID can be a 2-element tuple or a string.
    If REC is not None, then the record will also be unpacked.
    '''
    retval = None
    REC_TYP=-1
    REC_SUB=-1
    if Version not in supported().versions():
        raise STDFError("Unsupported STDF Version : %s" % Version)
    if Endian not in ['<', '>']:
        raise STDFError("Unsupported Endian : '%s'" % Endian)
    if isinstance(REC_ID, tuple) and len(REC_ID)==2:
        TS2ID = ts_to_id(Version)
        if (REC_ID[0], REC_ID[1]) in TS2ID:
            REC_TYP = REC_ID[0]
            REC_SUB = REC_ID[1]
            REC_ID = TS2ID[(REC_TYP, REC_SUB)]
    elif isinstance(REC_ID, str):
        ID2TS = id_to_ts(Version)
        if REC_ID in ID2TS:
            (REC_TYP, REC_SUB) = ID2TS[REC_ID]
    else:
        raise STDFError("Unsupported REC_ID : %s" % REC_ID)

    if REC_TYP!=-1 and REC_SUB!=-1:
        if REC_ID == 'PTR': retval = PTR(Version, Endian, REC)
        elif REC_ID == 'FTR': retval = FTR(Version, Endian, REC)
        elif REC_ID == 'MPR': retval = MPR(Version, Endian, REC)
        elif REC_ID == 'STR': retval = STR(Version, Endian, REC)
        elif REC_ID == 'MTR': retval = MTR(Version, Endian, REC)
        elif REC_ID == 'PIR': retval = PIR(Version, Endian, REC)
        elif REC_ID == 'PRR': retval = PRR(Version, Endian, REC)
        elif REC_ID == 'FAR': retval = FAR(Version, Endian, REC)
        elif REC_ID == 'ATR': retval = ATR(Version, Endian, REC)
        elif REC_ID == 'VUR': retval = VUR(Version, Endian, REC)
        elif REC_ID == 'MIR': retval = MIR(Version, Endian, REC)
        elif REC_ID == 'MRR': retval = MRR(Version, Endian, REC)
        elif REC_ID == 'WCR': retval = WCR(Version, Endian, REC)
        elif REC_ID == 'WIR': retval = WIR(Version, Endian, REC)
        elif REC_ID == 'WRR': retval = WRR(Version, Endian, REC)
        elif REC_ID == 'ADR': retval = ADR(Version, Endian, REC)
        elif REC_ID == 'ASR': retval = ASR(Version, Endian, REC)
        elif REC_ID == 'BPS': retval = BPS(Version, Endian, REC)
        elif REC_ID == 'BRR': retval = BRR(Version, Endian, REC)
        elif REC_ID == 'BSR': retval = BSR(Version, Endian, REC)
        elif REC_ID == 'CNR': retval = CNR(Version, Endian, REC)
        elif REC_ID == 'DTR': retval = DTR(Version, Endian, REC)
        elif REC_ID == 'EPDR': retval = EPDR(Version, Endian, REC)
        elif REC_ID == 'EPS': retval = EPS(Version, Endian, REC)
        elif REC_ID == 'ETSR': retval = ETSR(Version, Endian, REC)
        elif REC_ID == 'FDR': retval = FDR(Version, Endian, REC)
        elif REC_ID == 'FSR': retval = FSR(Version, Endian, REC)
        elif REC_ID == 'GDR': retval = GDR(Version, Endian, REC)
        elif REC_ID == 'GTR': retval = GTR(Version, Endian, REC)
        elif REC_ID == 'HBR': retval = HBR(Version, Endian, REC)
        elif REC_ID == 'IDR': retval = IDR(Version, Endian, REC)
        elif REC_ID == 'MCR': retval = MCR(Version, Endian, REC)
        elif REC_ID == 'MMR': retval = MMR(Version, Endian, REC)
        elif REC_ID == 'MSR': retval = MSR(Version, Endian, REC)
        elif REC_ID == 'NMR': retval = NMR(Version, Endian, REC)
        elif REC_ID == 'PCR': retval = PCR(Version, Endian, REC)
        elif REC_ID == 'PDR': retval = PDR(Version, Endian, REC)
        elif REC_ID == 'PGR': retval = PGR(Version, Endian, REC)
        elif REC_ID == 'PLR': retval = PLR(Version, Endian, REC)
        elif REC_ID == 'PMR': retval = PMR(Version, Endian, REC)
        elif REC_ID == 'PSR': retval = PSR(Version, Endian, REC)
        elif REC_ID == 'RDR': retval = RDR(Version, Endian, REC)
        elif REC_ID == 'SBR': retval = SBR(Version, Endian, REC)
        elif REC_ID == 'SCR': retval = SCR(Version, Endian, REC)
        elif REC_ID == 'SDR': retval = SDR(Version, Endian, REC)
        elif REC_ID == 'SHB': retval = SHB(Version, Endian, REC)
        elif REC_ID == 'SSB': retval = SSB(Version, Endian, REC)
        elif REC_ID == 'SSR': retval = SSR(Version, Endian, REC)
        elif REC_ID == 'STS': retval = STS(Version, Endian, REC)
        elif REC_ID == 'TSR': retval = TSR(Version, Endian, REC)
        elif REC_ID == 'WTR': retval = WTR(Version, Endian, REC)
        elif REC_ID == 'RR1': retval = RR1(Version, Endian, REC) # can not be reached because of -1
        elif REC_ID == 'RR2': retval = RR2(Version, Endian, REC) # can not be reached because of -1
    return retval

def wafer_map(data, parameter=None):
    '''
    data is a pandas data frame, it has at least 5 columns ('X_COORD', 'Y_COORD', 'LOT_ID', 'WAFER_ID' and the parameter)
    If the parameter is not named the following order of 'parameters' will be used :
        'HARD_BIN'
        'SOFT_BIN'
        'PART_PF'

    '''
    pass



def get_bytes_from_file(FileName, Offset, Number):
    '''
    This function will return 'Number' bytes starting after 'Offset' from 'FileName'
    '''
    if not isinstance(FileName, str): raise STDFError("'%s' is not a string")
    if not isinstance(Offset, int): raise STDFError("Offset is not an integer")
    if not isinstance(Number, int): raise STDFError("Number is not an integer")
    if not os.path.exists(FileName): raise STDFError("'%s' does not exist")
    if guess_type(FileName)[1]=='gzip':
        raise NotImplemented("Not yet implemented")
    else:
        with open(FileName, 'rb') as fd:
            fd.seek(Offset)
            retval = fd.read(Number)
    return retval

def get_record_from_file_at_position(fd, offset, REC_LEN_FMT):
    fd.seek(offset)
    header = fd.read(4)
    REC_LEN = struct.unpack(REC_LEN_FMT, header[:2])[0]
    footer = fd.read(REC_LEN)
    return header+footer

def get_STDF_setup_from_file(FileName):
    '''
    This function will determine the endian and the version of a given STDF file
    it must *NOT* be guaranteed that FileName exists or is an STDF File.
    '''
    endian = None
    version = None
    if os.path.exists(FileName) and os.path.isfile(FileName):
        if is_file_with_stdf_magicnumber(FileName):
            CPU_TYP, STDF_VER = struct.unpack('BB', get_bytes_from_file(FileName, 4, 2))
            if CPU_TYP == 1: endian = '>'
            elif CPU_TYP == 2: endian = '<'
            else: endian = '?'
            version = "V%s" % STDF_VER
    return endian, version

def get_MIR_from_file(FileName):
    '''
    This function will just get the MIR (near the start of the file) from the FileName and return it.
    it must *NOT* be guaranteed that FileName exists or is an STDF File.
    '''
    endian, version = get_STDF_setup_from_file(FileName)
    mir = None
    if endian!=None and version!=None: # file exists and is an STDF file
        for record in xrecords_from_file(FileName):
            _, REC_TYP, REC_SUB, REC = record
            if (REC_TYP, REC_SUB) == (1, 10):
                mir = MIR(version, endian, REC)
                break
    return mir

def get_partcount_from_file(FileName):
    '''
    This function will return the number of parts contained in FileName.
    it must *NOT* be guaranteed that FileName exists or is an STDF File.
    '''

def save_STDF_index(FileName, index):
    '''
    '''
    if os.path.exists(FileName) and os.path.isfile(FileName):
        Path, Name = os.path.split(FileName)
        Base, Ext = os.path.splitext(Name)
        if Ext in ['.stdf', '.pbz2']:
            pickle_file = os.path.join(Path, "%s.pbz2" % Base)
        else:
            raise Exception("FileName should have '.stdf' or '.pbz2' extension")
        with bz2.open(pickle_file, 'wb') as fd:
            pickle.dump(index, fd)
    else:
        raise Exception("File {} does not exists or is not a file!".format(FileName))



if __name__ == '__main__':
    endian = '<'
    version = 'V4'
    rec = b'\x1b\x00\x01P\x00\x00\x08\x00\x01\x02\x03\x04\x05\x06\x07\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    sdr = SDR(version, endian, rec)

    print(sdr)
