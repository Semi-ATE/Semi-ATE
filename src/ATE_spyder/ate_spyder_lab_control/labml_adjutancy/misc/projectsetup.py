"""
projectsetup.

Created on Thu Jan  7 17:18:03 2021

@author: jung
"""
import os
import sys
import json
import time
import getpass
import datetime
from pathlib import Path
from inspect import isclass
from labml_adjutancy.misc import environment
from labml_adjutancy.misc import common
from labml_adjutancy.misc import file_io
from ate_common.logger import (LogLevel)


__author__ = "Zlin526F"
__copyright__ = "Copyright 2021, Lab"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"
__version__ = '0.0.1'

mylogger = None


class JsonDecoder(json.JSONDecoder):

    def decode(self, obj):
        # TODO: implementend parser for hexnumbers and other special formats....
        # or better use YAML-files.....
        return json.JSONDecoder.decode(self, obj)


class diclist(list):
    """Dictionary list."""

    def __init__(*args, **kwargs):
        global myparent
        if len(args) > 1:
            myparent = args[1]
            args = list(args)
            del args[1]
        list.__init__(*args, **kwargs)

    def __getattr__(mylist, key):
        if key in mylist:
            list.__getattribute__(mylist, key)
        else:
            return diclist.values(mylist, key)

    def keys(mylist):
        result = []
        for item in mylist:
            result.append(list(item.keys())[0])
        return result

    def values(mylist, key=None):
        """Get the value(s) from the key found in mylist.
        """
        result = None
        if key is not None and key in diclist.keys(mylist):
            result = list(mylist[diclist.keys(mylist).index(key)].values())
        elif len(mylist) > 0:
            result = []
            for item in mylist:
                if key is None:
                    value = list(item.values())[0]
                elif key in list(item.values())[0].keys():
                    value = list(item.values())[0][key]
                else:
                    value = None
                if type(value) is str:
                    value = common.str2num(value)
                result.append(value)
        if result is not None and len(result) == 1:
            result = result[0]
        return result

    def run(mylist, **kwargs):
        """Call the runmacro from the parent.
        """
        result = None
        if myparent is not None and hasattr(myparent, 'runmacro'):
            mylogger.log_message(LogLevel.Debug(), f'run macro {myparent.mylastdotdic}: {mylist}')
            result = myparent.runmacro(mylist, **kwargs)
        else:
            mylogger.log_message(LogLevel.Error(), f'No instruction how to should interprete the list: {mylist}')
        return result


class setupstr(str):
    def arange(items):
        return(common.arange(items))

    def start(items):
        return (common.arange(items)[0])

    def end(items):
        return (common.arange(items)[-1])


