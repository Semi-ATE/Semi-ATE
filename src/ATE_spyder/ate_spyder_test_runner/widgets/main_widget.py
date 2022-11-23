# -*- coding: utf-8 -*-
from abc import ABC, abstractclassmethod
from dataclasses import dataclass
from enum import IntEnum, unique
import json
import math
from pathlib import Path
from typing import Callable, List, Optional, Tuple
import qtawesome as qta

from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout
from qtpy.QtCore import Signal

from ate_spyder.widgets.actions_on.program.PatternTab import PatternTab
from ate_spyder.widgets.actions_on.program.SignalToChannelTab import SignalToChannelTab

from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.validation import valid_float_regex
from ate_common.parameter import InputColumnKey, OutputColumnKey

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import uic

from spyder.api.translations import get_translation
from spyder.api.widgets.main_widget import PluginMainWidget

# Localization
_ = get_translation("spyder")


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

    def clear(self):
        self.rows.clear()


@unique
class TabIds(IntEnum):
    Run = 0
    Shmoo = 1
    Timing = 2
    Console = 3


@unique
class InputColumn(IntEnum):
    Name = 0
    Shmoo = 1
    Min = 2
    Call = 3
    Step = 4
    Max = 5
    Power = 6
    Unit = 7

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


PATTERN_TAB_INDEX = 2


