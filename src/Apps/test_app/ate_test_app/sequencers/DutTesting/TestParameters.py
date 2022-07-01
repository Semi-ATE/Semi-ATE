# # -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Dict
from ate_apps_common.stdf_utils import (generate_MPR_dict, generate_PTR_dict, generate_TSR_dict)
from ate_test_app.sequencers.DutTesting.Result import Result

import math

INITIAL_MEASUREMENT_NUMBER = 5000


class InputParameter:
    __slots__ = ['_value', '_shmoo', '_name', '_min', '_max', '_exponent']

    def __init__(self, name: str, shmoo: bool, value: float, min_value: float, max_value: float, exponent: int):
        self._value = value
        self._shmoo = shmoo
        self._name = name
        self._min = min_value
        self._max = max_value
        self._exponent = exponent

    def set_parameter_value(self, value: float):
        if self._shmoo is False:
            raise Exception(f"Input-parameter '{self._name}' is not shmooable")

        if value < self._min or value > self._max:
            raise Exception(f"Input-parameter '{self._name}' could not be set, value out of range '{value}'")

        self._value = value

    def __call__(self):
        return self._value


class Measurement(ABC):
    __slots__ = ['_measurement', '_is_set']

    def __init__(self):
        self._is_set = False

    def write(self, measurement):
        self._is_set = True
        self.write_impl(measurement)

    def read(self):
        return self._measurement

    def reset(self):
        self._is_set = False
        self.reset_impl()

    @property
    def is_set(self):
        return self._is_set

    @abstractmethod
    def write_impl(self, measurement):
        pass

    @abstractmethod
    def read_impl(self):
        pass

    @abstractmethod
    def reset_impl(self):
        pass


class MultiMeasurement(Measurement):
    def __init__(self):
        super().__init__()
        self._measurement = []

    def write_impl(self, measurement):
        self._measurement.append(measurement)

    def read_impl(self):
        return self._measurement

    def reset_impl(self):
        self._measurement.clear()


class SingleMeasurement(Measurement):
    def __init__(self):
        super().__init__()
        self._measurement = math.inf

    def write_impl(self, measurement):
        self._measurement = measurement

    def read_impl(self):
        return self._measurement

    def reset_impl(self):
        self._measurement = math.inf


