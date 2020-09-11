# -*- coding: utf-8 -*-
'''
Created on 16 Aug 2019

@author: tho
'''
import struct
from abc import ABC
from abc import abstractmethod
from zlib import adler32

from ATE.Data.Formats.STDF.records import hexify
from ATE.Data.Formats.STDF.records import sys_cpu
from ATE.Data.Formats.STDF.records import sys_endian
from ATE.utils.DT import DT

__latest_SEDF_version__ = 1 # will be casted to unsigned byte
__magic_number__ = 'SEDF'

'''
Type Definitions: (from the original STDF we use only the following types)

   struct  | SEDF |
    type   | type | Description                                                                       | C Type
   --------+------+-----------------------------------------------------------------------------------+---------------------
           | C*n  | Variable lenght character string (thus utf-8 coded !)                             |
           |      | First byte = unsigned count of bytes to follow (maximum 255 bytes)                |
      B    | U*1  | One byte unsigned integer (0 .. 255)                                              | unsigned char
      H    | U*2  | Two byte unsinged integer (0 .. 65,535)                                           | unsigned short
      I    | U*4  | Four byte unsinged integer (0 .. 4,294,967,295) ~~> 136+ years in epoch seconds ! | unsigned int
      Q    | U*8  | Eight byte unsinged integer (0 .. 18,446,744,073,709,551,615)                     | unsigned long long                                                             |
      b    | I*1  | one byte signed integer (-128 .. 127)                                             | char
      h    | I*2  | two byte signed integer (-32,768 .. 32,767)                                       | short
      i    | I*4  | four byte signed integer (-2,147,483,648 .. 2,147,483,647)                        | int
      q    | I*8  | Eight byte signed integer (-36,028,797,018,963,968 .. 36,028,797,018,963,967      | long long
      f    | R*4  | four byte floating point number                                                   | float
      d    | R*8  | eight byte floating point number                                                  | long float / double
           |      |                                                                                   |

   PS: DONT FORGET THE ENDIAN !!!
'''

RecordDefinitions = {
    0   : '---', # Testing records (will never be written)
    1   : 'FAR', # File Attribute Record -------> *MUST* be first record in stream!
    2   : 'CDR', # Calibration Due date Record
    3   : 'GOR', # Gain and Offset Record
    4   : 'GSR', # Generic String Record
    5   : 'GIR', # Generic Integer Record
    6   : 'GFR', # Generic Float Record
    7   : 'GTR', # Generic Time and date Record
    8   : 'GBR', # Generic BLOB record
    255 : 'MRR', # Master Result Record --------> *MUST* be last record in stream!
}

ImplementedRecords = [RecordDefinitions[k] for k in RecordDefinitions if k!=0]

TimeFields = ['CAL_DAT', 'CAL_DUE', 'GTR_VAL']

class SEDFError(Exception):
    pass

