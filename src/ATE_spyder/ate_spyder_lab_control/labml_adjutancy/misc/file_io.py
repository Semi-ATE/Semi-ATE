"""
Created on Fri Apr 12 15:58:04 2019

@author: started from pytestsharing/misc/file_io.py   (Matthis Scheulin)
         rework and add some Function C.Jung

"""
# from pytestsharing.instruments.base_instrument import logger
from labml_adjutancy.misc.common import choice
from labml_adjutancy.misc.common import str2num
import os
import pathlib
import inspect


def help():
    print("Lists all functions available in file_io module:")
    print("********************************************************")
    print(readVlogMemFile.__doc__)
    print("********************************************************")
    print(writeVlogMemFile.__doc__)


NETWORK = '//samba'


def openFile(fileName, *argv, **kwargs):
    '''open a file with name= fileName

        - fileName could contain $Variable, this will be interpret with os.environ.get('$Variable')
        - if os = windows and filename start with '/' than add //samba
    '''
    fileName = replaceFilename(fileName)
    file = None
    try:
        file = open(fileName, *argv, **kwargs)
    except Exception:
        #logger.error(f'{inspect.stack()[1][3]}: Cannot open {fileName}')
        print(f'ERROR: {inspect.stack()[1][3]}: Cannot open {fileName}')
    return file


def replaceFilename(fileName):
    if fileName.find('$') > -1:   # find environment variables inside the value?
        tmp = fileName.split('/')
        index = 0
        for s in tmp:
            if s.find('$') == 0:
                env = os.environ.get(s[1:])
                tmp[index] = env if env is not None else ''
            index += 1
        fileName = '/'.join(tmp)
    if len(fileName) > 0 and fileName[0] == '/' and os.name == "nt" and fileName.find(NETWORK) != 0:
        fileName = NETWORK + fileName
    return fileName


def readMemFile(filename, typ=None, interpret=None):
    """
    read a memory-file and  alocate data.

    Parameters
    ----------
    filename : TYPE
        DESCRIPTION.
    typ : TYPE
        DESCRIPTION.

    Returns
    -------
    data : memory data integer list, None entries for
            not used/initialized values
    """
    extensions = {'v': 'verilog',
                  'txt': 'txt'}
    start = None
    if typ is None:
        file_extension = pathlib.Path(filename).suffix[1:]
        if file_extension in extensions.keys():
            typ = extensions[file_extension]
        else:
            typ = f'.{file_extension}'
    if not choice(typ, ['verilog', 'txt']):
        return False
    if typ == 'verilog':
        data = readVlogMemFile(filename, 100)      # TODO!:  change  readVlogMemFile to get automatically the size
    elif typ == 'txt':
        start, data = readtxtMemFile(filename, interpret)
    return start, data


def readtxtMemFile(fileName, memSize=None, interpret=None):
    """
    reads a file with memory data in simple hex or integer format.

    Parameters
    ----------
    fileName : string
        DESCRIPTION.
    memSize : TYPE
        DESCRIPTION.
    interpret : {adr : base
                 dat : base}    # base could be 10 or 16

    Returns
    -------
     startadress : integer
     data : memory data integer list, None entries for
         not used/initialized values

    """
    file = openFile(fileName)
    if file is None:
        return None
    data = []
    for line in file:
        parts = line.split()
        base = 10
        for index in range(0, len(parts)):
            value = parts[index]
            base = 16 if value.find('0x') == 0 else base
            if index == 0 and (interpret is not None and 'adr' in interpret.keys()):
                base = interpret['adr']
            elif index != 0 and (interpret is not None and 'dat' in interpret.keys()):
                base = interpret['dat']
            value = str2num(value, base)
            if index == 0:
                adr = value
                continue
            data.append((adr, value))
            adr += 1
    file.close()
    minadr = min(data)[0]
    maxadr = max(data)[0]+1
    array = [None]*(maxadr-minadr)
    for index in range(0, len(data)):
        array[data[index][0]-minadr] = data[index][1]
    return minadr, array


def readQEMemFile(fileName, base=0x20):
    """
    reads a file with memory data in the DUMP_QE Software format:
        base address 0
        address 0
        data hex	0000	data dec	0
        address 1
        data hex	0000	data dec	0

    Parameters
    ----------
    fileName : string
        DESCRIPTION.

    Returns
    -------
     startadress : integer
     data : memory data integer list, None entries for
         not used/initialized values

    """
    file = openFile(fileName)
    if file is None:
        return None
    data = []
    for line in file:
        parts = line.split()
        if parts[0] == 'base':
            baseadr = int(parts[2])
            continue
        elif parts[0] == 'address':
            adr = baseadr * base + int(parts[1])
        elif parts[0] == 'data':
            value = str2num(parts[2], 16)
            data.append((adr, value))
    file.close()
    minadr = min(data)[0]
    maxadr = max(data)[0]+1
    array = [None]*(maxadr-minadr)
    for index in range(0, len(data)):
        array[data[index][0]-minadr] = data[index][1]
    return minadr, array

def readVlogMemFile(fileName, memSize, debug=False):
    """
    readVlogMemFile(fileName, debug=False)

    reads a file with memory data in verilog hex format

      fileName........path to verilog file
      memSize.........number of memory addresses
      debug...........if True it prints out the data loaded

    return data

      data............memory data integer list, None entries for
                      not used/initialized values

    """
    fi = openFile(fileName, 'rt')
    if fi is None:
        return fi
    # try:
    #     fi = open(fileName, 'rt')
    # except Exception:
    #     print(f'VlogMemFile ERROR: Cannot open {fileName}')
    #     return None
    data = [None]*(memSize)
    i = 0
    for line in fi:
        parts = line.split()
        try:
            if parts[0][0] == "@":
                i = int(parts[0][1:], 16)
                v = int(parts[1], 16)
            else:
                v = int(parts[0], 16)
            if i < len(data):
                data[i] = v
            else:
                #logger.error('VlogMemFile: %s > %d value(s)' % (fileName, memSize))
                print('ERROR: VlogMemFile: %s > %d value(s)' % (fileName, memSize))
                fi.close()
                return
            i += 1
        except Exception:
            continue
    #logger.info('VlogMemFile: %s read with %d value(s)' % (fileName, len(data)))
    print('VlogMemFile: %s read with %d value(s)' % (fileName, len(data)))
    if debug:
        for i, v in enumerate(data):
            # logger.debug('0x%X: 0x%X' % (i, v))
            print('0x%X: 0x%X' % (i, v))
    fi.close()
    return data


def writeVlogMemFile(fileName, mem, a_dig=4, d_dig=8, header=["", "verilog memory data file", ""]):
    """
    writeVlogMemFile(fileName, mem, a_dig, d_dig, comment)

    writes memory data to a file in verilog hex format

      fileName........path to verilog file
      mem.............list with integer memory data
      a_dig...........min address digits
      d_dig...........min data digits
      header..........string list placed as comments
                      at top of file

    return True/False

    """
    fi = openFile(fileName, 'wt', newline='\n')
    if fi is None:
        return False
    for comment in header:
        fi.write(f'// {comment}\n')
    for i, v in enumerate(mem):
        if v is not None:
            fi.write('@{:0{}x} {:0{}x}\n'.format(i, a_dig, v, d_dig))
    fi.write(' ')
    fi.close()
    return True


if __name__ == '__main__':
    data = [1, 2, 3, 4, 5]
    writeVlogMemFile('schrott.v', data)