class dotdict(dict):
    """dot.notation access to dictionary attributes."""

    def myget(keyname, value):
        result = dict.get(keyname, value)
        if value not in ['size', 'shape']:
            myparent.mylastdotdic = value
        # print(f'keyname: {keyname},\nvalue: {value},\nresult: {result},\n')
            if result is None:
                # self.logger.log_message(LogLevel.Warning(), f"'dotdict' has no attribute {value} -> result is None")
                raise AttributeError(f"'dotdict' has no attribute {value} ")
        return result

    __getattr__ = myget                   # __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class ProjectSetup(object):
    """
    Class for the Setup from your project.

    read the tb_projectsetup.json file in the directory ..../projec/version/workarea/..../harness

    and create instance slicing
    with init.'yourpath'  you have access to the initialisation setup, which is defined in the tb_projectsetup.json

    Example:
       "instruments": {
          "smu" : [
              {"voltage": 0},
              {"i_clamp": 0.2}
              ]
        }
    ==> create dictionary self.init.instruments.smu = [{'voltage': 0}, {'i_clamp': 0.2}]

    TODO: possibility to overwrite the values in tb_projectsetup.json with the file in tb_ate/src/'Hardware'/'Base'/tb_projectsetup.json

    """

    _RESULT = 'result_projectsetup.json'
    _SETUPFILE = 'tb_projectsetup.json'
    _MYCLASS = 'myclass'

    def __init__(self, logger=None, filename=None):
        """
        Initialise and save setup configuration to the setup-dictionary.

        read the setup-file tb_projectsetup.json
          and create all values in self.init.......

        Args: None

        *Examples:*
           * Initialization
              >>> setup = ProjectSetup()

           * Append some setup information:
              >>> tcc.setup.append('instruments.matrix', 'port', 'pxie6')
              >>> tcc.setup.append('instruments.smu', 'voltage', 5)
              >>> tcc.setup.append('instruments.smu', 'limit', 0.1)
        """
        global mylogger
        self.main_path = str(Path(sys.modules['__main__'].__file__).parent) + os.sep
        os.environ['PROJECT_PATH'] = str(Path(self.main_path).parent.parent.parent) + os.sep
        
        self.network = '' if os.environ.get('NETWORK') is None else os.environ.get('NETWORK')
        self.logger = logger
        mylogger = logger
        self.instName = 'setup'
        self.mylastdotdic = None
        self.lastresult = None
        self.lastmacro = None
        self.running = False
        self._setupfile = None
        if filename is not None:
            self.apply_configuration({'filename': filename})

    def create_dotdic(self, dic, root=None):
        """Make from a dictionary a dot-dictionary with diclist."""
        for mydic in dic.keys():
            if type(dic[mydic]) == dict:
                if root is not None:
                    object.__setattr__(root, mydic, self.create_dotdic(dic[mydic]))
                dic[mydic] = self.create_dotdic(dic[mydic])
            elif type(dic[mydic]) == list:
                dic[mydic] = diclist(self, dic[mydic])
            elif type(dic[mydic]) == str and dic[mydic].find(':') > 0:          # found an arange-function -> change to setupstr
                dic[mydic] = setupstr(dic[mydic])
        return dotdict(dic)

    def initialization(self, parent=None):
        """Set the instruments with the specified instname to its setup values in self.init.instruments.

        and save information (if instname exist!) from the instruments to result.instruments:
            - used class, version, id
        """
        self.parent = parent
        if not self.running:
            for instName in dir(parent):                  # add information from each instrument to result.instruments
                if instName.find('_') != -1:
                    continue
                instrument = getattr(parent, instName)
                if not isclass(instrument):         # filter out the class-definitions
                    if instrument.__class__.__name__ == 'RegisterMaster':
                        self._registermaster = instrument.filename
                    if hasattr(instrument, 'instName'):
                        name = instrument.instName
                    else:
                        name = instrument.__class__.__name__
                        if name in ['Logger', 'module', 'function']:
                            continue
                    # self.write('instruments', name, instrument.__class__)   # default is 'self.result.instruments'
                    self.write('instruments', instName, str(instrument.__class__))   # default is 'self.result.instruments'
        self.running = True
        # TODO!: call runmacro and merge missing function
        if not hasattr(self, 'init'):
            self.logger.log_message(LogLevel.Warning(), f'no instrument init found in actual initialsation: {self.setup.Setupfile}')
            return
        for instrument in self.init:                # initialise the instances to their values in self.init
            items = self.init[instrument]
            self.init_instrument(parent, instrument, items)
        self.logger.log_message(LogLevel.Info(), f"{self.__class__}.init: set instruments to its setup values, defined in {self.setup.Setupfile}")

    def init_instrument(self, parent, instrument, items):
        if type(items) is dotdict and list(items.keys())[0] == self._MYCLASS:
            for myclass in items[self._MYCLASS]:
                if hasattr(parent, instrument) and myclass == getattr(parent, instrument).__class__.__name__:
                    self.init_instrument(parent, instrument, items[self._MYCLASS][myclass])
            return
        if instrument not in dir(parent):
            self.logger.info(f"{self.setup.Setupfile}: Instrument '{instrument}' not found in your Hardware configuration -> do nothing")
            return
        if type(items) is dotdict and len(items.keys()) > 1:
            for item in items:
                self.init_instrument(getattr(parent, instrument), item, items[item])
            return
        for item in items:
            error = False
            cpitem = item
            mypath = getattr(parent, instrument)        # set mypath to the instrument
            if type(item) is dict:
                item = tuple(item.items())[0]
            cmd = item[0]
            value = item[1]
            getattribute = False
            if type(item) is str:
                cmd = item
                getattribute = True
            command = cmd
            if len(cmd.split('.')) > 1:
                split = cmd.split('.')
                if split[0] == 'parent':
                    mypath = parent
                    split.pop(0)
                for index in range(len(split)-1):
                    try:
                        mypath = getattr(mypath, split[index])
                    except Exception:
                        self.logger.info(f'{self.setup.Setupfile}: {instrument} path from {cpitem} not found --> do nothing')
                        error = True
                cmd = split[index+1]
            if error:
                continue
            result = None
            try:
                if getattribute:
                    result = getattr(mypath, cmd, None)
                    self.logger.info(f'{instrument}.{item} == {result}')
                elif cmd.find('(') < 0:
                    setattr(mypath, cmd, value)
                else:                                               # it is a function call
                    cmd = cmd[0:cmd.find('(')]
                    result = getattr(mypath, cmd, None)(value)
            except Exception:
                error = True
            if not error:
                self.write(f'setup.instruments.{instrument}', command, (value, result))
            else:
                self.logger.error(f'{self.setup.Setupfile}:  {instrument}.{cpitem} not found --> do nothing')

    def _replaceSomeThing(self, jsontable):
        """
        Check if jsontable has environment-variables starts with $, or jsontable has path-value.

        if yes than replace environment-variables with its value,
        if it a path-value than add //samba

        """
        for key in jsontable:
            if type(jsontable) == dict:
                value = jsontable[key]
            else:
                value = key
            if type(value) == dict or type(value) == list:
                self._replaceSomeThing(value)
            elif type(value) == str and value.find('$') > -1:   # find environment variables inside the value?
                tmp = value.split('/')
                nvalue = ''
                for s in tmp:
                    if s.find('$') == 0:
                        env = s[1:]
                        s = os.environ.get(env)
                    if s is None:
                        self.logger.log_message(LogLevel.Error(), f'environment {env} not defined')
                        s = ''
                    nvalue += s + '/'
                if nvalue != '':
                    if type(jsontable) == dict:
                        jsontable[key] = nvalue[:-1]
                    else:
                        jsontable[1] = nvalue[:-1]
            elif type(value) == str and len(value) > 0 and value[0] == '/' and os.name == "nt" and value.find(f'{self.network}') != 0:
                if type(jsontable) == dict:
                    jsontable[key] = self.network + value
                else:
                    jsontable[1] = self.network + value

    def write(self, path, name=None, value=None):
        """Write path to the dictionary in my class ProjectSetup.

        Path must be a string like 'instruments.smu'
        normaly append this path to result
        if path start with setup than write to setup.path

        e.q. write('instruments.smu', 'port', 'pxie5')
             write('setup.HostName', os.environ.get('COMPUTERNAME'))
        """
        path = path.split('.')
        lastindex = 'result'
        if path[0] == 'setup':
            lastindex = 'setup'
            path.pop(0)
        mydic = self.__dict__[lastindex]
        lastdic = mydic
        for index in path:
            if index not in mydic.keys():              # than create new dictionary
                if type(mydic) is diclist:
                    if mydic == []:
                        lastdic[lastindex] = dotdict({index: diclist(self)})
                        mydic = lastdic[lastindex]
                    else:
                        mydic.append(dotdict({index: diclist(self)}))
                        mydic = lastdic[lastindex][-1]
                else:
                    mydic[index] = diclist(self)
            lastdic = mydic
            if type(mydic) is diclist:
                mydic = mydic.values(index)
            else:
                mydic = mydic[index]
            lastindex = index
        if name is None:
            mydic += [value]
        else:
            mydic += [{name: value}]

    def _configsave2setup(self):
        self.setup.Date = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        self.setup.Timestamp = time.time()
        self.setup.PROJECT = os.environ.get('PROJECT')
        self.setup.VERSION = os.environ.get('VERSION')
        self.setup.USER = os.environ.get('USER') if os.environ.get('USER') is not None else getpass.getuser()
        self.setup.WORKAREA = os.environ.get('WORKAREA')
        self.setup.COMPUTERNAME = os.environ.get('COMPUTERNAME')
        self.setup.TCC_PYTHONPATH = os.environ.get('TCC_PYTHONPATH')
        self.setup.Setupfile = self._setupfile
        self.setup.Registermaster = self._registermaster if hasattr(self, '_registermaster') else os.environ.get('Registermaster')
        # self.setup.conda = check_output('conda -V', shell=True)[:-2].decode('utf-8')    with maxiconda doesnt' running anymore!?
        # self.setup.python = check_output('python -V', shell=True)[:-2].decode('utf-8')

    def runmacro(self, cmdlist, **kwargs):
        """Execute commands in the cmdlist.

        kwargs: 'wr2setup' : write result to the setup.result json file.
        """
        wr2setup = False
        if 'output' in kwargs:
            wr2setup = kwargs['output'] == 'wr2setup'
        result = []
        macro = myparent.mylastdotdic
        self.lastmacro = macro
        for cmd in cmdlist:
            myresult = self.call(cmd)
            if myresult is not None:
                result.append(myresult)
                self.lastresult = result
            if wr2setup:
                self.write(macro, cmd, myresult)
        if len(result) == 1:
            result = result[0]
        self.lastresult = result
        if cmdlist == []:
            self.logger.log_message(LogLevel.Warning(), f'Macro {macro} not defined in setup')
            if wr2setup:
                self.write('macro', macro, 'not defined in setup')
        return result

    def call(self, mycmd, value=None, senderror=True):              # TODO! : replace call with common.strcall()
        if type(mycmd) == str:
            mycmd = mycmd.split(',')
        result = []
        for cmd in mycmd:
            cmdsplit = cmd.split('.')
            found = False
            if cmdsplit[0] == 'tcc':
                cmdsplit.pop(0)
            if hasattr(self.result, 'instruments') and cmdsplit[0] in self.result.instruments.keys():
                path = self.parent
                found = True
            elif cmdsplit[0] in self.__dict__:
                path = self
                found = True
            if not found:
                if senderror:
                    self.logger.log_message(LogLevel.Error(), f'{cmdsplit[0]} not found in instrumentlist or in {self.instName}, {cmd} not performed')
                result.append(cmd)
                continue
            mypath = getattr(path, cmdsplit[0])
            cmdsplit.pop(0)
            if len(cmdsplit) > 1:
                for index in range(len(cmdsplit)-1):
                    mypath = getattr(mypath, cmdsplit[index])
                command = cmdsplit[index+1]
            else:
                command = cmdsplit[0]
            myresult = None
            if command.find('(') < 0:
                if value is None:
                    myresult = getattr(mypath, command, None)
                else:
                    myresult = setattr(mypath, command, value)
            else:                                               # it is a function call
                value = command[command.find('(')+1:command.find(')')]
                command = command[0:command.find('(')]
                if not hasattr(mypath, command):
                    self.logger.log_message(LogLevel.Error(), f"call error: '{mypath.instName}' has no attribute '{command}'")
                    return None
                if value == '':
                    myresult = getattr(mypath, command, None)()
                else:
                    value = common.str2num(value)
                    if type(value) is str and value.find("'") == 0:
                        value = value[value.find("'")+1:]
                        value = value[:value.find("'")]
                    # else:
                    #    logger.error('macro: variable not supported yet')
                    if type(value) is str and value.find('=') > 0:
                        mydic = {}
                        for arg in value.split(','):
                            tr2dic = arg.split('=')
                            mydic[tr2dic[0]] = common.str2num(tr2dic[1])
                        myresult = getattr(mypath, command, None)(**mydic)
                    else:
                        myresult = getattr(mypath, command, None)(value)
            if myresult is not None:
                result.append(myresult)
        if len(result) == 1:
            result = result[0]
        return result

    def micid(self, typ):
        micid = self.lastresult
        if typ == 'hal':
            value = ((micid[0] << 16)) + micid[1]
            self.logger.log_message(LogLevel.Info(), f'MicID == {hex(value)}')
            self.write(self.lastmacro, 'Y', value & 0x7f)          # Y = Bit 6-0
            self.logger.log_message(LogLevel.Info(), f'      Y == {value & 0x7f}')
            self.write(self.lastmacro, 'X', (value >> 7) & 0x7f)   # Y = Bit 13-7
            self.logger.log_message(LogLevel.Info(), f'      X == {(value >> 7) & 0x7f}')
            self.write(self.lastmacro, 'WNR', (value >> 14) & 0x1f)   # WNR = Bit 18-14
            self.logger.log_message(LogLevel.Info(), f' WNR == {(value >> 14) & 0x1f}')
            self.write(self.lastmacro, 'PLNR', (value >> 19) & 0x1fff)   # PLNR = Bit31-19
            self.logger.log_message(LogLevel.Info(), f' PLNR == {(value >> 19) & 0x1fff}')
        return value

    def regDump(self, liste='default', invert=False, output=None):
        """Read values from Register and return with a list of their values.

        Parameters
        ----------
           liste :
              * 'default' :  if define setup.reg.nodump -> read register without the registers which are defined in setup.reg.nodump
                             if define setup.reg.dump   -> read register which are defined in setup.reg.dump
              * 'all'     :  read all register
              *  type(liste) == list : use liste as a list

           invert :
              * True : use reg that are not in the list
              * False : use reg that are in the list

           output :  :
              * None : return with a list of all registers and their values
              *'wr2setup' : write return with a list of all registers and their values to setup.result.regs.dump
        """
        knownParameter = [None, 'wr2setup']
        if output not in knownParameter:
            self.logger.log_message(LogLevel.Error(), f'output = {output} not found as parameter')
        error = 0
        allregs = []
        allregs = diclist()
        dumplist = []
        mylist = self.parent.regs.register
        invert = False
        if type(liste) == list:
            dumplist = liste
        if liste == 'default' and hasattr(self.regs, 'dump'):
            dumplist = self.regs.dump
        elif hasattr(self.regs, 'nodump'):
            dumplist = self.regs.nodump
            invert = True
        elif liste == 'all':
            dumplist = self.parent.regs.register
        else:
            dumplist = liste
        if type(dumplist) == str:
            foundtcc = dumplist.find('tcc.')
            dumplist = dumplist[4:] if foundtcc == 0 else dumplist
            dump = self.call(dumplist, senderror=False)
        else:
            dump = dumplist
        if type(dump) == dotdict:                           # if it's a memorymap with different addr for the protocoll?
            try:
                dump = dump[self.parent.regs.use]
            except Exception:
                pass
        if type(dump) in [str, setupstr] and dump.find(':') > 0:
            dump = common.arange(dump)
            mylist = dump
        index = 0
        for regname in mylist:
            if (invert and regname not in dump) or (not invert and regname in dump):
                if type(regname) == str:
                    addr = self.parent.regs.register[regname].addr
                    bank = self.parent.regs.register[regname]._bank
                    value = self.parent.regs.register[regname].read()
                    width = self.parent.regs.register[regname]._len_slices() // 4
                else:
                    addr = regname
                    value = self.parent.regs.readreg(regname)
                    bank = 0                                    # self.parent.regs._bank
                    if self.parent.regs._len_slices is not None:
                        width = self.parent.regs._len_slices // 4
                    else:
                        width = 4
                    regname = self.parent.regs.find(addr)
                    if regname is None:
                        regname = f'{dumplist}_{hex(index)}'
                error += 1 if value < 0 else error
                if output is not None and 'wr2setup' in output:
                    bank = 0 if bank is None else bank
                    addr = 0 if addr is None else addr
                    self.write('regs.dump', regname, {'addr': f'0x{bank+addr:03x}', 'dat': f'0x{value:0{width}x}'})
                allregs.append({'addr': f'0x{bank+addr:03x}', 'dat': f'0x{value:0{width}x}'})
                index += 1
        return error, allregs

    def regDumpSave2DUT(self, mode='default', compare='cache'):
        """Write the register with values to the device.

        Parameters
        ----------
           mode :
              * 'default'  use the values from parent.setup.result.regs.dump
              * type(mode) == list : use mode as a list  (not yet implemented)

           compare :
              * 'cache' : compare with the cache value and write if orginal different from last cache value (faster as to read the register value)
              * True : write only if value different from actual values
              * False : write always
        """
        result = 0
        start = False
        if not hasattr(self, 'parent') or not hasattr(self, 'result') or not hasattr(self.result, 'regs'):
            self.logger.log_message(LogLevel.Warning(), f"{self.__class__}.regDumpSave2DUT: no setup.result.regs found, could'nt write back the original register values")
            return -1
        if type(mode) == list:
            dump = mode
        elif mode == 'default' and 'dump' in self.result.regs:
            dump = self.result.regs.dump
            # dump = self.result.regs.dump.keys()               # TODO: bei hana überpruefen, so war es bei HANA!!
        elif mode == 'default' and 'dump' in self.result.regs.keys():
            dump = self.result.regs.dump.values('addr')
            dump = self.result.regs.dump
        else:
            self.logger.log_message(LogLevel.Error(), f'{self.instName}.reg_dump_load: mode == {mode} is not available')
            return
        for reg in dump:
            if reg is str and not self.parent.regs.register[reg]._rw:     # TODO: check rw if a real rw-information
                continue
            addr = -1
            if type(mode) != list:
                if type(reg) == dict or type(reg) == dotdict:
                    originial = common.str2num(tuple(reg.values())[0]['dat'])
                    addr = common.str2num(tuple(reg.values())[0]['addr'])
                else:
                    originial = common.str2num(self.result.regs.dump.value(reg)['dat'])
            else:
                self.logger.log_message(LogLevel.Error(), '{self.instName}.regDumpSave2DUT: sorry this mode is not implemented yet, please investigate')
            if compare == 'cache' and addr == -1:
                actual = self.parent.regs.register[reg].value
            elif addr == -1:
                actual = self.parent.regs.register[reg].read()
            else:                                               # no cache available... have to be read to get the value
                actual = self.parent.regs.readreg(addr)
            if not compare or actual != originial:
                if not start:
                    self.logger.log_message(LogLevel.Info(), f'{self.instName}.regDumpSave2DUT: some values have been changed in the tests:')
                self.logger.log_message(LogLevel.Info(), f'      write back originial register values {reg} actual={hex(actual)}')
                start = True
                if addr == -1:
                    self.parent.regs.register[reg].write(originial)
                else:
                    self.parent.regs.writereg(addr, originial)
        if not start:
            self.logger.log_message(LogLevel.Info(), f'{self.instName}.regDumpSave2DUT: no register values changed in the tests')
        return result

    def unlock(self):
        self.logger.log_message(LogLevel.Info(), f'Try {self.instName}.unlock')
        # self.parent.interface.check_acknowledge = False
        forcebank = self.parent.regs._forcebank
        self.parent.regs._forcebank = False
        for unlock in self.regs.unlock:
            try:
                self.parent.regs.register[unlock[0]].write(unlock[1])
            except KeyError:
                self.logger.log_message(LogLevel.Error(), f"{self.instName}.unlock  register {unlock[0]} doesn't exist in registermaster")
        NVPROGM = self.parent.regs.NVPROGM._read()     # self.parent.regs.register[self.setup.reg_progm]._read()
        self.parent.regs._forcebank = forcebank
        if self.parent.regs.NVPROGM.UNLCK == 0:         # self.parent.regs.__dict__[self.tcc.setup.reg_progm].UNLCK==0:
            self.logger.log_message(LogLevel.Error(), "      -> could't unlock...... NVPROGM = 0x{:04x}".format(NVPROGM))
            result = -1
        else:
            self.logger.log_message(LogLevel.Info(), "      -> ok, unlocked,  0x{:04x}".format(NVPROGM))
            result = 0
        # self.parent.interface.check_acknowledge = True
        return(NVPROGM, result)

    def close(self):
        """Write EEPROM/NVRAM with the rescue values and close all instruments.

        Close all instruments and write the dictionary to the log-file.

        Returns
        -------
        None.
        """
        if not self.running:        # nothing to do, already closed
            return
        if hasattr(self, 'regs') and hasattr(self.regs, 'wrbackdump') and self.regs.wrbackdump:
            try:
                self.regDumpSave2DUT()          # write the orginal data to the device only if cache value different
            except Exception:
                self.logger.log_message(LogLevel.Error(), "setup.close(): Couln't execute reg_dump_load")
        self.running = False
        self._write()
        #if hasattr(self.parent, 'semictrl'):
        #    self.parent.semictrl.mqttc.close()
        self.logger.log_message(LogLevel.Info(), "setup closed")

    def _write(self):
        """Write the dictionary to the logfile."""
        # self.__dict__.pop('init')
        with open(os.getenv('PROJECT_PATH') + "output" + os.sep + self._RESULT, 'w') as outfile:
            outfile.write('{')
            self.jsondump(outfile, self.setup)
            outfile.write('    ,\n')
            self.jsondump(outfile, 'result')
            # json.dump(self.setup, outfile, indent=2)            # json.dump(self.result, outfile, indent=2)     # sort_keys=True
            outfile.write('\n}')
        self.logger.log_message(LogLevel.Info(), f'write results to {self._RESULT}')

    def jsondump(self, file, dictionary, ident=4):
        '''dump the dictionary to json-format

        you can also use json.dump but I think this generated output-format is better for easy reading
        '''
        def space(ident, lenght=2):
            if lenght < 2 and ident > 4:
                return
            for i in range(0, ident):
                file.write(' ')

        end = ''
        spara = '{'
        if type(dictionary) is str:
            space(ident, 3)
            file.write(f'"{dictionary}": {spara}')
            dictionary = self.__dict__[dictionary]
            end = '}'
            ident = 8
            space(ident, 3)
        length = len(dictionary)
        index = 0
        more = ','
        cr = '\n'
        if length < 2 and ident > 4:
            cr = ''
        else:
            pass
        file.write(f'{cr}')
        for item in dictionary:
            index += 1
            if index == length:
                more = ''
            if type(dictionary) in [dict, dotdict]:
                value = dictionary[item]
            else:
                value = dictionary[index-1]
            spara = '{'
            epara = '}'
            if type(value) in [list, diclist]:
                spara = '['
                epara = ']'
            if type(value) in [dict, dotdict, list, diclist]:
                space(ident, length)
                try:
                    if item == value and type(item) is dict:                   # is it a list with dictionaries
                        json.dump(item, file)
                        file.write(f'{more}{cr}')
                    elif item == value:                                        # it is a list with dotdictionaries
                        file.write(f'{spara}')
                        self.jsondump(file, value, ident+4)
                        file.write(f'{epara}{more}{cr}')
                    else:                               # it is dict or dotdict
                        file.write(f'"{item}": {spara}')
                        self.jsondump(file, value, ident+4)
                        file.write(f'{epara}{more}{cr}')
                except Exception:
                    file.write(f"ERROR!!!: coudn't write {item} as json dump {more}{cr}")
            else:
                if type(value) == str:
                    value = f'"{value.replace(os.sep, "/")}"'
                space(ident, length)
                if item != value:
                    file.write(f'"{item}": {value}{more}{cr}')
                else:
                    file.write(f'{value}{more}{cr}')
        if cr != '':
            space(ident-4, length)
        file.write(f'{end}')

    def __repr__(self):
        return f"{self.__class__}"

    def set_configuration_values(self, data):
        """Only empty dummy function."""
        self.logger.log_message(LogLevel.Warning(), 'TCCLabor.ProjectSetup: set_configuration_values only dummy function..................................')
        pass

    def apply_configuration(self, data):
        if 'Network prefix' in data and data['Network prefix'] != '' and os.name == "nt":
            self.network = data['Network prefix']
            os.environ['NETWORK'] = self.network
        config = environment.replaceEnvs(data)
        project_path = self.main_path
        harness = ''
        working_dir= ''
        if 'working directory' in config and config['working directory'] != '':        
            for path in config['working directory'].split(';'):
                if os.path.exists(path):
                    working_dir = path
            os.environ['WORKING_DIR'] = working_dir
            if working_dir != '':
                self.logger.log_message(LogLevel.Info(), f'LABML.Instruments: get WORKING_DIR from the Plugin parameter-file = {working_dir}')
        if 'add path' in config and config['add path'] != '':
            harness = config['add path']
        self.logger.log_message(LogLevel.Info(), '$LOGGINGFILENAME$ {};{}'.format(project_path, self.logger.get_log_file_information()['filename']))

        environment.environ_getpath(self, 'registermaster')      # replace environment for registermaster if os='nt'
        project_path = os.environ['PROJECT_PATH']
        harness = working_dir + harness if working_dir != "" else str(Path(project_path).parent) + os.sep + harness
        sys.path.append(working_dir if working_dir != "" else str(Path(project_path).parent))
        os.environ['harness'] = harness

        self.logger.log_message(LogLevel.Info(), f'TCCLabor.ProjectSetup: apply_configuration  {config}')
        setupfile = config['filename'] if 'filename' in config and config['filename'] != '' else None
        workarea = os.environ.get('WORKAREA')
        readonly = True