class SEDR(ABC):
    '''
    This is the Abstract Base Class Record for all SEDF records
    '''
    @abstractmethod
    def __init__(self, endian=None, record=None):
        self.__call__(endian, record)

    def __call__(self, endian = None, record = None):
        # id
        self.id = self.__class__.__name__
        # debug
        if not hasattr(self, 'debug'):
            self.debug = False
        if self.debug: print('-'*50, "> %s.__call__(%s, %s)" % (self.id, endian, record))
        self.buffer = b''
        # Endian
        if endian == None:
            self.endian = sys_endian()
        elif ((endian == '<') or (endian == '>')):
            self.endian = endian
        else:
            raise SEDFError("%s.__call__(%s, %s) : unsupported endian '%s'" % (self.id, endian, record, endian))
        # Sequence
        self.sequence = {self.fields[FieldID]['#']:FieldID for FieldID in self.fields}
        self._update()
        # Record
        if record != None:
            if self.debug: print("%s.__call__(%s, %s) : record length = %s bytes" % (self.id, endian, record, len(record)))
            self._unpack(record)
        if self.debug: print('<', '-'*50, " %s.__call(%s, %s)" % (self.id, endian, record))

    def get_fields(self, FieldID = None):
        '''
        Getter, returns a 5 element tuple (#, Type, Ref, Value, Text)
        '''
        if isinstance(FieldID, str) and FieldID in self.fields:
            return(self.fields[FieldID]['#'],
                   self.fields[FieldID]['Type'],
                   self.fields[FieldID]['Value'],
                   self.fields[FieldID]['Text'],
                   self.fields[FieldID]['Missing'])
        else:
            raise SEDFError("%s.get_value(%s) Error : '%s' is not a string or not a field key" % (self.id, FieldID, FieldID))

    def get_value(self, FieldID):
        '''
        Getter for only the value
        '''
        if isinstance(FieldID, str) and FieldID in self.fields:
            return self.fields[FieldID]['Value']
        else:
            raise SEDFError("%s.get_value(%s) Error : '%s' is not a string or not a field key" % (self.id, FieldID, FieldID))

    def set_value(self, FieldID, Value):
        '''
        Setter, sets the Value of the FieldID
        '''
        if not isinstance(FieldID, str) or FieldID not in self.fields:
            raise SEDFError("%s.set_value(%s, %s) : Error : '%s' is not a string or a field key" % (self.id, FieldID, Value, FieldID))

        Type = self.fields[FieldID]['Type']
        Type, Bytes = Type.split('*')

        if Type == 'U': # unsigned integer
            if not isinstance(Value, int):
                raise SEDFError("%s.set_value(%s, %s) Error : '%s' is not a an integer" % (self.id, FieldID, Value, Value))
            if Bytes == '1':
                if ((Value>=0) and (Value<=255)): temp = Value
                else: raise SEDFError("%s.set_value(%s, %s) Error : '%s' can not be casted into U*1" % (self.id, FieldID, Value, Value))
            elif Bytes == '2':
                if ((Value>=0) and (Value<=65535)): temp = Value
                else: raise SEDFError("%s.set_value(%s, %s) Error : '%s' can not be casted into U*2" % (self.id, FieldID, Value, Value))
            elif Bytes == '4':
                if ((Value>=0) and (Value<=4294967295)): temp = Value
                else: raise SEDFError("%s.set_value(%s, %s) Error : '%s' can not be casted into U*4" % (self.id, FieldID, Value, Value))
            elif Bytes == '8':
                if ((Value>=0) and (Value<=18446744073709551615)): temp = Value
                else: raise SEDFError("%s.set_value(%s, %s) Error : '%s' can not be casted into U*8" % (self.id, FieldID, Value, Value))
            else:
                raise SEDFError("%s.set_value(%s, %s) Error : '%s' is an unsupported Type" % (self.id, FieldID, Value, '*'.join((Type, Bytes))))
            self.fields[FieldID]['Value'] = temp
            if self.debug: print("%s._set_value(%s, %s) -> Value = %s" % (self.id, FieldID, Value, temp))
        elif Type == 'I': # signed integer
            if not isinstance(Value, int):
                raise SEDFError("%s.set_value(%s, %s) : '%s' is not an integer" % (self.id, FieldID, Value, Value))
            if Bytes == '1':
                if ((Value>=-128) and (Value<=127)): temp = Value
                else: raise SEDFError("%s.set_value(%s, %s) : '%s' can not be casted into I*1" % (self.id, FieldID, Value, Value))
            elif Bytes == '2':
                if ((Value>=-32768) and (Value<=32767)): temp = Value
                else: raise SEDFError("%s.set_value(%s, %s) : '%s' can not be casted into I*2" % (self.id, FieldID, Value, Value))
            elif Bytes == '4':
                if ((Value>=-2147483648) and (Value<=2147483647)): temp = Value
                else: raise SEDFError("%s.set_value(%s, %s) : '%s' can not be casted into I*4" % (self.id, FieldID, Value, Value))
            elif Bytes == '8':
                if ((Value>=-9223372036854775808) and (Value<=9223372036854775807)): temp = Value
                else: raise SEDFError("%s.set_value(%s, %s) : '%s' can not be casted into I*8" % (self.id, FieldID, Value, Value))
            else:
                raise SEDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldID, Value, '*'.join((Type, Bytes))))
            self.fields[FieldID]['Value'] = temp
            if self.debug: print("%s._set_value(%s, %s) -> Value = %s" % (self.id, FieldID, Value, temp))
        elif Type == 'R': # float
            if not isinstance(Value, float):
                raise SEDFError("%s.set_value(%s, %s) : '%s' is not a float" % (self.id, FieldID, Value, Value))
            if ((Bytes == '4') or (Bytes == '8')): temp = float(Value) # no checking for float & double, pack will cast with appropriate precision
            else: raise SEDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldID, Value, '*'.join((Type, Bytes))))
            self.fields[FieldID]['Value'] = temp
            if self.debug: print("%s._set_value(%s, %s) -> Value = %s" % (self.id, FieldID, Value, temp))
        elif Type == 'C': # string
            if not isinstance(Value, str):
                raise SEDFError("%s.set_value(%s, %s) Error : '%s' is not a python-string" % (self.id, FieldID, Value, Value))
            if Bytes == 'n':
                temp = Value.strip().encode()[:255].decode(errors='ignore')
            else:
                raise SEDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldID, Value, '*'.join((Type, Bytes))))
            self.fields[FieldID]['Value'] = temp
            if self.debug: print("%s._set_value(%s, %s) -> Value = %s" % (self.id, FieldID, Value, temp))
        else:
            raise SEDFError("%s.set_value(%s, %s) : Unsupported type '%s'" % (self.id, FieldID, Value, '*'.join((Type, Bytes))))
        self._update()

    def _type_size(self, FieldID):
        '''
        support function to determine the type size
        '''
        if not isinstance(FieldID, str) or FieldID not in self.fields:
            raise SEDFError("%s._type_size(%s) : Error : '%s' is not a string or a field key" % (self.id, FieldID, FieldID))

        Type = self.fields[FieldID]['Type']
        Type, Bytes = Type.split('*')

        if ((Type == 'U') or (Type == 'I')):
            if Bytes in ['1', '2', '4', '8']:
                retval = int(Bytes)
                if self.debug: print("%s._type_size('%s') = %s [%s] (%s)" % (self.id, FieldID, retval, '*'.join((Type, Bytes)), self.get_value(FieldID)))
                return retval
            else:
                raise SEDFError("%s_type_size('%s') : Unsupported type '%s'" % (self.id, FieldID, '*'.join((Type, Bytes))))
        elif Type == 'R':
            if Bytes in ['4', '8']:
                retval = int(Bytes)
                if self.debug: print("%s._type_size('%s') = %s [%s] (%s)" % (self.id, FieldID, retval, '*'.join((Type, Bytes)), self.get_value(FieldID)))
                return retval
            else:
                raise SEDFError("%s_type_size('%s') : Unsupported type '%s'" % (self.id, FieldID, '*'.join((Type, Bytes))))
        elif Type == 'C':
            if Bytes == 'n':
                str_as_bytes = self.fields[FieldID]['Value'].encode()
                retval = len(str_as_bytes)
                if retval > 255:
                    self.fields[FieldID]['Value'] = self.fields[FieldID]['Value'].encode()[:255].decode(errors='ignore') # cut to unicode boundary
                    retval = len(self.fields[FieldID]['Value'])
                retval+=1
                if self.debug: print("%s._type_size('%s') = %s [%s] ('%s')" % (self.id, FieldID, retval, '*'.join((Type, Bytes)), self.get_value(FieldID)))
                return retval
            else:
                raise SEDFError("%s_type_size('%s') : Unsupported type '%s'" % (self.id, FieldID, '*'.join((Type, Bytes))))

    def _update(self):
        '''
        Private method that updates the "bytes following the header" in the 'REC_LEN' field
        '''
        if self.debug: print('-'*50, "> %s._update() : REC_LEN = %s & CRC_ADLR = %s" % (self.id, self.get_value('REC_LEN'), self.get_value('CRC_ADLR')))
        # update Values
        for FieldID in self.fields:
            if self.fields[FieldID]['Value'] ==  None:
                self.fields[FieldID]['Value'] = self.fields[FieldID]['Missing']
                if self.debug: print("%s._update() Values : '%s' set to '%s' from missing" % (self.id, FieldID, self.get_value(FieldID)))
        # update REC_LEN
        reclen = 7
        for FieldID in self.fields:
            if FieldID not in ['CRC_ADLR', 'REC_LEN', 'REC_TYP']:
                fieldlen = self._type_size(FieldID)
                if self.debug: print("%s._update() REC_LEN : %s : %s + %s = %s" % (self.id, FieldID, reclen, fieldlen, reclen+fieldlen))
                reclen += fieldlen
        if self.debug: print("%s._update() REC_LEN : %s" % (self.id, reclen))
        self.fields['REC_LEN']['Value'] = reclen
        # update CRC_ADLR
        crc = 0
        for FieldID in self.fields:
            if FieldID != 'CRC_ADLR':
                crc = adler32(self._pack_item(FieldID), crc)
                if self.debug: print("%s._update() CRC_ADLR '%s' : %s " % (self.id, FieldID, crc))
        if self.debug: print("%s._update() CRC_ADLR %s" % (self.id, crc))
        self.fields['CRC_ADLR']['Value'] = crc
        if self.debug: print('<', '-'*50, " %s._update() : REC_LEN = %s & CRC_ADLR = %s" % (self.id, self.get_value('REC_LEN'), self.get_value('CRC_ADLR')))

    def _pack_item(self, FieldID):
        '''
        Private method that packs a field from the record and returns the packed version.
        '''
        if not isinstance(FieldID, str):
            raise SEDFError("%s._pack_item(%s) : '%s' a string" % (self.id, FieldID, FieldID))
        if FieldID not in self.fields:
            raise SEDFError("%s._pack_item(%s) : '%s' not a valid key" % (self.id, FieldID, FieldID))
        Value = self.fields[FieldID]['Value']

        if Value==None:
            if self.fields[FieldID]['Missing']!=None:
                Value=self.fields[FieldID]['Missing']
            else:
                raise SEDFError("%s._pack_item(%s) : no value present, and no 'missing' definition" % (self.id, FieldID,))

        TypeFormat = self.fields[FieldID]['Type']
        Type, Size = TypeFormat.split("*")
        fmt = ''
        pkg = b''
        if Type == 'U': # Unsigned integer
            if not isinstance(Value, int):
                if Value==None:
                    raise ValueError("%s._pack(%s)" % (self.id, FieldID))
                Value=int(Value)
            if Value < 0:
                Value=abs(Value)
            if Size.isdigit():
                if Size == '1': fmt = '%sB' % self.endian   # 1 byte unsigned integer(s) 0 .. 255
                elif Size == '2': fmt = '%sH' % self.endian # 2 byte unsigned integer(s) 0 .. 65.535
                elif Size == '4': fmt = '%sI' % self.endian # 4 byte unsigned integer(s) 0 .. 4.294.967.295
                elif Size == '8': fmt = '%sQ' % self.endian # 8 byte unsigned integer(s) 0 .. 18446744073709551615
                else:
                    raise SEDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldID, TypeFormat))
            else:
                raise SEDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldID, TypeFormat))
            pkg+=struct.pack(fmt, Value)
        elif Type == 'I': # Signed integer
            if not isinstance(Value, int):
                Value=int(Value)
            if Size.isdigit():
                if Size == '1': fmt = '%sb' % self.endian   # 1 byte signed integer(s) -128 .. +127
                elif Size == '2': fmt = '%sh' % self.endian # 2 byte signed integer(s) -32.768 .. +32.767
                elif Size == '4': fmt = '%si' % self.endian # 4 byte signed integer(s) -2.147.483.648 .. +2.147.483.647
                elif Size == '8': fmt = '%sq' % self.endian # 8 byte signed integer(s) -9.223.372.036.854.775.808 .. +9.223.372.036.854.775.807
                else:
                    raise SEDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldID, TypeFormat))
            else:
                raise SEDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldID, TypeFormat))
            pkg+=struct.pack(fmt, Value)
        elif Type == 'R': # floating point number
            if not isinstance(Value, float):
                Value=float(Value)
            if Size.isdigit():
                if Size == '4': fmt = '%sf' % self.endian # (list of) 4 byte floating point number(s) [float]
                elif Size == '8': fmt = '%sd' % self.endian # (list of) 8 byte floating point number(s) [double]
                else:
                    raise SEDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldID, TypeFormat))
            else:
                raise SEDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldID, TypeFormat))
            pkg+=struct.pack(fmt, Value)
        elif Type == 'C': # string
            if Size == 'n':
                if not isinstance(Value, str):
                    Value=str(Value)
                Value=Value.encode()
                K = len(Value)
                if K > 255:
                    K=255
                pkg+=struct.pack('B', K)
                pkg+=Value[:K]
            else:
                raise SEDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldID, TypeFormat))
        else:
            raise SEDFError("%s._pack_item(%s) : Unsupported type-format '%s'" % (self.id, FieldID, TypeFormat))
        return pkg

    def _pack(self):
        if self.debug: print('-'*50, "> %s._pack()" % self.id)
        # pack the body
        body = b''
        self._update()
        for item in range(3, len(self.sequence)):
            record = self._pack_item(self.sequence[item])
            if self.debug: print("%s._pack() '%s' : %s + %s = %s <> %s" %(self.id, self.sequence[item], len(body), len(record), len(body)+len(record), self.get_value('REC_LEN')-7))
            body += record
        # check the body length against the REC_LEN
        if self.fields['REC_LEN']['Value']-7 != len(body):
            raise SEDFError("%s.pack() length error %s != %s" % (self.id, self.fields['REC_LEN']['Value'], len(body)))
        # pack the header
        header = b''
        for item in range(0, 3):
            header += self._pack_item(self.sequence[item])
        # assemble the record
        retval = header + body
        if self.debug: print('<', '-'*50, " %s._pack() %s" % (self.id, retval))
        return retval


    def _unpack_item(self, FieldNr):
        if not isinstance(FieldNr, int):
            raise SEDFError("%s._unpack_item(%s) : '%s' should be an integer" % (self.id, FieldNr, FieldNr))
        if FieldNr not in self.sequence:
            raise SEDFError("%s._unpack_item(%s) : '%s' is an unknown FieldNr" % (self.id, FieldNr, FieldNr))
        FieldID = self.sequence[FieldNr]

        if len(self.buffer) == 0:
            if self.fields[FieldID]!=None:
                self.set_value(FieldID, self.fields[FieldID]['Missing'])
            else:
                raise SEDFError("%s._unpack_item(%s) : buffer is empty, and no 'missing' replacement available" % (self.id, FieldID))
        else:
            Type = self.fields[FieldID]['Type']
            Type, Bytes = Type.split("*")
            fmt = ''
            pkg = self.buffer
            if Type == 'U': # unsigned integer
                if Bytes.isdigit():
                    if Bytes == '1': fmt = "%sB" % self.endian   # unsigned char
                    elif Bytes == '2': fmt = "%sH" % self.endian # unsigned short
                    elif Bytes == '4': fmt = "%sL" % self.endian # unsigned long
                    elif Bytes == '8': fmt = "%sQ" % self.endian # unsigned long long
                    else:
                        raise SEDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldID, '*'.join((Type, Bytes))))
                    if len(self.buffer) < int(Bytes):
                        raise SEDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldID, Bytes, len(self.buffer)))
                    working_buffer = self.buffer[0:int(Bytes)]
                    self.buffer = self.buffer[int(Bytes):]
                    result = struct.unpack(fmt, working_buffer)[0]
                else:
                    raise SEDFError("%s._unpack_item(%s) : Unsupported type '%s'." % (self.id, FieldID, '*'.join((Type, Bytes))))
                if self.debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldID, hexify(pkg), '*'.join((Type, Bytes)), result))
                self.set_value(FieldID, result)
            elif Type == 'I': # signed integer
                if Bytes.isdigit():
                    if Bytes == '1': fmt = "%sb" % self.endian   # signed char
                    elif Bytes == '2': fmt = "%sh" % self.endian # signed short
                    elif Bytes == '4': fmt = "%sl" % self.endian # signed long
                    elif Bytes == '8': fmt = "%sq" % self.endian # signed long long
                    else:
                        raise SEDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldID, '*'.join((Type, Bytes))))
                    if len(self.buffer) < int(Bytes):
                        raise SEDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldID, Bytes, len(self.buffer)))
                    working_buffer = self.buffer[0:int(Bytes)]
                    self.buffer = self.buffer[int(Bytes):]
                    result = struct.unpack(fmt, working_buffer)[0]
                else:
                    raise SEDFError("%s._unpack_item(%s) : Unsupported type '%s'." % (self.id, FieldID, '*'.join((Type, Bytes))))
                if self.debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldID, hexify(pkg), '*'.join((Type, Bytes)), result))
                self.set_value(FieldID, result)
            elif Type == 'R': # float
                if Bytes.isdigit():
                    if Bytes == '4': fmt = "%sf" % self.endian # float
                    elif Bytes == '8': fmt = "%sd" % self.endian # double
                    else:
                        raise SEDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldID, '*'.join((Type, Bytes))))
                    if len(self.buffer) < int(Bytes):
                        raise SEDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldID, Bytes, len(self.buffer)))
                    working_buffer = self.buffer[0:int(Bytes)]
                    self.buffer = self.buffer[int(Bytes):]
                    result = struct.unpack(fmt, working_buffer)[0]
                else:
                    raise SEDFError("%s._unpack_item(%s) : Unsupported type '%s'." % (self.id, FieldID, '*'.join((Type, Bytes))))
                if self.debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldID, hexify(pkg), '*'.join((Type, Bytes)), result))
                self.set_value(FieldID, result)
            elif Type == 'C': # string
                if Bytes == 'n': # C*n
                    working_buffer = self.buffer[0:1]
                    self.buffer = self.buffer[1:]
                    n_bytes = struct.unpack('B', working_buffer)[0]
                    if len(self.buffer) < n_bytes:
                        raise SEDFError("%s._unpack_item(%s) : Not enough bytes in buffer (need %s while %s available)." % (self.id, FieldID, n_bytes, len(self.buffer)))
                    working_buffer = self.buffer[1:n_bytes]
                    self.buffer = self.buffer[n_bytes:] # consume buffer
                    result = working_buffer.decode(errors='ignore')
                else:
                    raise SEDFError("%s._unpack_item(%s) : Unsupported type '%s'." % (self.id, FieldID, '*'.join((Type, Bytes))))
                if self.debug: print("%s._unpack_item(%s)\n   '%s' [%s] -> %s" % (self.id, FieldID, hexify(pkg), '*'.join((Type, Bytes)), result))
                self.set_value(FieldID, result)
            else:
                raise SEDFError("%s._unpack_item(%s) : Unsupported type '%s'" % (self.id, FieldID, FieldID))

    def _unpack(self, record):
        '''
        Private method to unpack a record (including header -to-check-record-type-) and set the appropriate values in fields.
        '''
        if self.debug: print('-'*50, "> %s._unpack(%s)" % (self.id, record))
        if not isinstance(record, bytes):
            raise SEDFError("was expecting a byte array ... got a %s" % type(record))
        self.buffer = record
        if self.debug: print("%s._unpack(xx) with buffer length = %s" % (self.id, len(record)))
        if record[6] != self.fields['REC_TYP']['Value']:
            raise SEDFError("%s._unpack(%s) : REC_TYP doesn't match record" % (self.id, hexify(record)))
        for field in range(len(self.sequence)): # sort? no, better like this, if a code is missing it will explode :-)
            self._unpack_item(field)
        if self.debug: print('<', '-'*50, " %s._unpack(%s)" % (self.id, record))

    def __len__(self):
        return self.get_value('REC_LEN')

    def __repr__(self):
        return self._pack()

    def __str__(self):
        retval = "   %s\n" % self.id
        for field in sorted(self.sequence):
            retval += "      %s = '%s'" % (self.sequence[field], self.fields[self.sequence[field]]['Value'])
            retval += " [%s] (%s)" %  (self.fields[self.sequence[field]]['Type'], self.fields[self.sequence[field]]['Text'].strip())
            if self.sequence[field] in TimeFields:
                retval += " = %s" % DT(float(self.fields[self.sequence[field]]['Value']))
            retval += "\n"
        return retval

