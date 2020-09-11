'''
Created on 16 Aug 2019

@author: tho
'''

import os
import struct
from zlib import adler32

from ATE.Data.Formats.SEDF.records import (
    SEDR,
    SEDFError,
    __latest_SEDF_version__,
    __magic_number__,
    create_object_from_record,
    sys_cpu,
    sys_endian
)


def SEDFopen(FileName, mode):
    '''
    the opener to use with the 'with' statement
    '''
    if not isinstance(mode, str):
        raise SEDFError("mode must be a string")
    if mode in ['r', 'rb']:
        return sedf_file_object(FileName, mode)
    elif mode in ['w', 'wb', 'a', 'ab']:
        pass
    elif '+' in mode:
        raise SEDFError("a file can not be opened for reading *AND* writing")
    else:
        raise SEDFError("unsupported file mode '%s'" % mode)

class sedf_file_object(object):
    def __init__(self, FileName, mode):
        self.fd = None
        if not isinstance(FileName, str): return
        if not os.path.exists(FileName): return
        if not os.path.isfile(FileName): return
        self.FileName = FileName
        if mode in ['rb', 'r']: # reading -> endian & version from file
            self.mode = 'rb'
            self._endian_and_version_from_file()
            self.fd = open(self.FileName, self.mode)
        elif mode in ['wb', 'w']: # writing -> endian & version from system
            self.mode = 'wb'
            self.endian = sys_endian()
            self.cpu = sys_cpu()
            self.version = __latest_SEDF_version__
            self.fd = open(FileName, self.mode)
        elif mode == ['a', 'ab']: # append = writing at end -> endian & version from file
            self.mode = 'ab'
            self._endian_and_version_from_file()
            self.fd = open(FileName, self.mode)
        elif '+' in mode:
            raise SEDFError("SEDF files can not be opened for reading *AND* writing")
        else:
            raise SEDFError("unsupported mode '%s' for SEDF files" % mode)

    def _endian_and_version_from_file(self):
        tfd = open(self.FileName, 'rb')
        header = tfd.read(9)
        CPU_TYP = struct.unpack('B', header[7])
        self.cpu = CPU_TYP
        if self.cpy == 1:
            self.endian = '>'
        else:
            self.endian = '<'
        CRC_ADLR = struct.unpack('%sI'%self.endian, header[:4])
        REC_LEN = struct.unpack('%sH'%self.endian, header[4:6])
        REC_TYP = struct.unpack('%sB'%self.endian, header[6])
        if REC_TYP!=1:
            tfd.close()
            raise SEDFError("Not a FAR")
        SEDF_VER = struct.unpack('%sB'%self.endian, header[9])
        self.version = SEDF_VER
        footer = tfd.read(REC_LEN-9)
        tfd.close()
        string_size = struct.unpack('%sB'%self.endian, footer[0])
        MAG_NUM = str(footer[1:string_size+1])
        if MAG_NUM!=__magic_number__:
            raise SEDFError("Can not find the magic number")
        REC = header+footer
        if CRC_ADLR != adler32(REC[4:]):
            raise SEDFError("CRC Error on FAR")

    def peek(self, nbytes):
        '''
        reads nbytes from fd and rewind the position afterwards
        '''
        if self.mode != 'rb': return ''
        if not isinstance(nbytes, int): return ''
        if nbytes < 1 : return ''
        position = self.fd.tell()
        retval = self.fd.read(nbytes)
        self.fd.seek(position)
        return retval

    def read(self):
        '''
        reads the next SEDF record from self.fd
        '''
        REC = b''
        if self.mode == 'rb' and self.fd!=None:
            header = self.fd.read(7)
            REC_LEN = struct.unpack('%sH'%self.endian, header[4:6])
            footer = self.fd.read(REC_LEN-7)
            REC = header+footer
            if REC[6] == 255: # last record in a stream
                self.fd.close()
                self.fd = None
        return REC

    def write(self, obj):
        '''
        writes obj to self.fd
        if object is a byte array, write it verbatim,
        if object is an instance of SEDR then write the packed form.
        '''
        if fd.mode in ['ab', 'wb'] and self.fd!=None:
            if isinstance(obj, bytes):
                self.fd.write(obj)
            if isinstance(obj, SEDR):
                self.fd.write(obj.__repr__())

    def close(self):
        '''
        writes the MIR record and closes the stream.
        '''
        self.fd.close()
        self.fd = None

    def seek(self, ):
        pass

    def tell(self):
        return self.fd.tell()

class objects_from_file(sedf_file_object):
    '''
    This is a iterator for SEDF's file object
    '''
    def __init__(self, FileName, mode):
        if not isinstance(mode, str) or not isinstance(FileName, str):
            raise SEDFError("FileName and mode *must* be strings")
        if mode in ['rb', 'r']:
            super().__init__(FileName, mode)
        else:
            raise SEDFError("%s is a read iterator" % self.__class__.__name__)

    def __del__(self):
        if self.fd != None:
            self.fd.close()
            self.fd = None

    def __iter__(self):
        return self

    def __next__(self):
        while self.fd!=None:
            while True:
                record = self.read()
                if record == None:
                    raise StopIteration
                if int(struct.unpack('B', record[6])) == 255:
                    pass

                return create_object_from_record(self.read())


                header = self.fd.read(7)
                if len(header)!=7:
                    raise StopIteration
                REC_LEN, REC_TYP, REC_SUB = struct.unpack(self.unpack_fmt, header)
                footer = self.fd.read(REC_LEN)
                if len(footer)!=REC_LEN:
                    raise StopIteration
                return REC_LEN, REC_TYP, REC_SUB, header+footer


if __name__ == '__main__':
    FileName = r'C:\var\dev\eeprom'
    with SEDFopen(FileName, 'rb') as eeprom:
        for obj in eeprom:
            print(obj)

    for obj in objects_from_file(FileName, 'rb'):
        print(obj)

    fd = SEDFopen(FileName, 'rb')
    print(fd.read)
    fd.seek(-1)
    fd.close()
