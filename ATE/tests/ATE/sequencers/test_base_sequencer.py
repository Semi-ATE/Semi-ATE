import pytest

from ATE.org.sequencers import SequencerBase
from ATE.org.sequencers.ExecutionPolicy import SingleShotExecutionPolicy, ExecutionPolicyABC
from ATE.org.sequencers.Harness import Harness
from ATE.org.sequencers.TestCase import TestCaseABC


class dummy_execution_policy(ExecutionPolicyABC):
    def run(self, sequencer_instance):
        self.run_called = True


class dummy_harness(Harness):
    def __init__(self):
        self.status_sequence = []

    def send_status(self, status):
        self.status_sequence.append(status)

    def send_testresult(self, passfail, sbin, stdfdata):
        pass


class dummy_test_case(TestCaseABC):
    def run(self):
        return (True, 0, [])


@pytest.fixture
def sequencer():
    return SequencerBase(None)


def test_can_create_sequener(sequencer):
    assert(sequencer is not None)


def test_can_call_run(sequencer):
    policy = dummy_execution_policy()
    sequencer.run(policy)
    assert(policy.run_called)


# not happy path
def test_run_throws_if_called_with_none(sequencer):
    pass


# not happy path
def test_run_throws_if_called_with_bad_policy(sequencer):
    pass


def test_can_register_test(sequencer):
    sequencer.register_test(dummy_test_case())


class testTypeA(TestCaseABC):
    def run(self):
        return (True, 0, [])


class testTypeB(TestCaseABC):
    def run(self):
        return (True, 0, [])


def test_sets_instance_number_for_each_type(sequencer):
    testA1 = testTypeA()
    testA2 = testTypeA()
    testB1 = testTypeB()
    testB2 = testTypeB()
    sequencer.register_test(testA1)
    sequencer.register_test(testA2)
    sequencer.register_test(testB1)
    sequencer.register_test(testB2)
    assert(testA1.instance_number == 0)
    assert(testA2.instance_number == 1)
    assert(testB2.instance_number == 1)


# not happy path
def test_cannot_register_None_test(sequencer):
    pass


def test_sends_idle_on_set_testharness(sequencer):
    h = dummy_harness()
    sequencer.set_harness(h)
    assert(h.status_sequence[0] == "IDLE")


def test_sends_testing_and_idle_when_testing(sequencer):
    h = dummy_harness()
    sequencer.set_harness(h)
    assert(h.status_sequence[0] == "IDLE")
    sequencer.run(SingleShotExecutionPolicy())
    assert(h.status_sequence[1] == "TESTING")
    assert(h.status_sequence[2] == "IDLE")
