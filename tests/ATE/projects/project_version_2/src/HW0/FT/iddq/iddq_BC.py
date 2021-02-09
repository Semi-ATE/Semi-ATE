# -*- coding: utf-8 -*-
"""

Do **NOT** change anything in this module, as it is automatically generated thus your changes **WILL** be lost in time!

If you have the need to add things, add it to 'iddq.py' or 'common.py'

BTW : YOU SHOULD **NOT** BE READING THIS !!!
"""

from numpy import nan, inf
from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.TestParameters import OutputParameter
from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.DutTestCaseABC import DutTestCaseBase
from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.Result import Result
from ATE.Tester.TES.apps.testApp.parameters.ResolverFactory import create_parameter_resolver
from ATE.common.logger import (LogLevel, Logger)


class iddq_OP:
    """Class definition for the output parameters of iddq."""

    def __init__(self):
        self.num_outputs = 0
        self.new_parameter1 = OutputParameter('new_parameter1', -inf, nan, 0.0, nan, inf, 0)
        self.new_parameter1.set_format('.3f')
        self.new_parameter1.set_unit('˽')

    def set_parameter(self, name: str, id: int, ltl: float, utl: float, bin: int, bin_result: int, test_desc: str):
        output = getattr(self, f'{name}')
        output.set_limits(id, ltl, utl)
        output.set_bin(bin, bin_result)
        output.set_test_description(test_desc)
        self.num_outputs += 1

    def get_output_nums(self) -> int:
        return self.num_outputs

class iddq_IP:
    """Class definition for the input parameters of iddq."""

    def __init__(self):
        self.Temperature = None

    def set_parameter(self, name: str, type: str, value: float, min_value: float, max_value: float, power: int, context: str):
        setattr(self, f'{name}', create_parameter_resolver(type, f'{name}', '', value, min_value, max_value, power, context))


class iddq_BC(DutTestCaseBase):
    '''Base class definition for iddq'''

    hardware = 'HW0'
    base = 'FT'
    Type = 'custom'

    def __init__(self, logger: Logger):
        super().__init__(None, None, logger)
        self.ip = iddq_IP()
        self.op = iddq_OP()
        self._sbin = None
        self._test_num = None

    def aggregate_test_result(self, site_num: int, exception: bool):
        stdf_data = []
        test_result = Result.Inconclusive()
        test_bin = -1
        if not exception:
            current_result = self.op.new_parameter1.get_testresult()
            test_result = self._select_testresult(test_result, current_result)
            test_bin = self._select_bin(test_bin, current_result)
            stdf_data.append(self.op.new_parameter1.generate_ptr_record(current_result[0], site_num))
        else:
            test_result = Result.Fail()
            test_bin = self.get_sbin()
            stdf_data.append(self.op.new_parameter1.generate_ptr_record(test_result, site_num))

        return (test_result, test_bin, stdf_data)

    def aggregate_tests_summary(self, head_num: int, site_num: int):
        stdf_data = []
        stdf_data.append(self.op.new_parameter1.generate_tsr_record(head_num, site_num, self.get_average_test_execution_time()))

        return stdf_data

    def set_sbin(self, sbin: int):
        self._sbin = sbin

    def get_sbin(self):
        return self._sbin

    def set_test_num(self, test_num: int):
        self._test_num = test_num

    def get_test_num(self):
        return self._test_num

    def log_info(self, message: str):
        self.logger.log_message(LogLevel.Info(), message)

    def log_debug(self, message: str):
        self.logger.log_message(LogLevel.Debug(), message)

    def log_warning(self, message: str):
        self.logger.log_message(LogLevel.Warning(), message)

    def log_error(self, message: str):
        self.logger.log_message(LogLevel.Error(), message)

    def log_measure(self, message: str):
        self.logger.log_message(LogLevel.Measure(), message)

    def get_test_nums(self) -> int:
        return self.op.get_output_nums()