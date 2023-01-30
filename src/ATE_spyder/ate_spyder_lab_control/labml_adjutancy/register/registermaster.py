# $Id: $
"""User interface to the register master excel file.

This excel file descibes all registers of a sensor. For each register
the following items are mentioned:
    name
    address
    bank        (optional)
    description
    bitslices

A bitslice is a range of one or more consecutive bits in a register. Each
bitslice is descripted by the following items:
    name
    index_startbit
    index_stopbit
    read/write direction
    reset value
    description

"""

import re
import sys
import os
import pandas as pd
import ipywidgets as widgets

try:
    from itertools import zip_longest
except ImportError:
    from itertools import izip_longest as zip_longest
from collections import OrderedDict  # , namedtuple
from ate_common.logger import LogLevel
from labml_adjutancy.misc.mqtt_client import mqtt_deviceattributes
from labml_adjutancy.misc import environment
from labml_adjutancy.misc.common import check, str2num


__copyright__ = "Copyright 2023, Lab"
__version__ = "0.0.3"

mylogger = None


class RegDB(object):
    def __init__(self, filename=""):
        import xlrd

        self.bk = xlrd.open_workbook(filename)
        self.database = None
        self.database = []

    def get_row_data(self, bk, sh, rowx, colrange):
        """Utility function to extract a single row out of an Excel sheet"""
        import xlrd

        result = []
        dmode = bk.datemode
        ctys = sh.row_types(rowx)
        cvals = sh.row_values(rowx)
        for colx in colrange:
            cty = ctys[colx]
            cval = cvals[colx]
            if bk.formatting_info:
                cxfx = str(sh.cell_xf_index(rowx, colx))
            else:
                cxfx = ""
            if cty == xlrd.XL_CELL_DATE:
                try:
                    showval = xlrd.xldate_as_tuple(cval, dmode)
                except xlrd.XLDateError:
                    e1, e2 = sys.exc_info()[:2]
                    showval = "%s:%s" % (e1.__name__, e2)
                    cty = xlrd.XL_CELL_ERROR
            elif cty == xlrd.XL_CELL_NUMBER:
                showval = "%.0f" % (cval)
            elif cty == xlrd.XL_CELL_ERROR:
                showval = xlrd.error_text_from_code.get(cval, "<Unknown error code 0x%02x>" % cval)
            else:
                showval = "%s" % (cval)
            result.append((colx, cty, showval, cxfx))
        return result

    def build_database(self):
        """Fill database with register master fields"""
        shxrange = range(self.bk.nsheets)
        #
        #  Iterating over all sheets of the file
        #
        for shx in shxrange:
            sh = self.bk.sheet_by_index(shx)
            nrows, ncols = sh.nrows, sh.ncols
            colrange = range(ncols)
            rowrange = range(nrows)
            # print "Processing sheet %d: name = %r; nrows = %d; ncols = %d" % (shx, sh.name, sh.nrows, sh.ncols)
            if nrows and ncols:
                # Attempt to access the RHS corners
                sh.row_types(0)[ncols - 1]
                sh.row_values(0)[ncols - 1]
                sh.row_types(nrows - 1)[ncols - 1]
                sh.row_values(nrows - 1)[ncols - 1]
            cell_row = -1
            cell_col = -1
            pos_col = -1
            actual_block = None
            actual_header = None
            #
            #  Iterating over all rows of the sheet
            #
            for rowx in rowrange:
                row_data = {}
                #############################################################################
                #
                #  Fill 'row_data' dictionary with data of a complete row
                #
                for colx, ty, val, _unused in self.get_row_data(self.bk, sh, rowx, colrange):
                    #
                    #  First: idling until the keyword '::blk(xxx)' is found
                    #
                    if not actual_block:
                        try:
                            m = re.match("^::blk\(([^\)]*)\)", val)
                        except Exception:
                            m = None
                        if m:
                            #
                            #  '::blk(xxx)' found --> preparing 'actual_block' dictionary
                            #
                            cell_col = colx
                            cell_row = rowx
                            actual_block = {"cells": {}, "types": {}, "checks": {}, "registers": []}
                            actual_block["cells"][colx] = "blk"
                            actual_block["name"] = m.group(1)
                            actual_block["id"] = rowx
                    else:
                        #
                        #  While in the definition row, fill up the 'cells' dictionary
                        #
                        if cell_row == rowx:
                            try:
                                m = re.match("^([a-zA-Z_]+[a-zA-Z0-9_]*)$", val)
                            except Exception:
                                m = None
                            if m:
                                if m.group(1) == "pos":
                                    pos_col = colx
                                actual_block["cells"][colx] = m.group(1)
                        else:
                            #
                            #  Otherwise just filling 'row_data'
                            #
                            try:
                                m = re.match(".*", val)
                            except Exception:
                                m = None
                            if m:
                                row_data[colx] = val
                #############################################################################
                #
                #  If 'row_data" was filled up, processing it
                #
                if row_data:
                    #########################################################################
                    #
                    #  Check for a type conversion definition row ('::typ' in 'blk' column)
                    #
                    try:
                        m = re.match("^::typ", row_data[cell_col])
                    except Exception:
                        m = None
                    if m:
                        #
                        #  If found, fill up the 'types' dictionary with valid type conversions
                        #
                        for col in actual_block["cells"].keys():
                            try:
                                dat = row_data[col]
                            except Exception:
                                dat = None
                            if dat:
                                try:
                                    m = re.match("^(int|hex|dec|bin|flt|str)$", row_data[col])
                                except Exception:
                                    m = None
                                if m:
                                    actual_block["types"][actual_block["cells"][col]] = row_data[col]
                                    continue
                        continue
                    #########################################################################
                    #
                    #  Check for a check definition row ('::check' in 'blk' column)
                    #
                    try:
                        m = re.match("^::check", row_data[cell_col])
                    except Exception:
                        m = None
                    if m:
                        #
                        #  If found, fill up the 'checks' dictionary with valid checks
                        #
                        for col in actual_block["cells"].keys():
                            try:
                                dat = row_data[col]
                            except Exception:
                                dat = None
                            if dat:
                                try:
                                    m = re.match("^(hu|bu|br|,)+$", row_data[col])
                                except Exception:
                                    m = None
                                if m:
                                    actual_block["checks"][actual_block["cells"][col]] = row_data[col]
                                    continue
                        continue
                    #########################################################################
                    #
                    #  Check for a header definition row ('hdr' in 'pos' column)
                    #
                    try:
                        m = re.match("^hdr$", row_data[pos_col])
                    except Exception:
                        m = None
                    if m:
                        #
                        #  If found, prepare a new 'actual_header' dictionary
                        #  (if there already exists a filled dictionary, add it to
                        #   the list of registers of the 'actual_block')
                        #
                        if actual_header:
                            for col in actual_block["cells"].keys():
                                try:
                                    s = actual_header[actual_block["cells"][col]]
                                except Exception:
                                    actual_header[actual_block["cells"][col]] = ""
                            actual_block["registers"].append(actual_header)
                        actual_header = {"slices": [], "id": rowx}
                        #
                        #  Iterate through all valid columns
                        #
                        for col in actual_block["cells"].keys():
                            try:
                                s = row_data[col]
                            except Exception:
                                s = None
                            if s is not None and s != "":
                                #
                                #  If a valid entry is found, perform type conversion
                                #
                                conversion_error = None
                                try:
                                    conv = actual_block["types"][actual_block["cells"][col]]
                                except Exception:
                                    conv = "str"
                                if conv == "int" or conv == "dec":
                                    try:
                                        dat = int(s)
                                    except Exception:
                                        dat = s
                                        conversion_error = True
                                elif conv == "hex":
                                    try:
                                        dat = int(s, 16)
                                    except Exception:
                                        dat = s
                                        conversion_error = True
                                elif conv == "bin":
                                    try:
                                        dat = int(s, 2)
                                    except Exception:
                                        dat = s
                                        conversion_error = True
                                elif conv == "flt":
                                    try:
                                        dat = float(s)
                                    except Exception:
                                        dat = s
                                        conversion_error = True
                                else:
                                    dat = s
                                # if conversion_error:
                                # print "ERROR: While converting value '%s' to type '%s' for cell '%s' in header '%s'"%(dat, conv, actual_block['cells'][col], actual_header['blk'])
                                #
                                #  If a check is specified, perform it
                                #
                                try:
                                    c = re.match("hu", actual_block["checks"][actual_block["cells"][col]])
                                except Exception:
                                    c = None
                                if c:
                                    #
                                    #  Check for unique value in header cell
                                    #
                                    for register in actual_block["registers"]:
                                        try:
                                            p = register[actual_block["cells"][col]]
                                        except Exception:
                                            p = None
                                        # if p and p == dat:
                                        # print "ERROR: Duplicate value '%s' in cell '%s' for header '%s' (same value found in header '%s')"%(dat, actual_block['cells'][col], actual_header['blk'], register['blk'])
                                #
                                #  Store value into 'actual_header' dictionary
                                #
                                actual_header[actual_block["cells"][col]] = dat
                                #
                                #  If an inheritance is requested, perform this
                                #
                                # ###  --> TO BE DONE (adapt 'blk' value and copy slice array from somewhere)
                        continue
                    #########################################################################
                    #
                    #  Check for a slice definition row (slice definition in 'pos' column)
                    #
                    try:
                        m = re.match("^([0-9][0-9:]*)$", row_data[pos_col])
                    except Exception:
                        m = None
                    if m:
                        #
                        #  If found, prepare a new 'actual_slice' dictionary
                        #
                        flds = m.group(0).split(":")
                        if len(flds) == 2:
                            mn = int(flds[1])
                            mx = int(flds[0])
                            actual_slice = {"id": rowx, "posmin": mn, "posmax": mx, "poswidth": (mx - mn), "posmask": (((1 << (mx + 1)) - 1) - ((1 << mn) - 1))}
                        else:
                            mn = int(flds[0])
                            actual_slice = {"id": rowx, "posmin": mn, "posmax": mn, "poswidth": 1, "posmask": (1 << mn)}
                        #
                        #  Iterate through all valid columns
                        #
                        for col in actual_block["cells"].keys():
                            try:
                                s = row_data[col]
                            except Exception:
                                s = None
                            if s is not None and s != "":
                                #
                                #  If a valid entry is found, perform type conversion
                                #
                                conversion_error = None
                                try:
                                    conv = actual_block["types"][actual_block["cells"][col]]
                                except Exception:
                                    conv = "str"
                                if conv == "int" or conv == "dec":
                                    try:
                                        dat = int(s)
                                    except Exception:
                                        dat = s
                                        conversion_error = True
                                elif conv == "hex":
                                    try:
                                        dat = int(s, 16)
                                    except Exception:
                                        dat = s
                                        conversion_error = True
                                elif conv == "bin":
                                    try:
                                        dat = int(s, 2)
                                    except Exception:
                                        dat = s
                                        conversion_error = True
                                elif conv == "flt":
                                    try:
                                        dat = float(s)
                                    except Exception:
                                        dat = s
                                        conversion_error = True
                                else:
                                    dat = s
                                # if conversion_error:
                                # print "ERROR: While converting value '%s' to type '%s' for cell '%s' in slice '%s' of header '%s'"%(dat, conv, actual_block['cells'][col], m.group(0), actual_header['blk'])
                                #
                                #  If a check is specified, perform it
                                #
                                try:
                                    c = re.match("bu", actual_block["checks"][actual_block["cells"][col]])
                                except Exception:
                                    c = None
                                if c:
                                    #
                                    #  Check for unique value in slice cell
                                    #
                                    for slice in actual_header["slices"]:
                                        try:
                                            p = slice[actual_block["cells"][col]]
                                        except Exception:
                                            p = None
                                        # if p and p == dat:
                                        # print "ERROR: Duplicate value '%s' in cell '%s' for slice '%s' of header '%s'"%(dat, actual_block['cells'][col], actual_slice['pos'], actual_header['blk'])
                                #
                                #  Store value into 'actual_slice' dictionary
                                #
                                actual_slice[actual_block["cells"][col]] = dat
                        #
                        #  Check whether all required entries are existant
                        #
                        for check in actual_block["checks"].keys():
                            try:
                                c = re.match("br", actual_block["checks"][check])
                            except Exception:
                                c = None
                            if c:
                                try:
                                    p = re.match("^.*$", actual_slice[check])
                                except Exception:
                                    p = None
                                # if not p:
                                # print "ERROR: Required cell '%s' not found for slice '%s' of header '%s'"%(check, actual_slice['pos'], actual_header['blk'])

                        #
                        #  Add 'actual_slice' dictionary to 'actual_header' dictionary
                        #
                        if actual_header and actual_slice:
                            for col in actual_block["cells"].keys():
                                try:
                                    s = actual_slice[actual_block["cells"][col]]
                                except Exception:
                                    actual_slice[actual_block["cells"][col]] = ""
                            actual_header["slices"].append(actual_slice)
                        continue
            #
            #  Add 'actual_header' dictionary to 'actual_block' dictionary (if one exists)
            #
            if actual_header:
                for col in actual_block["cells"].keys():
                    try:
                        s = actual_header[actual_block["cells"][col]]
                    except Exception:
                        actual_header[actual_block["cells"][col]] = ""
                actual_block["registers"].append(actual_header)
            #
            #  Add 'actual_block' dictionary to 'database' array (if one exists)
            #
            if actual_block:
                self.database.append(actual_block)
                actual_block = None
        return


