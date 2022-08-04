# -*- coding: utf-8 -*-
from abc import ABC, abstractclassmethod
from enum import IntEnum, unique
from pathlib import Path
import re
from typing import List, Tuple

from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog
from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.validation import valid_integer_regex, valid_float_regex
from ate_common.parameter import InputColumnKey, OutputColumnKey

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


class TabIds(IntEnum):
    Run = 0
    Shmoo = 1
    Timing = 2
    Console = 3


@unique
class InputColumn(IntEnum):
    Name = 0
    Min = 1
    Call = 2
    Max = 3
    Power = 4
    Unit = 5

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

        regx = QtCore.QRegExp(valid_integer_regex)
        integer_validator = QtGui.QRegExpValidator(regx, self.parent)
        self.parent.iteration.setValidator(integer_validator)

        self.parent.inputParameter.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.parent.outputParameter.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def setup_callbacks(self):
        self.parent.start.clicked.connect(self._start_execution)

    def _start_execution(self):
        # TODO: make sure this is the right interpretation
        # if int(self.parent.iteration.text()) == self.parent.maxIteration.value():
        #     ''' max iteration is reached '''

        configured_test = self._collect_data()
        file_path = Path(self.parent.project_info.project_directory).joinpath('runner', f'{self.test_name}_{self.hardware}_{self.base}_test_runner.py')
        self.parent.project_info.create_test_runner_main(file_path, configured_test)

        # TODO: emit signal to spyder

    def _fill_output_parameter_table(self):
        output_table = self.parent.outputParameter
        output_table.setRowCount(0)

        if not self.test_name:
            return

        data = self.parent.project_info.get_test(self.test_name, self.hardware, self.base)
        output_parameters = data.definition['output_parameters']

        output_table.cellChanged.connect(lambda row, col: self._call_value_updated(row, col))
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
            item.setFlags(QtCore.Qt.NoItemFlags)
            output_table.setItem(index, OutputColumn.Name, item)

            item = QtWidgets.QTableWidgetItem(str(value[OutputColumnKey.LSL()]))
            item.setFlags(QtCore.Qt.NoItemFlags)
            output_table.setItem(index, OutputColumn.LSL, item)

            item = QtWidgets.QTableWidgetItem(str(value[OutputColumnKey.LTL()]))
            output_table.setItem(index, OutputColumn.LTL, item)

            item = QtWidgets.QTableWidgetItem(str(value[OutputColumnKey.UTL()]))
            output_table.setItem(index, OutputColumn.UTL, item)

            item = QtWidgets.QTableWidgetItem(str(value[OutputColumnKey.USL()]))
            item.setFlags(QtCore.Qt.NoItemFlags)
            output_table.setItem(index, OutputColumn.USL, item)

            item = QtWidgets.QTableWidgetItem(str(value[OutputColumnKey.UNIT()]))
            item.setFlags(QtCore.Qt.NoItemFlags)
            output_table.setItem(index, OutputColumn.Unit, item)
        output_table.blockSignals(False)


    def _fill_input_parameter_table(self):
        input_table = self.parent.inputParameter
        input_table.setRowCount(0)

        if not self.test_name:
            return

        data = self.parent.project_info.get_test(self.test_name, self.hardware, self.base)
        input_parameters = data.definition['input_parameters']

        input_table.cellChanged.connect(lambda row, col: self._call_value_updated(row, col))
        input_table.cellDoubleClicked.connect(lambda row, col: self._call_value_double_clicked(
            input_table,
            row,
            col,
            float(self.parent.inputParameter.item(row, InputColumn.Min).text()),
            float(self.parent.inputParameter.item(row, InputColumn.Max).text()))
        )

        input_table.blockSignals(True)
        for index, (key, value) in enumerate(input_parameters.items()):
            input_table.insertRow(index)

            item = QtWidgets.QTableWidgetItem(key)
            item.setFlags(QtCore.Qt.NoItemFlags)
            input_table.setItem(index, InputColumn.Name, item)

            item = QtWidgets.QTableWidgetItem(str(value[InputColumnKey.MIN()]))
            item.setFlags(QtCore.Qt.NoItemFlags)
            input_table.setItem(index, InputColumn.Min, item)

            item = QtWidgets.QTableWidgetItem(str(value[InputColumnKey.MAX()]))
            item.setFlags(QtCore.Qt.NoItemFlags)
            input_table.setItem(index, InputColumn.Max, item)

            item = QtWidgets.QTableWidgetItem(str(value[InputColumnKey.DEFAULT()]))
            input_table.setItem(index, InputColumn.Call, item)

            item = QtWidgets.QTableWidgetItem(str(value[InputColumnKey.POWER()]))
            item.setFlags(QtCore.Qt.NoItemFlags)
            input_table.setItem(index, InputColumn.Power, item)

            item = QtWidgets.QTableWidgetItem(str(value[InputColumnKey.UNIT()]))
            item.setFlags(QtCore.Qt.NoItemFlags)
            input_table.setItem(index, InputColumn.Unit, item)
        input_table.blockSignals(False)

    @QtCore.pyqtSlot(int, int, float, float)
    def _call_value_double_clicked(self, table: QtWidgets.QTableWidget, row: int, col: int, min: float, max: float):
        item = table.item(row, col)
        initial_value = item.text()

        regx = QtCore.QRegExp(valid_float_regex)
        integer_validator = QtGui.QRegExpValidator(regx, self.parent)
        line = QtWidgets.QLineEdit(str(item.text()))
        line.setValidator(integer_validator)
        line.textChanged.connect(lambda text: self._call_value_changed(text, row, col, min, max))
        line.editingFinished.connect(lambda: self._call_value_edited(table, initial_value, row, col, min, max))

        line.blockSignals(True)
        line.setText(initial_value)
        line.blockSignals(False)

        table.setCellWidget(row, col, line)

    @QtCore.pyqtSlot(int, int)
    def _call_value_updated(self, row: int, col: int):
        if col != InputColumn.Call():
            return

    @QtCore.pyqtSlot(str, QtWidgets.QTableWidget, int, int, float, float)
    def _call_value_edited(self, table: QtWidgets.QTableWidget, initial_value: str, row: int, col: int, min: float, max: float):
        value = initial_value
        text = table.cellWidget(row, col).text()
        if self._validate_value(text, row, min, max):
            value = text

        table.removeCellWidget(row, col)
        item = QtWidgets.QTableWidgetItem(value)
        table.setItem(row, col, item)

    @QtCore.pyqtSlot(str, int, int, float, float)
    def _call_value_changed(self, text: str, row: int, col: int, min: float, max: float):
        if not self._validate_value(text, row, min, max):
            ''' set feedback '''
            print('not valid')

    def _validate_value(self, text: str, row: int, min: float, max: float) -> bool:
        print(text, max, min)
        self.parent.feedback.setText('')

        if not text or text in ['-', '+']:
            self.parent.feedback.setText('call value is empty')
            return False

        value = float(text)

        if value > max or value < min:
            self.parent.feedback.setText('call value is out of range')
            return False

        return True

    def _collect_data(self) -> dict:
        value_tuples = self._get_table_values()
        data = self.parent.project_info.get_test(self.test_name, self.hardware, self.base)
        input_parameters = data.definition['input_parameters']

        for name, value in value_tuples:
            input_parameters[name]['value'] = value

        return data

    def _get_table_values(self) -> List[Tuple[str, float]]:
        value_tuples = []
        for row in range(self.parent.inputParameter.rowCount()):
            name = self.input_table.item(row, InputColumn.Name).text()
            value = self.input_table.item(row, InputColumn.Call).text()

            value_tuples.append((name, float(value)))

        return value_tuples

    @QtCore.pyqtSlot(int)
    def _hardware_changed(self, _: int):
        self._update_test_names()

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
        # self.parent.testName.setText(self.parent.test_name)
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
    def __init__(self, *tabs: List[TabInterface]) -> None:
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
