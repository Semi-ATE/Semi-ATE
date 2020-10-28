'''
Created on Sep 13, 2019

@author: hoeren
'''
import bz2
import gzip
import lzma
import os
import sys

import tqdm
from ATE.utils import DT
from ATE.utils.magicnumber import extension_from_magic_number_in_file

supported_compressions = {'lzma' : '.xz', 'gzip' : '.gz', 'bz2' : '.bz2'}
supported_compressions_extensions = {supported_compressions[k]:k for k in supported_compressions}
default_compression = 'lzma'

if default_compression not in supported_compressions:
    raise KeyError("%s not in %s" % (default_compression, supported_compressions))

def deflate(FileNames, compression=default_compression, progress=True, bs=128*1024, use_hash=False):
    '''
    compresses all give 'FileNames'

    TODO: add the hashing possibility
    '''
    def comp(FileName, compression='lzma', annotation='', bs=128*1024, progress=False, indent=0, callback=None):
        lbl = "Compressing %s : '%s' with %s" % (annotation, os.path.split(FileName)[1], compression)
        ttl = os.stat(FileName)[6]
        dt = DT(FileName)
        pb = tqdm.tqdm(total=ttl, desc=lbl, unit='B', unit_scale=True, leave=False, disable=not progress, position=indent)
        ext = supported_compressions[compression]
        if compression=='lzma':
            with open(FileName, 'rb') as fdi, lzma.open(FileName+ext, 'wb') as fdo:
                chunk = fdi.read(bs)
                while len(chunk) == bs:
                    fdo.write(chunk)
                    pb.update(bs)
                    if progress and callback!=None: callback(bs)
                    chunk = fdi.read(bs)
                fdo.write(chunk)
                pb.update(bs)
                if progress and callback!=None: callback(bs)
            os.utime(FileName+ext, times=(dt.epoch, dt.epoch))
        elif compression=='bz2':
            with open(FileName, 'rb') as fdi, bz2.open(FileName+ext, 'wb') as fdo:
                chunk = fdi.read(bs)
                while len(chunk) == bs:
                    fdo.write(chunk)
                    pb.update(bs)
                    if progress and callback!=None: callback(bs)
                    chunk = fdi.read(bs)
                fdo.write(chunk)
                pb.update(bs)
                if progress and callback!=None: callback(bs)
            os.utime(FileName+ext, times=(dt.epoch, dt.epoch))
        elif compression=='gzip':
            with open(FileName, 'rb') as fdi, gzip.open(FileName+ext, 'wb') as fdo:
                chunk = fdi.read(bs)
                while len(chunk) == bs:
                    fdo.write(chunk)
                    pb.update(bs)
                    if progress and callback!=None: callback(bs)
                    chunk = fdi.read(bs)
                fdo.write(chunk)
                pb.update(bs)
                if progress and callback!=None: callback(bs)
            os.utime(FileName+ext, times=(dt.epoch, dt.epoch))
        else:
            raise Exception("Supported but un-implemented compression '%s'" % compression)
        pb.close()

    if compression not in supported_compressions:
        raise Exception("don't know how to handle '%s' compression" % compression)

    if isinstance(FileNames, str): # single file
        comp(FileNames, progress=progress)
    if isinstance(FileNames, list): # multiple files
        label = "%s progress of %d files" % (compression, len(FileNames))
        total = 0
        for FileName in FileNames:
            total+=os.stat(FileName)[6]
        tpb = tqdm.tqdm(total=total, desc=label, unit='B', unit_scale=True, leave=False, disable=not progress)
        for FileNumber, FileName in enumerate(FileNames):
            annotation = 'file %s/%s' % (FileNumber+1, len(FileNames))
            comp(FileName, annotation = annotation, progress=progress, indent=1, callback=tpb.update)
        tpb.close()

def inflate(FileNames, progress=True, bs=128*1024):
    '''
    de-compress *ALL* given FileNames
    '''
    def decomp(FileName, compression='lzma', annotation='', bs=128*1024, progress=False, indent=0, callback=None):
        pass

def get_deflated_file_size(FileName):
    '''
    This function returns the (deflated) file size of FileName.

    if FileName is a compressed file, but not supported, -1 is returned.
    if FileName is not (recognized) as a compressed file, the filesize is returned.
    '''
    compression = ''
    ext = extension_from_magic_number_in_file(FileName, list(supported_compressions_extensions))
    if len(ext) == 1:
        compression = supported_compressions_extensions[ext[0]]

    if compression=='lzma':
        with lzma.open(FileName, 'rb') as fd:
            fd.seek(0, 2)
            size = fd.tell()
    elif compression=='bz2':
        with bz2.open(FileName, 'rb') as fd:
            fd.seek(0, 2)
            size = fd.tell()
    elif compression=='gzip':
        with gzip.open(FileName, 'rb') as fd:
            fd.seek(0, 2)
            size = fd.tell()
    else:
        with open(FileName, 'rb') as fd:
            fd.seek(0,2)
            size = fd.tell()
    return size

if __name__ == '__main__':
    from ATE.Data.Formats.STDF import get_stdf_files, get_stdf_gz_files, get_stdf_bz2_files, get_stdf_zx_files
    from myconsole import stdf_resources

    stdf_files = get_stdf_files(stdf_resources)
    deflate(stdf_files, compression='gzip') # gzip
    deflate(stdf_files, compression='bz2') # bz2
    deflate(stdf_files) # lzma, default
