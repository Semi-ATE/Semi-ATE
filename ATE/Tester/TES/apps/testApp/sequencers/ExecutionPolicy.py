from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.Result import Result
from abc import ABC, abstractmethod
import time


class ExecutionPolicyABC(ABC):

    @abstractmethod
    def run(self, sequencer_instance):
        raise Exception("Cannot use base execution policy directly")


class LoopCycleExecutionPolicy(ExecutionPolicyABC):
    def __init__(self, num_cycles):
        self.num_cycles = num_cycles

    def run(self, sequencer_instance: object):
        for _ in range(self.num_cycles):
            test_index = 0
            num_written_op = 0
            start = time.time()
            sequencer_instance.pre_cycle_cb()       # ToDo: This will kill all records generated up to now, which is probably not what we want if num_cycles > 1
            test_result = Result.Inconclusive()
            for test_case in sequencer_instance.test_cases:

                sequencer_instance.pre_test_cb(test_index)
                result, exception = test_case.run(sequencer_instance.site_id)

                # Push result back to sequencer, abort testing if sequencer
                # returns false
                if not sequencer_instance.after_test_cb(test_index, result, test_case.get_test_num(), exception):
                    end = time.time()
                    break

                test_index += 1
                num_written_op += test_case.get_test_nums()

                if not exception:
                    test_result = test_case._select_testresult(test_result, result)

            end = time.time()
            execution_time = int((end - start) * 1000.0)
            sequencer_instance.after_cycle_cb(execution_time, num_written_op, test_result)


class SingleShotExecutionPolicy(LoopCycleExecutionPolicy):
    def __init__(self):
        super().__init__(1)
