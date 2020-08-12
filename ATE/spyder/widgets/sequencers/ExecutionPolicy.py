from abc import ABC, abstractmethod
import time


class ExecutionPolicyABC(ABC):

    @abstractmethod
    def run(self, sequencer_instance):
        raise Exception("Cannot use base execution policy directly")


class LoopCycleExecutionPolicy(ExecutionPolicyABC):
    def __init__(self, num_cycles):
        self.num_cycles = num_cycles

    def run(self, sequencer_instance):
        for _ in range(self.num_cycles):
            test_index = 0
            start = time.time()
            sequencer_instance.pre_cycle_cb()
            for test_case in sequencer_instance.test_cases:
                result = test_case.run()

                # Push result back to sequencer, abort testing if sequencer
                # returns false
                if not sequencer_instance.after_test_cb(test_index, result):
                    end = time.time()
                    break

                test_index += 1

            end = time.time()
            execution_time = int(end - start)

            sequencer_instance.after_cycle_cb(execution_time, test_index)


class SingleShotExecutionPolicy(LoopCycleExecutionPolicy):
    def __init__(self):
        super().__init__(1)
