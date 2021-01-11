import numpy as np
import copy
from ATE.spyder.widgets.actions_on.program.Utils import Action, ParameterState, ResolverTypes
from ATE.spyder.widgets.actions_on.program.Parameters.InputParameter import InputParameter
from ATE.spyder.widgets.actions_on.program.Parameters.OutputParameter import OutputParameter


PARAM_PREFIX = '_ate_var_'


class TestParameters:
    def __init__(self, name, test_base, input_parameters, output_parameters):
        self._test_name = name
        self._test_base = test_base
        self._input_parameters = {}
        self._output_parameters = {}
        self._valid = ParameterState.Valid()
        self._sbin = None

        self._add_input_parameter(input_parameters)
        self._add_output_parameter(output_parameters)

    def _add_input_parameter(self, input_parameters):
        for name in input_parameters.keys():
            self._input_parameters[name] = InputParameter(name, input_parameters[name])

    def _add_output_parameter(self, output_parameters):
        for name in output_parameters.keys():
            self._output_parameters[name] = OutputParameter(name, output_parameters[name])

    def update_test_name(self, name):
        self._test_name = name

    def get_input_parameter(self, input_name):
        return self._input_parameters[input_name]

    def get_output_parameter(self, output_name):
        return self._output_parameters[output_name]

    def get_input_parameters(self):
        return self._input_parameters

    def get_output_parameters(self):
        return self._output_parameters

    def get_test_base(self):
        return self._test_base

    def get_test_name(self):
        return self._test_name

    def set_valid_flag(self, valid):
        if self._valid == ParameterState.Changed():
            return

        self._valid = valid

    def get_valid_flag(self):
        for _, input in self.get_input_parameters().items():
            if not input.is_valid_value():
                return False

        for _, output in self.get_output_parameters().items():
            if not output.is_valid_value():
                return False

        return self.get_validity()

    def get_validity(self):
        return self._valid

    def append_new_input_parameter(self, name, input_parameter):
        self._input_parameters[name] = input_parameter
        self._input_parameters[name].set_validity(ParameterState.New())

    def append_new_output_parameter(self, name, output_parameter):
        self._output_parameters[name] = output_parameter
        self._output_parameters[name].set_validity(ParameterState.New())

    def set_temperature(self, temp):
        validity = ParameterState.Valid()
        for _, input in self.get_input_parameters().items():
            validity = input.set_temperature(temp)
            if validity is not None:
                break

        self.set_valid_flag(validity)

    def is_valid_range(self, input_parameter, output_name):
        output_parameter = self.get_output_parameter(output_name)
        out_l_limit, out_u_limit, out_exponent = output_parameter.get_range_infos()

        in_l_limit, in_u_limit, in_exponent = input_parameter.get_range_infos()
        if (in_l_limit, in_u_limit) == (-np.infty, np.infty):
            return True

        power = self._get_power(in_exponent, out_exponent)

        if (in_l_limit * power) <= out_l_limit and (in_u_limit * power) >= out_u_limit:
            return True

        return False

    @staticmethod
    def _get_power(exponent_input, exponent_output):
        exponent = None
        if exponent_input > exponent_output:
            exponent = exponent_input - exponent_output
        else:
            exponent = exponent_output - exponent_input

        return pow(10, exponent)

    def set_sbin(self, sbin):
        self._sbin = sbin

    def get_sbin(self):
        return self._sbin