class FAR(SEDR):
    '''
    File Attributes Record
    '''
    def __init__(self, endian=None, record=None):
        self.id = 'FAR'
        self.local_debug = False
        self.buffer = b''
        self.fields = {
            # header
            'CRC_ADLR' : {'#' :  0, 'Type' :  'U*4', 'Value' : None, 'Text' : 'Adler32 checksum of the record                            ', 'Missing' :                     None},
            'REC_LEN'  : {'#' :  1, 'Type' :  'U*2', 'Value' : None, 'Text' : 'Bytes of data following header                            ', 'Missing' :                     None},
            'REC_TYP'  : {'#' :  2, 'Type' :  'U*1', 'Value' :    1, 'Text' : 'Record type                                               ', 'Missing' :                        1},
            # footer
            'CPU_TYP'  : {'#' :  3, 'Type' :  'U*1', 'Value' : None, 'Text' : 'The used endian                                           ', 'Missing' :                sys_cpu()},
            'SEDF_VER' : {'#' :  4, 'Type' :  'U*1', 'Value' : None, 'Text' : 'The version with wich this stream is created              ', 'Missing' :  __latest_SEDF_version__},
            'MAG_NUM'  : {'#' :  5, 'Type' :  'C*n', 'Value' : None, 'Text' : "The 'magic number'                                        ", 'Missing' :         __magic_number__}}
        self.__call__(endian, record)

