import numpy as np
from ATE.spyder.widgets.actions_on.program.Utils import ParameterEditability, ParameterState, OutputFieldsPosition
from ATE.spyder.widgets.actions_on.program.Parameters.ParameterField import ParameterField

MAX_SBIN_NUM = 65535


class OutputParameter:
    def __init__(self, name, parameter):
        self.name = ParameterField(name)
        self.lsl = ParameterField(parameter['LSL'])
        self.ltl = ParameterField(parameter['LTL'], editable=ParameterEditability.Editable())
        self.utl = ParameterField(parameter['UTL'], editable=ParameterEditability.Editable())
        self.usl = ParameterField(parameter['USL'])
        self.exponent = ParameterField(parameter['10ᵡ'])
        self.unit = ParameterField(parameter['Unit'])
        self.format = ParameterField(parameter['fmt'])
        self._update_binning_parameters(parameter)
        self.valid = True

    def _update_binning_parameters(self, parameter: dict):
        if parameter.get('Binning') is None:
            self.bin = ParameterField(None if parameter.get('bin') is None else parameter['bin'])
            self.bin_result = ParameterField(None if parameter.get('bin_result') is None else parameter['bin_result'])
        else:
            self.bin = ParameterField(parameter['Binning']['bin'])
            self.bin_result = ParameterField(parameter['Binning']['result'])

    def set_bin_infos(self, bin, bin_result):
        self.bin.set_validity(ParameterState.Valid())
        if not self._is_bin_valid(bin):
            self.bin.set_validity(ParameterState.Invalid())

        self.bin.set_value(bin)

        self.bin_result.set_value(bin_result)

    def set_validity(self, validity):
        for field in self.get_parameters():
            field.set_validity(validity)

        if validity in (ParameterState.Invalid(), ParameterState.Removed()):
            self.valid = False
        else:
            self.valid = True

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
                            OutputFieldsPosition.Format(): self.format}[filed_col]

            return output_filed
        except KeyError:
            return None

    def _is_in_range(self, value):
        return self.lsl < float(value) < self.usl

    def is_valid_value(self):
        return self.ltl.is_valid() and self.utl.is_valid()

    def is_valid(self):
        return self.valid

    def format_value(self, value):
        return ('%' + self.format.get_value()) % float(value)

    def get_parameters(self):
        return [self.name, self.lsl, self.ltl, self.utl, self.usl, self.unit, self.format]

    def get_parameters_content(self):
        return {'name': self.name.get_value(), 'lsl': self.lsl.get_value(), 'ltl': self.ltl.get_value(),
                'usl': self.usl.get_value(), 'utl': self.utl.get_value(), 'unit': self.unit.get_value(),
                'format': self.format.get_value(), 'bin': self.bin.get_value(), 'bin_result': self.bin_result.get_value(),
                'exponent': self.exponent.get_value()}

    def get_field_state(self):
        return self.name.get_state()

    def get_limits(self):
        l_limit = self.lsl.get_value()
        u_limit = self.usl.get_value()
        if not np.isnan(float(self.ltl.get_value())):
            l_limit = self.ltl.get_value()

        if not np.isnan(float(self.utl.get_value())):
            u_limit = self.utl.get_value()

        return float(l_limit), float(u_limit)

    def get_range_infos(self):
        l_limit, u_limit = self.get_limits()
        return l_limit, u_limit, int(self.exponent.get_value())
