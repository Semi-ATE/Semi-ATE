from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.TestParameters import OutputParameter
from pytest import fixture
from ATE.spyder.widgets.actions_on.program.Parameters.TestProgram import TestParameters, TestProgram
from ATE.spyder.widgets.actions_on.program.Utils import Action, ParameterState
from numpy import inf, nan

TEST_NAME = 'Contact_1'
NEW_TEST_NAME = 'Contact_2'

SECOND_TEST_NAME = 'Contact_3'
TEST_BASE_NAME = 'Contact'

INPUT_PARAMETER = {'Temperature':
                   {'Shmoo': True, 'Min': -40.0, 'Default': 25.0, 'Max': 170.0, '10ᵡ': '', 'Unit': '°C', 'fmt': '.0f'},
                   'new_parameter2':
                   {'Shmoo': False, 'Min': -inf, 'Default': 0.0, 'Max': inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.3f'}}

CHANGED_INPUT_PARAMETER = {'Temperature':
                           {'Shmoo': True, 'Min': -40.0, 'Default': 25.0, 'Max': 170.0, '10ᵡ': '', 'Unit': '°C', 'fmt': '.0f'},
                           'new_parameter3':
                           {'Shmoo': False, 'Min': -inf, 'Default': 0.0, 'Max': inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.3f'}}

OUTPUT_PARAMETER = {'new_parameter1':
                    {'LSL': -inf, 'LTL': nan, 'Nom': 0.0, 'UTL': nan, 'USL': inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.3f'},
                    'new_parameter2':
                    {'LSL': -inf, 'LTL': nan, 'Nom': 0.0, 'UTL': nan, 'USL': inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.3f'}}

CHANGED_OUTPUT_PARAMETER = {'new_parameter3':
                            {'LSL': -inf, 'LTL': nan, 'Nom': 0.0, 'UTL': nan, 'USL': inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.3f'},
                            'new_parameter2':
                            {'LSL': -inf, 'LTL': nan, 'Nom': 0.0, 'UTL': nan, 'USL': inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.3f'}}

OUTPUT_PARAMETER1 = {'new_parameter1':
                     {'LSL': -inf, 'LTL': 1, 'Nom': 0.0, 'UTL': 2, 'USL': inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.3f'},
                     'new_parameter2':
                     {'LSL': -inf, 'LTL': 1, 'Nom': 0.0, 'UTL': 2, 'USL': inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.3f'}}


@fixture(scope='module')
def parameter_handler():
    return TestProgram()


def test_parameter_handler_correct_number_of_in_out_put_is_generated(parameter_handler):
    parameter_handler.add_test(TEST_NAME, TEST_BASE_NAME, INPUT_PARAMETER, OUTPUT_PARAMETER)
    assert parameter_handler.get_test_names() == [TEST_NAME]
    assert len(parameter_handler.get_test_inputs_parameters(TEST_NAME)) == len(INPUT_PARAMETER)
    assert len(parameter_handler.get_test_outputs_parameters(TEST_NAME)) == len(OUTPUT_PARAMETER)


def test_parameter_handler_update_test_name(parameter_handler):
    parameter_handler.update_test_name(TEST_NAME, NEW_TEST_NAME)
    assert parameter_handler.get_test_names() == [NEW_TEST_NAME]


def test_parameter_handler_reorder_tests(parameter_handler):
    parameter_handler.add_test(SECOND_TEST_NAME, TEST_BASE_NAME, INPUT_PARAMETER, OUTPUT_PARAMETER)
    assert parameter_handler.get_test_names()[0] == NEW_TEST_NAME
    assert parameter_handler.get_test_names()[1] == SECOND_TEST_NAME
    parameter_handler.reorder_test(SECOND_TEST_NAME, Action.Up())
    assert parameter_handler.get_test_names()[1] == NEW_TEST_NAME
    assert parameter_handler.get_test_names()[0] == SECOND_TEST_NAME


def test_parameter_handler_set_valid_temperature(parameter_handler):
    parameter_handler.set_temperature([40.0])
    assert parameter_handler.are_all_tests_valid()


def test_parameter_handler_set_invalid_temperature(parameter_handler):
    parameter_handler.set_temperature([400.0])
    assert not parameter_handler.are_all_tests_valid()


def test_parameter_handler_test_changed(parameter_handler: TestProgram):
    parameter_handler.add_test(NEW_TEST_NAME, TEST_BASE_NAME, CHANGED_INPUT_PARAMETER, OUTPUT_PARAMETER)

    standard_parameter = TestProgram()
    standard_parameter.add_test(TEST_BASE_NAME, TEST_BASE_NAME, CHANGED_INPUT_PARAMETER, CHANGED_OUTPUT_PARAMETER)
    parameter_handler.validate_test_parameters(NEW_TEST_NAME, standard_parameter)
    test, _ = parameter_handler.get_test(NEW_TEST_NAME)

    new_parameter_name = "new_parameter3"
    out_params: OutputParameter = test.get_output_parameter(new_parameter_name)

    assert out_params.get_test_number() == 103


def test_parameter_test_enumeration(parameter_handler: TestProgram):
    parameter_handler._tests.clear()
    parameter_handler.add_test(NEW_TEST_NAME, TEST_BASE_NAME, CHANGED_INPUT_PARAMETER, OUTPUT_PARAMETER)
    parameter_handler.add_test(SECOND_TEST_NAME, TEST_BASE_NAME, CHANGED_INPUT_PARAMETER, OUTPUT_PARAMETER1)
    test, _ = parameter_handler.get_test(NEW_TEST_NAME)
    assert set(test.get_tests_range()) == set([100])
    test, _ = parameter_handler.get_test(SECOND_TEST_NAME)
    assert set(test.get_tests_range()) == set([200])


def test_parameter_handler_validate_changed_tests(parameter_handler):
    changed_tests = [TEST_BASE_NAME]
    parameter_handler.validate_tests(changed_tests)
    test, _ = parameter_handler.get_test(NEW_TEST_NAME)
    assert test.get_validity() == ParameterState.Changed()


def test_parameter_handler_remove_test():
    parameter = TestProgram()
    parameter.add_test(TEST_NAME, TEST_BASE_NAME, INPUT_PARAMETER, OUTPUT_PARAMETER)
    parameter.remove_test(TEST_NAME)
    assert parameter.get_test_names() == []