class CDR(SEDR):
    '''
    Calibration and Due Date Record
    '''
    def __init__(self, endian=None, record=None):
        self.id = 'CDR'
        self.local_debug = False
        self.buffer = b''
        self.fields = {
            # header
            'CRC_ADLR' : {'#' :  0, 'Type' :  'U*4', 'Value' : None, 'Text' : 'Adler32 checksum of the record                            ', 'Missing' :                     None},
            'REC_LEN'  : {'#' :  1, 'Type' :  'U*2', 'Value' : None, 'Text' : 'Bytes of data following header                            ', 'Missing' :                     None},
            'REC_TYP'  : {'#' :  2, 'Type' :  'U*1', 'Value' :    2, 'Text' : 'Record type                                               ', 'Missing' :                        2},
            # footer
            'RSC_NAM'  : {'#' :  3, 'Type' :  'C*n', 'Value' : None, 'Text' : 'Name/SN of the resource that the calibration applies to   ', 'Missing' :                       ''},
            'CAL_INST' : {'#' :  4, 'Type' :  'C*n', 'Value' : None, 'Text' : 'Name/SN of the calibrator instrument                      ', 'Missing' :                       ''},
            'CAL_NAM'  : {'#' :  5, 'Type' :  'C*n', 'Value' : None, 'Text' : 'Name of the person/organization that did the calibration  ', 'Missing' :                       ''},
            'CAL_DAT'  : {'#' :  6, 'Type' :  'U*4', 'Value' : None, 'Text' : 'Calibration date                                          ', 'Missing' :               DT().epoch},
            'CAL_DUE'  : {'#' :  7, 'Type' :  'U*4', 'Value' : None, 'Text' : 'Next calibration due date                                 ', 'Missing' :                     None}}
        self.__call__(endian, record)

