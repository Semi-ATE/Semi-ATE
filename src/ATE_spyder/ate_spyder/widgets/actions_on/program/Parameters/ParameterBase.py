from typing import Callable
from PyQt5.QtWidgets import QTableWidget
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

from ate_common.program_utils import ParameterEditability, ValidatorTypes
from ate_common.program_utils import ParameterState


ORANGE = (255, 127, 39)
RED = (237, 28, 36)
GREEN = (34, 117, 76)


class ParameterBase():

    def __init__(self):
        self.table = None
        self.table_row = None

    def on_edit_done(self, new_text: str, value_index: int, complete_cb: Callable):
        self.on_edit_done_impl(new_text, value_index)
        self._display_impl()
        complete_cb()

    def on_edit_done_impl(self, new_text: str, value_index: int):
        pass

    def _display_impl(self):
        pass

    def _set_value_impl(self):
        pass

    def _get_validator_type(self, value_index: int) -> ValidatorTypes:
        return ValidatorTypes.FloatValidation

    def display(self, target_table: QTableWidget):
        row = target_table.rowCount()
        self.table_row = row
        self.table = target_table
        target_table.setRowCount(row + 1)
        self._display_impl()

    def get_editable_flag_value(self, value_index: int):
        # overridden by InputParameter!
        return ParameterEditability.Editable()

    def edit(self, value_index: int, complete_cb: Callable):
        if self.get_editable_flag_value(value_index) != ParameterEditability.Editable():
            return

        validator = None
        if self._get_validator_type(value_index) == ValidatorTypes.FloatValidation:
            from ate_spyder.widgets.validation import valid_float_regex
            validator = QtGui.QRegExpValidator(QtCore.QRegExp(valid_float_regex), None)
        elif self._get_validator_type(value_index) == ValidatorTypes.IntValidation:
            from ate_spyder.widgets.validation import valid_integer_regex
            validator = QtGui.QRegExpValidator(QtCore.QRegExp(valid_integer_regex), None)

        item = self.table.item(self.table_row, value_index)
        self.create_checkable_cell(item, validator, lambda txt, value: self.on_edit_done(txt, value, complete_cb))

    def create_checkable_cell(self, item, validator, edit_complete_callback):
        column = item.column()
        row = item.row()
        checkable_widget = QtWidgets.QLineEdit()
        checkable_widget.setText(item.text())
        if validator is not None:
            checkable_widget.setValidator(validator)

        self.table.setCellWidget(row, column, checkable_widget)
        checkable_widget.editingFinished.connect(lambda: _edit_cell_done(checkable_widget, column, edit_complete_callback))

    def _set_input_fields(self, input_parameter_filed, row, col):
        item = QtWidgets.QTableWidgetItem(str(input_parameter_filed.get_value()))
        if col == 0:
            item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        else:
            item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)

        flag = input_parameter_filed.get_editable_flag_value()
        if flag == ParameterEditability.NotEditable():
            item.setFlags(QtCore.Qt.NoItemFlags)
        elif flag == ParameterEditability.Selectable():
            item.setFlags(QtCore.Qt.ItemIsEnabled)
        else:
            item.setFlags(item.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

        try:
            color = {ParameterState.Invalid(): RED,
                     ParameterState.Changed(): RED,
                     ParameterState.Removed(): RED,
                     ParameterState.PartValid(): ORANGE,
                     ParameterState.New(): GREEN}[input_parameter_filed.get_state()]
            _set_widget_color(item, color)
        except KeyError:
            pass

        self.table.setItem(row, col, item)


def _set_widget_color(item, color):
    item.setBackground(_generate_color(color))
    item.setForeground(QtCore.Qt.black)


def _generate_color(color):
    return QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2]))


def _edit_cell_done(checkable_widget, value_index, edit_complete_cb):
    edit_complete_cb(checkable_widget.text(), value_index)
