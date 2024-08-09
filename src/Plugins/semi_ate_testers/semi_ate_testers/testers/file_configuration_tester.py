import sys
import os
import socket
from pathlib import Path
import importlib
import inspect
from semi_ate_testers.testers.tester_interface import TesterInterface

TESTER_CONFIG_FILE = 'testerconfig'


class FileConfigurationTester(TesterInterface):
    SITE_COUNT = 1

    def __init__(self, logger):
        import __main__

        TesterInterface.__init__(self, logger)
        self.hw_path = str(Path(__main__.__file__).parent.parent) + os.sep

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
        testerconfig = self.hw_path + TESTER_CONFIG_FILE
        testerconfigTemp = Path(testerconfig + "_tmp.py")
        extension = ""
        for ad in [os.getenv('USER'), socket.gethostname()]:
            if ad is not None and Path(testerconfig + "_" + ad + ".py").is_file():
                extension = "_" + ad

        if extension != "":
            self.log_warning("You are not using the default Tester configuration file !!!")

        with open(testerconfigTemp, 'w') as f:
            f.write('# -*- coding: utf-8 -*-\n"""\n\n')
            f.write("Don't edit this file. It will be overwriten at runtime. Any manual edits will be lost\n")
            f.write('"""\n')
            f.write("import sys\n")
            f.write("logger = sys.argv[2]\n")
        self.logger.debug = self.log_debug
        self.logger.measure = self.log_measure
        self.logger.info = self.log_info
        self.logger.warning = self.log_warning
        self.logger.error = self.log_error

        if Path(testerconfig + extension + ".py").is_file():
            self.log_info(f"Use Tester configuration file : {testerconfig + extension}.py")
            with open(testerconfigTemp, 'a') as dest:
                with open(testerconfig + extension + ".py", "r") as src:
                    lines = src.readlines()
                dest.writelines(lines)
            sys.argv.append('--labml')
            sys.argv.append(self.logger)
            pythonPath = f'{self.hw_path.split(os.sep)[-2].upper()}.'
            doExit = False
            try:
                testerconfig = importlib.import_module(pythonPath + TESTER_CONFIG_FILE + "_tmp")
            except Exception as ex:
                msg = f'exception in {TESTER_CONFIG_FILE} : {ex}'
                self.log_error(msg)
                doExit = True
                testerconfig = None
            sys.argv.pop()
            sys.argv.pop()
            if doExit:
                raise Exception(msg)
        else:
            self.log_error(f"No Tester file configuration found, you have to create {self.hw_path + TESTER_CONFIG_FILE}.py")

        self.testerconfig = testerconfig

        for instName in dir(testerconfig):  # add information from each instrument to result.instruments
            if instName.find("_") == 0:
                continue
            instrument = getattr(testerconfig, instName)
            if not inspect.isclass(instrument):  # filter out the class-definitions
                if hasattr(instrument, "instName"):
                    setattr(self, instrument.instName, instrument)
                elif instName not in dir(self) or instName in ['SITE_COUNT', 'run_pattern', 'teardown', 'setup', 'do_request', 'test_in_progress', 'test_done', 'do_init_state']:
                    setattr(self, instName, instrument)
                elif instName not in ['logger']:
                    self.log_error(f' keyword "{instName}" not allowed in {TESTER_CONFIG_FILE}')

        self.log_info(f"FileConfigurationTester.do_int_state({site_id}): done")
