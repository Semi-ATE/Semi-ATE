# -*- coding: utf-8 -*-
from abc import ABC, abstractclassmethod
from dataclasses import dataclass
from enum import IntEnum, unique, auto
import math
from pathlib import Path
import re
from typing import Callable, List, Optional, Tuple

from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog
from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.validation import valid_float_regex
from ate_common.parameter import InputColumnKey, OutputColumnKey

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


@dataclass
class InputRow:
    __slot__ = ['name', 'shmoo', 'min', 'call', 'step', 'max', 'exponent', 'unit']

    def __init__(self, name: str, shmoo: bool, min: float, max: float, exponent: int, unit: str):
        self.name = name
        self.shmoo = shmoo
        self.min = min
        self.max = max
        self.exponent = exponent
        self.unit = unit

        self.shmoo_state = shmoo

        self.call = None
        self.step = None

    def is_shmooable(self) -> bool:
        return self.shmoo

    def set_shmooable(self, shmoo_state: bool):
        self.shmoo_state = shmoo_state


@dataclass
class InputTable:
    def __init__(self):
        self.rows = []

    def add_row(self, row: InputRow):
        self.rows.append(row)

    def get_row(self, row: int) -> InputRow:
        return self.rows[row]


@unique
class TabIds(IntEnum):
    Run = 0
    Shmoo = 1
    Timing = 2
    Console = 3


@unique
class InputColumn(IntEnum):
    Name = 0
    Shmoo = auto()
    Min = auto()
    Call = auto()
    Step = auto()
    Max = auto()
    Power = auto()
    Unit = auto()

    def __call__(self):
        return self.value


@unique
class OutputColumn(IntEnum):
    Name = 0
    LSL = 1
    LTL = 2
    UTL = 3
    USL = 4
    Unit = 5

    def __call__(self):
        return self.value


@dataclass
class CellInfo:
    row: int
    col: int


class TabInterface(ABC):
    def __init__(self, parent: 'TestRunner'):
        self.parent = parent

    @abstractclassmethod
    def setup_view(self):
        pass

    @abstractclassmethod
    def setup_callbacks(self):
        pass


