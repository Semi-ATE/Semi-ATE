from ATE.TCC.Actuators.MagfieldSTL.magfieldimpl.magfieldimpl import MagFieldImpl, CURVE_ITEM_SIZE, MAX_CURVE_SIZE, MIN_TIMEOUT
from ATE.TCC.Actuators.MagfieldSTL.driver.stldcs6k import DCS6K
from tests.ATE.TCC.actuators.MagfieldSTL.util import DummyCommChan


from pytest import fixture


class MagfieldContainer:
    
    def __init__(self, impl, dcs, comm):
        self.comm_chan = comm
        self.dcs6k = dcs
        self.impl = impl

@fixture
def magfield_impl():
    chan = DummyCommChan()
    dcs = DCS6K(chan)
    impl = MagFieldImpl(dcs)
    return MagfieldContainer(impl, dcs, chan)


def test_unknown_command_yields_bad_ioctl(magfield_impl):
    request = {"timeout": 5.0}
    result = magfield_impl.impl.do_io_control("I am not a Ioctl!", request)
    assert (result["status"] == "bad_ioctl")


def test_missing_parameters_are_reported(magfield_impl):
    request = {"timeout": 5.0}
    result = magfield_impl.impl.do_io_control("play_curve", request)
    assert (result["status"] == "missing_parameter")


def test_disable_sets_output_off(magfield_impl):
    request = {}
    magfield_impl.comm_chan.expect_send_with_reply("SetOutputState(off)", "SetOutputState 00000")
    result = magfield_impl.impl.do_io_control("disable", request)
    assert(result["status"] == "ok")
    magfield_impl.comm_chan.check_send_expectations()


def test_bad_parameter_values_are_reported(magfield_impl):
    request = {"timeout": 5.0, "millitesla": 5000}
    result = magfield_impl.impl.do_io_control("set_field", request)
    assert (result["status"] == "badparamvalue")


def test_program_curve_yields_ok_with_good_params(magfield_impl):
    request = {"id": 10,
               "hull": [[1.25, 0.5], [2.5, 3]],
               "timeout": 5.0}
    offset_p1 = 10 * MAX_CURVE_SIZE * CURVE_ITEM_SIZE
    magfield_impl.comm_chan.expect_send_with_reply(f"SetSequenceLine({offset_p1 + 0},1.25,0,0,standard,0)", "SetSequenceLine 00000")
    magfield_impl.comm_chan.expect_send_with_reply(f"SetSequenceLine({offset_p1 + 1},2.5,0,0,standard,0)", "SetSequenceLine 00000")

    result = magfield_impl.impl.do_io_control("program_curve", request)
    assert (result["status"] == "ok")


def test_program_curve_yields_error_with_non_numeric_curve_id(magfield_impl):
    request = {"id": "i am not a number",
               "hull": [[1.25, 0.5], [2.5, 3]],
               "timeout": 5.0}
    result = magfield_impl.impl.do_io_control("program_curve", request)
    assert (result["status"] == "invalidid")


def test_program_curve_yields_error_with_negative_curve_id(magfield_impl):
    request = {"id": -10,
               "hull": [[1.25, 0.5], [2.5, 3]],
               "timeout": 5.0}
    result = magfield_impl.impl.do_io_control("program_curve", request)
    assert (result["status"] == "invalidid")


def program_curve(magfield_impl):
    request = {"id": 5,
               "hull": [[1.25, 0.5], [2.5, 3], [9.55, 1]],
               "timeout": 5.0}
    point_offset = 5 * MAX_CURVE_SIZE
    magfield_impl.comm_chan.expect_send_with_reply(f"SetSequenceLine({point_offset  + 0},1.25,0,0,standard,0)", "SetSequenceLine 00000")
    magfield_impl.comm_chan.expect_send_with_reply(f"SetSequenceLine({point_offset  + 1},2.5,0,0,standard,0)", "SetSequenceLine 00000")
    magfield_impl.comm_chan.expect_send_with_reply(f"SetSequenceLine({point_offset  + 2},9.55,0,0,standard,0)", "SetSequenceLine 00000")
    result = magfield_impl.impl.do_io_control("program_curve", request)
    assert (result["status"] == "ok")


def test_play_curve_stepwise_yields_ok_for_known_curve_and_outputs_first_value(magfield_impl):
    program_curve(magfield_impl)
    magfield_impl.comm_chan.expect_send_with_reply("SetValue(1.25)", "SetValue 00000")
    result = magfield_impl.impl.do_io_control("play_curve_stepwise", {"id": 5})
    assert (result["status"] == "ok")
    magfield_impl.comm_chan.check_send_expectations()


def test_play_curve_stepwise_yields_unknown_if_curve_was_not_programmed_before(magfield_impl):
    result = magfield_impl.impl.do_io_control("play_curve_stepwise", {"id": 5})
    assert (result["status"] == "unknown")


def test_curve_step_yields_ok_after_curve_was_started(magfield_impl):
    program_curve(magfield_impl)
    magfield_impl.comm_chan.expect_send_with_reply("SetValue(1.25)", "SetValue 00000")
    magfield_impl.comm_chan.expect_send_with_reply("SetValue(2.5)", "SetValue 00000")
    magfield_impl.impl.do_io_control("play_curve_stepwise", {"id": 5})
    result = magfield_impl.impl.do_io_control("curve_step", {"id": 5})
    assert (result["status"] == "ok")


def test_curve_step_outputs_values(magfield_impl):
    program_curve(magfield_impl)
    magfield_impl.comm_chan.expect_send_with_reply("SetValue(1.25)", "SetValue 00000")
    magfield_impl.comm_chan.expect_send_with_reply("SetValue(2.5)", "SetValue 00000")
    magfield_impl.comm_chan.expect_send_with_reply("SetValue(9.55)", "SetValue 00000")
    magfield_impl.impl.do_io_control("play_curve_stepwise", {"id": 5})
    magfield_impl.impl.do_io_control("curve_step", {"id": 5})
    result = magfield_impl.impl.do_io_control("curve_step", {"id": 5})
    assert (result["status"] == "done")


def test_play_curve_yields_ok_if_curve_is_known(magfield_impl):
    program_curve(magfield_impl)
    magfield_impl.comm_chan.expect_send_with_reply("StartSequence(5120,5123,1,time,1.5,intern,3.0)", "StartSequence 00000")
    result = magfield_impl.impl.do_io_control("play_curve", {"id": 5})
    assert (result["status"] == "ok")


def test_play_curve_yields_unknown_if_curve_is_unknwon(magfield_impl):
    result = magfield_impl.impl.do_io_control("play_curve", {"id": 47})
    assert (result["status"] == "unknown")


def test_play_curve_yields_invalidid_if_curveid_has_bad_type(magfield_impl):
    result = magfield_impl.impl.do_io_control("play_curve", {"id": "not a curve man."})
    assert (result["status"] == "invalidid")
