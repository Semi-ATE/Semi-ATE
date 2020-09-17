'''
Created on Aug 15, 2019

@author: hoeren

The hashing algorithm used is md5!
'''
import bz2
import gzip
import lzma
import os
from hashlib import md5 as hasher

from ATE.Data.Formats.STDF.utils import is_STDF
from ATE.utils.compression import supported_compressions
from ATE.utils.magicnumber import (
    extension_from_magic_number_in_file,
    is_compressed_file
)


def file_contents_hash(FileName):
    '''
    This function returns the md5 (hex) digest (in string format) of the file contents of FileName.
    If the given file is in one of the given supportd_compressions, then the hash is
    created from the uncompressed contents!
    if something goes wrong, an empty string is returned.
    '''
    retval = ''
    if os.path.exists(FileName) and os.path.isfile(FileName) and is_STDF(FileName):
        _hash = hasher()
        if is_compressed_file(FileName, supported_compressions):
            compression_lookup = dict((v,k) for k,v in supported_compressions.items())
            ext = extension_from_magic_number_in_file(FileName)
            if len(ext)!=1:
                raise Exception("WTF!")
            compression = compression_lookup[ext]
            if compression=='lzma':
                with lzma.open(FileName, 'rb') as fd:
                    for chunk in iter(lambda: fd.read(_hash.block_size), b''):
                        _hash.update(chunk)
                retval = _hash.hexdigest()
            elif compression=='bz2':
                with bz2.open(FileName, 'rb') as fd:
                    for chunk in iter(lambda: fd.read(_hash.block_size), b''):
                        _hash.update(chunk)
                retval = _hash.hexdigest()
            elif compression=='gzip':
                with gzip.open(FileName, 'rb') as fd:
                    for chunk in iter(lambda: fd.read(_hash.block_size), b''):
                        _hash.update(chunk)
                retval = _hash.hexdigest()
            else:
                raise Exception("Supported but un-implemented compression '%s'" % compression)
        else:
            with open(FileName, 'rb') as fd:
                for chunk in iter(lambda: fd.read(_hash.block_size), b''):
                    _hash.update(chunk)
            retval = _hash.hexdigest()
    return retval

def is_hash_name(FileName):
    '''
    This function will return True if FileName could be a hashname.
    '''
    if not isinstance(FileName, str): return False
    if not os.path.exists(FileName): return False
    if not os.path.isfile(FileName): return False
    basename = os.path.split(FileName)[1].split('.')[0]
    _hash = hasher()
    if len(basename)!=len(_hash.hexdigest()): return False
    try:
        int(basename, 16)
    except:
        return False
    else:
        return True

def has_good_hash(FileName):
    '''
    '''



if __name__ == '__main__':
    pass