class RunTab(TabInterface):
    def __init__(self, plugin, parent: 'TestRunner', project_info: ProjectNavigation, test_name: str = ''):
        super().__init__(parent)
        self.plugin = plugin
        self.current_cell_info: Optional[CellInfo] = None
        self.input_table_data = InputTable()
        self.output_table_data = []
        self.project_info = project_info
        self.pattern_tab = PatternTab(parent, self.project_info, read_only=False)
        self.pattern_tab.setup()
        self.pattern_tab.add_pattern_items(test_name)
        self.signal_to_channel = SignalToChannelTab(parent, read_only=False)

    def setup_view(self):
        # the running tab doesn't support both Trends and Statistics in the current version
        self.parent.tabWidget.setTabVisible(3, False)
        self.parent.tabWidget.setTabVisible(4, False)

        self.parent.start.setToolTip('run without debugging')
        self.parent.debug.setToolTip('run in debug mode')

        self.parent.maxIteration.setEnabled(False)
        self.parent.maxIteration.setToolTip('no supported yet')

        available_hardwares = self.project_info.get_active_hardware_names()
        self.parent.hardware.blockSignals(True)
        self.parent.hardware.addItems(available_hardwares)
        self.parent.hardware.blockSignals(False)
        hw_index = self.parent.hardware.findText(self.project_info.active_hardware)
        self.parent.hardware.setCurrentIndex(hw_index)

        self._update_hardware(self.project_info.active_hardware)
        self._update_base(self.project_info.active_base)

        # the hardware and base setup shall be inherited from the Semi-ATE Toolbar Plugin
        # uncomment these two lines to setup independently
        self.parent.hardware.setEnabled(False)
        self.parent.base.setEnabled(False)

        self.parent.feedback.setStyleSheet('color: orange')

        self.parent.inputParameter.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.parent.outputParameter.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        self.parent.inputParameter.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.parent.outputParameter.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.parent.inputParameter.selectionModel().selectionChanged.connect(lambda selected, deselected: self._update_cell(selected, deselected, self.parent.inputParameter))
        self.parent.outputParameter.selectionModel().selectionChanged.connect(lambda selected, deselected: self._update_cell(selected, deselected, self.parent.outputParameter))

        self.parent.patternLayout.addTab(self.signal_to_channel, 'Signal to Channel')
        self.signal_to_channel.setup()

        # the manual generation of the signal to channel yaml file is only available for the
        # test runner as it is generated differently than a test flow
        self.signal_to_channel.generate_button.setVisible(True)
        self.signal_to_channel.generate_button.setIcon(qta.icon('mdi.file-cog-outline', color='orange'))
        self.signal_to_channel.generate_button.clicked.connect(self._generate_signal_to_channel_yaml_file)

    def _generate_signal_to_channel_yaml_file(self):
        self.feedback.setText('')
        self.signal_to_channel.generate_yml_file(self.test_runner_sig_to_channel_file_path)

    def setup_callbacks(self):
        self.parent.start.clicked.connect(self._start_execution)
        self.parent.start.setIcon(qta.icon('mdi.play', color='orange'))

        self.parent.debug.clicked.connect(self._start_execution_in_debug_mode)
        self.parent.debug.setIcon(qta.icon('mdi.play-circle', color='orange'))

        self.parent.compile.clicked.connect(self._compile_patterns)

        self.parent.compile.setIcon(qta.icon('mdi.file-cog-outline', color='orange'))
        self.parent.testName.currentIndexChanged.connect(self._fill_test_config)
        self.parent.testName.setSizeAdjustPolicy(QtWidgets.QComboBox.AdjustToContents)

        self.parent.base.currentIndexChanged.connect(lambda index: self._base_changed(index))
        self.parent.hardware.currentIndexChanged.connect(lambda index: self._hardware_changed(index))

        self.semi_ate_main_widget.select_hardware.connect(self._update_hardware)
        self.semi_ate_main_widget.select_base.connect(self._update_base)

        self.parent.stop_button.clicked.connect(self._stop_debugging)
        self.parent.stop_button.setIcon(qta.icon('mdi.square', color='orange'))

        self.parent.inputParameter.itemClicked.connect(self._shmoo_state_update)
        self.parent.inputParameter.cellDoubleClicked.connect(lambda row, col: self._call_value_double_clicked(
            self.parent.inputParameter,
            row,
            col,
            float(self.parent.inputParameter.item(row, InputColumn.Min).text()),
            float(self.parent.inputParameter.item(row, InputColumn.Max).text()))
        )

        self.parent.outputParameter.cellDoubleClicked.connect(lambda row, col: self._call_value_double_clicked(
            self.parent.outputParameter,
            row,
            col,
            float(self.parent.outputParameter.item(row, OutputColumn.LSL).text()),
            float(self.parent.outputParameter.item(row, OutputColumn.USL).text()))
        )

        # receive any changes happens inside the test tree
        self.plugin.sig_test_tree_update.connect(self._update_view)

    def _update_view(self):
        current_test = self.parent.testName.currentText()
        self._update_test_names()

        # get test index
        index = self.parent.testName.findText(current_test)
        if index is None:
            return

        self.parent.testName.setCurrentIndex(index)

    def _stop_debugging(self):
        # stop button is always active as we cannot track the state of the process
        # the problem currently is the ability to stop a process from different places
        # in spyder IDE
        self.plugin.sig_stop_debugging.emit()

    def _update_hardware(self, hw: str):
        self.parent.hardware.blockSignals(True)
        self.parent.hardware.clear()
        available_hardwares = self.project_info.get_active_hardware_names()
        self.parent.hardware.addItems(available_hardwares)
        hw_index = self.parent.hardware.findText(hw)
        self.parent.hardware.setCurrentIndex(hw_index)
        self.parent.hardware.blockSignals(False)

        self._hardware_changed(hw_index)

    def _update_base(self, base: str):
        self.parent.base.blockSignals(True)
        base_index = self.parent.base.findText(base)
        self.parent.base.setCurrentIndex(base_index)
        self.parent.base.blockSignals(False)

        self._base_changed(base_index)

    def _compile_patterns(self):
        self.feedback.setText('')

        if not self.test_runner_sig_to_channel_file_path.exists():
            self.feedback.setText('signal to channel yaml file is required for the compilation, generate it first!')
            self.parent.patternLayout.setCurrentIndex(1)
            return

        patterns = self.pattern_tab.collect_pattern()

        pattern_path_list = set([pattern[1] for pattern in patterns[self.test_name]])

        self.project_info.compile_stil_patterns(
            [str(Path(self.project_info.project_directory).joinpath(pattern_rel_path)) for pattern_rel_path in pattern_path_list],
            str(self.test_runner_sig_to_channel_file_path)
        )

    def _setup_before_run(self):
        configured_test = self._collect_data()

        self.project_info.create_test_runner_main(self.test_runner_path, configured_test)

        # send signal to spyder to open the generated file inside the editor
        self.plugin.sig_edit_goto_requested.emit(str(self.test_runner_path), 1, "")

    def _start_execution(self):
        self._setup_before_run()
        self.plugin.sig_run_cell.emit()

    def _start_execution_in_debug_mode(self):
        self._setup_before_run()
        self.plugin.sig_debug_cell.emit()

    @property
    def test_runner_file_name(self) -> str:
        return f'{self.test_name}_{self.hardware}_{self.base}_test_runner.py'

    @property
    def test_runner_path(self) -> Path:
        return Path(self.project_info.project_directory).joinpath('runner', self.test_runner_file_name)

    @property
    def test_runner_config_file_name(self) -> str:
        return f'{self.test_name}_{self.hardware}_{self.base}_test_runner_config.json'

    @property
    def test_runner_config_path(self) -> Path:
        return Path(self.project_info.project_directory).joinpath('runner', self.test_runner_config_file_name)

    @property
    def test_runner_sig_to_channel_file_path(self) -> Path:
        return Path(self.project_info.project_directory).joinpath('runner', f'{self.test_name}_{self.hardware}_{self.base}_test_runner.yaml')

    @property
    def semi_ate_main_widget(self) -> QtWidgets.QWidget:
        return self.project_info.parent

    @property
    def feedback(self) -> QtWidgets.QLabel:
        return self.parent.feedback

    def _fill_output_parameter_table(self):
        output_table = self.parent.outputParameter
        # reset table
        output_table.setRowCount(0)

        if not self.test_name:
            return

        data = self.project_info.get_test(self.test_name, self.hardware, self.base)
        output_parameters = data.definition['output_parameters']

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
        # reset table
        input_table.setRowCount(0)
        self.input_table_data.clear()

        if not self.test_name:
            return

        data = self.project_info.get_test(self.test_name, self.hardware, self.base)
        input_parameters = data.definition['input_parameters']

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
                item.setFlags(QtCore.Qt.ItemIsSelectable)

            item = QtWidgets.QTableWidgetItem(str(value[InputColumnKey.MIN()]))
            item.setFlags(QtCore.Qt.ItemIsSelectable)
            input_table.setItem(index, InputColumn.Min, item)

            item = QtWidgets.QTableWidgetItem(str(value[InputColumnKey.MAX()]))
            item.setFlags(QtCore.Qt.ItemIsSelectable)
            input_table.setItem(index, InputColumn.Max, item)

            item = QtWidgets.QTableWidgetItem(str(value[InputColumnKey.DEFAULT()]))
            item.setToolTip('call is only enabled when shmoo is not set')
            input_table.setItem(index, InputColumn.Call, item)

            item = QtWidgets.QTableWidgetItem('0.0')
            input_table.setItem(index, InputColumn.Step, item)
            item.setToolTip('step is only enabled when shmoo is set')

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

        # any invalid parameter configuration will be automatically rejected
        # and the default value is set
        self.parent.start.setEnabled(True)
        self.parent.debug.setEnabled(True)
        self.parent.feedback.setText('')

    @QtCore.pyqtSlot(str, int, int, float, float)
    def _call_value_changed(self, text: str, row: int, col: int, min: float, max: float, validate_callback: Callable):
        if validate_callback(text, row, col, min, max):
            self.parent.start.setEnabled(True)
            self.parent.debug.setEnabled(True)
        else:
            self.parent.start.setEnabled(False)
            self.parent.debug.setEnabled(False)

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

        data = self.project_info.get_test(self.test_name, self.hardware, self.base)
        input_parameters = data.definition['input_parameters']

        output_parameters = data.definition['output_parameters']
        output_value_tuples = self._get_output_table_values()

        for name, value, step, is_shmoo in input_value_tuples:
            input_parameters[name]['value'] = value
            input_parameters[name]['step'] = step
            input_parameters[name]['is_shmoo'] = is_shmoo
            input_parameters[name]['type'] = 'static'

        for name, ltl, utl in output_value_tuples:
            output_parameters[name]['ltl'] = ltl
            output_parameters[name]['utl'] = utl

        # patterns config is not part of the test configuration but is needed to store
        # test specific configuration that could be loaded at any time
        data.definition['patterns'] = self.pattern_tab.collect_pattern()

        return data

    def _get_input_table_values(self) -> List[Tuple[str, float]]:
        value_tuples = []
        for row in range(self.input_table.rowCount()):
            name = self.input_table.item(row, InputColumn.Name).text()
            value = self.input_table.item(row, InputColumn.Call).text()
            step = self.input_table.item(row, InputColumn.Step).text()
            is_shmoo = True if self.input_table.item(row, InputColumn.Shmoo).checkState() == QtCore.Qt.Checked else False

            value_tuples.append((name, float(value), float(step), is_shmoo))

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

    def project_changed(self):
        self._update_test_names()

    def _update_test_names(self):
        self.parent.testName.clear()
        tests = self.project_info.get_tests_from_db(self.hardware, self.base)
        test_names = [test.name for test in tests]
        self.parent.testName.addItems(test_names)
        self.parent.testName.setCurrentIndex(0)

        self.parent.setEnabled(True)

        if not self.parent.testName.currentText() or not test_names:
            self.pattern_tab.pattern_table.setRowCount(0)
            self.signal_to_channel.signal_to_channel_table.setRowCount(0)
            self.parent.setEnabled(False)
            return

        self._fill_test_config()

    def _fill_test_config(self):
        self._fill_input_parameter_table()
        self._fill_output_parameter_table()

        # reset table to update the new content
        self.pattern_tab.pattern_table.setRowCount(0)
        if self.test_runner_config_path.exists():
            self._fill_with_custom_values()
        else:
            self.pattern_tab.add_pattern_items(self.test_name)

        # reset table to update the new content
        self.signal_to_channel.signal_to_channel_table.setRowCount(0)
        if self.test_runner_sig_to_channel_file_path.exists():
            self.signal_to_channel.load_table(self.test_runner_sig_to_channel_file_path)

        # check if pattern list is empty
        # if so, disable pattern tab
        if self.pattern_tab.pattern_table.rowCount() == 0:
            self.parent.tabWidget.setTabEnabled(PATTERN_TAB_INDEX, False)
            self.parent.tabWidget.setTabToolTip(PATTERN_TAB_INDEX, 'pattern list is empty')
        else:
            self.parent.tabWidget.setTabEnabled(PATTERN_TAB_INDEX, True)
            self.parent.tabWidget.setTabToolTip(PATTERN_TAB_INDEX, '')

        self._validate_pattern_table()

    def _validate_pattern_table(self):
        if not self.pattern_tab.collect_pattern():
            self.parent.compile.setEnabled(False)
            self.parent.compile.setToolTip('no pattern files available')
        else:
            self.parent.compile.setEnabled(True)
            self.parent.compile.setToolTip('')

    def _fill_with_custom_values(self):
        if not self.test_name:
            return

        with open(self.test_runner_config_path, 'r') as f:
            configuration = json.load(f)

            for row in range(self.input_table.rowCount()):
                name_item = self.input_table.item(row, InputColumn.Name)
                if not configuration['input_parameters'].get(name_item.text()):
                    # skip this parameter as it's probably newly created while updating the current test
                    continue
                value = configuration['input_parameters'][name_item.text()]['value']
                step = configuration['input_parameters'][name_item.text()]['step']
                is_shmoo = configuration['input_parameters'][name_item.text()]['is_shmoo']
                self.input_table.item(row, InputColumn.Call).setText(str(value))
                self.input_table.item(row, InputColumn.Step).setText(str(step))

                shmoo_item = self.input_table.item(row, InputColumn.Shmoo)
                shmoo_item.setCheckState(QtCore.Qt.Checked if is_shmoo else QtCore.Qt.Unchecked)
                self._update_row(shmoo_item.row(), shmoo_item.checkState() == QtCore.Qt.Checked)

            for row in range(self.output_table.rowCount()):
                name_item = self.output_table.item(row, OutputColumn.Name)
                if not configuration['output_parameters'].get(name_item.text()):
                    # skip this parameter as it's probably newly created while updating the current test
                    continue
                ltl_value = configuration['output_parameters'][name_item.text()]['ltl']
                utl_value = configuration['output_parameters'][name_item.text()]['utl']
                self.output_table.item(row, OutputColumn.LTL).setText(str(ltl_value))
                self.output_table.item(row, OutputColumn.UTL).setText(str(utl_value))

            self.pattern_tab.fill_pattern_table([self.test_name], configuration['patterns'])

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


class TestRunnerDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(__file__.replace('.py', '.ui'), self)

    def reject(self):
        pass

    def _verify(self):
        pass


# Test Runner Plugin main widget
class TestRunner(PluginMainWidget):
    sig_edit_goto_requested = Signal(str, int, str)
    sig_run_cell = Signal()
    sig_debug_cell = Signal()
    sig_stop_debugging = Signal()
    sig_test_tree_update = Signal()

    def __init__(self, name, plugin, parent=None):
        super().__init__(name, plugin, parent)
        self.setEnabled(False)

    def setup(self):
        # TODO: use a signal to setup the test name from a tree option
        self.test_name = None

        self.test_runner_widget = TestRunnerDialog()

        layout = QHBoxLayout()
        layout.addWidget(self.test_runner_widget)
        self.setLayout(layout)

    def setup_widget(self, project_info: ProjectNavigation):
        # since Test Runner Plugin depends on the Semi-ATE Main Plugin
        # the widget setup could only be done is this stage after
        # the project initialization is done
        self.project_info = project_info

        self.setEnabled(True)
        self.run_tab = RunTab(self, self.test_runner_widget, self.project_info)
        self.widget = Widget(self.test_runner_widget)

        setup = Setup(self.widget, self.run_tab)
        setup.setup_view().setup_callback()

    def teardown(self):
        self.setEnabled(False)

    def get_title(self):
        return _('Test Runner')

    def update_actions(self):
        pass
