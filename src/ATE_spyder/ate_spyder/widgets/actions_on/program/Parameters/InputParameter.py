import copy

from ate_common.program_utils import ParameterState, ParameterEditability, ResolverTypes, ValidatorTypes, Range, InputFieldsPosition
from ate_spyder.widgets.actions_on.program.Parameters.ParameterField import ParameterField
from ate_spyder.widgets.actions_on.program.Parameters.ParameterBase import ParameterBase
from ate_spyder.widgets.actions_on.program.Parameters.Utils import PARAM_PREFIX


class InputParameter(ParameterBase):
    class InputParameterFieldType(ParameterField):
        def __init__(self, value, editable):
            editable = ParameterEditability.Selectable() if editable == ParameterEditability.Editable() else editable
            super().__init__(value, editable)

    def __init__(self, name, input_params):
        editable = ParameterEditability.Editable()

        if name == 'Temperature':
            editable = ParameterEditability.NotEditable()

        self.name = ParameterField(name)
        self.min = ParameterField(input_params['Min'])
        self.max = ParameterField(input_params['Max'])
        self.format = ParameterField(input_params['fmt'])
        self.unit = ParameterField(input_params['Unit'])
        self.exponent = ParameterField(input_params['10ᵡ'])
        self.type = self.InputParameterFieldType(ResolverTypes.Static() if input_params.get('type') is None else input_params['type'], editable=editable)
        self.default = ParameterField(self.format_value(input_params['Default']), editable=editable)
        self.value = copy.deepcopy(self.default) if input_params.get('value') is None else ParameterField(self._get_value(input_params))
        self.valid = True
        self.shmoo = ParameterField(input_params['Shmoo'])

        self._select_editability_for_resolvertype(editable)

    def update_parameters(self, param: 'InputParameter'):
        self.exponent.set_value(param.exponent.get_value())
        self.unit.set_value(param.unit.get_value())
        self.format.set_value(param.format.get_value())
        self.shmoo.set_value(param.shmoo.get_value())

    def _select_editability_for_resolvertype(self, editable):
        if editable is not ParameterEditability.NotEditable():
            if self.type == ResolverTypes.Static():
                self.set_value_editability(ParameterEditability.Editable)
            elif self.type == ResolverTypes.Local():
                self.set_value_editability(ParameterEditability.Selectable)
            else:
                self.set_value_editability(ParameterEditability.Editable)

    @staticmethod
    def _get_value(input_params):
        if PARAM_PREFIX in str(input_params['value']):
            return input_params['content']

        return input_params['value']

    def set_value(self, value):
        self.value.set_validity(ParameterState.Valid())
        if self.type.get_value() == ResolverTypes.Static():
            resolver_type = ResolverTypes.Static()
            formatted = self.format_value(value)
            self.value.set_value(formatted)

            if self.min > float(value) or float(value) > self.max:
                self.value.set_validity(ParameterState.Invalid())
        elif self.type.get_value() == ResolverTypes.Local():
            resolver_type = ResolverTypes.Local()
            self.value.set_value(value)
        else:
            # Remote!
            resolver_type = self.type.get_value()
            self.value(value)

        self._set_validity_flag(resolver_type)

    def set_validity(self, validity):
        for field in self.get_parameters():
            field.set_validity(validity)

        self.valid = validity not in (ParameterState.Invalid(), ParameterState.Removed())

    def set_value_editability(self, editable_flag):
        self.value.set_editable(editable_flag)

    def set_type(self, type):
        self.type.set_value(type)
        self._set_validity_flag(type)

    def _set_validity_flag(self, type):
        convertable = True
        try:
            float(self.value.get_value())
        except Exception:
            convertable = False

        self.value.set_validity(ParameterState.Valid())
        if type == ResolverTypes.Static() and not convertable:
            self.value.set_value(self.default.get_value())
        if type == ResolverTypes.Local() and convertable:
            self.value.set_validity(ParameterState.Invalid())
        if ResolverTypes.Remote() in type:
            self.value.set_validity(ParameterState.Valid())

    def _get_input_field(self, field_column):
        try:
            input_field = {InputFieldsPosition.Name(): self.name,
                           InputFieldsPosition.Min(): self.min,
                           InputFieldsPosition.Value(): self.value,
                           InputFieldsPosition.Max(): self.max,
                           InputFieldsPosition.Unit(): self.unit,
                           InputFieldsPosition.Format(): self.format,
                           InputFieldsPosition.Type(): self.type}[field_column]

            return input_field
        except KeyError:
            return None

    def _get_validator_type(self, value_index: int) -> ValidatorTypes:
        if ResolverTypes.Remote() in self.type.get_value():
            return ValidatorTypes.NoValidation
        else:
            return ValidatorTypes.FloatValidation

    def get_editable_flag_value(self, field_col):
        return self._get_input_field(field_col).get_editable_flag_value()

    def get_value(self):
        # we do not need to format the value in case of type local as it is not
        # a decimal number
        if self.type.get_value() == ResolverTypes.Local():
            return self.value.get_value()

        return float(self.format_value(self.value))

    def format_value(self, value):
        try:
            int(value)
            return ('%' + self.format.get_value()) % float(value)
        except Exception:
            return value

    def get_name(self):
        return self.name.get_value()

    def get_parameters(self):
        return [self.name, self.min, self.value, self.max, self.unit, self.format, self.type, self.exponent]

    def get_parameters_content(self):
        return {'name': self.name.get_value(), 'min': self.min.get_value(), 'value': self.value.get_value(),
                'max': self.max.get_value(), 'format': self.format.get_value(), 'unit': self.unit.get_value(),
                'type': self.type.get_value(), 'exponent': self.exponent.get_value(), 'default': self.default.get_value(),
                'shmoo': self.shmoo.get_value()}

    def is_valid(self):
        return self.valid

    def is_valid_value(self):
        return self.value.is_valid()

    def set_temperature(self, temps):
        validity = ParameterState.Valid()
        if self.name.get_value() != 'Temperature':
            return None

        range = self._get_temperatures_range(temps)
        if range == Range.Out_Of_Range():
            validity = ParameterState.Invalid()
        elif range == Range.Limited_Range():
            validity = ParameterState.PartValid()
        else:
            validity = ParameterState.Valid()

        self.value.set_validity(validity)
        if len(temps) > 1:
            text = '' if temps is None else f"{self.format_value(temps[0])}..{self.format_value(temps[len(temps) - 1])}"
        else:
            text = self.format_value(temps[0])

        self.value.set_value(text)

        return validity

    def _get_temperatures_range(self, temps):
        if temps is None:
            return Range.In_Range()

        temps.sort()
        in_range_list = [x for x in temps if x >= self.min and x <= self.max]

        if len(in_range_list) == len(temps):
            return Range.In_Range()
        elif not len(in_range_list):
            return Range.Out_Of_Range()
        else:
            return Range.Limited_Range()

    def get_limits(self):
        return float(self.min.get_value()), float(self.max.get_value())

    def get_range_infos(self):
        l_limit, u_limit = self.get_limits()
        return l_limit, u_limit, int(self.exponent.get_value())

    def _display_impl(self):
        self._set_input_fields(self.name, self.table_row, InputFieldsPosition.Name())
        self._set_input_fields(self.min, self.table_row, InputFieldsPosition.Min())
        self._set_input_fields(self.value, self.table_row, InputFieldsPosition.Value())
        self._set_input_fields(self.max, self.table_row, InputFieldsPosition.Max())
        self._set_input_fields(self.unit, self.table_row, InputFieldsPosition.Unit())
        self._set_input_fields(self.format, self.table_row, InputFieldsPosition.Format())
        self._set_input_fields(self.type, self.table_row, InputFieldsPosition.Type())

    def on_edit_done_impl(self, new_text, _):
        try:
            float_val = float(new_text)
            self.value.set_value(float_val)
        except ValueError:
            self.value.set_value(new_text)

    def is_shmooable(self):
        return self.shmoo.get_value()
