from ATE.spyder.widgets.actions_on.program.Parameters.OutputValidator import OutputValidator
from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.Result import Result
from ATE.spyder.widgets.actions_on.program.Utils import Action, ParameterState, ResolverTypes
from ATE.spyder.widgets.actions_on.program.Parameters.InputParameter import InputParameter
from ATE.spyder.widgets.actions_on.program.Parameters.OutputParameter import Bininfo, OutputParameter
from PyQt5.QtWidgets import QTableWidget
from typing import Callable, List, Optional, Tuple
import copy


PARAM_PREFIX = '_ate_var_'
MAX_TEST_RANGE = 100


class TestParameters:
    def __init__(self, name: str, test_base: str, input_parameters: dict, output_parameters: dict, output_validator: OutputValidator, test_num: int, is_selected: bool = True):
        self._test_name = name
        self._test_base = test_base
        self._input_parameters = {}
        self._output_parameters = {}
        self._valid = ParameterState.Valid()
        self._sbin = None
        self._is_selected = is_selected
        self._output_validator = output_validator
        self.test_num = test_num

        self._add_input_parameter(input_parameters)
        self._add_output_parameter(output_parameters)

    def _add_input_parameter(self, input_parameters):
        for name in input_parameters.keys():
            self._input_parameters[name] = InputParameter(name, input_parameters[name])

    def _add_output_parameter(self, output_parameters):
        for name in output_parameters.keys():
            self._output_parameters[name] = OutputParameter(name, output_parameters[name], self._output_validator)

    def update_test_name(self, name):
        self._test_name = name

    def get_input_parameter(self, input_name):
        return self._input_parameters[input_name]

    def get_output_parameter(self, output_name):
        return self._output_parameters[output_name]

    def get_input_parameters(self) -> dict:
        return self._input_parameters

    def get_output_parameters(self) -> dict:
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

    def append_new_output_parameter(self, name: str, output_parameter: OutputParameter):
        output_parameter.set_test_number(self._get_test_num_for_output())
        self._output_parameters[name] = output_parameter
        self._output_parameters[name].set_validity(ParameterState.New())

    def _get_test_num_for_output(self):
        test_nums = []
        for index, (_, output) in enumerate(self._output_parameters.items()):
            if output.get_test_number() in test_nums:
                continue

            test_nums.append(output.get_test_number())

        multiplier = int(test_nums[0] / MAX_TEST_RANGE)
        for index, test_num in enumerate(test_nums):
            # index 0 is reserved for test instance number
            if index == 0:
                continue
            if (test_num % MAX_TEST_RANGE) != index:
                value = (MAX_TEST_RANGE * multiplier) + index
                if value in test_nums:
                    continue

                return value

        return max(test_nums) + 1

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

        import math
        if (in_l_limit, in_u_limit) == (-math.inf, math.inf):
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

    def display(self, ip_box, op_box):
        ip_box.setRowCount(0)
        op_box.setRowCount(0)

        for _, ip in self._input_parameters.items():
            ip.display(ip_box)

        for _, op in self._output_parameters.items():
            op.display(op_box)

    def edit_ip(self, ip_name: str, value_index: int, complete_cb):
        self._input_parameters[ip_name].edit(value_index, complete_cb)
        return self._input_parameters[ip_name]

    def edit_op(self, op_name: str, value_index: int, complete_cb):
        self._output_parameters[op_name].edit(value_index, complete_cb)
        return self._output_parameters[op_name]

    def set_selectability(self, selectable: bool):
        self._is_selected = selectable

    def get_selectability(self):
        return self._is_selected

    def get_tests_range(self):
        ranges = []
        for _, output in self._output_parameters.items():
            range = int(output.get_test_number() / MAX_TEST_RANGE) * MAX_TEST_RANGE

            if range in ranges:
                continue

            ranges.append(range)

        return ranges

    def get_available_test_nums(self):
        ranges = []
        for _, output in self._output_parameters.items():
            ranges.append(output.get_test_number())

        ranges.append(self.get_test_number())

        return ranges

    def get_test_number(self) -> int:
        return self.test_num

    def set_test_number(self, test_num: int):
        self.test_num = test_num


