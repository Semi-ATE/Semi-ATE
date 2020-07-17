import pytest

from ATE.org.sequencers.TestParameters import InputParameter, OutputParameter


def test_can_create_input_parameter():
    ip = InputParameter("Test", False, 100.0)
    assert(ip is not None)


def test_getter_will_return_value():
    ip = InputParameter("Test", False, 117.0)
    assert(ip() == 117.0)


def test_can_create_output_parameter():
    op = OutputParameter("Op", 0, 10, 20, 30, 40)
    assert(op is not None)


def test_can_write_output_parameter():
    op = OutputParameter("Op", 0, 10, 20, 30, 40)
    op.write(25)
    assert(op._measurement == 25)


def test_output_parameter_is_pass_yields_false_if_out_of_spec():
    op = OutputParameter("Op", 0, 10, 20, 30, 40)
    op.write(-5)
    assert(op.is_pass() is False)
    op.write(45)
    assert(op.is_pass() is False)


def test_output_parameter_is_pass_yields_false_if_out_of_testlimit():
    op = OutputParameter("Op", 0, 10, 20, 30, 40)
    op.write(9)
    assert(op.is_pass() is False)
    op.write(31)
    assert(op.is_pass() is False)


def test_output_parameter_is_pass_yields_true_if_within_testlimit():
    op = OutputParameter("Op", 0, 10, 20, 30, 40)
    op.write(25)
    assert(op.is_pass() is True)


def test_set_parameters_throws_exception_if_ltl_larger_than_utl():
    with pytest.raises(ValueError):
        op = OutputParameter("Op", 0, 10, 20, 30, 40)
        op.set_limits(30, 20)


def test_set_parameters_throws_exception_if_lowerlimit_violates_specs():
    with pytest.raises(ValueError):
        op = OutputParameter("Op", 0, 10, 20, 30, 40)
        op.set_limits(-10, 20)


def test_set_parameters_throws_exception_if_upperlimit_violates_specs():
    with pytest.raises(ValueError):
        op = OutputParameter("Op", 0, 10, 20, 30, 40)
        op.set_limits(10, 110)
