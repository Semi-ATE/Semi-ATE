from abc import ABC, abstractmethod
import time


class DutTestCaseABC(ABC):
    def run(self, site_num):
        start = time.time()
        self.do()
        end = time.time()
        self._execution_time += end - start
        self._test_executions += 1
        return self.aggregate_test_result(site_num)

    def set_instance_number(self, instance_number):
        self.instance_number = instance_number

    @abstractmethod
    def aggregate_test_result(self, site_num):
        pass

    @abstractmethod
    def do(self):
        pass


class DutTestCaseBase(DutTestCaseABC):
    def __init__(self, sbins, active_hardware):
        self.sbins = sbins
        self.active_hardware = active_hardware
        self._execution_time = 0
        self._test_executions = 0

    def aggregate_test_result(self, site_num):
        pass

    def do(self):
        pass

    @staticmethod
    def _select_bin(current_bin, test_result_tuple):
        '''
            At this point we use a hardcoded ATE.org binning
            strategy, where
            bin 0 = Contact Fail
            bin 1 - 10 = Passbins
            bins > 10 = Failbins
            this means:
            No result will be able to change a fail bin to
            a pass bin
            No result will be able to change a fail bin to
            another fail bin
            No result will be able to change a low grade bin
            to a higher grade bin
        '''

        if current_bin == -1:
            return test_result_tuple[1]

        if current_bin in range(1, 10) and test_result_tuple[1] in range(1, 10):
            if current_bin < test_result_tuple[1]:
                return test_result_tuple[1]
            return current_bin

        # cannot change a once failed bin
        if current_bin > 10 and test_result_tuple[1] > 10:
            return current_bin

        if current_bin in range(1, 10) and test_result_tuple[1] > 10:
            return test_result_tuple[1]

        return current_bin

    @staticmethod
    def _select_testresult(current_testresult, test_result_tuple):
        if current_testresult < test_result_tuple[0]:
            return test_result_tuple[0]
        return current_testresult

    def get_average_test_execution_time(self):
        try:
            return float(self._execution_time / (self._test_executions * self.op.num_outputs))
        except ZeroDivisionError:
            return -1.0