class Register:
    # read-only attributes
    def __setattr__(self, name, value):
        valid = "__cache__", "_cache", "_debug", "value", "value_bin", "read", "write", "res"
        if name not in valid and name not in self._slices:
            raise AttributeError("can't set attribute {}".format(repr(name)))
        object.__setattr__(self, name, value)

    def _get_addr(self):
        paddr = self._addr  # set to default
        if self._rm._protocol_typ == "tin":
            paddr = self._cpuaddr
        if paddr == -1:
            msg = "access not possible, interface in {!r} mode, please use e.g. tin".format(self._rm._protocol_typ)
            raise ValueError(msg)
        return paddr

    def writebase(self, bank):
        if self._rm._forcebank or (bank != self._rm._bank):
            self._rm._protocol.writebase(bank)
            self._rm._bank = bank

    def __init__(self, cpuaddr, addr, bank=0, name="", slices={}, description="", rm=None):
        global mylogger
        _setattr = object.__setattr__.__get__(self, self.__class__)
        if bank == "":
            mylogger.log_message(LogLevel.Warning(), f"Regisermaster {name} entray 'bank' is empty, use 0  instead")
            bank = 0
        _setattr("_cpuaddr", cpuaddr)
        _setattr("_addr", addr)
        _setattr("_bank", bank)
        _setattr("_name", name)
        _setattr("_slices", slices)
        _setattr("_desc", description)
        _setattr("_rm", rm)
        _setattr("_reset", 0)
        _setattr("__cache__", None)
        _setattr("_rw", all([slc["dir"] == "RW" or slc["dir"] == "R" for slc in slices.values()]))
        _setattr("mqtt_list", ["read", "write"])

    def _validate(self, value, length):
        if isinstance(value, int):
            if value > 2**length - 1:
                msg = "{!r} too big for {} bits".format(value, length)
                raise ValueError(msg)
            elif value < 0:
                msg = "value = {!r} must be positive".format(value)
                raise ValueError(msg)
        else:
            msg = "value {!r} is not an integer".format(value)
            raise ValueError(msg)
        return value

    @property
    def _cache(self):
        if not self._rm._atomic and self.__cache__ is None:
            msg = "cache is empty\n"
            msg += "use either _cache = <value>, _use_reset(), "
            msg += "_read() or _write(<value>)"
            raise ValueError(msg)
        return self.__cache__

    @_cache.setter
    def _cache(self, value):
        if value is None:
            object.__setattr__(self, "__cache__", None)
        else:
            self._validate(value, len(self))
            object.__setattr__(self, "__cache__", value)

    @property
    def value(self):
        """bit-slice over full register

        shadow register, read/write the true regiser only if None"""
        if self._rm._atomic and self.__cache__ is None:
            if self._bank is not None and self._bank != "":
                self.writebase(self._bank)
            value = self._rm._protocol.readreg(self._get_addr())
            value &= 2 ** self._len_slices() - 1
            self._check_r_err()
        else:
            value = self._cache
        return value

    @value.setter
    def value(self, value):
        self._validate(value, len(self))
        if self._rm._atomic and self.__cache__ is None:
            if self._bank is not None and self._bank != "":
                self.writebase(self._bank)
            self._rm._protocol.writereg(self._get_addr(), value)
            self._check_w_err()
        else:
            self._cache = value

    @property
    def addr(self):
        """returns the register address"""
        return self._get_addr()

    def _get_slice(self, name):
        lsb = self._slices[name]["lsb"]
        msb = self._slices[name]["msb"]
        length = msb - lsb + 1
        mask = (2**length - 1) << lsb
        if self._rm._atomic and self.__cache__ is None:
            if self._bank is not None and self._bank != "":
                self.writebase(self._bank)
            value = self._rm._protocol.readreg(self._get_addr())
            value &= 2 ** self._len_slices() - 1
            self._check_r_err()
        else:
            value = self._cache
        value = (value & mask) >> lsb
        return value

    def _set_slice(self, name, value):
        if "W" not in self._slices[name]["dir"].upper():
            msg = "can't write slice {!r}, it's not writeable"
            msg = msg.format(name)
            raise ValueError(msg)
        lsb = self._slices[name]["lsb"]
        msb = self._slices[name]["msb"]
        length = msb - lsb + 1
        self._validate(value, length)
        if self._rm._atomic and self.__cache__ is None:
            if not self._rw:
                msg = "can´t use read-modify-write because "
                msg += "not all bits are readable\n"
                msg += "use either _cache = <value>, _use_reset(), "
                msg += "_read() or _write(<value>)"
                raise ValueError(msg.format(self._name))
            if self._bank is not None and self._bank != "":
                self.writebase(self._bank)
            current = self._rm._protocol.readreg(self._get_addr())
            current &= 2 ** self._len_slices() - 1
            self._check_r_err()
        else:
            current = self._cache
        # clear all bits between msb:lsb
        mask = (2**length - 1) << lsb
        current &= ~mask  # & (2**len(obj) - 1)
        # set value
        current = current | (value << lsb)
        if self._rm._atomic and self.__cache__ is None:
            self._rm._protocol.writereg(self._get_addr(), current)
            self._check_w_err()
        else:
            self._cache = current

    def _use_reset(self, default=None):
        """Copy reset values from all bit-slices into _cache.

        Note: All bit-slices must have a reset value otherwise an error occurs."""
        cache_old = self.__cache__
        self._cache = 0
        for name, slice in self._slices.items():
            valres = slice["res"]
            if (valres is None) and (default is None):
                self.__cache__ = cache_old
                msg = "bit-slice {!r} has no reset value"
                raise ValueError(msg.format(name))
            elif valres is None:
                valres = default
                msg = "WARNING: register {!r} [{!r}:{!r}] has no reset value, set to default={!r}"
                print(msg.format(name, slice["msb"], slice["lsb"], default))
                pass
            self._set_slice(name, valres)

    @property
    def __has_reset(self):
        for name, slice in self._slices.items():
            valres = slice["res"]
            if valres is None:
                return False
        return True

    def __slices2attr(self):
        _setattr = object.__setattr__.__get__(self, self.__class__)
        dct = {}
        for name, slice in self._slices.items():

            def getter(self, name=name):
                if "R" not in self._slices[name]["dir"].upper():
                    msg = "can't read slice {!r}, it's not readable"
                    msg = msg.format(name)
                    raise ValueError(msg)
                return self._get_slice(name)

            def setter(obj, value, name=name):
                obj._set_slice(name, value)

            dct[name] = property(getter, setter, doc=slice["desc"])
        dct["__doc__"] = self.__class__.__doc__
        SliceRegister = type("Register", (self.__class__,), dct)
        new_reg = SliceRegister(self._cpuaddr, self._addr, self._bank, self._name, self._slices, self._desc, self._rm)
        object.__setattr__(new_reg, "_reset", self._reset)
        return new_reg

    @property
    def value_bin(self):
        fmt = "{{:0{}b}}".format(len(self))
        groups = self.__grouper(fmt.format(self.value), 4)
        return " ".join(groups)

    @value_bin.setter
    def value_bin(self, value):
        self.value = int(value.replace(" ", ""), base=2)

    def read(self, compare=None, onlycheck=True, tolerance=0, mask=None):
        """
        read from the Register with selected protokoll

        Parameters
        ----------
        compare : integer
            compare value, if None than no compare
        onlycheck: boolean
            True (default) result is the compare value 0 or 1
            False result is compare value and the read value
        tolerance : integer

        Returns
        -------
        dat : integer
            data.
        check : if compare defined this is the compare result:
            0 = ok
            1 = error
        """
        global mylogger
        if self._rm._protocol is None:
            mylogger.log_message(LogLevel.Error(), f"{self.__class__.__name__} protocol not defined!!")
            return -1
        value = self._read()
        mylogger.log_message(LogLevel.Measure(), f"{self.__class__.__name__}.{self._name} == {hex(value)}")
        if compare is not None:
            error = check(f"{self.__class__.__name__}.{self._name}", compare, value, tolerance, mask)
            if onlycheck:
                return error
            else:
                return error, value
        self._rm.publish_set(f"{self._name}.read", value)
        return value

    def write(self, value=None):
        global mylogger
        if self._rm._protocol is None:
            mylogger.log_message(LogLevel.Error(), f"{self.__class__.__name__} protocol not defined!!")
            return -1
        result = self._write(value)
        msg = f"{self.__class__.__name__}.{self._name} := "
        msg = f"{msg} {hex(result)}" if value is not None else f"{msg} {result}"
        mylogger.log_message(LogLevel.Measure(), msg)
        self._rm.publish_get(f"{self._name}.write", value)
        return result

    def res(self):
        for name, slice in self._slices.items():
            valres = slice["res"]
        return valres

    def _read(self, protocol=None):
        if self._bank is not None and self._bank != "":
            self.writebase(self._bank)
        value = self._rm._protocol.readreg(self._get_addr())
        value &= 2 ** self._len_slices() - 1
        self._check_r_err()
        if value > -1:
            self._cache = value
        return value

    def _write(self, value=None, protocol=None, verify=False):
        if value is None:
            _value = self._cache
        else:
            _value = self._validate(value, len(self))
        if _value is not None:
            if self._bank is not None and self._bank != "":
                self.writebase(self._bank)
            self._rm._protocol.writereg(self._get_addr(), _value)
            self._check_w_err()
        else:
            msg = "nothing to write (neither argument nor _cache value is given)"
            raise ValueError(msg)
        if self._rm._atomic and _value is None:
            self._cache = None
        else:
            self._cache = _value
        return _value

    def _check_r_err(self):
        if self._rm._protocol.board.error is True:
            msg = "can't read from interface - {!r}"
            msg = msg.format(self._rm._protocol.board.errortext)
            raise ValueError(msg)

    def _check_w_err(self):
        if self._rm._protocol.board.error is True:
            msg = "can't write to interface - {!r}"
            msg = msg.format(self._rm._protocol.board.errortext)
            raise ValueError(msg)

    @property
    def value_table(self):
        cache_old = self._cache
        self._cache = self.value
        slices = []
        for name, dct in self._slices.items():
            slice = OrderedDict()
            slice["name"] = name
            if dct["msb"] == dct["lsb"]:
                loc = "[{msb}]".format(**dct)
            else:
                loc = "[{msb}:{lsb}]".format(**dct)
            slice["loc"] = loc
            length = dct["msb"] - dct["lsb"] + 1

            value = self._get_slice(name)
            slice["dec"] = str(value)

            fmt = "0x{{:0{}x}}".format(length // 4 + (1 if length % 4 else 0))
            slice["hex"] = fmt.format(value)

            fmt = "{{:0{}b}}".format(length)
            groups = self.__grouper(fmt.format(value), 4)
            slice["bin"] = "" + " ".join(groups)

            valres = dct["res"]
            slice["res"] = "-" if valres is None else valres
            slice["dir"] = dict(R="R", W="W", RW="RW").get(dct["dir"].upper())
            slices.append(slice)
        df = pd.DataFrame(slices, columns=["loc", "name", "dir", "dec", "hex", "bin", "res"])
        df = df.set_index("loc")
        df.index.name = None
        self._cache = cache_old
        return df

    @property
    def help(self):
        print(self.__doc__)

    @property
    def __doc__(self):
        lines = [self._desc, ""]
        width_left = 0
        for name, s in self._slices.items():
            if s["res"] != 0:
                name = name + " (={})".format(s["res"])
            width_left = max(width_left, len(name))
            if s["msb"] == s["lsb"]:
                slc = "[{}]".format(s["msb"])
            else:
                slc = "[{msb}:{lsb}]".format(**s)
            rw = dict(RW="RW", R="R", W="W").get(s["dir"], "")
            field = " ".join([slc, rw])
            width_left = max(width_left, len(field))
        for name, s in self._slices.items():
            if s["res"] != 0:
                name = name + " (={!r})".format(s["res"])
            if s["msb"] == s["lsb"]:
                slc = "[{}]".format(s["msb"])
            else:
                slc = "[{msb}:{lsb}]".format(**s)
            rw = dict(RW="RW", R="R", W="W").get(s["dir"], "")
            field = " ".join([slc, rw])
            left = name, field
            right = s["desc"].split("\n")
            for le, r in zip_longest(left, right, fillvalue=""):
                fmt = "{{:{}}}  {{}}".format(width_left)
                lines.append(fmt.format(le, r))
            lines.append("")
        # lines.append('note: direction is RW if not marked as RO or WO')
        lines.append("note: reset value is zero if not marked with (=<res>)")
        return "\n".join(lines)

    def _len_slices(self):
        return sum(s["msb"] - s["lsb"] + 1 for s in self._slices.values())

    def __len__(self):
        return self._rm._len_reg

    def __repr__(self):
        args = ["cpuaddr=0x{:x}".format(self._cpuaddr)]
        args.append("addr=0x{:x}".format(self._addr))
        args.append("bank={}".format(self._bank))
        args.append("name={!r}".format(self._name))
        return "{classname}({args})".format(classname=self.__class__.__name__, args=", ".join(args))

    @staticmethod
    def __grouper(seq, n):
        """grouper('ABCDEFG', 3) --> A BCD EFG"""
        rseq = seq[::-1]
        return [rseq[i : i + n][::-1] for i in range(0, len(seq), n)][::-1]

    @staticmethod
    def __int2dec(value, length=None):
        try:
            groups = Register.__grouper("{}".format(value), 3)
            return " ".join(groups)
        except ValueError:
            return value

    @staticmethod
    def __int2hex(value, length):
        try:
            fmt = "{{:0{}X}}".format(length // 4 + (1 if length % 4 else 0))
            groups = Register.__grouper(fmt.format(value), 2)
            return "0x " + " ".join(groups)
        except ValueError:
            return value

    @staticmethod
    def __int2bin(value, length):
        try:
            fmt = "{{:0{}b}}".format(length)
            groups = Register.__grouper(fmt.format(value), 4)
            return "0b " + " ".join(groups)
        except ValueError:
            return value

    def _calc(self):
        names = OrderedDict()
        names["cpuaddr"] = dict(width=50)
        names["addr"] = dict(width=50)
        names["bank"] = dict(width=50)
        names["name"] = dict(width=100)
        names["res"] = dict(width=60)
        names["dec"] = dict(width=75)
        names["hex"] = dict(width=75)
        names["bin"] = dict(width=175)
        names["description"] = dict(width=380, margin="0px 0px 10px 10px")

        reg_header = []
        for name, dct in names.items():
            params = dct.copy()
            if "width" in params:
                params["width"] = "{}px".format(dct["width"])
            box = widgets.HTML("<b>{}</b>".format(name), layout=params)
            reg_header.append(box)
        reg_header = widgets.HBox(reg_header)

        reg_hline = widgets.Box(layout=dict(border="1px solid", margin="0px 2px 5px 2px"))
        width_max = sum(dct["width"] for dct in names.values())
        reg_hline.layout.width = "{}px".format(width_max)

        reg_line = []
        reg_line.append(widgets.Label("0x{:X}".format(self._cpuaddr)))
        reg_line.append(widgets.Label("0x{:X}".format(self._addr)))
        reg_line.append(widgets.Label("{}".format(self._bank)))
        reg_line.append(widgets.Label(str(self._name)))
        freset = widgets.Button(description="Reset", disabled=not self.__has_reset)
        reg_line.append(freset)

        def on_reset(obj):
            self._use_reset()
            reg_line.children[4].value = self.__int2dec(self._cache, len(self))
            reg_line.children[5].value = self.__int2hex(self._cache, len(self))
            reg_line.children[6].value = self.__int2bin(self._cache, len(self))
            for (name, dct), line in zip(self._slices.items(), lines):
                value = self._get_slice(name)
                slen = dct["msb"] - dct["lsb"] + 1
                line.children[4].value = self.__int2dec(value, slen)
                line.children[5].value = self.__int2hex(value, slen)
                line.children[6].value = self.__int2bin(value, slen)

        freset.on_click(on_reset)

        try:
            value = self._cache
        except ValueError:
            value = ""
        length = len(self)
        fdec = widgets.Text("", placeholder="0d ...")
        fdec.value = self.__int2dec(value, length)
        reg_line.append(fdec)

        fhex = widgets.Text("", placeholder="0d ...")
        fhex.value = self.__int2hex(value, length)
        reg_line.append(fhex)

        fbin = widgets.Text("", placeholder="0d ...")
        fbin.value = self.__int2bin(value, length)
        reg_line.append(fbin)

        fmt = '<p style="line-height:1.2">{}</p>'
        field = widgets.HTML(fmt.format(self._desc.replace("\n", "<br>")))
        field.layout.margin = "0px 0px 10px 10px"
        reg_line.append(field)

        for field, dct in zip(reg_line, names.values()):
            field.layout.width = "{}px".format(dct["width"])
        reg_line = widgets.HBox(reg_line)
        reg_line.layout.margin = "0px 0px 10px 0px"

        def dec2other(obj, length=len(self), fdec=fdec, fhex=fhex, fbin=fbin):
            try:
                value = int(fdec.value.replace(" ", ""))
                self._cache = value
                fdec.value = self.__int2dec(value, length)
                fhex.value = self.__int2hex(value, length)
                fbin.value = self.__int2bin(value, length)
                for name, line in zip(self._slices, lines):
                    value = self._get_slice(name)
                    dct = self._slices[name]
                    slen = dct["msb"] - dct["lsb"] + 1
                    line.children[4].value = self.__int2dec(value, slen)
                    line.children[5].value = self.__int2hex(value, slen)
                    line.children[6].value = self.__int2bin(value, slen)
            except ValueError:
                fdec.value = self.__int2dec("", length)

        fdec.on_submit(dec2other)

        def hex2other(obj, length=len(self), fdec=fdec, fhex=fhex, fbin=fbin):
            try:
                value = int(fhex.value.replace(" ", ""), 16)
                self._cache = value
                fdec.value = self.__int2dec(value, length)
                fhex.value = self.__int2hex(value, length)
                fbin.value = self.__int2bin(value, length)
                for name, line in zip(self._slices, lines):
                    value = self._get_slice(name)
                    dct = self._slices[name]
                    slen = dct["msb"] - dct["lsb"] + 1
                    line.children[4].value = self.__int2dec(value, slen)
                    line.children[5].value = self.__int2hex(value, slen)
                    line.children[6].value = self.__int2bin(value, slen)
            except ValueError:
                fhex.value = self.__int2hex("", length)

        fhex.on_submit(hex2other)

        def bin2other(obj, length=len(self), fdec=fdec, fhex=fhex, fbin=fbin):
            try:
                value = int(fbin.value.replace(" ", ""), base=2)
                self._cache = value
                fdec.value = self.__int2dec(value, length)
                fhex.value = self.__int2hex(value, length)
                fbin.value = self.__int2bin(value, length)
                for name, line in zip(self._slices, lines):
                    value = self._get_slice(name)
                    dct = self._slices[name]
                    slen = dct["msb"] - dct["lsb"] + 1
                    line.children[4].value = self.__int2dec(value, slen)
                    line.children[5].value = self.__int2hex(value, slen)
                    line.children[6].value = self.__int2bin(value, slen)
            except ValueError:
                fbin.value = self.__int2bin("", length)

        fbin.on_submit(bin2other)

        names = OrderedDict()
        names["bits"] = dict(width=50)
        names["dir"] = dict(width=50)
        names["slice"] = dict(width=100)
        names["res"] = dict(width=60)
        names["dec"] = dict(width=75)
        names["hex"] = dict(width=75)
        names["bin"] = dict(width=175)
        names["description"] = dict(width=380, margin="0px 0px 10px 10px")

        header = []
        for name, dct in names.items():
            params = dct.copy()
            if "width" in params:
                params["width"] = "{}px".format(dct["width"])
            box = widgets.HTML("<b>{}</b>".format(name), layout=params)
            header.append(box)
        header = widgets.HBox(header)

        hline = widgets.Box(layout=dict(border="1px solid", margin="0px 2px 5px 2px"))
        width_max = sum(dct["width"] for dct in names.values())
        hline.layout.width = "{}px".format(width_max)

        lines = []
        for name, dct in self._slices.items():
            if dct["msb"] == dct["lsb"]:
                loc = "[{msb}]".format(**dct)
            else:
                loc = "[{msb}:{lsb}]".format(**dct)
            ro = not "W" in dct["dir"].upper()
            length = dct["msb"] - dct["lsb"] + 1
            res = "-" if dct["res"] is None else dct["res"]
            try:
                value = self._get_slice(name)
            except ValueError:
                value = ""

            line = []
            line.append(widgets.Label(loc))

            dir = dict(R="R", W="W", RW="RW").get(dct["dir"].upper())
            line.append(widgets.Label(dir))

            line.append(widgets.Label(name))
            line.append(widgets.Label("{}".format(res)))

            fdec = widgets.Text("", placeholder="0d ...", disabled=ro)
            fdec.value = self.__int2dec(value, length)
            line.append(fdec)
            fhex = widgets.Text("", placeholder="0x ...", disabled=ro)
            fhex.value = self.__int2hex(value, length)
            line.append(fhex)
            fbin = widgets.Text("", placeholder="0b ...", disabled=ro)
            fbin.value = self.__int2bin(value, length)
            line.append(fbin)
            fmt = '<p style="line-height:1.2">{}</p>'
            field = widgets.HTML(fmt.format(dct["desc"].replace("\n", "<br>")))
            field.layout.margin = "0px 0px 10px 10px"
            line.append(field)

            def dec2other(obj, self=self, name=name, length=length, fdec=fdec, fhex=fhex, fbin=fbin):
                old = self._get_slice(name)
                try:
                    value = int(fdec.value.replace(" ", ""))
                    self._set_slice(name, value)
                    fdec.value = self.__int2dec(value, length)
                    fhex.value = self.__int2hex(value, length)
                    fbin.value = self.__int2bin(value, length)
                    reg_line.children[4].value = self.__int2dec(self._cache, len(self))
                    reg_line.children[5].value = self.__int2hex(self._cache, len(self))
                    reg_line.children[6].value = self.__int2bin(self._cache, len(self))
                except ValueError:
                    fdec.value = self.__int2dec("", length)
                    if not "W" in self._slices[name]["dir"].upper():
                        fdec.value = self.__int2dec(old, length)
                    else:
                        fdec.value = self.__int2dec("", length)

            fdec.on_submit(dec2other)

            def hex2other(obj, self=self, name=name, length=length, fdec=fdec, fhex=fhex, fbin=fbin):
                old = self._get_slice(name)
                try:
                    value = int(fhex.value.replace(" ", ""), 16)
                    self._set_slice(name, value)
                    fdec.value = self.__int2dec(value, length)
                    fhex.value = self.__int2hex(value, length)
                    fbin.value = self.__int2bin(value, length)
                    reg_line.children[4].value = self.__int2dec(self._cache, len(self))
                    reg_line.children[5].value = self.__int2hex(self._cache, len(self))
                    reg_line.children[6].value = self.__int2bin(self._cache, len(self))
                except ValueError:
                    if not "W" in self._slices[name]["dir"].upper():
                        fhex.value = self.__int2hex(old, length)
                    else:
                        fhex.value = self.__int2hex("", length)

            fhex.on_submit(hex2other)

            def bin2other(obj, self=self, name=name, length=length, fdec=fdec, fhex=fhex, fbin=fbin):
                old = self._get_slice(name)
                try:
                    value = int(fbin.value.replace(" ", ""), base=2)
                    self._set_slice(name, value)
                    fdec.value = self.__int2dec(value, length)
                    fhex.value = self.__int2hex(value, length)
                    fbin.value = self.__int2bin(value, length)
                    reg_line.children[4].value = self.__int2dec(self._cache, len(self))
                    reg_line.children[5].value = self.__int2hex(self._cache, len(self))
                    reg_line.children[6].value = self.__int2bin(self._cache, len(self))
                except ValueError:
                    if not "W" in self._slices[name]["dir"].upper():
                        fbin.value = self.__int2bin(old, length)
                    else:
                        fbin.value = self.__int2bin("", length)

            fbin.on_submit(bin2other)

            for field, dct in zip(line, names.values()):
                field.layout.width = "{}px".format(dct["width"])
            lines.append(widgets.HBox(line))

        boxes = [reg_header, reg_hline, reg_line, header, hline] + lines
        return widgets.VBox(boxes)


class RegisterMaster(mqtt_deviceattributes):
    """Returns a container object for registers imported from registermaster.

    filename:   name of registermaster (excel file), default from ENV:registermaster
    atomic:     enables read-modify-write behavoiur of bit-slices
                (reset: False)
    interface:  hardware object for STI/BiPhase protocol
    """

    # read-only attributes
    def __setattr__(self, name, value):
        valid = (
            "_cached",
            "_debug",
            "_interface",
            "_protocol",
            "_atomic",
            "_forcebank",
            "_bank",
            "_len_slices",
            "register",
            "use",
            "mqtt_status",
            "_mqtt_status",
            "_mqttclient",
            "mqtt_list",
            "mqtt_enable",
            "gui",
            "mqtt_all",
            "filename",
        )
        if name not in valid:
            raise AttributeError("can't set attribute {}".format(repr(name)))
        object.__setattr__(self, name, value)
        if hasattr(self, "mqtt_all") and name in self.mqtt_all:
            self.publish_set(name, value)

    def __init__(self, logger=None, filename=None, interface=None, instname="regs", read_mod_write=False):
        global mylogger
        self.gui = "labml_adjutancy.gui.instruments.regs.registermaster"
        _setattr = object.__setattr__.__get__(self, self.__class__)
        super().__init__()
        self.mqtt_all = ["filename", "use"]
        filename = os.environ.get("registermaster") if filename is None else filename
        mylogger = logger
        _setattr("instName", instname)
        _setattr("filename", filename)
        _setattr("_cached", False)
        _setattr("_debug", False)
        _setattr("_buffer", [])
        _setattr("_regs", {})
        _setattr("_cpuregs", {})
        _setattr("_protocol_typ", None)
        _setattr("_interface", interface)
        _setattr("_protocol", None)
        _setattr("_forcebank", True)
        _setattr("_bank", -1)
        _setattr("_atomic", read_mod_write)
        _setattr("_len_reg", 0)

    def __repr__(self):
        args = ["{!r}".format(self.filename)]
        if self._interface is not None:
            args.append("interface={!r}".format(self._interface))
        args.append("read_mod_write={!r}".format(self._atomic))
        return "{classname}({args})".format(classname=self.__class__.__name__, args=", ".join(args))

    def init(self):
        from semictrl import mqttc

        filename = self.filename
        if filename is None:
            raise IOError(f"{__class__}: no filename defined")
        print(f'   {self.instName}.init:   self._mqttclient = {self._mqttclient}')
        if self._mqttclient is None and mqttc is not None:
            self.mqtt_add(mqttc, self)
        blocked_regs = tuple(self.__class__.__dict__)
        blocked_slices = tuple(Register.__dict__)
        db = RegDB(filename)
        db.build_database()
        for item in db.database[0]["registers"]:
            slices = OrderedDict()
            for bsl in item["slices"]:
                name = bsl["bsn"]
                if name in blocked_slices:
                    msg = "WARNING: can't use name {!r} for slice\n" "Change slice name {!r} (line {!r}) in file {!r}"
                    msg = msg.format(name, name, bsl["id"], filename)
                    print(msg)
                elif not isinstance(bsl["posmin"], int):
                    msg = "WARNING: bit-slice {!r} in register {!r} has "
                    msg += "invalid lsb: {!r}"
                    print(msg.format(name, item["blk"], bsl["posmin"]))
                elif not isinstance(bsl["posmax"], int):
                    msg = "WARNING: bit-slice {!r} in register {!r} has "
                    msg += "invalid msb: {!r}"
                    print(msg.format(name, item["blk"], bsl["posmax"]))
                else:
                    try:
                        valres = str2num(bsl["res"])
                    except ValueError:
                        valres = None
                    slices[name] = dict(
                        lsb=bsl["posmin"],
                        msb=bsl["posmax"],
                        res=valres,
                        dir=bsl["dir"],
                        desc=bsl["des"],
                    )
            name = item["blk"]
            if name in blocked_regs:
                msg = "WARNING: can't use name {!r} for register\n" "Change register name {!} in file {!r}"
                msg = msg.format(name, name, filename)
                print(msg)
            elif item.get("adr") is None and item.get("prgadr") is None:
                msg = "WARNING: register {!r} has invalid address: {!r}"
                # print(msg.format(name, item['adr']))
                print(msg.format(name, item))
            #            elif item.get ('bank'):                  # to avoid  Keyerror if 'bank' not exist      --> not necessary anymore
            #                msg = 'WARNING: register {!r} has invalid bank: {!r}'
            #                print(msg.format(name, item['bank']))
            else:
                addr = -1
                cpuaddr = -1
                if item.get("adr") is not None and item["adr"] != "":
                    addr = item["adr"]
                elif item.get("prgadr") is not None and item["prgadr"] != "":
                    addr = item["prgadr"]
                if item.get("cpuadr") is not None and item["cpuadr"] != "":
                    cpuaddr = item["cpuadr"]
                if name != "":
                    reg = Register(
                        cpuaddr=cpuaddr,
                        addr=addr,
                        bank=item.get("bank"),
                        name=name,
                        description=item["des"],
                        slices=slices,
                        rm=self,
                    )
                    reg = reg._Register__slices2attr()
                    if not isinstance(reg._addr, int):
                        msg = f"ERROR: {name} addr is not a integer!  addr= {addr}"
                        print(msg)
                        continue
                    if reg._addr >= 0:
                        self._regs.setdefault(reg._addr, []).append(reg)
                    if reg._cpuaddr >= 0:
                        self._cpuregs.setdefault(reg._cpuaddr, []).append(reg)
                    object.__setattr__(self, item["blk"], reg)
        len_max = max(reg._len_slices() for reg in self)
        object.__setattr__(self, "_len_reg", len_max)
        for reg in self:
            if reg._len_slices() < len_max:
                msg = "WARNING: misses some slices ({} {}) in register {!r}"
                num = len_max - reg._len_slices()
                unit = "bits" if num > 1 else "bit"
                msg = msg.format(num, unit, reg._name)
                # logger.warning(msg)
        try:
            self.use = "tin"
        except AttributeError:
            pass
        object.__setattr__(self, "mapping", {})
        object.__setattr__(self, "_len_slices", None)
        self.register = self.__dict__.copy()  # create attribute register with all registernames
        for reg in self.__dict__:
            if reg != "register" and not hasattr(self.register[reg], "_Register__has_reset"):
                self.register.pop(reg, None)
            elif reg != "register":
                bank = self.register[reg]._bank
                if bank is not None and bank != "":
                    self.mapping[bank] = self.register[reg]._len_slices()
        self.mqtt_list = list(self.register) + self.mqtt_all
        return self

    def __iter__(self):
        global mylogger
        if self._protocol_typ == "tin":
            for regs in self._cpuregs.values():
                for reg in regs:
                    yield reg
        else:
            if not bool(self._regs.values()):
                mylogger.log_message(LogLevel.Error(), "\n####################################################")
                mylogger.log_message(LogLevel.Error(), 'ERROR: No "addr" has been defined in register master')
                mylogger.log_message(LogLevel.Error(), "####################################################\n")
            for regs in self._regs.values():
                for reg in regs:
                    yield reg

    def __len__(self):
        if self._protocol_typ == "tin":
            return sum(len(regs) for regs in self._cpuregs.values())
        else:
            return sum(len(regs) for regs in self._regs.values())

    def _mqtt2json(self, value, attr=None):
        if attr in self.mqtt_all:
            return value
        return "nomqtt"

    def close(self):
        pass

    def find(self, addr):
        try:
            if self._protocol_typ == "tin":
                return self._cpuregs[addr][0]
            else:
                return self._regs[addr][0]._name
        except Exception:
            return None

    @property
    def use(self):
        return self._protocol_typ

    @use.setter
    def use(self, typ):
        """
        Set/Get interface to 'typ'.

        typ must be defined in the interface
        """
        interface = getattr(self._interface, typ)
        object.__setattr__(self, "_protocol", interface)
        object.__setattr__(self, "_protocol_typ", typ)
        object.__setattr__(self, "_bank", -1)

    def set_bank(self, adr):
        """
        Set the bank from a giving adr and recalculate adr.

        Parameters
        ----------
        adr : TYPE
            DESCRIPTION.

        Returns
        -------
          adr.
        """
        if self.mapping != {}:
            mybank = 0
            for bank in self.mapping:
                mybank = bank if adr >= bank else mybank
            self._bank = mybank
            self._len_slices = self.mapping[mybank]
            adr = adr - mybank
        else:
            self._bank = None
            self._len_slices = None
        return adr

    def readreg(self, adr, bank=None, compare=None, onlycheck=True, tolerance=0, mask=None):
        """
        Read Register with selected protokoll.

        Parameters
        ----------
        adr : integer
            address.
        bank : integer
            bank adress
        compare : integer
            compare value, if None than no compare
        tolerance : integer

        Returns
        -------
        dat : integer
            data.
        check : if compare defined this is the compare result:
            0 = ok
            1 = error
        """
        if bank is not None:
            self._bank = bank
        else:
            adr = self.set_bank(adr)
        if self._bank is not None and self._bank != "":
            self._protocol.writebase(self._bank)
        value = self._protocol.readreg(adr)
        if self._len_slices is not None:
            value &= 2**self._len_slices - 1
        if compare is not None:
            bank = 0 if self._bank is None else self._bank
            error = check(f"{hex(bank+adr)}", compare, value, tolerance, mask)
            if onlycheck:
                return error
            else:
                return error, value
        return value

    def writereg(self, adr, dat, bank=None):
        """
        Write Register with selected protokoll.

        Parameters
        ----------
        adr : integer
            address.
        bank : integer
            bank adress
        dat : integer
            data.

        Returns
        -------
        None.

        """
        if bank is not None:
            self._bank = bank
        else:
            adr = self.set_bank(adr)
        if self._bank is not None and self._bank != "":
            self._protocol.writebase(self._bank)
        self._protocol.writereg(adr, dat)

    def reset(self):
        self._protocol.reset()
        object.__setattr__(self, "_bank", -1)
        for reg in self:
            object.__setattr__(reg, "__cache__", None)

    def reset_internal(self):
        object.__setattr__(self, "_bank", -1)
        try:
            self._protocol.reset_internal()
        except AttributeError:
            msg = "{!r} protocol has no 'reset_internal'."
            raise AttributeError(msg.format(self._protocol.__class__.__name__))
        for reg in self:
            object.__setattr__(reg, "__cache__", None)

    def reset_regs(self, default=None):
        global mylogger
        for regname in self:
            try:
                # print (regname)
                for slices in regname._slices:
                    if "W" in regname._slices[slices]["dir"]:
                        regname._use_reset(default)
            except Exception:
                pass
        mylogger.log_message(LogLevel.Info(), "Reset register Cache to resetvalues")

    def set_configuration_values(self, data):
        """Only empty dummy function."""
        global mylogger
        mylogger.log_message(LogLevel.Warning(), "labml_adjutancy.RegisterMaster: set_configuration_values only dummy function.....")
        pass

    def apply_configuration(self, data):
        """
        Call from the Plugin if the modul placed in the hardwaresetups.

        Parameters
        ----------
        data : TYPE
            DESCRIPTION.

        Returns
        -------
        None.

        """
        _setattr = object.__setattr__.__get__(self, self.__class__)
        config = environment.replaceEnvs(data)
        filename = config["filename"] if "filename" in config and config["filename"] != "" else self.filename
        filename = environment.checkNetworkPath(filename)
        _setattr("filename", filename)

        instname = config["instance name"] if "instance name" in config and config["instance name"] != "" else self.instName
        _setattr("instName", instname)
        read_mod_write = config["read mod write"] if "read mod write" in config and config["read mod write"] != "" else self._atomic
        _setattr("_atomic", read_mod_write)
        forcebank = config["force bank"] if "force bank" in config and config["force bank"] != "" else self._forcebank
        _setattr("_forcebank", forcebank)
        resetvalue = config["reset value"] if "reset value" in config and config["reset value"] != "" else 0
        self.init()
        # self.reset_regs(resetvalue)    # TODO: definition interface is missing


if __name__ == "__main__":
    filename = "your_registermaster.xls"
    regs = RegisterMaster(filename=filename)
    regs.init()

