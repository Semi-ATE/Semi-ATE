"""
Created on Fri Apr 12 15:58:04 2019

@author: started from pytestsharing/misc/file_io.py   (Matthis Scheulin)
         rework and add some Function C.Jung

"""
# from pytestsharing.instruments.base_instrument import logger
from labml_adjutancy.misc.common import choice
from labml_adjutancy.misc.common import str2num
from labml_adjutancy.misc.common import complement_num
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
        # logger.error(f'{inspect.stack()[1][3]}: Cannot open {fileName}')
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


def loadIHexFile(fileName, bytemem=None, size=0x10000):
    """
    loadIHexFile(fileName, bytemem=None, size=0x10000)

    reads the ihex file(s) and builds a byte image

      ihexfileName....path to IntelHex file
      bytemem.........byte image, default=None
      size............size of byte memory, default 64kB


    return bytemem    or None if fileName not exist
    """

    try:
        fop = open(fileName, 'rt')
        print('loadIHexFile: open %s' % fileName)
    except Exception:
        print('loadIHexFile: Cannot open %s' % fileName)
        return None

    if bytemem is None:
        bytemem = [0] * size
    firstaddr = 0xffffffff
    lastaddr = 0x0
    addr_offset = 0
    # read const file
    for line in fop:
        if line[0:3] != ':00' and line[7:9] == '00':                # Data Record (Typ 00)
            byte_count = int(line[1:3], 16)
            addr = int(line[3:7], 16) + addr_offset
            if addr < firstaddr:
                firstaddr = addr
            if addr < size:
                if addr+byte_count-1 > lastaddr:
                    lastaddr = addr+byte_count-1
                    for i in range(byte_count):
                        bytemem[addr + i] = int(line[9 + (i * 2):11 + (i * 2)], 16)
        elif line[7:9] == '01':                                    # Enf of File Record (Typ 01)
            break
        elif line[7:9] == '02':                                    # Extended Segment Address Record (Typ 02)
            addr_offset = line[10:12] << 4
    fop.close()
    print('  Read IHex image in address range 0x%0X to 0x%0X' % (firstaddr, lastaddr))
    return bytemem


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
        start, data = readVlogMemFile(filename, 0)      # TODO!:  change  readVlogMemFile to get automatically the size
    elif typ == 'txt':
        start, data = readtxtMemFile(filename, interpret)
    return start, data


