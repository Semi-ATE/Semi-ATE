import copy
from ATE.spyder.widgets.actions_on.program.Utils import (ParameterState, ParameterEditability, ResolverTypes, Range, InputFieldsPosition)
from ATE.spyder.widgets.actions_on.program.Parameters.ParameterField import ParameterField


class InputParameter:
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
        self.factor = ParameterField(input_params['10ᵡ'])
        self.type = self.InputParameterFieldType(ResolverTypes.Static() if input_params.get('type') is None else input_params['type'], editable=editable)
        self.default = ParameterField(self.format_value(input_params['Default']), editable=editable)
        self.value = copy.deepcopy(self.default) if input_params.get('value') is None else ParameterField(input_params['value'])

        self.editable = ParameterEditability.Editable()

        self.valid = True

    def set_value(self, value):
        self.value.set_validity(ParameterState.Valid())
        if self.type.get_value() == ResolverTypes.Static():
            resolver_type = ResolverTypes.Static()
            formatted = self.format_value(value)
            self.value.set_value(formatted)
            self._set_validity_flag(resolver_type)

            if self.min > float(value) or float(value) > self.max:
                self.value.set_validity(ParameterState.Invalid())
        else:
            resolver_type = ResolverTypes.Local()
            self.value.set_value(value)
            self._set_validity_flag(resolver_type)

    def set_validity(self, validity):
        for field in self.get_parameters():
            field.set_validity(validity)

        if validity in (ParameterState.Invalid(), ParameterState.Removed()):
            self.valid = False
        else:
            self.valid = True

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
            print(self.default.get_value())
            self.value.set_value(self.default.get_value())
        if type == ResolverTypes.Local() and convertable:
            self.value.set_validity(ParameterState.Invalid())

    def _get_input_field(self, filed_col):
        try:
            input_filed = {InputFieldsPosition.Name(): self.name,
                           InputFieldsPosition.Min(): self.min,
                           InputFieldsPosition.Value(): self.value,
                           InputFieldsPosition.Max(): self.max,
                           InputFieldsPosition.Unit(): self.unit,
                           InputFieldsPosition.Format(): self.format,
                           InputFieldsPosition.Type(): self.type}[filed_col]

            return input_filed
        except KeyError:
            return None

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
        return [self.name, self.min, self.value, self.max, self.unit, self.format, self.type, self.factor]

    def get_parameters_content(self):
        return {'name': self.name.get_value(), 'min': self.min.get_value(), 'value': self.value.get_value(),
                'max': self.max.get_value(), 'format': self.format.get_value(), 'unit': self.unit.get_value(),
                'type': self.type.get_value(), 'factor': self.factor.get_value(), 'default': self.default.get_value()}

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

    def _is_temperature_in_range(self, test, temps):
        if temps is None:
            return Range.In_Range()

        min, max = self.project_info.get_test_temp_limits(test, self.project_info.active_hardware, self.project_info.active_base)
        temps.sort()

        in_range_list = [x for x in temps if x >= min and x <= max]

        if len(in_range_list) == len(temps):
            return Range.In_Range()
        elif not len(in_range_list):
            return Range.Out_Of_Range()
        else:
            return Range.Limited_Range()
