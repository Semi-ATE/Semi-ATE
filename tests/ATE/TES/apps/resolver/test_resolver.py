import pytest
from pytest import fixture
from ATE.Tester.TES.apps.testApp.parameters.LocalResolver import LocalResolver
from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.TestParameters import OutputParameter


NAME = 'i_input_1'
SHMOO = False
OP = OutputParameter('o_output', -10, -3, 1, 3, 10, 2)

MAX_VALUE = 10
MIN_VALUE = 0
EXPONENT = 3


@fixture
def local_resolver():
    return LocalResolver(NAME, SHMOO, OP, MIN_VALUE, MAX_VALUE, EXPONENT)


def test_local_resolver_get_valid_value(local_resolver):
    OP.write(10)

    input_value = local_resolver.get_input_value()
    assert input_value == 10


def test_local_resolver_get_invalid_value(local_resolver):
    OP.write(150)

    with pytest.raises(Exception):
        # value is out of range
        _ = local_resolver.get_input_value()