class RunTab(TabInterface):
    def __init__(self, parent: 'TestRunner'):
        super().__init__(parent)
        self.current_cell_info: Optional[CellInfo] = None
        self.input_table_data = InputTable()
        self.output_table_data = []

    def setup_view(self):
        # the running tab doesn't support both Trends and Statistics in the current version
        self.parent.tabWidget.setTabVisible(2, False)
        self.parent.tabWidget.setTabVisible(3, False)

        self.parent.base.currentIndexChanged.connect(lambda index: self._base_changed(index))

        available_hardwares = self.parent.project_info.get_active_hardware_names()
        self.parent.hardware.currentIndexChanged.connect(lambda index: self._hardware_changed(index))
        self.parent.hardware.addItems(available_hardwares)
        self.parent.hardware.setCurrentIndex(0)

        self.parent.feedback.setStyleSheet('color: orange')

        self.parent.inputParameter.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.parent.outputParameter.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.parent.inputParameter.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.parent.outputParameter.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.parent.inputParameter.selectionModel().selectionChanged.connect(lambda selected, deselected: self._update_cell(selected, deselected, self.parent.inputParameter))
        self.parent.outputParameter.selectionModel().selectionChanged.connect(lambda selected, deselected: self._update_cell(selected, deselected, self.parent.outputParameter))

    def setup_callbacks(self):
        # TODO: the implementation of this part shall be done in #239
        self.parent.start.clicked.connect(self._start_execution)
        ''''''

    def _start_execution(self):
        # TODO: the code generation may be the same as generating a test program but with only one test
        # TODO: emit signal to spyder
        self.parent.feedback.setText('not implemented yet')

    def _fill_output_parameter_table(self):
        output_table = self.parent.outputParameter
        output_table.setRowCount(0)

        if not self.test_name:
            return

        data = self.parent.project_info.get_test(self.test_name, self.hardware, self.base)
        output_parameters = data.definition['output_parameters']

        output_table.cellDoubleClicked.connect(lambda row, col: self._call_value_double_clicked(
            output_table,
            row,
            col,
            float(self.parent.outputParameter.item(row, OutputColumn.LSL).text()),
            float(self.parent.outputParameter.item(row, OutputColumn.USL).text()))
        )

        output_table.blockSignals(True)
        for index, (key, value) in enumerate(output_parameters.items()):
            output_table.insertRow(index)

            item = QtWidgets.QTableWidgetItem(key)
            item.setFlags(QtCore.Qt.ItemIsSelectable)
            output_table.setItem(index, OutputColumn.Name, item)

            item = QtWidgets.QTableWidgetItem(str(value[OutputColumnKey.LSL()]))
            item.setFlags(QtCore.Qt.ItemIsSelectable)
            output_table.setItem(index, OutputColumn.LSL, item)

            item = QtWidgets.QTableWidgetItem(str(value[OutputColumnKey.LTL()]))
            output_table.setItem(index, OutputColumn.LTL, item)

            item = QtWidgets.QTableWidgetItem(str(value[OutputColumnKey.UTL()]))
            output_table.setItem(index, OutputColumn.UTL, item)

            item = QtWidgets.QTableWidgetItem(str(value[OutputColumnKey.USL()]))
            item.setFlags(QtCore.Qt.ItemIsSelectable)
            output_table.setItem(index, OutputColumn.USL, item)

            item = QtWidgets.QTableWidgetItem(str(value[OutputColumnKey.UNIT()]))
            item.setFlags(QtCore.Qt.ItemIsSelectable)
            output_table.setItem(index, OutputColumn.Unit, item)
        output_table.blockSignals(False)

    def _fill_input_parameter_table(self):
        input_table = self.parent.inputParameter
        input_table.setRowCount(0)

        if not self.test_name:
            return

        data = self.parent.project_info.get_test(self.test_name, self.hardware, self.base)
        input_parameters = data.definition['input_parameters']

        input_table.itemClicked.connect(self._shmoo_state_update)
        input_table.cellDoubleClicked.connect(lambda row, col: self._call_value_double_clicked(
            input_table,
            row,
            col,
            float(self.parent.inputParameter.item(row, InputColumn.Min).text()),
            float(self.parent.inputParameter.item(row, InputColumn.Max).text()))
        )

        input_table.blockSignals(True)
        for index, (key, value) in enumerate(input_parameters.items()):
            row = InputRow(key, value[InputColumnKey.SHMOO()], value[InputColumnKey.MIN()], value[InputColumnKey.MAX()], value[InputColumnKey.POWER()], value[InputColumnKey.UNIT()])
            self.input_table_data.add_row(row)

            input_table.insertRow(index)

            item = QtWidgets.QTableWidgetItem(key)
            item.setFlags(QtCore.Qt.ItemIsSelectable)
            input_table.setItem(index, InputColumn.Name, item)

            item = QtWidgets.QTableWidgetItem()
            item.setFlags(QtCore.Qt.NoItemFlags)
            input_table.setItem(index, InputColumn.Shmoo, item)
            if not row.is_shmooable():
                item.setToolTip('parameter is not shmooable')
            else:
                item.setCheckState(QtCore.Qt.Checked if row.is_shmooable() else QtCore.Qt.Unchecked)

            item = QtWidgets.QTableWidgetItem(str(value[InputColumnKey.MIN()]))
            item.setFlags(QtCore.Qt.ItemIsSelectable)
            input_table.setItem(index, InputColumn.Min, item)

            item = QtWidgets.QTableWidgetItem(str(value[InputColumnKey.MAX()]))
            item.setFlags(QtCore.Qt.ItemIsSelectable)
            input_table.setItem(index, InputColumn.Max, item)

            item = QtWidgets.QTableWidgetItem(str(value[InputColumnKey.DEFAULT()]))
            item.setToolTip('call is only enabled when shmoo is not set')
            input_table.setItem(index, InputColumn.Call, item)

            if row.is_shmooable():
                item.setFlags(QtCore.Qt.ItemIsSelectable)

            item = QtWidgets.QTableWidgetItem('0.0')
            input_table.setItem(index, InputColumn.Step, item)
            item.setToolTip('step is only enabled when shmoo is set')

            if not row.is_shmooable():
                item.setFlags(QtCore.Qt.ItemIsSelectable)

            item = QtWidgets.QTableWidgetItem(str(value[InputColumnKey.POWER()]))
            item.setFlags(QtCore.Qt.ItemIsSelectable)
            input_table.setItem(index, InputColumn.Power, item)

            item = QtWidgets.QTableWidgetItem(str(value[InputColumnKey.UNIT()]))
            item.setFlags(QtCore.Qt.ItemIsSelectable)
            input_table.setItem(index, InputColumn.Unit, item)
        input_table.blockSignals(False)

    @QtCore.pyqtSlot(str, QtWidgets.QTableWidget, int, int, float, float)
    def _call_value_double_clicked(self, table: QtWidgets.QTableWidget, row: int, col: int, min: float, max: float):
        if col == InputColumn.Shmoo:
            return

        if table == self.parent.outputParameter:
            self._check_table_parameter(table, row, col, min, max, self._validate_output_parameter)
        else:
            self._check_table_parameter(table, row, col, min, max, self._validate_value)

    def _shmoo_state_update(self, item: QtWidgets.QTableWidgetItem):
        if item.column() != InputColumn.Shmoo:
            return

        if not self.input_table_data.get_row(item.row()).is_shmooable():
            return

        self.input_table.blockSignals(True)
        new_check_state = QtCore.Qt.Checked if item.checkState() == QtCore.Qt.Unchecked else QtCore.Qt.Unchecked
        item.setCheckState(new_check_state)
        self._update_row(item.row(), new_check_state == QtCore.Qt.Checked)
        self.input_table.blockSignals(False)

    def _update_row(self, row_index: int, is_checked: bool):
        row = self.input_table_data.get_row(row_index)
        row.set_shmooable(is_checked)

        if row.shmoo_state:
            item = self.input_table.item(row_index, InputColumn.Call)
            item.setFlags(QtCore.Qt.ItemIsSelectable)

            item = self.input_table.item(row_index, InputColumn.Step)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
        else:
            item = self.input_table.item(row_index, InputColumn.Call)
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)

            item = self.input_table.item(row_index, InputColumn.Step)
            item.setFlags(QtCore.Qt.ItemIsSelectable)

    def _check_table_parameter(self, table: QtWidgets.QTableWidget, row: int, col: int, min: float, max: float, validate_callback: Callable):
        item = table.item(row, col)
        initial_value = item.text()

        regx = QtCore.QRegExp(valid_float_regex)
        integer_validator = QtGui.QRegExpValidator(regx, self.parent)
        line = QtWidgets.QLineEdit(str(item.text()))
        line.setValidator(integer_validator)
        line.textChanged.connect(lambda text: self._call_value_changed(text, row, col, min, max, validate_callback))
        line.editingFinished.connect(lambda: self._call_value_edited(table, initial_value, row, col, min, max, validate_callback))

        line.blockSignals(True)
        line.setText(initial_value)
        line.blockSignals(False)

        table.setCellWidget(row, col, line)

    @QtCore.pyqtSlot(str, QtWidgets.QTableWidget, int, int, float, float, object)
    def _call_value_edited(self, table: QtWidgets.QTableWidget, initial_value: str, row: int, col: int, min: float, max: float, validate_callback: Callable):
        value = initial_value
        text = table.cellWidget(row, col).text()
        if validate_callback(text, row, col, min, max):
            value = text

        table.removeCellWidget(row, col)
        item = QtWidgets.QTableWidgetItem(value)
        table.setItem(row, col, item)

    @QtCore.pyqtSlot(str, int, int, float, float)
    def _call_value_changed(self, text: str, row: int, col: int, min: float, max: float, validate_callback: Callable):
        _ = validate_callback(text, row, col, min, max)

    def _validate_value(self, text: str, row: int, col: int, min: float, max: float) -> bool:
        self.parent.feedback.setText('')

        if not text or text in ['-', '+']:
            self.parent.feedback.setText('call value is empty')
            return False

        value = float(text)

        if value > max or value < min:
            self.parent.feedback.setText('call value is out of range')
            return False

        row_data = self.input_table_data.get_row(row)
        if col == InputColumn.Call:
            row_data.call = value
        if col == InputColumn.Step:
            row_data.step = value

        return True

    def _validate_output_parameter(self, text: str, row: int, col: int, min: float, max: float):
        if self._validate_value(text, row, col, min, max):
            return self.check_utl_ltl(text, row, col)

    def check_utl_ltl(self, text: str, row: int, col: int) -> bool:
        if col == OutputColumn.LTL:
            utl = float(self.parent.outputParameter.item(row, OutputColumn.UTL).text())
            if math.isnan(float(utl)):
                return True

            ltl = float(text)
        else:
            ltl = float(self.parent.outputParameter.item(row, OutputColumn.LTL).text())
            if math.isnan(float(ltl)):
                return True

            utl = float(text)

        if not utl > ltl:
            self.parent.feedback.setText('upper limit should be bigger than lower limit')
            return False

        return True

    def _collect_data(self) -> dict:
        input_value_tuples = self._get_input_table_values()

        data = self.parent.project_info.get_test(self.test_name, self.hardware, self.base)
        input_parameters = data.definition['input_parameters']

        output_parameters = data.definition['output_parameters']
        output_value_tuples = self._get_output_table_values()

        for name, value in input_value_tuples:
            input_parameters[name]['value'] = value

        for name, ltl, utl in output_value_tuples:
            output_parameters[name]['ltl'] = ltl
            output_parameters[name]['utl'] = utl

        return data

    def _get_input_table_values(self) -> List[Tuple[str, float]]:
        value_tuples = []
        for row in range(self.input_table.rowCount()):
            name = self.input_table.item(row, InputColumn.Name).text()
            value = self.input_table.item(row, InputColumn.Call).text()

            value_tuples.append((name, float(value)))

        return value_tuples

    def _get_output_table_values(self) -> List[Tuple[str, float, float]]:
        value_tuples = []
        for row in range(self.output_table.rowCount()):
            name = self.output_table.item(row, OutputColumn.Name).text()
            ltl = self.output_table.item(row, OutputColumn.LTL).text()
            utl = self.output_table.item(row, OutputColumn.UTL).text()

            value_tuples.append((name, float(ltl), float(utl)))

        return value_tuples

    @QtCore.pyqtSlot(int)
    def _hardware_changed(self, _: int):
        self._update_test_names()

    def _update_cell(self, _selected, _deselected, table):
        if self.current_cell_info is not None:
            table.removeCellWidget(self.current_cell_info.row, self.current_cell_info.col)

        item = table.currentItem()
        self.current_cell_info = CellInfo(table.row(item), table.column(item))

    @QtCore.pyqtSlot(int)
    def _base_changed(self, _: int):
        self._update_test_names()

    def _update_test_names(self):
        self.parent.testName.clear()
        tests = self.parent.project_info.get_tests_from_db(self.hardware, self.base)
        test_names = [test.name for test in tests]
        self.parent.testName.addItems(test_names)
        self.parent.testName.setCurrentIndex(0)

        self._fill_input_parameter_table()
        self._fill_output_parameter_table()

    @property
    def input_table(self) -> QtWidgets.QTableWidget:
        return self.parent.inputParameter

    @property
    def output_table(self) -> QtWidgets.QTableWidget:
        return self.parent.outputParameter

    @property
    def hardware(self) -> str:
        return self.parent.hardware.currentText()

    @property
    def base(self) -> str:
        return self.parent.base.currentText()

    @property
    def test_name(self) -> str:
        return self.parent.testName.currentText()


