from ATE.TCC.Actuators.MagfieldSTL.driver.stldcs6k import DCS6K
from tests.ATE.TCC.actuators.MagfieldSTL.util import DummyCommChan

from pytest import fixture


@fixture
def dcs6k():
    return DCS6K(DummyCommChan())


def expect_send_with_reply(dcs6k, data_to_send, reply):
    dcs6k.comm_chan.expect_send_with_reply(data_to_send, reply)


def check_send_expectations(dcs6k):
    fail = False
    for sends in dcs6k.comm_chan.sent_data:
        print(f"Expected send of \"{sends}\"")
        fail = True
    assert(not fail)


def test_query_id_reads_id(dcs6k):
    expect_send_with_reply(dcs6k, "*IDN?", "STL DCS-6K ABCD")
    id = dcs6k.query_id()
    assert (id == "ABCD")
    check_send_expectations(dcs6k)


def test_clear_sequence(dcs6k):
    expect_send_with_reply(dcs6k, "ClearSequences()", "ClearSequences 00000")
    dcs6k.clear_sequences()
    check_send_expectations(dcs6k)


def test_init_pid(dcs6k):
    expect_send_with_reply(dcs6k, "InitializePID()", "InitializePID 00000")
    dcs6k.initialize_pid()
    check_send_expectations(dcs6k)


def test_init_pid2(dcs6k):
    expect_send_with_reply(dcs6k, "InitializePID(all)", "InitializePID 00000")
    dcs6k.initialize_pid_2("all", False)
    check_send_expectations(dcs6k)


def test_init_pid2_bad_value_sends_nothing(dcs6k):
    dcs6k.initialize_pid_2("somepid", False)
    check_send_expectations(dcs6k)


def test_measure_impedance(dcs6k):
    expect_send_with_reply(dcs6k, "MeasureCurrentImpedance()", "MeasureCurrentImpedance 00000,123,456")
    result = dcs6k.measure_current_impedance()
    assert(result["value0"] == "123")
    assert(result["value1"] == "456")
    check_send_expectations(dcs6k)


def test_set_value(dcs6k):
    expect_send_with_reply(dcs6k, "SetValue(1000)", "SetValue 00000")
    dcs6k.set_value(1000, False)
    check_send_expectations(dcs6k)


def test_set_value_bad_param_does_not_call_to_device(dcs6k):
    dcs6k.set_value(5000, False)
    check_send_expectations(dcs6k)
