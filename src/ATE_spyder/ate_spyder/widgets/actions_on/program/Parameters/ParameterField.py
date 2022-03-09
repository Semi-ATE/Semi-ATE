from ate_common.program_utils import (ParameterState, ParameterEditability)


class ParameterField:
    def __init__(self, value, editable: ParameterEditability = ParameterEditability.NotEditable(), state: ParameterState = ParameterState.Valid()):
        self._value = value
        self._editable = editable
        self._state = state

    def set_value(self, value):
        self._value = value

    def set_validity(self, validity: ParameterState):
        if validity == ParameterState.Removed():
            self.set_editable(ParameterEditability.NotEditable())

        self._state = validity

    def set_editable(self, editable: ParameterEditability):
        self._editable = editable

    def is_editable(self):
        return self._editable == ParameterEditability.Editable()

    def get_state(self):
        return self._state

    def is_valid(self):
        return self._state in (ParameterState.Valid(), ParameterState.Removed(), ParameterState.New())

    def get_value(self):
        return self._value

    def get_editable_flag_value(self):
        return self._editable

    def __lt__(self, rhs):
        return float(self._value) < float(rhs)

    def __le__(self, rhs):
        return float(self._value) <= float(rhs)

    def __gt__(self, rhs):
        return float(self._value) > float(rhs)

    def __ge__(self, rhs):
        return float(self._value) >= float(rhs)