#        if workarea is None and setupfile is None:
#            self.logger.log_message(LogLevel.Warning(), "TCCLabor.ProjectSetup: No setup file name and no $WORKAREA exist !!")
        if setupfile is None:
            setupfile = file_io.replaceFilename(f'$HARNESS/{self._SETUPFILE}')
            readonly = False
        if os.path.isfile(setupfile):
            with file_io.openFile(setupfile, 'r') as file:
                try:
                    self.setup = json.load(file, cls=JsonDecoder)
                except Exception as error:
                    self.logger.error(f"{self.instName}: syntax error in {setupfile} : {error}")      # TODO!: add json validator: pip install jsonschema
                    sys.exit()
            self._replaceSomeThing(self.setup)        # replace path-variables if windows, replace env-variable with their values
        else:
            self.setup = {'Setupfile': None}
            level = LogLevel.Warning() if setupfile is None else LogLevel.Error()
            self.logger.log_message(level, "TCCLabor.ProjectSetup: setup file not exist !!")
            setupfile = None

        self.create_dotdic(self.setup, self)
        self.setup = dotdict({})
        self._setupfile = setupfile
        self.mylastdotdic = None
        self.lastresult = None
        self.lastmacro = None
        self.running = False
        #if not readonly:
        if True:
            self._configsave2setup()
            self.result = dotdict([])


if __name__ == '__main__':
    from ATE.common.logger import Logger

    logger = Logger('logger')
    setup = ProjectSetup(logger, '//samba/proot/hana/0504/workareas/appslab/units/lab.Win64/source/python/tb_ate/src/HW0/FT/result_projectsetup-20012022.json')
    print(setup.result.regs.dump.keys())

    setup.initialization()

    print(setup.init.smu)
    print(setup.init.matrix)

    setup.write('regs', 'EEPROM1', 5)
    setup.write('regs', 'EEPROM2', 15)
    setup.write('empty', 'Idontknow', 'test')

    print(setup.result.instruments)
    print(setup.result.regs)
    print(type(setup.result.regs))
    print(setup.result.regs.keys())
    setup.result.regs.value('EEPROM2')
    setup.result.regs.value('Mytest')
    setup.result.regs.value()
    setup.macro.hwid.run()

    setup.close()
