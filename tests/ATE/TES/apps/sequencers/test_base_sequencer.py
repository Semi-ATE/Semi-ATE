import pytest

from ATE.Tester.TES.apps.testApp.sequencers.SequencerBase import SequencerBase
from ATE.Tester.TES.apps.testApp.sequencers.ExecutionPolicy import SingleShotExecutionPolicy, ExecutionPolicyABC
from ATE.Tester.TES.apps.testApp.sequencers.Harness import Harness
from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.DutTestCaseABC import DutTestCaseABC, DutTestCaseBase
from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.Result import Result
from ATE.Tester.TES.apps.testApp.sequencers.binning.BinStrategy import BinStrategy


import os
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'binmapping.json')
BIN_SETTINGS = [{'Bin-Name': 'F_DAW', 'Typ': 'Fail Electric', 'SBin': 3},
                {'Bin-Name': 'Good1', 'Typ': 'Type1', 'SBin': 2}]
SITE_INFO = {'sites_info': [{'siteid': '0', 'partid': '1', 'binning': '-1'}]}


class dummy_execution_policy(ExecutionPolicyABC):
    def run(self, sequencer_instance):
        self.run_called = True


class dummy_harness(Harness):
    def __init__(self):
        self.status_sequence = []

    def send_status(self, status):
        self.status_sequence.append(status)

    def send_testresult(self, stdfdata):
        pass


class dummy_test_case(DutTestCaseBase):
    def __init__(self, result=Result.Pass()):
        self.result = result
        self.has_run = False

    def run(self, site_num):
        self.has_run = True
        return (self.result, 0, [])

    def aggregate_test_result(self, site_num):
        pass

    def do(self):
        pass


@pytest.fixture
def sequencer():
    bin_strategy = BinStrategy(BIN_SETTINGS, CONFIG_FILE)
    return SequencerBase(bin_strategy)


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


class testTypeA(DutTestCaseABC):
    def run(self, site_num):
        return (True, 0, [])

    def aggregate_test_result(self, site_num):
        pass

    def do(self):
        pass


class testTypeB(DutTestCaseABC):
    def run(self, site_num):
        return (True, 0, [])

    def aggregate_test_result(self, site_num):
        pass

    def do(self):
        pass


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


class TriggerOut:
    def __init__(self):
        self.was_triggered = False
        self.pulse_width = 0
        self.num_pulses = 0

    def pulse_trigger_out(self, pulse_width_ms):
        self.was_triggered = True
        self.pulse_width = pulse_width_ms
        self.num_pulses = self.num_pulses + 1


def test_trigger_on_test_will_pulse_triggerout(sequencer):
    trigger = TriggerOut()
    sequencer.set_tester_instance(trigger)
    sequencer.register_test(dummy_test_case())
    sequencer.register_test(dummy_test_case())
    sequencer.register_test(dummy_test_case())
    test_settings = {"trigger_on_test": {'active': True, 'value': 2}}
    test_settings.update(SITE_INFO)
    sequencer.run(SingleShotExecutionPolicy(), test_settings)
    assert(trigger.was_triggered)
    assert(trigger.num_pulses == 1)
    assert(trigger.pulse_width == 250)


def test_trigger_on_test_will_not_pulse_triggerout_if_testindex_is_not_available(sequencer):
    trigger = TriggerOut()
    sequencer.set_tester_instance(trigger)
    sequencer.register_test(dummy_test_case())
    sequencer.register_test(dummy_test_case())
    sequencer.register_test(dummy_test_case())
    test_settings = {"trigger_on_test": {'active': True, 'value': 7}}
    test_settings.update(SITE_INFO)
    sequencer.run(SingleShotExecutionPolicy(), test_settings)
    assert(trigger.was_triggered is False)
    assert(trigger.num_pulses == 0)
    assert(trigger.pulse_width == 0)


def test_trigger_on_test_will_not_crash_if_trigger_on_test_is_set_but_no_triggerout(sequencer):
    sequencer.register_test(dummy_test_case())
    sequencer.register_test(dummy_test_case())
    sequencer.register_test(dummy_test_case())
    test_settings = {"trigger_on_test": {'active': True, 'value': 1}}
    test_settings.update(SITE_INFO)
    sequencer.run(SingleShotExecutionPolicy(), test_settings)


def test_trigger_on_fail_will_pulse_trigger_out_on_testfail(sequencer):
    trigger = TriggerOut()
    sequencer.set_tester_instance(trigger)
    sequencer.register_test(dummy_test_case(Result.Fail()))
    sequencer.register_test(dummy_test_case())
    sequencer.register_test(dummy_test_case())
    test_settings = {"trigger_on_fail": {'active': True, 'value': -1}}
    test_settings.update(SITE_INFO)
    sequencer.run(SingleShotExecutionPolicy(), test_settings)
    assert(trigger.was_triggered is True)
    assert(trigger.num_pulses == 1)
    assert(trigger.pulse_width == 250)


def test_trigger_on_fail_will_pulse_trigger_out_multiple_times(sequencer):
    trigger = TriggerOut()
    sequencer.set_tester_instance(trigger)
    sequencer.register_test(dummy_test_case(Result.Fail()))
    sequencer.register_test(dummy_test_case())
    sequencer.register_test(dummy_test_case(Result.Fail()))
    test_settings = {"trigger_on_fail": {'active': True, 'value': -1}, "stop_on_fail": {'active': False, 'value': -1}}
    test_settings.update(SITE_INFO)
    sequencer.run(SingleShotExecutionPolicy(), test_settings)
    assert(trigger.was_triggered is True)
    assert(trigger.num_pulses == 2)
    assert(trigger.pulse_width == 250)


def test_stop_on_fail_stop_on_failure(sequencer):
    t1 = dummy_test_case(Result.Fail())
    t2 = dummy_test_case()
    sequencer.register_test(t1)
    sequencer.register_test(t2)

    test_settings = {"stop_on_fail": {'active': True, 'value': -1}}
    test_settings.update(SITE_INFO)
    sequencer.run(SingleShotExecutionPolicy(), test_settings)
    assert(t1.has_run is True)
    assert(t2.has_run is False)