class OutputParameter:
    __slots__ = [
        '_name', '_lsl', '_ltl', '_nom', '_utl', '_usl', '_exponent', '_fmt', '_unit',
        '_mpr', '_measurements', '_measurement', '_id', 'bin', 'bin_result', '_test_executions',
        '_test_failures', '_alarmed_tests', '_test_description'
    ]

    def __init__(self, name: str, lsl: float, ltl: float, nom: float, utl: float, usl: float, exponent: int, mpr: bool = False):
        self._name = name
        self._lsl = lsl
        self._ltl = ltl
        self._nom = nom
        self._utl = utl
        self._usl = usl
        self._exponent = int(exponent)
        self._fmt = None
        self._unit = None
        self._mpr = mpr

        self._measurements = [] * INITIAL_MEASUREMENT_NUMBER
        self._measurement = SingleMeasurement() if not mpr else MultiMeasurement()
        self._id = 0
        self.bin = 0
        self.bin_result = Result.Fail()
        self._test_executions = 0
        self._test_failures = 0
        self._alarmed_tests = 0
        self._test_description = ''

    def set_format(self, fmt: str):
        self._fmt = fmt

    def set_unit(self, unit: str):
        self._unit = unit

    def set_test_description(self, test_description: str):
        self._test_description = test_description

    def generate_stdf_result_record(self, is_pass: bool, site_num: int) -> Dict[str, str]:
        if self._mpr is True:
            return self._generate_mpr_record(is_pass, site_num)
        else:
            return self._generate_ptr_record(is_pass, site_num)

    def _get_output_parameter_name(self):
        return self._test_description + '.' + self._name

    def get_measurement(self):
        return self._measurement.read()

    def get_exponent(self):
        return self._exponent

    def write(self, measurement: float):
        self._measurement.write(measurement)
        self._measurements.append(measurement)

    def default(self):
        if math.isnan(self._ltl):
            LTL = self._lsl
        else:
            LTL = self._ltl

        if math.isnan(self._utl):
            UTL = self._usl
        else:
            UTL = self._utl

        if math.isinf(LTL):
            value = -math.inf
        elif math.isinf(UTL):
            value = math.inf
        else:
            value = (UTL - LTL) / 2 + LTL

        self.write(value)

    def set_limits(self, id: int, ltl: float, utl: float):
        self._id = id
        if(ltl > utl):
            raise ValueError("LTL must be smaller than UTL")

        if(ltl < self._lsl or utl > self._usl):
            raise ValueError("Testlimits must not violate speclimits")

        self._ltl = ltl
        self._utl = utl

    def set_bin(self, bin: int, bin_result: int):
        self.bin = bin
        self.bin_result = bin_result

    def _generate_ptr_record(self, is_pass: bool, site_num: int) -> Dict[str, str]:
        l_limit, u_limit = self._get_limits()
        l_limit = l_limit * (10**self._exponent)
        u_limit = u_limit * (10**self._exponent)
        lsl = self._lsl * (10**self._exponent)
        usl = self._usl * (10**self._exponent)

        is_pass = self._measurement.read() >= l_limit and self._measurement.read() <= u_limit and self._measurement.is_set

        measurement = lsl if self._measurement is None else self._measurement.read() * (10**self._exponent)
        return generate_PTR_dict(
            test_num=self._id,
            head_num=0,
            site_num=int(site_num),
            is_pass=is_pass,
            param_flag=0,
            measurement=measurement,
            test_txt=self._get_output_parameter_name(),
            alarm_id='',
            l_limit=l_limit,
            u_limit=u_limit,
            unit=self._unit,
            fmt=self._fmt,
            exponent=int(self._exponent) * -1,
            ls_limit=lsl,
            us_limit=usl)

    def _generate_mpr_record(self, is_pass: bool, site_num: int) -> Dict[str, str]:
        l_limit, u_limit = self._get_limits()
        l_limit = l_limit * (10**self._exponent)
        u_limit = u_limit * (10**self._exponent)
        lsl = self._lsl * (10**self._exponent)
        usl = self._usl * (10**self._exponent)
        record = generate_MPR_dict(
            test_num=self._id,
            head_num=0,
            site_num=int(site_num),
            is_pass=is_pass == Result.Pass(),
            param_flag=0,
            measurements=[measurement * (10**self._exponent) for measurement in self._measurement.read()],
            test_txt=self._get_output_parameter_name(),
            alarm_id='',
            l_limit=l_limit,
            u_limit=u_limit,
            unit=self._unit,
            fmt=self._fmt,
            exponent=int(self._exponent) * -1,
            ls_limit=lsl,
            us_limit=usl)

        self._measurement.reset()
        return record

    def get_testresult(self):
        self._test_executions += 1

        if self._mpr is False:
            return self._get_ptr_test_result()
        else:
            return self._get_mpr_test_result()

    def _get_ptr_test_result(self):
        ll, ul = self._get_limits()
        if not self._measurement.is_set:
            raise Exception(f'no measured value is available for test parameter "{self._get_output_parameter_name()}"')

        if math.isnan(ll) and math.isnan(ul):
            return (Result.Pass(), 1)

        fail_result = -1
        pass_result = -1
        if self.bin_result == Result.Fail():
            fail_result = self.bin
        if self.bin_result == Result.Pass():
            pass_result = self.bin

        if self._measurement.read() >= ll and self._measurement.read() <= ul:
            return (Result.Pass(), pass_result)
        else:
            self._test_failures += 1
            return (Result.Fail(), fail_result)

    def _get_mpr_test_result(self):
        ll, ul = self._get_limits()
        if not self._measurement.is_set:
            raise Exception(f'no measured value is available for test parameter "{self._get_output_parameter_name()}"')

        if math.isnan(ll) and math.isnan(ul):
            return (Result.Pass(), 1)

        fail_result = -1
        pass_result = -1
        if self.bin_result == Result.Fail():
            fail_result = self.bin
        if self.bin_result == Result.Pass():
            pass_result = self.bin

        any_fail = any(m < ll or m > ul for m in self._measurements)

        if any_fail is True:
            self._test_failures += 1
            return (Result.Fail(), fail_result)
        else:
            return (Result.Pass(), pass_result)

    def _get_limits(self):
        ll, ul = -math.inf, math.inf
        lls = [self._ltl, self._lsl]
        uls = [self._utl, self._usl]
        try:
            ll = [limit for limit in lls if not math.isnan(limit) and math.isfinite(limit)][0]
        except IndexError:
            pass

        try:
            ul = [limit for limit in uls if not math.isnan(limit) and math.isfinite(limit)][0]
        except IndexError:
            pass

        return ll, ul

    def generate_tsr_record(self, head_num: int, site_num: int, execution_time: float):
        if execution_time > 0 and len(self._measurements) != 0:
            return self._generate_valid_tsr_record(head_num, site_num, execution_time)
        else:
            return self._generate_empty_tsr_record(head_num, site_num, execution_time)

    def _generate_valid_tsr_record(self, head_num: int, site_num: int, execution_time: float):
        return generate_TSR_dict(head_num=head_num, site_num=site_num, test_typ='P',
                                 test_num=self._id, exec_cnt=self._test_executions, fail_cnt=self._test_failures,
                                 alarm_cnt=1, test_nam=self._test_description, seq_name='seq_name',
                                 test_lbl=self._get_output_parameter_name(),
                                 opt_flag=['0', '0', '0', '1', '0', '0', '0', '0'],
                                 test_tim=execution_time,
                                 test_min=self._get_lowest_test_result(),
                                 test_max=self._get_highest_test_result(),
                                 tst_sums=self._sum_of_test_result_values(),
                                 tst_sqrs=self._sum_of_squares_of_test_result_values())

    def _generate_empty_tsr_record(self, head_num: int, site_num: int, execution_time: float):
        return generate_TSR_dict(head_num=head_num, site_num=site_num, test_typ='P',
                                 test_num=self._id, exec_cnt=self._test_executions, fail_cnt=self._test_failures,
                                 alarm_cnt=1, test_nam=self._test_description, seq_name='seq_name',
                                 test_lbl=self._get_output_parameter_name(),
                                 opt_flag=['1', '1', '1', '1', '1', '1', '1', '1'],
                                 test_tim=execution_time,
                                 test_min=0.0,
                                 test_max=0.0,
                                 tst_sums=0.0,
                                 tst_sqrs=0.0)

    def _get_highest_test_result(self):
        return max(self._measurements)

    def _get_lowest_test_result(self):
        return min(self._measurements)

    def _sum_of_test_result_values(self):
        return sum(self._measurements)

    def _sum_of_squares_of_test_result_values(self):
        try:
            average = sum(self._measurements) / len(self._measurements)
        except ZeroDivisionError:
            return 0.0

        return sum([pow((result - average), 2) for result in self._measurements])