def readtxtMemFile(fileName, memSize=None, bitsize_source=None, bitsize_target=None, numerative=None, raw_data=False):
    """
    Read a file with memory data in simple hex or integer format.

    Parameters
    ----------
    fileName : string
        DESCRIPTION.
    memSize : int
        size from the reserved memory array.
    bitsize_source: int
        size from one datum, e.q. 8-bit, 16-bit, must be multiple times of 8
        this has an effect on the adress counting
        if None each datum will assign to an adress, otherwise each 8-bit datum has an adress
        only little endian is supported yet
    bitsize_target: int
        size from one datum in the array result.
            needed if negative values in the sourcefile
    numerative : {adr : base
                 dat : base}    # base could be 10(decimal) or 16(hex)
    raw_data: bool
        if True than return with a list of adr + data
        if False than return with a coherent memory, beginning with startadr

    Returns
    -------
     startadress : integer
     data : memory data integer list, None entries for
         not used/initialized values

    """
    file = openFile(fileName)
    if file is None:
        return None
    base_adr = numerative['adr'] if (numerative is not None and 'adr' in numerative.keys()) else 10
    base_dat = numerative['dat'] if (numerative is not None and 'dat' in numerative.keys()) else 10

    data = []
    for line in file:
        parts = line.split()
        for index in range(0, len(parts)):
            value = parts[index]
            if value == '//':
                break
            value = str2num(value, base_adr if index == 0 else base_dat)
            if type(value) == str:
                continue
            if index == 0:
                adr = value
                continue
            if bitsize_source is None:
                data.append((adr, value))
            else:
                for i in range(bitsize_source // 8):
                    data.append((adr, value % 256))
                    value = value // 256
                    adr += 1
                continue
            adr += 1
    file.close()
    if raw_data:
        return data
    minadr = min(data)[0]
    maxadr = max(data)[0]+1
    bitsize_source = 8 if bitsize_source is None else bitsize_source
    array = [None]*((maxadr-minadr) // (bitsize_source//8)) if memSize is None else [None]*memSize
    adr = minadr
    for index in range(0, len(data)):
        adr = data[index][0]
        dat = data[index][1]
        realadr = (adr-minadr) // (bitsize_source//8)
        oldat = 0 if array[realadr] is None else array[realadr]
        shift = adr % (bitsize_source//8)
        array[realadr] = (dat << (shift*8)) + oldat
    if bitsize_target is not None:
        for index in range(0, len(array)):
            if array[index] < 0:
                array[index] = complement_num(abs(array[index]), bitsize_target) + 1   # calculated 2 complement
    return minadr, array


def readQEMemFile(fileName, base=0x20):
    """Read a file with memory data in the DUMP_QE Software format.

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


def readVlogMemFile(fileName, memSize=0, defaultvalues=None, debug=False):
    """
    readVlogMemFile(fileName, debug=False)

    reads a file with memory data in verilog hex format

      fileName........path to verilog file
      memSize.........number of memory addresses, if 0 then calculate from the data of the file
      debug...........if True it prints out the data loaded

    return data

      data............memory data integer list, None entries for
                      not used/initialized values

    """
    fi = openFile(fileName, 'rt')
    if fi is None:
        return fi

    startadr = 0
    calc_memSize = 0
    for line in fi:
        parts = line.split()
        try:
            if len(parts) == 0 or (len(parts) > 0 and parts[0] == '//'):
                continue
            elif parts[0][0] == "@":
                adr = int(parts[0][1:], 16)
                calc_memSize = adr if adr >= calc_memSize else calc_memSize
                startadr = adr if adr <= startadr else startadr
                parts.pop(0)
            if len(parts) > 0:
                for value in parts:
                    int(value, 16)
                    memSize += 1
        except Exception:
            continue
    fi.seek(0)

    memSize = calc_memSize if memSize == 0 else memSize
    data = [defaultvalues]*(memSize)
    adr = 0
    for line in fi:
        parts = line.split()
        try:
            if len(parts) == 0 or (len(parts) > 0 and parts[0] == '//'):
                continue
            elif parts[0][0] == "@":
                adr = int(parts[0][1:], 16)
                v = int(parts[1], 16)
            else:
                v = int(parts[0], 16)
            if adr < len(data):
                data[adr] = v
            else:
                # logger.error('VlogMemFile: %s > %d value(s)' % (fileName, memSize))
                print('ERROR: VlogMemFile: %s > %d value(s)' % (fileName, memSize))
                fi.close()
                return
            adr += 1
        except Exception:
            continue
    # logger.info('VlogMemFile: %s read with %d value(s)' % (fileName, len(data)))
    print('VlogMemFile: %s read with %d value(s)' % (fileName, len(data)))
    if debug:
        for i, v in enumerate(data):
            # logger.debug('0x%X: 0x%X' % (i, v))
            print('0x%X: 0x%X' % (i, v))
    fi.close()
    return startadr, data


def writeVlogMemFile(fileName, mem, a_dig=4, d_dig=8, adroffset=0, adrinc=1, header=["", "verilog memory data file", ""]):
    """
    Write memory data to a file in verilog hex format.

      fileName........path to verilog file
      mem.............list with integer memory data
      a_dig...........min address digits
      d_dig...........min data digits
      adroffset.......adress offset
      adrinc..........increment adr by
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
            fi.write('@{:0{}x} {:0{}x}\n'.format(i*adrinc+adroffset, a_dig, v, d_dig))
    fi.write(' ')
    fi.close()
    return True


if __name__ == '__main__':
    data = [1, 2, 3, 4, 5]
    writeVlogMemFile('schrott.v', data)
