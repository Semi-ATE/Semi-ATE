from ate_test_app.sequencers.DutTesting.Result import Result
from abc import ABC, abstractmethod
import time
from enum import Enum


TIMEOUT = 100


class ExecutionType(Enum):
    SingleShot = 'singleShot'
    LoopCycle = 'loopCycle'

    def __call__(self):
        return self.value


def get_execution_policy(execution_type: ExecutionType):
    try:
        return {
            ExecutionType.SingleShot(): lambda: SingleShotExecutionPolicy(),
            ExecutionType.LoopCycle(): lambda: LoopCycleExecutionPolicy(),
        }[execution_type]()
    except Exception as e:
        raise Exception(f'exception occurred while instantiating execution policy: {e}')


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
                if sequencer_instance.test_sequence and (test_case.instance_name not in sequencer_instance.test_sequence):
                    continue

                if not sequencer_instance.tester_instance.do_request(int(sequencer_instance.site_id), TIMEOUT):
                    raise Exception('no response')

                sequencer_instance.tester_instance.test_in_progress(int(sequencer_instance.site_id))

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