class TestProgram:
    def __init__(self):
        self._tests = []
        self.output_validator = OutputValidator(self)
        self._test_ranges = []

    def display_test(self, test_name: str, ip_box: QTableWidget, op_box: QTableWidget):
        test, _ = self.get_test(test_name)
        test.display(ip_box, op_box)

    def edit_input_parameter(self, test_name: str, ip_name: str, value_index: int, complete_cb: Callable):
        test, _ = self.get_test(test_name)
        return test.edit_ip(ip_name, value_index, complete_cb)

    def edit_output_parameter(self, test_name: str, op_name: str, value_index: int, complete_cb: Callable):
        test, _index = self.get_test(test_name)
        return test.edit_op(op_name, value_index, complete_cb)

    def add_test(self, name: str, test_base: str, input_parameters: dict, output_parameters: dict, is_custom: bool = True):
        test_num = -1
        if is_custom:
            test_num = self._generate_test_num_if_needed(output_parameters)

        self._tests.append(TestParameters(name, test_base, input_parameters, output_parameters, self.output_validator, test_num))

    def _generate_test_num_if_needed(self, output_parameters: dict):
        free_range = self._get_free_range(self.assigned_ranges)
        test_num = -1
        for _, output_parameter in output_parameters.items():
            if output_parameter.get('test_num'):
                continue

            if test_num == -1:
                test_num = free_range

            free_range += 1
            output_parameter['test_num'] = free_range

        return test_num

    @staticmethod
    def _get_free_range(ranges: list):
        ranges.sort()
        for index, range in enumerate(ranges):
            new_range = MAX_TEST_RANGE * (index + 1)
            if range != new_range:
                return new_range

        return max(ranges) + MAX_TEST_RANGE if len(ranges) != 0 else MAX_TEST_RANGE

    def get_test(self, test_name: str) -> Tuple[TestParameters, int]:
        for index, test in enumerate(self._tests):
            if test.get_test_name() != test_name:
                continue

            return test, index

        return None, None

    def update_test_name(self, test_name: str, new_name: str):
        _, index = self.get_test(test_name)
        test = self._tests.pop(index)
        test.update_test_name(new_name)
        self._tests.append(test)

    def remove_test(self, test_name: str):
        _, index = self.get_test(test_name)
        self._tests.pop(index)

    def reorder_test(self, test_name: str, action: Action):
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

    def get_input_parameter(self, test_name: str, input_name: str) -> InputParameter:
        test, _ = self.get_test(test_name)
        return test.get_input_parameter(input_name)

    def get_output_parameter(self, test_name: str, output_name: str) -> OutputParameter:
        test, _ = self.get_test(test_name)
        return test.get_output_parameter(output_name)

    def get_test_inputs_parameters(self, test_name: str) -> dict:
        test, _ = self.get_test(test_name)
        return test.get_input_parameters()

    def get_test_outputs_parameters(self, test_name: str) -> dict:
        test, _ = self.get_test(test_name)
        return test.get_output_parameters()

    def get_tests_outputs_parameters(self) -> List:
        output_params = []
        for test in self._tests:
            test_out_param = {}
            for k, _ in test.get_output_parameters().items():
                test_out_param.setdefault(test.get_test_name(), []).append(k)

            output_params.append(test_out_param)

        return output_params

    def get_tests(self) -> List:
        return self._tests

    def get_test_names(self) -> List:
        return [test.get_test_name() for test in self._tests]

    def set_temperature(self, temp):
        for test in self._tests:
            test.set_temperature(temp)

    def build_defintion(self) -> List:
        definition = []
        for test in self._tests:
            struct = {}
            struct['is_selected'] = test.get_selectability()
            struct['input_parameters'] = {}
            struct['output_parameters'] = {}
            struct['description'] = test.get_test_name()
            struct['name'] = test.get_test_base()
            struct['sbin'] = test.get_sbin()
            struct['test_num'] = test.get_test_number()
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
                bin_parameter: Bininfo = parameter_content['binning']
                struct['output_parameters'][output] = {'UTL': parameter_content['utl'], 'LTL': parameter_content['ltl'],
                                                       'LSL': parameter_content['lsl'], 'USL': parameter_content['usl'],
                                                       'Binning': {'bin': bin_parameter.bin_number,
                                                                   'result': Result.Fail() if int(bin_parameter.bin_number) not in range(1, 10) else Result.Pass(),
                                                                   'name': bin_parameter.bin_name,
                                                                   'group': bin_parameter.bin_group,
                                                                   'description': bin_parameter.bin_description},
                                                       'fmt': parameter_content['format'], 'Unit': parameter_content['unit'],
                                                       '10ᵡ': parameter_content['exponent'], 'test_num': int(parameter_content['test_num'])}

            definition.append(struct)

        return definition

    @staticmethod
    def _prepare_input_parameter(value, type):
        if type == ResolverTypes.Static() or ResolverTypes.Remote() in type:
            return value
        else:
            if PARAM_PREFIX in value:
                return value

            value_parts = value.split('.')
            return f'{PARAM_PREFIX}{value_parts[0]}.op.{value_parts[1]}'

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
    def _get_binning_structure(test: TestParameters) -> dict:
        return {'name': test.get_test_base(), 'description': test.get_test_name(), 'output_parameters': test.get_output_parameters()}

    def import_tests_parameters(self, sequence_information):
        for test_info in sequence_information:
            test_parameter = TestParameters(test_info['description'], test_info['name'], test_info['input_parameters'], test_info['output_parameters'], self.output_validator, test_info['test_num'], is_selected=test_info['is_selected'])
            self._tests.append(test_parameter)

    def validate_test_parameters(self, test_name, available_tests_handler):
        for test in self._tests:
            if test.get_test_name() != test_name:
                continue

            input_parameters = available_tests_handler.get_test_inputs_parameters(test.get_test_base())
            output_parameters = available_tests_handler.get_test_outputs_parameters(test.get_test_base())

            self._update_parameters(input_parameters, test.get_input_parameters(), lambda missing_param, param_content: test.append_new_input_parameter(missing_param, param_content))
            self._update_parameters(output_parameters, test.get_output_parameters(), lambda missing_param, param_content: test.append_new_output_parameter(missing_param, param_content))

            self._update_parameters_fields(input_parameters, test.get_input_parameters())
            self._update_parameters_fields(output_parameters, test.get_output_parameters())

    @staticmethod
    def _update_parameters(parameters: dict, custom_parameters: dict, callback: Callable):
        removed_parameters = set(custom_parameters.keys()) - set(parameters.keys())
        for removed_parameter in removed_parameters:
            custom_parameters[removed_parameter].set_validity(ParameterState.Removed())

        missing_parameters = set(parameters.keys()) - set(custom_parameters.keys())
        for missing_parameter in missing_parameters:
            callback(missing_parameter, copy.deepcopy(parameters[missing_parameter]))

    @staticmethod
    def _update_parameters_fields(parameters, custom_parameters):
        for name, custom_parameter in custom_parameters.items():
            if not custom_parameter.is_valid():
                continue
            custom_parameter.update_parameters(parameters[name])

    def are_all_tests_valid(self):
        for test in self._tests:
            if test.get_valid_flag() == ParameterState.Invalid():
                return False

        return True

    def validate_tests(self, test_names):
        for test in self._tests:
            if test.get_test_base() not in test_names:
                continue

            test.set_valid_flag(ParameterState.Changed())

    def is_valid_range(self, test, input_param, output_name):
        test, _ = self.get_test(test)
        return test.is_valid_range(input_param, output_name)

    def get_output_parameter_from_test_instance(self, test_instance_name: str) -> Optional[OutputParameter]:
        test: TestParameters = self.get_test_from_test_instance_name(test_instance_name)
        if test:
            out_params = test.get_output_parameters()
            for out_param, value in out_params.items():
                if out_param not in test_instance_name:
                    continue

                return value

        return None

    def get_test_from_test_instance_name(self, test_instance_name: str) -> Optional[TestParameters]:
        for test in self._tests:
            test_instance = test_instance_name.replace(test.get_test_name(), '')

            if test_instance.split('_')[0] != '':
                continue

            return test

        return None

    def update_test_selectability(self, test_name: str, selectable: bool):
        test, _ = self.get_test(test_name)
        test.set_selectability(selectable)

    @property
    def assigned_ranges(self):
        ranges = []
        for test in self._tests:
            ranges += test.get_tests_range()

        ranges += self._test_ranges
        # remove duplicated elements
        return list(dict.fromkeys(ranges))

    def get_ranges(self):
        return self.assigned_ranges

    def is_valid_test_number(self, test_number: int):
        available_test_nums = []
        for test in self._tests:
            available_test_nums += test.get_available_test_nums()

        if test_number in available_test_nums:
            return False, f'test_num {test_number} is already occupied by one of the tests'

        return True, ''

    def set_test_num_ranges(self, test_ranges):
        self._test_ranges = test_ranges
