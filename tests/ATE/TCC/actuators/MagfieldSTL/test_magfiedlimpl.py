from ATE.TCC.Actuators.MagfieldSTL.magfieldimpl.magfieldimpl import MagFieldImpl
from ATE.TCC.Actuators.MagfieldSTL.driver.stldcs6k import DCS6K
from tests.ATE.TCC.actuators.MagfieldSTL.util import DummyCommChan


from pytest import fixture


@fixture
def magfield_impl():
    chan = DummyCommChan()
    dcs = DCS6K(chan)
    impl = MagFieldImpl(dcs)
    return (impl, dcs, chan)


def test_unknown_command_yields_bad_ioctl(magfield_impl):
    request = {"timeout": 5.0}
    result = magfield_impl[0].do_io_control("I am not a Ioctl!", request)
    assert (result["status"] == "bad_ioctl")


def test_missing_parameters_are_reported(magfield_impl):
    request = {"timeout": 5.0}
    result = magfield_impl[0].do_io_control("play_curve", request)
    assert (result["status"] == "missing_parameter")


def test_disable_sets_output_off(magfield_impl):
    request = {}
    magfield_impl[2].expect_send_with_reply("SetOutputState(off)", "SetOutputState 00000")
    result = magfield_impl[0].do_io_control("disable", request)
    assert(result["status"] == "ok")
    magfield_impl[2].check_send_expectations()


def test_bad_parameter_values_are_reported(magfield_impl):
    request = {"timeout": 5.0, "millitesla": 5000}
    result = magfield_impl[0].do_io_control("set_field", request)
    assert (result["status"] == "badparamvalue")