class TestProgram:
    def __init__(self):
        self._tests = []

    def add_test(self, name, test_base, input_parameters, output_parameters):
        self._tests.append(TestParameters(name, test_base, input_parameters, output_parameters))

    def get_test(self, test_name):
        for index, test in enumerate(self._tests):
            if test.get_test_name() != test_name:
                continue

            return test, index

        return None, None

    def update_test_name(self, test_name, new_name):
        _, index = self.get_test(test_name)
        test = self._tests.pop(index)
        test.update_test_name(new_name)
        self._tests.append(test)

    def remove_test(self, test_name):
        _, index = self.get_test(test_name)
        self._tests.pop(index)

    def reorder_test(self, test_name, action):
        reorder_index = 0
        if action == Action.Up():
            reorder_index -= 1
        elif action == Action.Down():
            reorder_index += 1
        else:
            return

        _, index = self.get_test(test_name)
        test = self._tests[index]
        self._tests.remove(test)
        self._tests.insert(index + reorder_index, test)

    def get_input_parameter(self, test_name, input_name):
        test, _ = self.get_test(test_name)
        return test.get_input_parameter(input_name)

    def get_output_parameter(self, test_name, output_name):
        test, _ = self.get_test(test_name)
        return test.get_output_parameter(output_name)

    def get_test_inputs_parameters(self, test_name):
        test, _ = self.get_test(test_name)
        return test.get_input_parameters()

    def get_test_outputs_parameters(self, test_name):
        test, _ = self.get_test(test_name)
        return test.get_output_parameters()

    def get_tests_outputs_parameters(self):
        output_params = []
        for test in self._tests:
            test_out_param = {}
            for k, _ in test.get_output_parameters().items():
                test_out_param.setdefault(test.get_test_name(), []).append(k)

            output_params.append(test_out_param)

        return output_params

    def get_tests(self):
        return self._tests

    def get_test_names(self):
        return [test.get_test_name() for test in self._tests]

    def set_temperature(self, temp):
        for test in self._tests:
            test.set_temperature(temp)

    def build_defintion(self):
        definition = []
        for test in self._tests:
            struct = {}
            struct['input_parameters'] = {}
            struct['output_parameters'] = {}
            struct['description'] = test.get_test_name()
            struct['name'] = test.get_test_base()
            struct['sbin'] = test.get_sbin()
            for input, value in test.get_input_parameters().items():
                if not value.is_valid():
                    continue
                parameter_content = value.get_parameters_content()
                struct['input_parameters'][input] = {'value': self._prepare_input_parameter(parameter_content['value'], parameter_content['type']),
                                                     'type': parameter_content['type'], 'Min': parameter_content['min'], 'Max': parameter_content['max'],
                                                     'fmt': parameter_content['format'], 'Unit': parameter_content['unit'], '10ᵡ': parameter_content['exponent'],
                                                     'Default': parameter_content['default'], 'content': parameter_content['value']}

            for output, value in test.get_output_parameters().items():
                if not value.is_valid():
                    continue
                parameter_content = value.get_parameters_content()
                struct['output_parameters'][output] = {'UTL': parameter_content['utl'], 'LTL': parameter_content['ltl'],
                                                       'LSL': parameter_content['lsl'], 'USL': parameter_content['usl'],
                                                       'Binning': {'bin': parameter_content['bin'], 'result': parameter_content['bin_result']},
                                                       'fmt': parameter_content['format'], 'Unit': parameter_content['unit'], '10ᵡ': parameter_content['exponent']}

            definition.append(struct)

        return definition

    @staticmethod
    def _prepare_input_parameter(value, type):
        if type == ResolverTypes.Static():
            return value
        else:
            if PARAM_PREFIX in value:
                return value

            value_parts = value.split('.')
            return f'{PARAM_PREFIX}{value_parts[0]}.op.o_{value_parts[1]}'

    def binning_information(self):
        binning_info = []
        for test in self._tests:
            struct = self._get_binning_structure(test)
            binning_info.append(struct)

        return binning_info

    def get_binning_info_for_test(self, test_name):
        test, _ = self.get_test(test_name)
        return self._get_binning_structure(test)

    @staticmethod
    def _get_binning_structure(test):
        return {'name': test.get_test_base(), 'description': test.get_test_name(), 'output_parameters': test.get_output_parameters()}

    def import_tests_parameters(self, sequence_information):
        for test_info in sequence_information:
            test_parameter = TestParameters(test_info['description'], test_info['name'], test_info['input_parameters'], test_info['output_parameters'])
            self._tests.append(test_parameter)

    def validate_test_parameters(self, test_name, available_tests_handler):
        for test in self._tests:
            if test.get_test_name() != test_name:
                continue

            input_parameters = available_tests_handler.get_test_inputs_parameters(test.get_test_base())
            custom_input_parameters = test.get_input_parameters()

            removed_parameters = set(custom_input_parameters.keys()) - set(input_parameters.keys())
            for removed_parameter in removed_parameters:
                custom_input_parameters[removed_parameter].set_validity(ParameterState.Removed())

            missing_parameters = set(input_parameters.keys()) - set(custom_input_parameters.keys())
            for missing_parameter in missing_parameters:
                test.append_new_input_parameter(missing_parameter, copy.deepcopy(input_parameters[missing_parameter]))

            output_parameters = available_tests_handler.get_test_outputs_parameters(test.get_test_base())
            custom_output_parameters = test.get_output_parameters()

            removed_parameters = set(custom_output_parameters.keys()) - set(output_parameters.keys())
            for removed_parameter in removed_parameters:
                custom_output_parameters[removed_parameter].set_validity(ParameterState.Removed())

            missing_parameters = set(output_parameters.keys()) - set(custom_output_parameters.keys())
            for missing_parameter in missing_parameters:
                test.append_new_output_parameter(missing_parameter, copy.deepcopy(output_parameters[missing_parameter]))

    def are_all_tests_valid(self):
        for test in self._tests:
            if test.get_valid_flag() == ParameterState.Invalid():
                return False

        return True

    def validate_tests(self, test_names):
        for test in self._tests:
            if test.get_test_base() not in (test_names):
                continue

            test.set_valid_flag(ParameterState.Changed())

    def is_valid_range(self, test, input_param, output_name):
        test, _ = self.get_test(test)
        return test.is_valid_range(input_param, output_name)
