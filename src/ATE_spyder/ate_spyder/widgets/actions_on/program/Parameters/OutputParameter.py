from dataclasses import dataclass
from ate_common.program_utils import (ParameterEditability, ParameterState, OutputFieldsPosition, ValidatorTypes)
from ate_spyder.widgets.actions_on.program.Parameters.ParameterField import ParameterField
from ate_spyder.widgets.actions_on.program.Parameters.ParameterBase import ParameterBase
from ate_spyder.widgets.actions_on.program.Parameters.OutputValidator import OutputValidator

MAX_SBIN_NUM = 65535


@dataclass
class Bininfo:
    bin_number: str = ''
    bin_name: str = ''
    bin_group: str = ''
    bin_description: str = ''
    is_valid: bool = True


class OutputParameter(ParameterBase):
    def __init__(self, name: str, parameter: dict, output_validator: OutputValidator):
        self.name = ParameterField(name)
        self.lsl = ParameterField(parameter['LSL'])
        self.ltl = ParameterField(parameter['LTL'], editable=ParameterEditability.Editable())
        self.utl = ParameterField(parameter['UTL'], editable=ParameterEditability.Editable())
        self.usl = ParameterField(parameter['USL'])
        self.exponent = ParameterField(parameter['10ᵡ'])
        self.unit = ParameterField(parameter['Unit'])
        self.format = ParameterField(parameter['fmt'])
        self.bin_parameter = None
        self.test_number = ParameterField(parameter['test_num'], editable=ParameterEditability.Editable()) if parameter.get('test_num') else ParameterField('', editable=ParameterEditability.Editable())
        self._update_binning_parameters(parameter)
        self.valid = True
        self.output_validator = output_validator

    def _update_binning_parameters(self, parameter: dict):
        if parameter.get('Binning') is None:
            self.bin_parameter = Bininfo()
        else:
            self.bin_parameter = Bininfo(parameter['Binning']['bin'],
                                         parameter['Binning']['name'],
                                         parameter['Binning']['group'],
                                         parameter['Binning']['description'])

    def update_parameters(self, param):
        self.lsl.set_value(param.lsl.get_value())
        self.usl.set_value(param.usl.get_value())
        self.exponent.set_value(param.exponent.get_value())
        self.unit.set_value(param.unit.get_value())
        self.format.set_value(param.format.get_value())

    def set_bin_infos(self, bin_name: str, bin_num: str, bin_group: str, bin_description: str):
        self.bin_parameter.bin_number = bin_num
        self.bin_parameter.bin_name = bin_name
        self.bin_parameter.bin_group = bin_group
        self.bin_parameter.bin_description = bin_description

    def set_bin_name(self, bin_name: str):
        self.bin_parameter.bin_name = bin_name
        self.set_bin_parameter_validity(True)

    def set_bin_parameter_validity(self, valid: bool):
        self.bin_parameter.is_valid = valid

    def is_bin_parameter_valid(self) -> bool:
        return self.bin_parameter.is_valid

    def get_bin_infos(self) -> Bininfo:
        return self.bin_parameter

    def set_validity(self, validity):
        for field in self.get_parameters():
            field.set_validity(validity)

        self.valid = True

        if validity in (ParameterState.Invalid(), ParameterState.Removed()):
            self.valid = False

    @staticmethod
    def _is_bin_valid(text):
        try:
            sbin = int(text)
        except Exception:
            return False

        return sbin < MAX_SBIN_NUM

    def get_bin_state(self):
        return self.bin.get_state()

    def set_limit(self, value, col):
        if col == OutputFieldsPosition.Ltl():
            self._set_ltl(value)
        elif col == OutputFieldsPosition.Utl():
            self._set_utl(value)
        elif col == OutputFieldsPosition.No():
            self.set_test_number_if_possible(int(value))
        else:
            return

    def _set_ltl(self, value):
        self.set_value(self.ltl, value)
        if not self._is_in_range(value):
            self.ltl.set_validity(ParameterState.Invalid())

        if float(self.ltl.get_value()) > float(self.utl.get_value()):
            self.ltl.set_validity(ParameterState.Invalid())

    def _set_utl(self, value):
        self.set_value(self.utl, value)

        if not self._is_in_range(value):
            self.utl.set_validity(ParameterState.Invalid())

        if float(self.utl.get_value()) < float(self.ltl.get_value()):
            self.utl.set_validity(ParameterState.Invalid())

    def set_value(self, field, value):
        field.set_validity(ParameterState.Valid())
        field.set_value(str(self.format_value(value)))

    def _get_output_field(self, filed_col):
        try:
            output_filed = {OutputFieldsPosition.Name(): self.name,
                            OutputFieldsPosition.Lsl(): self.lsl,
                            OutputFieldsPosition.Ltl(): self.ltl,
                            OutputFieldsPosition.Utl(): self.utl,
                            OutputFieldsPosition.Usl(): self.usl,
                            OutputFieldsPosition.Unit(): self.unit,
                            OutputFieldsPosition.Format(): self.format,
                            OutputFieldsPosition.No(): self.test_number}[filed_col]

            return output_filed
        except KeyError:
            return None

    def _is_in_range(self, value):
        return self.lsl < float(value) < self.usl

    def is_valid_value(self):
        return self.ltl.is_valid() and self.utl.is_valid() and self.test_number.is_valid()

    def is_valid(self):
        return self.valid

    def format_value(self, value):
        return ('%' + self.format.get_value()) % float(value)

    def get_parameters(self):
        return [self.name, self.lsl, self.ltl, self.utl, self.usl, self.unit, self.format, self.test_number]

    def get_parameters_content(self):
        return {'name': self.name.get_value(), 'lsl': self.lsl.get_value(), 'ltl': self.ltl.get_value(),
                'usl': self.usl.get_value(), 'utl': self.utl.get_value(), 'unit': self.unit.get_value(),
                'format': self.format.get_value(), 'binning': self.bin_parameter,
                'exponent': self.exponent.get_value(), 'test_num': self.test_number.get_value()}

    def get_field_state(self):
        return self.name.get_state()

    def get_limits(self):
        l_limit = self.lsl.get_value()
        u_limit = self.usl.get_value()
        import math
        if not math.isnan(float(self.ltl.get_value())):
            l_limit = self.ltl.get_value()

        if not math.isnan(float(self.utl.get_value())):
            u_limit = self.utl.get_value()

        return float(l_limit), float(u_limit)

    def get_range_infos(self):
        l_limit, u_limit = self.get_limits()
        return l_limit, u_limit, int(self.exponent.get_value())

    def _display_impl(self):
        self._set_input_fields(self.name, self.table_row, OutputFieldsPosition.Name())
        self._set_input_fields(self.lsl, self.table_row, OutputFieldsPosition.Lsl())
        self._set_input_fields(self.ltl, self.table_row, OutputFieldsPosition.Ltl())
        self._set_input_fields(self.utl, self.table_row, OutputFieldsPosition.Utl())
        self._set_input_fields(self.usl, self.table_row, OutputFieldsPosition.Usl())
        self._set_input_fields(self.unit, self.table_row, OutputFieldsPosition.Unit())
        self._set_input_fields(self.format, self.table_row, OutputFieldsPosition.Format())
        self._set_input_fields(self.test_number, self.table_row, OutputFieldsPosition.No())

    def on_edit_done_impl(self, new_text, value_index):
        self.set_limit(float(new_text), value_index)

    def _get_validator_type(self, value_index: int) -> ValidatorTypes:
        if value_index == OutputFieldsPosition.No():
            return ValidatorTypes.IntValidation

        return ValidatorTypes.FloatValidation

    def get_test_number(self):
        return int(self.test_number.get_value())

    def set_test_number_if_possible(self, test_num: int):
        self.output_validator.set_invalid_test_number_message()
        success, message = self.output_validator.is_valid_test_number(test_num)
        if not success:
            self.output_validator.set_invalid_test_number_message(test_num, message)
            return

        self.set_test_number(test_num)

    def set_test_number(self, test_num: int):
        self.test_number.set_value(str(test_num))
