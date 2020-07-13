from abc import ABC, abstractmethod


class ExecutionPolicyABC(ABC):

    @abstractmethod
    def run(self, sequencer_instance):
        raise Exception("Cannot use base execution policy directly")


class LoopCylceExecutionPolicy(ExecutionPolicyABC):
    def __init__(self, num_cycles):
        self.num_cycles = num_cycles

    def run(self, sequencer_instance):
        for i in range(self.num_cycles):
            test_index = 0
            for test_case in sequencer_instance.test_cases:
                result = test_case.run()
                # Push result back to sequencer, abort testing if sequencer
                # returns false
                if sequencer_instance.after_test_cb(test_case, test_index, result) is False:
                    return
                test_index += 1
            sequencer_instance.after_cycle_cb(i)


class SingleShotExecutionPolicy(LoopCylceExecutionPolicy):
    def __init__(self):
        super().__init__(1)
