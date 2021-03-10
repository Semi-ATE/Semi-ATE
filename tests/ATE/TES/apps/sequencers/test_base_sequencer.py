import pytest

from ATE.Tester.TES.apps.testApp.sequencers.SequencerBase import SequencerBase
from ATE.Tester.TES.apps.testApp.sequencers.ExecutionPolicy import SingleShotExecutionPolicy, ExecutionPolicyABC
from ATE.Tester.TES.apps.testApp.sequencers.Harness import Harness
from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.DutTestCaseABC import DutTestCaseABC, DutTestCaseBase
from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.Result import Result
from ATE.Tester.TES.apps.testApp.sequencers.binning.BinStrategy import BinStrategy
from tests.ATE.TES.apps.sequencers.Loggerstub import LoggerStub


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
        self.instance_name = ""

    def run(self, site_num):
        self.has_run = True
        return (self.result, 0, []), False

    def get_test_num(self):
        return 911

    def get_test_nums(self) -> int:
        return 2

    def aggregate_test_result(self, site_num):
        pass

    def do(self):
        pass


class dummy_cache():
    def __init__(self):
        self.publish_called = False
        self.drop_called = False
        self.read_called = False

    def publish(self, program_name, part_id, data):
        self.publish_called = True

    def drop_part(self, part_id):
        self.drop_called = True

    def get_value(self, part_id, value_name):
        pass

    def do_fetch(self, part_id):
        self.read_called = True


@pytest.fixture
def sequencer():
    bin_strategy = BinStrategy(CONFIG_FILE)
    ret_val = SequencerBase("Testprog", bin_strategy)
    ret_val.set_logger(LoggerStub())
    ret_val.set_auto_script(AutoScript())
    return ret_val


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


class Logger:
    @staticmethod
    def log_message(loglevel, msg):
        print(f'{loglevel}|{msg}')


class Context:
    def __init__(self):
        self.logger: Logger = Logger()


class AutoScript:
    def after_cycle_teardown(self):
        pass


class testTypeA(DutTestCaseABC):
    def __init__(self):
        super().__init__(Context())

    def run(self, site_num):
        return (True, 0, [])

    def aggregate_test_result(self, site_num):
        pass

    def do(self):
        pass


class testTypeB(DutTestCaseABC):
    def __init__(self):
        super().__init__(Context())

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
    test_settings = {"trigger_on_test": {'active': True, 'value': 1}}
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


def test_sequencer_will_publish_to_cache(sequencer):
    t2 = dummy_test_case()
    cache = dummy_cache()
    sequencer.register_test(t2)
    sequencer.set_caching_policy("store")
    sequencer.set_cache_instance(cache)
    assert(cache.publish_called is False)
    sequencer.run(SingleShotExecutionPolicy(), SITE_INFO)
    assert(cache.publish_called is True)


def test_sequencer_will_read_from_cache_if_caching_is_active(sequencer):
    t2 = dummy_test_case()
    cache = dummy_cache()
    sequencer.register_test(t2)
    sequencer.set_caching_policy("store")
    sequencer.set_cache_instance(cache)
    assert(cache.read_called is False)
    sequencer.run(SingleShotExecutionPolicy(), SITE_INFO)
    assert(cache.read_called is True)


def test_sequencer_will_not_read_from_cache_if_caching_is_disabled(sequencer):
    t2 = dummy_test_case()
    cache = dummy_cache()
    sequencer.register_test(t2)
    sequencer.set_caching_policy("disable")
    sequencer.set_cache_instance(cache)
    assert(cache.read_called is False)
    sequencer.run(SingleShotExecutionPolicy(), SITE_INFO)
    assert(cache.read_called is False)


def test_sequencer_will_delete_from_cache(sequencer):
    t2 = dummy_test_case()
    cache = dummy_cache()
    sequencer.register_test(t2)
    sequencer.set_caching_policy("drop")
    sequencer.set_cache_instance(cache)
    assert(cache.drop_called is False)
    sequencer.run(SingleShotExecutionPolicy(), SITE_INFO)
    assert(cache.drop_called is True)


def test_sequencer_will_ignore_cache(sequencer):
    t2 = dummy_test_case()
    cache = dummy_cache()
    sequencer.register_test(t2)
    sequencer.set_caching_policy("disable")
    sequencer.set_cache_instance(cache)
    assert(cache.drop_called is False)
    assert(cache.publish_called is False)
    sequencer.run(SingleShotExecutionPolicy(), SITE_INFO)
    assert(cache.drop_called is False)
    assert(cache.publish_called is False)


def test_sequencer_will_throw_if_invalid_caching_policy_was_set(sequencer):
    t2 = dummy_test_case()
    sequencer.register_test(t2)
    with pytest.raises(ValueError):
        sequencer.set_caching_policy("Foobar")


def test_sequencer_will_throw_if_caching_was_enabled_and_no_cache_instance_was_set(sequencer):
    t2 = dummy_test_case()
    sequencer.register_test(t2)
    sequencer.set_caching_policy("store")
    with pytest.raises(ValueError):
        sequencer.run(SingleShotExecutionPolicy(), SITE_INFO)