class GOR(SEDR):
    '''
    Gain and Offset Record
    '''
    def __init__(self, endian=None, record=None):
        self.id = 'GOR'
        self.local_debug = False
        self.buffer = b''
        self.fields = {
            # header
            'CRC_ADLR' : {'#' :  0, 'Type' :  'U*4', 'Value' : None, 'Text' : 'Adler32 checksum of the record                            ', 'Missing' :                     None},
            'REC_LEN'  : {'#' :  1, 'Type' :  'U*2', 'Value' : None, 'Text' : 'Bytes of data following header                            ', 'Missing' :                     None},
            'REC_TYP'  : {'#' :  2, 'Type' :  'U*1', 'Value' :    3, 'Text' : 'Record type                                               ', 'Missing' :                        3},
            # footer
            'RSC_NAM'  : {'#' :  3, 'Type' :  'C*n', 'Value' : None, 'Text' : 'Name/SN of the resource that the gain & offset apply to   ', 'Missing' :                     None},
            'CAL_INST' : {'#' :  4, 'Type' :  'C*n', 'Value' : None, 'Text' : 'Name/SN of the calibrator instrument                      ', 'Missing' :                       ''},
            'CAL_NAM'  : {'#' :  5, 'Type' :  'C*n', 'Value' : None, 'Text' : 'Name of the person/organization that did the calibration  ', 'Missing' :                       ''},
            'CAL_GAIN' : {'#' :  6, 'Type' :  'R*8', 'Value' : None, 'Text' : 'The Gain                                                  ', 'Missing' :                        0},
            'CAL_DUE'  : {'#' :  7, 'Type' :  'R*8', 'Value' : None, 'Text' : 'The Offset                                                ', 'Missing' :                        0},
            'CAL_UNT'  : {'#' :  8, 'Type' :  'C*n', 'Value' : None, 'Text' : 'Unit                                                      ', 'Missing' :                       ''}}
        self.__call__(endian, record)