class Widget(TabInterface):
    def __init__(self, parent: 'TestRunner'):
        super().__init__(parent)

    def setup_view(self):
        self.parent.testName.setEnabled(True)
        self.parent.hardware.setEnabled(True)
        self.parent.base.setEnabled(True)

        # Timing and Console are not supported yet
        self.parent.testTabs.setTabVisible(2, False)
        self.parent.testTabs.setTabVisible(3, False)

    def setup_callbacks(self):
        pass


class SetupCallback:
    def __init__(self, tabs: Tuple[TabInterface]):
        self.tabs = tabs

    def setup_callback(self):
        for tab in self.tabs:
            tab.setup_callbacks()


class Setup:
    def __init__(self, *tabs: List[TabInterface]):
        self.tabs = tabs

    def setup_view(self) -> SetupCallback:
        for tab in self.tabs:
            tab.setup_view()

        return SetupCallback(self.tabs)


class TestRunner(BaseDialog):
    def __init__(self, test_name: str, project_info: ProjectNavigation):
        super().__init__(__file__, project_info.parent)
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', Path(__file__).name.replace('.py', ''))))

        self.project_info = project_info
        self.test_name = test_name

        self.run_tab = RunTab(self)
        self.widget = Widget(self)

        setup = Setup(self.widget, self.run_tab)
        setup.setup_view().setup_callback()
