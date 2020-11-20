# # -*- coding: utf-8 -*-
import numpy as np

from ATE.Tester.TES.apps.testApp.sequencers.Utils import (generate_PTR_dict, generate_TSR_dict)
from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.Result import Result


class InputParameter:
    def __init__(self, name, shmoo, value):
        self._value = value
        self._shmoo = shmoo
        self._name = name

    def __call__(self):
        return self._value


class OutputParameter:
    def __init__(self, name, lsl, ltl, nom, utl, usl):
        self._name = name
        self._lsl = lsl
        self._ltl = ltl
        self._nom = nom
        self._utl = utl
        self._usl = usl

        self._measurements = []
        self._measurement = self._lsl
        self._id = 0
        self.bin = 0
        self.bin_result = Result.Fail()
        self._test_executions = 0
        self._test_failures = 0
        self._alarmed_tests = 0
        self._test_description = ''

    def set_test_description(self, test_description):
        self._test_description = test_description

    def _get_PTR_test_name(self):
        return self._test_description + '.' + self._name

    def write(self, measurement):
        self._measurement = measurement
        self._measurements.append(measurement)

    def randn(self):
        if np.isnan(self._ltl):
            LTL = self._lsl
        else:
            LTL = self._ltl

        if np.isnan(self._utl):
            UTL = self._usl
        else:
            UTL = self._utl

        μ = self._nom

        σ = abs(μ - LTL)
        if σ < abs(UTL - μ):
            σ = abs(UTL - μ)
        σ = σ / 3

        self.write(np.random.normal(μ, σ))

    def set_limits(self, id, ltl, utl):
        self._id = id
        if(ltl > utl):
            raise ValueError("LTL must be smaller than UTL")

        if(ltl < self._lsl or utl > self._usl):
            raise ValueError("Testlimits must not violate speclimits")

        self._ltl = ltl
        self._utl = utl

    def set_bin(self, bin, bin_result):
        self.bin = bin
        self.bin_result = bin_result

    def generate_ptr_record(self, is_pass, site_num):
        return generate_PTR_dict(test_num=self._id + 1, head_num=0, site_num=int(site_num),
                                 is_pass=is_pass == Result.Pass(), param_flag=0, measurement=self._measurement,
                                 test_txt=self._get_PTR_test_name(), alarm_id='')

    def get_testresult(self):
        self._test_executions += 1

        ll, ul = self._get_limits()
        if np.isnan(ll) and np.isnan(ul):
            return (Result.Pass(), 1)

        fail_result = -1
        pass_result = -1
        if self.bin_result == Result.Fail():
            fail_result = self.bin
        if self.bin_result == Result.Pass():
            pass_result = self.bin

        if self._measurement >= ll and self._measurement <= ul:
            return (Result.Pass(), pass_result)
        else:
            self._test_failures += 1
            return (Result.Fail(), fail_result)

    def _get_limits(self):
        ll, ul = -np.Inf, np.Inf
        lls = [self._ltl, self._lsl]
        uls = [self._utl, self._usl]
        try:
            ll = [limit for limit in lls if not np.isnan(limit) and not np.isneginf(limit)][0]
        except IndexError:
            pass

        try:
            ul = [limit for limit in uls if not np.isnan(limit) and not np.isposinf(limit)][0]
        except IndexError:
            pass

        return ll, ul

    def generate_tsr_record(self, head_num, site_num, execution_time):
        if execution_time > 0:
            return self._generate_valid_tsr_record(head_num, site_num, execution_time)
        else:
            return self._generate_empty_tsr_record(head_num, site_num, execution_time)

    def _generate_valid_tsr_record(self, head_num, site_num, execution_time):
        return generate_TSR_dict(head_num=head_num, site_num=site_num, test_typ='P',
                                 test_num=self._id, exec_cnt=self._test_executions, fail_cnt=self._test_failures,
                                 alarm_cnt=1, test_nam=self._test_description, seq_name='seq_name',
                                 test_lbl=self._get_PTR_test_name(),
                                 opt_flag=['0', '0', '0', '1', '0', '0', '0', '0'],
                                 test_tim=execution_time,
                                 test_min=self._get_lowest_test_result(),
                                 test_max=self._get_highest_test_result(),
                                 tst_sums=self._sum_of_test_result_values(),
                                 tst_sqrs=self._sum_of_squares_of_test_result_values())

    def _generate_empty_tsr_record(self, head_num, site_num, execution_time):
        return generate_TSR_dict(head_num=head_num, site_num=site_num, test_typ='P',
                                 test_num=self._id, exec_cnt=self._test_executions, fail_cnt=self._test_failures,
                                 alarm_cnt=1, test_nam=self._test_description, seq_name='seq_name',
                                 test_lbl=self._get_PTR_test_name(),
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