class GSR(SEDR):
    '''
    Generic String Record
    '''
    def __init__(self, endian=None, record=None):
        self.id = 'GSR'
        self.local_debug = False
        self.buffer = b''
        self.fields = {
            # header
            'CRC_ADLR' : {'#' :  0, 'Type' :  'U*4', 'Value' : None, 'Text' : 'Adler32 checksum of the record                            ', 'Missing' :                     None},
            'REC_LEN'  : {'#' :  1, 'Type' :  'U*2', 'Value' : None, 'Text' : 'Bytes of data following header                            ', 'Missing' :                     None},
            'REC_TYP'  : {'#' :  2, 'Type' :  'U*1', 'Value' :    4, 'Text' : 'Record type                                               ', 'Missing' :                        4},
            # footer
            'GSR_KEY'  : {'#' :  3, 'Type' :  'C*n', 'Value' : None, 'Text' : "KEY identifying 'VAL'                                     ", 'Missing' :                     None},
            'GSR_VAL'  : {'#' :  4, 'Type' :  'C*n', 'Value' : None, 'Text' : 'VALue = up to 255 bytes long (utf-8 unicoded) string      ', 'Missing' :                       ''}}
        self.__call__(endian, record)

class GIR(SEDR):
    '''
    Generic Integer Record
    '''
    def __init__(self, endian=None, record=None):
        self.id = 'GIR'
        self.local_debug = False
        self.buffer = b''
        self.fields = {
            # header
            'CRC_ADLR' : {'#' :  0, 'Type' :  'U*4', 'Value' : None, 'Text' : 'Adler32 checksum of the record                            ', 'Missing' :                     None},
            'REC_LEN'  : {'#' :  1, 'Type' :  'U*2', 'Value' : None, 'Text' : 'Bytes of data following header                            ', 'Missing' :                     None},
            'REC_TYP'  : {'#' :  2, 'Type' :  'U*1', 'Value' :    5, 'Text' : 'Record type                                               ', 'Missing' :                        5},
            # footer
            'GIR_KEY'  : {'#' :  3, 'Type' :  'C*n', 'Value' : None, 'Text' : "KEY identifying 'VAL'                                     ", 'Missing' :                     None},
            'GIR_VAL'  : {'#' :  4, 'Type' :  'I*8', 'Value' : None, 'Text' : "VALue = 8 byte wide signed integer                        ", 'Missing' :                        0}}
        self.__call__(endian, record)

