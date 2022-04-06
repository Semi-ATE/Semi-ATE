from typing import Dict, Optional

# from ATE.Tester.TES.apps.testApp.sequencers.DutTesting.Result import Result

from enum import Enum


# The enummembers are numbered by "severity". A given test
# can never decrease a result for the complete program, i.e.
# once we have a fail it will stay a fail regardless of what
# others say.
class Result(Enum):
    Fail = 2
    Pass = 1
    Inconclusive = 0

    def __call__(self):
        return self.value


from ate_spyder.widgets.actions_on.program.Parameters.OutputValidator import OutputValidator
from ate_spyder.widgets.actions_on.program.Parameters.InputParameter import InputParameter
from ate_spyder.widgets.actions_on.program.Parameters.OutputParameter import Bininfo, OutputParameter
from ate_spyder.widgets.actions_on.program.Parameters.Utils import MAX_TEST_RANGE, PARAM_PREFIX
from ate_common.program_utils import ParameterState, ResolverTypes


class TestParameters:
    def __init__(
        self,
        name: str,
        test_base: str,
        input_parameters: dict,
        output_parameters: dict,
        output_validator: OutputValidator,
        test_num: int,
        is_selected: bool = True,
        executions: Optional[Dict[str, int]] = None
    ):
        self._test_name = name
        self._test_base = test_base
        self._input_parameters = {
            name: InputParameter(name, value) for name, value in input_parameters.items()
        }
        self._output_parameters = {
            name: OutputParameter(name, value, output_validator)
            for name, value in output_parameters.items()
        }
        self._valid = ParameterState.Valid()
        self._sbin = None
        self._is_selected = is_selected
        self.test_num = test_num

        self.executions: Dict[str, int] = executions if executions is not None else {}

    @staticmethod
    def from_database(definition, output_validator) -> "TestParameters":
        return TestParameters(
            definition['description'],
            definition['name'],
            definition['input_parameters'],
            definition['output_parameters'],
            output_validator,
            definition['test_num'],
            is_selected=definition['is_selected']
        )

    def serialize_definition(self) -> Dict[str, any]:
        struct = {}
        struct['is_selected'] = self.get_selectability()
        struct['input_parameters'] = {}
        struct['output_parameters'] = {}
        struct['description'] = self.get_test_name()
        struct['name'] = self.get_test_base()
        struct['sbin'] = self.get_sbin()
        struct['test_num'] = self.get_test_number()
        struct['input_parameters'] = self.serialize_input_parameters()
        struct['output_parameters'] = self.serialize_output_parameters()
        return struct

    def serialize_input_parameters(self):
        struct = {}
        for input, value in self.get_input_parameters().items():
            if not value.is_valid():
                continue
            parameter_content = value.get_parameters_content()
            struct[input] = {
                'value': self._prepare_input_parameter(parameter_content['value'], parameter_content['type']),
                'type': parameter_content['type'],
                'Min': parameter_content['min'],
                'Max': parameter_content['max'],
                'fmt': parameter_content['format'],
                'Unit': parameter_content['unit'],
                '10ᵡ': parameter_content['exponent'],
                'Default': parameter_content['default'],
                'content': parameter_content['value'],
                'Shmoo': parameter_content['shmoo']
            }
        return struct

    def serialize_output_parameters(self):
        struct = {}
        for output, value in self.get_output_parameters().items():
            if not value.is_valid():
                continue
            parameter_content = value.get_parameters_content()
            bin_parameter: Bininfo = parameter_content['binning']
            struct[output] = {
                'UTL': parameter_content['utl'],
                'LTL': parameter_content['ltl'],
                'LSL': parameter_content['lsl'],
                'USL': parameter_content['usl'],
                'Binning': {
                    'bin': bin_parameter.bin_number,
                    'result': Result.Fail() if int(bin_parameter.bin_number) not in range(1, 10) else Result.Pass(),
                    'name': bin_parameter.bin_name,
                    'group': bin_parameter.bin_group,
                    'description': bin_parameter.bin_description
                },
                'fmt': parameter_content['format'], 'Unit': parameter_content['unit'],
                '10ᵡ': parameter_content['exponent'], 'test_num': int(parameter_content['test_num'])
            }
        return struct

    @staticmethod
    def _prepare_input_parameter(value, type):
        if type == ResolverTypes.Static() or ResolverTypes.Remote() in type:
            return value
        else:
            if PARAM_PREFIX in value:
                return value

            value_parts = value.split('.')
            return f'{PARAM_PREFIX}{value_parts[0]}.op.{value_parts[1]}'

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
