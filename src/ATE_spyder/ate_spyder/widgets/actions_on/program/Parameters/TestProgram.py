from typing import Callable, Dict, List, Optional, Tuple
import copy

from ate_spyder.widgets.actions_on.program.Parameters.OutputValidator import OutputValidator
from ate_common.program_utils import Action, ParameterState
from ate_spyder.widgets.actions_on.program.Parameters.InputParameter import InputParameter
from ate_spyder.widgets.actions_on.program.Parameters.OutputParameter import OutputParameter
from ate_spyder.widgets.actions_on.program.Parameters.TestParameters import TestParameters
from ate_spyder.widgets.actions_on.program.Parameters.Utils import MAX_TEST_RANGE
from PyQt5.QtWidgets import QTableWidget


class TestProgram:
    def __init__(self):
        self._tests: List[TestParameters] = []
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

    def add_test(
        self,
        name: str,
        test_base: str,
        input_parameters: dict,
        output_parameters: dict,
        is_custom: bool = True,
        position: int = -1,
        executions: Dict[str, int] = None
    ):
        test_num = -1
        if is_custom:
            test_num = self._generate_test_num_if_needed(output_parameters)

        test_instance = TestParameters(
            name,
            test_base,
            input_parameters,
            output_parameters,
            self.output_validator,
            test_num,
            executions=executions
        )

        if position == -1:
            self._tests.append(test_instance)
        else:
            self._tests.insert(position, test_instance)

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
        test, _ = self.get_test(test_name)
        test.update_test_name(new_name)

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

    def get_tests(self) -> List[TestParameters]:
        return self._tests

    def get_test_names(self) -> List[str]:
        return [test.get_test_name() for test in self._tests]

    def set_temperature(self, temp):
        for test in self._tests:
            test.set_temperature(temp)

    def build_defintion(self) -> List:
        definition = []
        for test in self._tests:
            definition.append(test.serialize_definition())

        return definition

    def get_binning_information(self):
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
            self._tests.append(TestParameters.from_database(test_info, self.output_validator))

    def import_tests_executions(self, executions: Dict[str, List[int]]):
        for parallelism_name, ping_pong_list in executions.items():
            assert len(ping_pong_list) == len(self._tests)
            for index, test in enumerate(self._tests):
                test.executions[parallelism_name] = ping_pong_list[index]

    def serialize_execution(self):
        data = {}
        for test in self._tests:
            for parallelism_name, ping_pong_id in test.executions.items():
                data.setdefault(parallelism_name, []).append(ping_pong_id)
        return data

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

                pos = test_instance_name.find(out_param)
                if pos == -1:
                    continue

                output_param_name = test_instance_name[pos: len(test_instance_name)]

                if output_param_name != out_param:
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
