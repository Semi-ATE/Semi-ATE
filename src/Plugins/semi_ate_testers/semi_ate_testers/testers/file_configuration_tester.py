import sys
import os
from pathlib import Path
import importlib
import inspect
from semi_ate_testers.testers.tester_interface import TesterInterface

TESTER_CONFIG_FILE = 'testerconfig.py'

class FileConfigurationTester(TesterInterface):
    SITE_COUNT = 1
    
    def __init__(self, logger):
        TesterInterface.__init__(self, logger)
        self.hw_path = str(Path(sys.modules['__main__'].__file__).parent.parent) + os.sep
        

    def pulse_trigger_out(self, pulse_width_ms):
        # ToDo: Implement with actual hardware.
        self.log_info("Single Tester: Pulse Trigger Out")

    def do_request(self, site_id: int, timeout: int) -> bool:
        return True

    def test_in_progress(self, site_id: int):
        pass

    def test_done(self, site_id: int, timeout: int):
        pass

    def do_init_state(self, site_id: int):
        myfile = '$$$HW' + TESTER_CONFIG_FILE
        testerconfig = None
        with open(self.hw_path + myfile, 'w') as f:
            f.write('# -*- coding: utf-8 -*-\n"""\n\n')
            f.write("Don't edit this file. It will be overwriten at runtime. Any manual edits will be lost\n")
            f.write('"""\n')
            f.write("import sys\n")
            f.write("logger = sys.argv[2]\n")
        if Path(self.hw_path + TESTER_CONFIG_FILE).is_file():
            source = self.hw_path + TESTER_CONFIG_FILE
            with open(self.hw_path+myfile, 'a') as dest:
                with open(Path(source), 'r') as src:
                    lines = src.readlines()
                dest.writelines(lines)
            sys.argv.append('--labml')
            sys.argv.append(self.logger)
            pythonPath = f'{self.hw_path.split(os.sep)[-3]}.{self.hw_path.split(os.sep)[-2].upper()}.'
            doExit = False
            try:
                testerconfig = importlib.import_module(pythonPath + os.path.splitext(myfile)[0])
            except Exception as ex:
                msg = f'exception in {TESTER_CONFIG_FILE} : {ex}'
                self.log_error(msg)
                doExit = True
            sys.argv.pop()
            sys.argv.pop()
            if doExit:
                raise Exception(msg)
        else:
            self.log_error(f'No Tester file configuration found, you have to create {self.hw_path + TESTER_CONFIG_FILE}')
        self.testerconfig = testerconfig
        for instrument in dir(testerconfig):  # add information from each instrument to result.instruments
            if instrument.find("_") != -1:
                continue
            instrument = getattr(testerconfig, instrument)
            if not inspect.isclass(instrument):  # filter out the class-definitions
                if hasattr(instrument, "instName"):
                    setattr(self, instrument.instName, instrument)
        self.log_info(f"FileConfigurationTester.do_int_state({site_id}): done")