class GFR(SEDR):
    '''
    Generic Float Record
    '''
    def __init__(self, endian=None, record=None):
        self.id = 'GFR'
        self.local_debug = False
        self.buffer = b''
        self.fields = {
            # header
            'CRC_ADLR' : {'#' :  0, 'Type' :  'U*4', 'Value' : None, 'Text' : 'Adler32 checksum of the record                            ', 'Missing' :                     None},
            'REC_LEN'  : {'#' :  1, 'Type' :  'U*2', 'Value' : None, 'Text' : 'Bytes of data following header                            ', 'Missing' :                     None},
            'REC_TYP'  : {'#' :  2, 'Type' :  'U*1', 'Value' :    6, 'Text' : 'Record type                                               ', 'Missing' :                        6},
            # footer
            'GFR_KEY'  : {'#' :  3, 'Type' :  'C*n', 'Value' : None, 'Text' : "KEY identifying 'VAL'                                     ", 'Missing' :                     None},
            'GFR_VAL'  : {'#' :  4, 'Type' :  'R*8', 'Value' : None, 'Text' : "VALue = 8 byte wide float                                 ", 'Missing' :                        0}}
        self.__call__(endian, record)

class GTR(SEDR):
    '''
    Generic Time Record
    '''
    def __init__(self, endian=None, record=None):
        self.id = 'GTR'
        self.local_debug = False
        self.buffer = b''
        self.fields = {
            # header
            'CRC_ADLR' : {'#' :  0, 'Type' :  'U*4', 'Value' : None, 'Text' : 'Adler32 checksum of the record                            ', 'Missing' :                     None},
            'REC_LEN'  : {'#' :  1, 'Type' :  'U*2', 'Value' : None, 'Text' : 'Bytes of data following header                            ', 'Missing' :                     None},
            'REC_TYP'  : {'#' :  2, 'Type' :  'U*1', 'Value' :    7, 'Text' : 'Record type                                               ', 'Missing' :                        7},
            # footer
            'GTR_KEY'  : {'#' :  3, 'Type' :  'C*n', 'Value' : None, 'Text' : "KEY identifying 'VAL'                                     ", 'Missing' :                     None},
            'GTR_VAL'  : {'#' :  4, 'Type' :  'U*4', 'Value' : None, 'Text' : 'VALue = seconds since epoch                               ', 'Missing' :               DT().epoch}}
        self.__call__(endian, record)

class MRR(SEDR):
    '''
    Master Result Record
    '''
    def __init__(self, endian=None, record=None):
        self.id = 'MRR'
        self.local_debug = False
        self.buffer = b''
        self.fields = {
            # header
            'CRC_ADLR' : {'#' :  0, 'Type' :  'U*4', 'Value' : None, 'Text' : 'Adler32 checksum of the record                            ', 'Missing' :                     None},
            'REC_LEN'  : {'#' :  1, 'Type' :  'U*2', 'Value' : None, 'Text' : 'Bytes of data following header                            ', 'Missing' :                     None},
            'REC_TYP'  : {'#' :  2, 'Type' :  'U*1', 'Value' :  255, 'Text' : 'Record type                                               ', 'Missing' :                      255},
            # footer
            'REC_CNT'  : {'#' :  3, 'Type' :  'C*n', 'Value' : None, 'Text' : 'Record count of all preceding records (excluding this one)', 'Missing' :                     None},
            'CRC_ADLR' : {'#' :  4, 'Type' :  'U*4', 'Value' : None, 'Text' : 'Adler32 checksum over *ALL* records (excluding this one)  ', 'Missing' :                     None}}
        self.__call__(endian, record)

def create_object_from_record(record=None):
    '''
    given a (byte array) record, this function instantiates the object
    '''
    if record==None:
        return None
    if not isinstance(record, bytes):
        raise SEDFError("record is not a byte array")
    if len(record)<7:
        raise SEDFError("not a full record")
    recid = int(record[6])
    if recid not in RecordDefinitions:
        raise SEDFError("record id '%s' not defined" % recid)
    obj = None # just for the freaking editor so it stops complaining
    exec("obj = %s(%s)" % (RecordDefinitions[recid], record))
    return obj

if __name__ == '__main__':
    class TST(SEDR):
        def __init__(self, endian=None, record=None):
            import numpy as np
            self.debug=False
            self.fields = {
                # header
                'CRC_ADLR' : {'#' :  0, 'Type' :  'U*4', 'Value' : None, 'Text' : 'Adler32 checksum of the record                            ', 'Missing' :                     None},
                'REC_LEN'  : {'#' :  1, 'Type' :  'U*2', 'Value' : None, 'Text' : 'Bytes of data following header                            ', 'Missing' :                     None},
                'REC_TYP'  : {'#' :  2, 'Type' :  'U*1', 'Value' :    0, 'Text' : 'Record type                                               ', 'Missing' :                        0},
                # footer with all types for testing
                'U*1 Min'  : {'#' :  3, 'Type' :  'U*1', 'Value' : None, 'Text' : 'smallest value for a U*1                                  ', 'Missing' :   np.iinfo(np.uint8).min},
                'U*1 Max'  : {'#' :  4, 'Type' :  'U*1', 'Value' : None, 'Text' : 'biggest value for a U*1                                   ', 'Missing' :   np.iinfo(np.uint8).max},
                'U*2 Min'  : {'#' :  5, 'Type' :  'U*2', 'Value' : None, 'Text' : 'smallest value for a U*2                                  ', 'Missing' :  np.iinfo(np.uint16).min},
                'U*2 Max'  : {'#' :  6, 'Type' :  'U*2', 'Value' : None, 'Text' : 'biggest value for a U*2                                   ', 'Missing' :  np.iinfo(np.uint16).max},
                'U*4 Min'  : {'#' :  7, 'Type' :  'U*4', 'Value' : None, 'Text' : 'smallest value for a U*4                                  ', 'Missing' :  np.iinfo(np.uint32).min},
                'U*4 Max'  : {'#' :  8, 'Type' :  'U*4', 'Value' : None, 'Text' : 'biggest value for a U*4                                   ', 'Missing' :  np.iinfo(np.uint32).max},
                'U*8 Min'  : {'#' :  9, 'Type' :  'U*8', 'Value' : None, 'Text' : 'smallest value for a U*8                                  ', 'Missing' :  np.iinfo(np.uint64).min},
                'U*8 Max'  : {'#' : 10, 'Type' :  'U*8', 'Value' : None, 'Text' : 'biggest value for a U*8                                   ', 'Missing' :  np.iinfo(np.uint64).max},
                'I*1 Min'  : {'#' : 11, 'Type' :  'I*1', 'Value' : None, 'Text' : 'smallest value for a I*1                                  ', 'Missing' :    np.iinfo(np.int8).min},
                'I*1 Max'  : {'#' : 12, 'Type' :  'I*1', 'Value' : None, 'Text' : 'biggest value for a I*1                                   ', 'Missing' :    np.iinfo(np.int8).max},
                'I*2 Min'  : {'#' : 13, 'Type' :  'I*2', 'Value' : None, 'Text' : 'smallest value for a I*2                                  ', 'Missing' :   np.iinfo(np.int16).min},
                'I*2 Max'  : {'#' : 14, 'Type' :  'I*2', 'Value' : None, 'Text' : 'biggest value for a I*2                                   ', 'Missing' :   np.iinfo(np.int16).max},
                'I*4 Min'  : {'#' : 15, 'Type' :  'I*4', 'Value' : None, 'Text' : 'smallest value for a I*4                                  ', 'Missing' :   np.iinfo(np.int32).min},
                'I*4 Max'  : {'#' : 16, 'Type' :  'I*4', 'Value' : None, 'Text' : 'biggest value for a I*4                                   ', 'Missing' :   np.iinfo(np.int32).max},
                'I*8 Min'  : {'#' : 17, 'Type' :  'I*8', 'Value' : None, 'Text' : 'smallest value for a I*8                                  ', 'Missing' :   np.iinfo(np.int64).min},
                'I*8 Max'  : {'#' : 18, 'Type' :  'I*8', 'Value' : None, 'Text' : 'biggest value for a I*8                                   ', 'Missing' :   np.iinfo(np.int64).max},
                'R*4 Min'  : {'#' : 19, 'Type' :  'R*4', 'Value' : None, 'Text' : 'smallest value for a R*4                                  ', 'Missing' : np.finfo(np.float32).min},
                'R*4 Max'  : {'#' : 20, 'Type' :  'R*4', 'Value' : None, 'Text' : 'biggest value for a R*4                                   ', 'Missing' : np.finfo(np.float32).max},
                'R*8 Min'  : {'#' : 21, 'Type' :  'R*8', 'Value' : None, 'Text' : 'smallest value for a R*8                                  ', 'Missing' : np.finfo(np.float64).min},
                'R*8 Max'  : {'#' : 22, 'Type' :  'R*8', 'Value' : None, 'Text' : 'biggest value for a R*8                                   ', 'Missing' : np.finfo(np.float64).max},
                'C*n Min'  : {'#' : 23, 'Type' :  'C*n', 'Value' : None, 'Text' : 'An empty string                                           ', 'Missing' :                       ''},
                'C*n utf-8': {'#' : 24, 'Type' :  'C*n', 'Value' : None, 'Text' : 'An unicode (utf-8) string                                 ', 'Missing' :'μV ΔT °C ≤≥ àáâãäçèéêëö'},
                'C*n Max'  : {'#' : 25, 'Type' :  'C*n', 'Value' : None, 'Text' : 'A string capped to 255 (unicode) characters               ', 'Missing' :                  'ö'*300}}
            self.__call__(endian, record)

    tst = TST()
    tst_pack = tst._pack()
    print(tst)
    endian = tst.endian
    record = tst._pack()
    brol = TST()
    brol(endian, record)
    print(brol)
    brol_pack = brol._pack()
    print(tst_pack)
    print(brol_pack)
