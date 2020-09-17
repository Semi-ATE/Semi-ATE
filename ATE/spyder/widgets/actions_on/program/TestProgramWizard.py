import copy
import os
import re
from enum import Enum, IntEnum

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from ATE.spyder.widgets.actions_on.utils.BaseDialog import BaseDialog

MAX_SBIN_NUM = 65535
ORANGE = (255, 127, 39)
RED = (237, 28, 36)
GREEN = (34, 117, 76)
ORANGE_LABEL = 'color: orange'
GRADES = [("Grade_A", 1),
          ("Grade_B", 2),
          ("Grade_C", 3),
          ("Grade_D", 4),
          ("Grade_E", 5),
          ("Grade_F", 6),
          ("Grade_G", 7),
          ("Grade_H", 8),
          ("Grade_I", 9)]


class ParameterState(IntEnum):
    Invalid = 0
    Valid = 1
    Changed = 2
    New = 3

    def __call__(self):
        return self.value


class BinningColumns(Enum):
    Grade = 1
    Result = 2
    Context = 3

    def __call__(self):
        return self.value


class Result(Enum):
    Fail = ('FAIL', 0)
    Pass = ('PASS', 1)

    def __call__(self):
        return self.value


class Tabs(Enum):
    Sequence = 'Sequence'
    Binning = 'Binning'
    PingPong = 'Ping_Pong'
    Execution = 'Execution'

    def __call__(self):
        return self.value


class Action(Enum):
    Up = 'Up'
    Down = 'Down'
    Left = 'Left'
    Right = 'Right'

    def __call__(self):
        return self.value


class Range(Enum):
    In_Range = 0
    Out_Of_Range = 1
    Limited_Range = 2

    def __call__(self):
        return self.value


# ToDo: Add numeric type! These strings are display values that
# are bound to change, which would break all projects.
class Sequencer(Enum):
    Static = 'Fixed Temperature'  # 'Static'
    Dynamic = 'Variable Temperature'  # 'Dynamic'

    def __call__(self):
        return self.value


class ErrorMessage(Enum):
    NotSelected = 'no test is selected'
    InvalidInput = 'invalid input'
    InvalidTemperature = 'invalid temperature value(s)'
    OutOfRange = 'value out of range'
    TargetMissed = 'target is missing'
    UsertextMissed = 'usertext is missing'
    TemperatureMissed = 'temperature is missing'
    NoTestSelected = 'no test was selected'
    MultipleTestSelection = 'multiple tests are selected'
    EmtpyTestList = 'no test was choosen'
    NoValidTestRange = 'test range is not valid'
    TemperatureNotValidated = 'temperature(s) could not be validated'
    SbinInvalid = 'sbin is invalid'
    TestInvalid = 'test(s) is(are) invalid'
    TestDescriptionNotUnique = 'test description must be unique'

    def __call__(self):
        return self.value


DEFAULT_TEMPERATURE = '25'


class TestProgramWizard(BaseDialog):
    def __init__(self, project_info, owner, parent=None, read_only=False, enable_edit=True, prog_name=''):
        super().__init__(__file__, project_info.parent)
        self.project_info = project_info
        self.owner = owner

        self.available_tests = []
        self.selected_tests = []
        self.read_only = read_only
        self.enable_edit = enable_edit
        self.prog_name = prog_name

        self.current_selected_test = None
        self.result = None
        self._is_dynamic_range_valid = True
        self.bin_counter = 10
        self.cell_size = 0
        self.is_valid_temperature = True

        self._setup()
        self._view()
        self._connect_event_handler()

    def _setup(self):
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))
        self.setWindowTitle("Test Program Configuration")

        # TODO: do we need tool tips
        # self.RightButton.setToolTip("select")

        self._set_icon(self.testAdd, 'arrow-right')
        self._set_icon(self.testRemove, 'arrow-left')
        self._set_icon(self.moveTestDown, 'arrow-down')
        self._set_icon(self.moveTestUp, 'arrow-up')

        self._resize_table(self.parametersInput, 50)
        self._resize_table(self.parametersOutput, 50)

        from ATE.spyder.widgets.validation import valid_float_regex
        regx = QtCore.QRegExp(valid_float_regex)
        self.positive_float_validator = QtGui.QRegExpValidator(regx, self)

        from ATE.spyder.widgets.validation import valid_integer_regex
        regx = QtCore.QRegExp(valid_integer_regex)
        integer_validator = QtGui.QRegExpValidator(regx, self)
        self.temperature.setValidator(integer_validator)

        self.existing_programs = self.project_info.get_programs_for_owner(self.owner)

        self.selectedTests.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.selectedTests.horizontalHeader().setStretchLastSection(True)
        self.selectedTests.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        self.selectedTests.itemDoubleClicked.connect(self._double_click_handler)
        self.selectedTests.itemClicked.connect(self._test_selected)
        self.selectedTests.itemSelectionChanged.connect(self._table_clicked)

        self.tabWidget.currentChanged.connect(self._tab_changed)
        self.binning_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.binning_tree.itemClicked.connect(self._binning_tree_item_clicked)
        self.binning_tree.customContextMenuRequested.connect(self._context_menu)
        self.binning_tree.itemChanged.connect(self._binning_item_changed)

    def _connect_event_handler(self):
        self.availableTests.itemClicked.connect(self._available_test_selected)
        self.availableTests.itemSelectionChanged.connect(self._available_table_clicked)

        self.parametersInput.itemDoubleClicked.connect(self._double_click_handler_input_param)
        self.parametersOutput.itemDoubleClicked.connect(self._double_click_handler_output_param)
        self.parametersInput.itemClicked.connect(self._input_param_table_clicked)
        self.parametersOutput.itemClicked.connect(self._output_param_table_clicked)

        self.testAdd.clicked.connect(lambda: self._move_test(Action.Right()))
        self.moveTestDown.clicked.connect(lambda: self._move_test(Action.Down()))
        self.moveTestUp.clicked.connect(lambda: self._move_test(Action.Up()))
        self.testRemove.clicked.connect(lambda: self._move_test(Action.Left()))

        self.hardware.currentIndexChanged.connect(self._hardware_changed)
        self.base.currentIndexChanged.connect(self._base_changed)
        self.usertext.textChanged.connect(self._usertext_changed)
        self.target.currentIndexChanged.connect(self._target_changed)

        self.sequencerType.currentIndexChanged.connect(self._sequencer_type_changed)
        self.temperature.textChanged.connect(self._verify_temperature)
        from ATE.spyder.widgets.validation import valid_user_text_name_regex
        user_text_reg_ex = QtCore.QRegExp(valid_user_text_name_regex)
        user_text_name_validator = QtGui.QRegExpValidator(user_text_reg_ex, self)
        self.usertext.setValidator(user_text_name_validator)

        self.OKButton.clicked.connect(self._save_configuration)
        self.CancelButton.clicked.connect(self._cancel)

    def _view(self):
        self.existing_hardwares = self.project_info.get_active_hardware_names()
        self.hardware.addItems(self.existing_hardwares)
        current_hw_index = self.hardware.findText(self.project_info.active_hardware, QtCore.Qt.MatchExactly)
        self.hardware.setCurrentIndex(current_hw_index)

        self.hardware.setEnabled(False)
        self.target.setEnabled(False)
        self.base.setEnabled(False)

        current_base_index = self.base.findText(self.project_info.active_base, QtCore.Qt.MatchExactly)
        self.base.setCurrentIndex(current_base_index)

        self._update_target()

        self.sequencerType.addItems([Sequencer.Static(), Sequencer.Dynamic()])
        self.temperature.setText(DEFAULT_TEMPERATURE)

        self._update_test_list()
        self.Feedback.setText('')
        self.Feedback.setStyleSheet(ORANGE_LABEL)
        self.usertext_feedback.setStyleSheet(ORANGE_LABEL)
        self.temperature_feedback.setStyleSheet(ORANGE_LABEL)
        self.target_feedback.setStyleSheet(ORANGE_LABEL)
        self.usertext_feedback.setStyleSheet(ORANGE_LABEL)
        self._verify()
        self._verify_tests()

    @staticmethod
    def _update_binning_tree(text, item, pos):
        item.setText(pos, text)

    @staticmethod
    def _is_bin_valid(text):
        try:
            sbin = int(text)
        except Exception:
            return False

        return sbin < MAX_SBIN_NUM

    @staticmethod
    def _generate_binning_structure(bin, result, context):
        return {'Binning': {'bin': bin, 'result': result, 'context': context}}

    @staticmethod
    def _does_test_changed(test_desc, item_changed_text):
        desc_len = len(test_desc)
        return item_changed_text[:desc_len] == test_desc

    def _get_binning_structure(self, item):
        for test in self.selected_tests:
            if not self._does_test_changed(test['description'], item.text(0)):
                continue

            for key, value in test['output_parameters'].items():
                if key not in item.text(0):
                    continue

                return value['Binning']

        return None

    @staticmethod
    def _get_binning_params(item):
        return (item.text(1), item.text(2), item.text(3))

    def _update_binning_field(self, item):
        params = self._get_binning_params(item)
        for test in self.selected_tests:
            if not self._does_test_changed(test['description'], item.text(0)):
                continue

            for key, value in test['output_parameters'].items():
                if key not in item.text(0):
                    continue

                value['Binning']['bin'] = params[0]
                value['Binning']['result'] = Result.Pass()[1] if params[1] == Result.Pass()[0] else Result.Fail()[1]
                value['Binning']['context'] = params[2]

    def _update_binning_table(self, item):
        binning = self._get_binning_structure(item)
        self._update_feedback('')

        if not self._is_bin_valid(item.text(1)):
            self._update_binning_tree(binning['bin'], item, BinningColumns.Grade())
            self._update_feedback(ErrorMessage.SbinInvalid())
            return

        if not self._is_pass(item.text(1)):
            self._update_binning_tree(Result.Fail()[0], item, BinningColumns.Result())
        else:
            self._update_binning_tree(Result.Pass()[0], item, BinningColumns.Result())

        self._update_binning_field(item)

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem)
    def _binning_item_changed(self, item):
        if not item.text(1):
            return

        self._update_binning_table(item)

    @staticmethod
    def _generate_menu():
        menu = QtWidgets.QMenu()
        for grade in GRADES:
            menu.addAction(grade[0])

        return menu

    def _get_selected_menu_label(self, point):
        menu = self._generate_menu()
        action = menu.exec_(self.binning_tree.mapToGlobal(point))

        if action is None:
            return None

        return action.text()

    def _get_current_column(self):
        return self.binning_tree.currentColumn()

    def _is_binning_child_item(self):
        return self.binning_tree.currentItem().parent() is not None

    def _is_menu_supported(self):
        return (self._get_current_column() == BinningColumns.Grade()
                and self._is_binning_child_item())

    @staticmethod
    def _is_pass(text):
        grade = int(text)
        return grade >= 1 and grade <= 9

    @staticmethod
    def _get_sbin(text):
        for elem in GRADES:
            if elem[0] == text:
                return str(elem[1])

        return text

    @QtCore.pyqtSlot(QtCore.QPoint)
    def _context_menu(self, point):
        if not self._is_menu_supported():
            return

        label = self._get_selected_menu_label(point)
        if label is None:
            return None

        item = self.binning_tree.itemAt(point)
        self._update_binning_tree(self._get_sbin(label), item, BinningColumns.Grade())

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def _binning_tree_item_clicked(self, item, column):
        if not self._is_binning_child_item():
            return

        if column == BinningColumns.Grade()\
           or column == BinningColumns.Context():
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        else:
            item.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

    def _tab_changed(self, index):
        tab_name = self.tabWidget.tabText(index)
        self.binning_tree.clear()
        if tab_name == Tabs.Binning():
            self._populate_binning_tree()

    def _table_clicked(self):
        if len(self.selectedTests.selectedItems()):
            return

        self.parametersInput.setRowCount(0)
        self.parametersOutput.setRowCount(0)
        self._update_test_list_table()

    def _double_click_handler(self, item):
        if item.column() == 0:
            return

        from ATE.spyder.widgets.validation import valid_test_name_description_regex
        regx = QtCore.QRegExp(valid_test_name_description_regex)
        name_validator = QtGui.QRegExpValidator(regx, self)

        self._create_checkable_cell(item.text(), self.selectedTests, "description", item, name_validator)

    @QtCore.pyqtSlot(QtWidgets.QTableWidgetItem)
    def _input_param_table_clicked(self, item):
        if item.column() in (0, 1, 3, 4, 5) or self.read_only:
            return

        param_name = self.parametersInput.item(item.row(), 0).text()
        flag = self._get_appropriate_item_flag_for_table(param_name, 'input_parameters')
        item.setFlags(flag)

    @QtCore.pyqtSlot(QtWidgets.QTableWidgetItem)
    def _output_param_table_clicked(self, item):
        if item.column() in (0, 1, 4, 5, 6) or self.read_only:
            return

        param_name = self.parametersOutput.item(item.row(), 0).text()
        flag = self._get_appropriate_item_flag_for_table(param_name, 'output_parameters')
        item.setFlags(flag)

    def _get_appropriate_item_flag_for_table(self, param_name, type):
        for test in self.selected_tests:
            for param, val in test[type].items():
                if param != param_name:
                    continue

                if val['validity'] == ParameterState.Invalid():
                    return QtCore.Qt.NoItemFlags

                return QtCore.Qt.ItemIsEnabled

    @staticmethod
    def _set_icon(button, icon_type):
        from ATE.spyder.widgets.actions_on.program.Actions import ACTIONS
        icon = QtGui.QIcon(ACTIONS[icon_type][0])
        button.setIcon(icon)
        button.setText("")

    @staticmethod
    def _resize_table(table, col_size):
        for c in range(table.columnCount()):
            table.setColumnWidth(c, col_size)

        table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

    def _update_target(self):
        self.target.blockSignals(True)
        self.target.clear()
        if self.base.currentText() == 'PR':
            existing_targets = self.project_info.get_active_die_names_for_hardware(self.hardware.currentText())
        else:
            existing_targets = self.project_info.get_active_device_names_for_hardware(self.hardware.currentText())

        self.target.addItems(existing_targets)
        current_target_index = self.target.findText(self.project_info.active_target, QtCore.Qt.MatchExactly)
        # If we cannot find the active target, we just use the first
        # available target.
        if (current_target_index < 0):
            current_target_index = 0
        self.target.setCurrentIndex(current_target_index)
        self.target.blockSignals(False)

    @QtCore.pyqtSlot(str)
    def _usertext_changed(self, text):
        self._verify()

    @QtCore.pyqtSlot()
    def _hardware_changed(self):
        self._update_target()
        self._verify()

    @QtCore.pyqtSlot()
    def _base_changed(self):
        self._update_target()
        self._verify()

    @QtCore.pyqtSlot()
    def _target_changed(self):
        self._verify()

    @QtCore.pyqtSlot(int)
    def _sequencer_type_changed(self, index):
        if self.sequencerType.itemText(index) == Sequencer.Static():
            from ATE.spyder.widgets.validation import valid_integer_regex
            regx = QtCore.QRegExp(valid_integer_regex)
            integer_validator = QtGui.QRegExpValidator(regx, self)
            self.temperature.setValidator(integer_validator)
            self.temperature.setText(DEFAULT_TEMPERATURE)
            return

        from ATE.spyder.widgets.validation import valid_temp_sequence_regex
        regx = QtCore.QRegExp(valid_temp_sequence_regex)
        integer_validator = QtGui.QRegExpValidator(regx, self)
        self.temperature.setValidator(integer_validator)

        self.temperature.setText(f'{DEFAULT_TEMPERATURE},')

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def _available_test_selected(self, item):
        self.parametersInput.setEnabled(False)
        self.parametersOutput.setEnabled(False)

        self._update_tables_with_standard_values(item.text(), item.text())

    @QtCore.pyqtSlot()
    def _available_table_clicked(self):
        self.parametersInput.setEnabled(False)
        self.parametersOutput.setEnabled(False)
        self.parametersInput.setRowCount(0)
        self.parametersOutput.setRowCount(0)

    @QtCore.pyqtSlot(QtWidgets.QTableWidgetItem)
    def _test_selected(self, item):
        self.parametersInput.setEnabled(True)
        self.parametersOutput.setEnabled(True)

        row = item.row()
        self.selectedTests.item(row, 0).setSelected(True)
        self.selectedTests.item(row, 1).setSelected(True)

        self.selected_cell = item

        self._handle_selection(self.availableTests, item)

    def _handle_selection(self, test_list, item):
        test_name = self.selectedTests.item(item.row(), 0).text()
        test_instance_name = self.selectedTests.item(item.row(), 1).text()
        self._deselect_items(test_list)
        self._update_tables_with_custom_parameters(test_name, test_instance_name)

    def _deselect_items(self, selected_list):
        for index in range(selected_list.count()):
            selected_list.item(index).setSelected(False)

    def _deselect_table_items(self):
        for row in range(self.selectedTests.rowCount()):
            for col in range(self.selectedTests.columnCount()):
                self.selectedTests.item(row, col).setSelected(False)

    @staticmethod
    def _extract_base_test_name(indexed_test_name):
        return indexed_test_name.split('_')[0]

    def _update_tables_with_standard_values(self, test_name, test_instance_name):
        self.input_parameters, self.output_parameters = self._get_in_output_paramters(test_name)
        for test in self.available_tests:
            if test['description'] != test_instance_name:
                continue

            for parameter in test['input_parameters'].items():
                param = copy.deepcopy(parameter)
                self.input_parameters[param[0]].update({'Default': {'Value': self.input_parameters[param[0]]['Default'],
                                                                    'validity': ParameterState.Valid()}})
                self.input_parameters[param[0]].update({'is_valid': ParameterState.Valid()})

            for param in test['output_parameters'].items():
                self.output_parameters[param[0]].update({'is_valid': ParameterState.Valid()})

            break

        self._fill_input_parameter_table()
        self._fill_output_parameter_table()

    def _get_in_output_paramters(self, test_name):
        name = self._extract_base_test_name(test_name)
        self.current_selected_test = name
        parameters = self._get_test_parameters(name)
        self._add_is_valid_flag(parameters)

        return parameters['input_parameters'], parameters['output_parameters']

    @staticmethod
    def _add_is_valid_flag(parameters):
        for _, parameter in parameters['input_parameters'].items():
            parameter.update({'is_valid': ParameterState.New()})

        for _, parameter in parameters['output_parameters'].items():
            parameter.update({'is_valid': ParameterState.New()})

    def _update_tables_with_custom_parameters(self, test_name, test_instance_name):
        self.input_parameters, self.output_parameters = self._get_in_output_paramters(test_name)

        # update table content if content changed
        for test in self.selected_tests:
            name = test['description']
            if name != test_instance_name:
                continue

            self._update_input_parameters(test['input_parameters'])
            self._update_output_parameters(test['output_parameters'])
            break

        self._fill_input_parameter_table()
        self._fill_output_parameter_table()

    def _update_input_parameters(self, input_parameters):
        for parameter in input_parameters.items():
            param = copy.deepcopy(parameter)
            if not self.input_parameters.get(param[0]):
                self.input_parameters.update({param[0]: self._generate_invalid_input_parameter(param[1])})
                continue

            self.input_parameters[param[0]]['Default'] = param[1]
            self.input_parameters[param[0]].update({'is_valid': param[1]['validity']})

    def _update_output_parameters(self, output_parameters):
        for parameter in output_parameters.items():
            param = copy.deepcopy(parameter)
            if not self.output_parameters.get(param[0]):
                self.output_parameters.update({param[0]: self._generate_invalid_output_parameter(param[1]['LTL'], param[1]['UTL'])})
                continue

            self.output_parameters[param[0]]['LTL'], self.output_parameters[param[0]]['UTL'] = \
                output_parameters[param[0]]['LTL'], \
                output_parameters[param[0]]['UTL']

            self.output_parameters[param[0]].update({'is_valid': param[1]['validity']})

    @staticmethod
    def _generate_invalid_input_parameter(temp):
        return {'Shmoo': True, 'Min': 'nan', 'Default': temp, 'Max': 'nan', '10ᵡ': '', 'Unit': 'nan', 'fmt': '.0f', 'is_valid': ParameterState.Invalid()}

    @staticmethod
    def _generate_invalid_output_parameter(ltl, utl):
        return {'LSL': 'nan', 'LTL': ltl, 'Nom': 0.0, 'UTL': utl, 'USL': 'nan', '10ᵡ': '', 'Unit': 'nan', 'fmt': '.0f', 'is_valid': ParameterState.Invalid()}

    # ToDo: Improve Exception handling, as all exceptions
    #       thrown in handlers will be discarded and replaced
    #       by "action not recognized"
    @QtCore.pyqtSlot(str)
    def _move_test(self, action):
        try:
            {Action.Up(): lambda: self._move_up(),
             Action.Down(): lambda: self._move_down(),
             Action.Left(): lambda: self._remove_from_testprogram(),
             Action.Right(): lambda: self._add_to_testprogram(),
             }[action]()
        except Exception:
            raise (f'action "{action}" not recognized')

    # Naming: Name is confusing
    def _is_selected(self, test_list):
        selected_items = len(test_list.selectedItems())
        if not selected_items:
            return False
        return True

    @QtCore.pyqtSlot()
    def _move_up(self):
        selected = self.selectedTests.selectedItems()
        if not len(selected):
            self._update_feedback(ErrorMessage.NotSelected())
            return

        row = selected[0].row()
        if row == 0:
            return

        index = row
        self._fit_test_sequence(index, index - 1)

        self._update_test_list_table()

    # ToDo: Naming: What does this method actually do`?
    def _fit_test_sequence(self, index, new_index):
        clicked_item = self.selected_tests[index]
        element2 = self.selected_tests[new_index]

        self.selected_tests.insert(new_index, clicked_item)
        del self.selected_tests[new_index + 1]

        self.selected_tests.insert(index, element2)
        del self.selected_tests[index + 1]

    @QtCore.pyqtSlot()
    def _move_down(self):
        selected = self.selectedTests.selectedItems()
        if not len(selected):
            self._update_feedback(ErrorMessage.NotSelected())
            return

        row = selected[0].row()
        if row == self.selectedTests.rowCount() - 1:
            return

        index = row
        self._fit_test_sequence(index, index + 1)

        self._update_test_list_table()

    @QtCore.pyqtSlot()
    def _remove_from_testprogram(self):
        # blocking signals for selectedTests table prevent any callback event to fire
        self.selectedTests.blockSignals(True)
        selected_items = self.selectedTests.selectedItems()
        if not len(selected_items):
            self._update_feedback(ErrorMessage.NotSelected())
            return

        self.parametersInput.setRowCount(0)
        self.parametersOutput.setRowCount(0)

        test_index = self.selectedTests.currentRow()
        del self.selected_tests[test_index]
        self._update_test_list_table()
        self.selectedTests.blockSignals(False)

    @QtCore.pyqtSlot()
    def _add_to_testprogram(self):
        if not self._is_selected(self.availableTests):
            self._update_feedback(ErrorMessage.NotSelected())
            return

        for item in self.availableTests.selectedItems():
            self._add_test_tuple_items(item.text())

        self._update_test_list_table()

    @QtCore.pyqtSlot(str)
    def _verify_temperature(self, text):
        self.parametersInput.setRowCount(0)
        self.parametersOutput.setRowCount(0)
        self._deselect_items(self.availableTests)
        self._deselect_table_items()

        if not text:
            self.temperature_feedback.setText(ErrorMessage.TemperatureMissed())

        if self.sequencer_type == Sequencer.Static():
            if not len(self.temperature.text()):
                self.temperature_feedback.setText(ErrorMessage.InvalidTemperature())

        if self.sequencer_type == Sequencer.Dynamic():
            if self._get_dynamic_temp(text) is None:
                self.temperature_feedback.setText(ErrorMessage.InvalidTemperature())

        self._update_test_list_table()
        self._update_test_list()

    def _update_test_list(self):
        self.availableTests.clear()
        alltests = self._get_available_tests()
        for t in alltests:
            self.availableTests.addItem(t.name)
            self.available_tests.append(self._generate_test_struct(t.name, t.name))

    def _validate_temperature_input(self, text, pattern):
        index = text.rfind(pattern)
        if index == -1:
            return

        text_list = list(text)
        text_list[index] = ''
        if not text_list[len(text_list) - 1].isdigit():
            text_list[len(text_list) - 1] = ''

        self.temperature.setText(''.join(text_list))

    def _get_dynamic_temp(self, text):
        temp_vars = []
        try:
            self._validate_temperature_input(text, ',,')
            temps = text.split(',')
            if len(temps) == 0:
                return None

            for i in temps:
                if i == '-':
                    return

                if i != '':
                    temp_vars.append(int(i))

        except ValueError:
            self._validate_temperature_input(text, '--')
            return None

        return temp_vars

    def _get_available_tests(self):
        available_tests = []
        tests = self.project_info.get_tests_from_db(self.hardware.currentText(),
                                                    self.base.currentText())
        if not self.temperature.text():
            return tests

        if self.sequencerType.currentText() == Sequencer.Static():
            temps = [int(self.temperature.text())]
        else:
            temps = self._get_dynamic_temp(self.temperature.text())

        if temps is None:
            return tests

        for test in tests:
            min, max = self.project_info.get_test_temp_limits(test.name, self.project_info.active_hardware, self.project_info.active_base)
            for temp in temps:
                if temp > (min - 1) and temp < max + 1 and \
                   test not in available_tests:
                    available_tests.append(test)

        return available_tests

    def _set_sample_visible_mode(self, is_visible):
        self.sample.setVisible(is_visible)
        self.sample_label.setVisible(is_visible)
        self.one_label.setVisible(is_visible)

    def _verify(self):
        success = True
        self.usertext_feedback.setText('')
        self.target_feedback.setText('')
        self.temperature_feedback.setText('')
        self._update_feedback('')

        if self.base.currentText() == 'PR':
            self._set_sample_visible_mode(False)
        else:
            self._set_sample_visible_mode(True)

        if not self.target.currentText():
            self.target_feedback.setText(ErrorMessage.TargetMissed())
            success = False

        if self.selectedTests.rowCount() == 0:
            self._update_feedback(ErrorMessage.EmtpyTestList())
            success = False

        if not self._is_dynamic_range_valid:
            self._update_feedback(ErrorMessage.NoValidTestRange())
            success = False

        if not self.temperature.text() or not self._is_valid_temperature():
            self.temperature_feedback.setText(ErrorMessage.TemperatureNotValidated())
            success = False

        if success:
            self.usertext_feedback.setText('')
            self.target_feedback.setText('')
            self.temperature_feedback.setText('')
            self._update_feedback('')
            self.OKButton.setEnabled(True)
        else:
            self.OKButton.setEnabled(False)

    def _verify_tests(self):
        self._update_feedback('')
        self.OKButton.setEnabled(True)

        for test in self.selected_tests:
            parameters = self._get_test_parameters(test['name'])
            if not self._verify_input_parameters(test['input_parameters'], parameters) \
               or not self._verify_output_parameters(test['output_parameters'], parameters):
               return

    def _verify_input_parameters(self, input_parameters, parameters):
        for param, val, in input_parameters.items():
            if not self._is_input_limit_valid(param, val['Value'], parameters):
                self._update_feedback(f'input parameter, {param} is not valid')
                self.OKButton.setEnabled(False)
                return False

        return True

    def _verify_output_parameters(self, output_parameters, parameters):
        for param, val in output_parameters.items():
            if not self._is_output_limit_valid(param, val['LTL'], 'LTL', parameters) \
               or not self._is_output_limit_valid(param, val['UTL'], 'UTL', parameters):
                self._update_feedback(f'output parameter, {param} is not valid')
                self.OKButton.setEnabled(False)
                return False

        return True

    def _is_valid_temperature(self):
        if self.sequencer_type == Sequencer.Dynamic():
            return self._get_dynamic_temp(self.temperature.text())
        else:
            return self.temperature.text() and self.is_valid_temperature

    @property
    def program_name(self):
        return f'Prog_{self.hardware.currentText()}_{self.base.currentText()}_{self.target.currentText()}_{self.usertext.text()}'

    @property
    def sequencer_type(self):
        return self.sequencerType.currentText()

    def _update_feedback(self, message):
        if message:
            self.Feedback.setText(message)
        else:
            self.Feedback.setText('')

    # ToDo Encapsulate temperature range into class
    def _is_temperature_in_range(self, test, temps):
        if temps is None:
            return Range.In_Range()

        min, max = self.project_info.get_test_temp_limits(test, self.project_info.active_hardware, self.project_info.active_base)
        temps.sort()

        in_range_list = [x for x in temps if x >= min and x <= max]

        if len(in_range_list) == len(temps):
            return Range.In_Range()
        elif not len(in_range_list):
            self.is_valid_temperature = False
            return Range.Out_Of_Range()
        else:
            return Range.Limited_Range()

    @staticmethod
    def _generate_color(color):
        return QtGui.QBrush(QtGui.QColor(color[0], color[1], color[2]))

    def _set_widget_color(self, item, color):
        item.setBackground(self._generate_color(color))
        item.setForeground(QtCore.Qt.black)

    def _get_test_info(self, fmt):
        if not len(self.temperature.text()):
            return '', []

        if self.sequencer_type == Sequencer.Static():
            temps = [int(self.temperature.text())]
            text = '' if not len(temps) else self._get_text(temps[0], fmt)
        else:
            temps = self._get_dynamic_temp(self.temperature.text())
            temps.sort()
            text = '' if temps is None else f"{self._get_text(temps[0], fmt)}..{self._get_text(temps[len(temps) - 1], fmt)}"

        return text, temps

    def _generate_temperature_item(self, fmt):
        text, temps = self._get_test_info(fmt)

        item = QtWidgets.QTableWidgetItem(text)
        if len(text):
            which_range = self._is_temperature_in_range(self.current_selected_test, temps)
            if which_range == Range.Out_Of_Range():
                self._set_widget_color(item, RED)

            if which_range == Range.Limited_Range():
                self._set_widget_color(item, ORANGE)

        return item

    def _fill_input_parameter_table(self):
        self._clear_table_content(self.parametersInput)
        self.parametersInput.setRowCount(len(self.input_parameters))
        self.parametersInput.setColumnCount(6)
        fmt = '.0f'  # set format to zero as default
        row = 0
        for key, value in self.input_parameters.items():
            for col in range(self.parametersInput.columnCount()):
                parameter_name = list(self.input_parameters.items())[row][0]
                if parameter_name:
                    fmt = self.input_parameters[parameter_name]['fmt']

                if col == 0:
                    name_item = QtWidgets.QTableWidgetItem(key)
                    name_item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                    name_item.setFlags(QtCore.Qt.NoItemFlags)
                    self.parametersInput.setItem(row, col, name_item)
                    continue
                elif col == 1:
                    item = QtWidgets.QTableWidgetItem(str(self._get_text(value['Min'], fmt)))
                elif col == 2:
                    if key == 'Temperature':
                        item = self._generate_temperature_item(fmt)
                        item.setFlags(QtCore.Qt.NoItemFlags)
                    else:
                        item = self._generate_configurable_table_cell(self.parametersInput, value['Default']['Value'], fmt, 2)
                        if value['Default']['validity'] not in (ParameterState.Valid(), ParameterState.New()):
                            item.setFlags(QtCore.Qt.NoItemFlags)

                        try:
                            if self.selected_cell is not None and not self._is_input_limit_valid(parameter_name, value['Default']['Value'], self._get_test_parameters(self.selected_cell.text())):
                                self._set_widget_color(item, RED)
                        except:
                            pass

                elif col == 3:
                    item = QtWidgets.QTableWidgetItem(str(self._get_text(value['Max'], fmt)))
                elif col == 4:
                    item = QtWidgets.QTableWidgetItem(value['Unit'])
                elif col == 5:
                    item = QtWidgets.QTableWidgetItem(value['fmt'])

                if col in (1, 3, 4, 5):
                    item.setFlags(QtCore.Qt.NoItemFlags)

                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                self.parametersInput.setItem(row, col, item)

            row += 1

        self._validate_table(self.parametersInput, self.input_parameters)

    @staticmethod
    def _is_input_limit_valid(param_name, limit, parameters):
        try:
            if parameters['input_parameters'][param_name]['Min'] > limit \
               or parameters['input_parameters'][param_name]['Max'] < limit:
                return False
        except KeyError:
            # keyError exception is a sign that the parameter looking for was deleted from the associated test and we could ignore it
            return True

        return True

    def _validate_table(self, table, elements):
        for param_name, element in elements.items():
            for row in range(table.rowCount()):
                if not table.item(row, 0):
                    continue

                if table.item(row, 0).text() == param_name:
                    if element['is_valid'] == ParameterState.Invalid():
                        self._highlight_invalid_row(row, table, RED)
                    if element['is_valid'] == ParameterState.New():
                        self._highlight_invalid_row(row, table, GREEN)

    def _highlight_invalid_row(self, row, table, color):
        cols = table.columnCount()
        for col in range(cols):
            self._set_widget_color(table.item(row, col), color)

    def _get_text(self, value, fmt):
        return ('%' + fmt) % float(value)

    def _clear_table_content(self, table):
        for row in range(table.rowCount()):
            for col in range(table.columnCount()):
                table.removeCellWidget(row, col)

    def _fill_output_parameter_table(self):
        self._clear_table_content(self.parametersOutput)
        self.parametersOutput.setRowCount(len(self.output_parameters))
        self.parametersOutput.setColumnCount(7)
        row = 0
        header = self.parametersOutput.horizontalHeader()
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        for key, value in self.output_parameters.items():
            for col in range(self.parametersOutput.columnCount()):
                parameter_name = list(self.output_parameters.items())[row][0]
                fmt = self.output_parameters[parameter_name]['fmt']

                if col == 0:
                    name_item = QtWidgets.QTableWidgetItem(key)
                    name_item.setTextAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                    name_item.setFlags(QtCore.Qt.NoItemFlags)
                    self.parametersOutput.setItem(row, col, name_item)
                    continue
                elif col == 1:
                    item = QtWidgets.QTableWidgetItem(str(self._get_text(value['LSL'], fmt)))
                elif col == 2:
                    item = self._generate_configurable_table_cell(self.parametersOutput, value['LTL'], fmt, col)
                    if value['is_valid'] not in (ParameterState.Valid(), ParameterState.New()):
                        item.setFlags(QtCore.Qt.NoItemFlags)

                    try:
                        if self.selected_cell is not None and not self._is_output_limit_valid(parameter_name, value['LTL'], 'LTL', self._get_test_parameters(self.selected_cell.text())):
                            self._set_widget_color(item, RED)
                    except:
                        pass
                # TODO: should the nom be a part of the table
                # elif col == 3:
                #     item = QtWidgets.QTableWidgetItem(str(value['NOM']))
                elif col == 3:
                    item = self._generate_configurable_table_cell(self.parametersOutput, value['UTL'], fmt, col)
                    if value['is_valid'] not in (ParameterState.Valid(), ParameterState.New()):
                        item.setFlags(QtCore.Qt.NoItemFlags)
                    try:
                        if self. selected_cell is not None and not self._is_output_limit_valid(parameter_name, value['UTL'], 'UTL', self._get_test_parameters(self.selected_cell.text())):
                            self._set_widget_color(item, RED)
                    except:
                        pass
                elif col == 4:
                    item = QtWidgets.QTableWidgetItem(str(self._get_text(value['USL'], fmt)))
                elif col == 5:
                    item = QtWidgets.QTableWidgetItem(value['Unit'])
                elif col == 6:
                    item = QtWidgets.QTableWidgetItem(value['fmt'])

                if col in (1, 4, 5, 6):
                    item.setFlags(QtCore.Qt.NoItemFlags)

                item.setTextAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                self.parametersOutput.setItem(row, col, item)

            row += 1

        self._validate_table(self.parametersOutput, self.output_parameters)

    def _get_test_parameters(self, test_name):
        return self.project_info.get_test_table_content(self._extract_base_test_name(test_name), self.project_info.active_hardware, self.project_info.active_base)

    @staticmethod
    def _is_output_limit_valid(param_name, limit, type, parameters):
        try:
            if type == 'LTL' and parameters['output_parameters'][param_name]['LSL'] > limit:
                return False

            if type == 'UTL' and parameters['output_parameters'][param_name]['USL'] < limit:
                return False
        except KeyError:
            # keyError exception is a sign that the parameter looking for was deleted from the associated test and we could ignore it for now
            return True

        return True

    def _generate_configurable_table_cell(self, parameter_table, value, fmt, cell):
        if isinstance(value, str) and not len(value):
            return
        text = str(self._get_text(value, fmt))
        item = QtWidgets.QTableWidgetItem(text)

        self._resize_table_cell(parameter_table, cell, item)

        if self.read_only:
            item.setFlags(QtCore.Qt.NoItemFlags)

        return item

    def _resize_table_cell(self, parameter_table, cell, item):
        font = QtGui.QFont()
        metric = QtGui.QFontMetrics(font)
        text_size = metric.boundingRect(item.text()).width()
        colum_size = self.parametersInput.columnWidth(1)
        if (text_size + colum_size) > self.cell_size:
            self.cell_size = text_size + colum_size

        parameter_table.setColumnWidth(cell, self.cell_size)

    @QtCore.pyqtSlot(QtWidgets.QTableWidgetItem)
    def _double_click_handler_input_param(self, item):
        test_name = self.selectedTests.item(self.selectedTests.currentRow(), 0).text()
        self._create_checkable_cell(test_name, self.parametersInput, 'input', item, self.positive_float_validator)

    @QtCore.pyqtSlot(QtWidgets.QTableWidgetItem)
    def _double_click_handler_output_param(self, item):
        test_name = self.selectedTests.item(self.selectedTests.currentRow(), 0).text()
        self._create_checkable_cell(test_name, self.parametersOutput, 'output', item, self.positive_float_validator)

    def _create_checkable_cell(self, test_name, table, table_type, item, validator):
        column = item.column()
        row = item.row()
        checkable_widget = QtWidgets.QLineEdit()
        checkable_widget.setText(item.text())

        checkable_widget.setValidator(validator)

        table.setCellWidget(row, column, checkable_widget)
        checkable_widget.editingFinished.connect(lambda row=row, column=column,
                                                 checkable_widget=checkable_widget, table=table,
                                                 table_type=table_type:
                                                 self._edit_cell_done(test_name, table, table_type, checkable_widget, row, column))

    def _edit_cell_done(self, test_name, table, table_type, checkable_widget, row, column):
        if table_type == 'description':
            description = checkable_widget.text()
            if self._is_description_valid(table, description):
                self.selectedTests.item(row, column).setText(str(checkable_widget.text()))
                self._update_test_description(row, checkable_widget.text())
            else:
                self._update_feedback(ErrorMessage.TestDescriptionNotUnique())

            self._update_row(row)
            if not self.selectedTests.selectedItems():
                self.parametersInput.setRowCount(0)
                self.parametersOutput.setRowCount(0)

        else:
            param_type = table.item(row, 0).text()
            value = float(checkable_widget.text())
            if table_type == 'input':
                if not self._validate_input_parameter(test_name, value, param_type):
                    return
            else:
                if not self._validate_output_parameter(test_name, value, param_type, column):
                    return

            self._verify_tests()

    @staticmethod
    def _is_description_valid(table, description):
        for row in range(table.rowCount()):
            item = table.item(row, 1)
            if not item:
                continue

            if item.text() != description:
                continue

            return False

        return True
        
    def _update_test_description(self, test_row, new_description):
        self.selected_tests[test_row]['description'] = new_description

    def _update_row(self, row):
        test_name = self.selectedTests.item(row, 0).text()
        test_description = self.selectedTests.item(row, 1).text()

        self.selectedTests.blockSignals(True)
        self.selectedTests.removeRow(row)
        self.selectedTests.insertRow(row)
        self._insert_test_tuple_items(row, test_name, test_description)
        self.selectedTests.blockSignals(False)

    def _validate_output_parameter(self, test_name, value, param_type, column):
        limits = (self.output_parameters[param_type]['LSL'], self.output_parameters[param_type]['USL'])
        limit = 'UTL' if column == 3 else 'LTL'

        if not self._is_valid_value(value, limits) or \
           not self._is_valid_output_value(value, param_type, limit):
            self._fill_output_parameter_table()
            self._update_feedback(ErrorMessage.OutOfRange())
            return False

        self._verify()
        self.output_parameters[param_type][limit] = value
        self._update_selected_tests_parameters('output_parameters',
                                               param_type,
                                               value,
                                               limit)
        self._fill_output_parameter_table()
        return True

    def _is_valid_output_value(self, value, param_type, limit):
        import numpy as np

        if str(self.output_parameters[param_type]['UTL']) == str(np.nan) and limit != 'UTL' or \
           str(self.output_parameters[param_type]['LTL']) == str(np.nan) and limit != 'LTL':
            return True

        if limit == 'LTL':
            return self.output_parameters[param_type]['UTL'] > value

        if limit == 'UTL':
            return self.output_parameters[param_type]['LTL'] < value

        return False

    def _validate_input_parameter(self, test_name, value, param_type):
        limits = (self.input_parameters[param_type]['Min'], self.input_parameters[param_type]['Max'])
        if not self._is_valid_value(value, limits):
            self._fill_input_parameter_table()
            self._update_feedback(ErrorMessage.OutOfRange())
            return False

        self._verify()
        self.input_parameters[param_type]['Default']['Value'] = value
        self._update_selected_tests_parameters('input_parameters',
                                               param_type,
                                               value)
        self._fill_input_parameter_table()
        return True

    def _is_valid_value(self, value, limits):
        left_limit = limits[0]
        right_limit = limits[1]
        if left_limit == '-inf' and right_limit == 'inf':
            return True

        if left_limit == '-inf':
            return value <= float(right_limit)

        if right_limit == 'inf':
            return value >= float(left_limit)

        return float(left_limit) <= value <= float(right_limit)

    def _generate_test_struct(self, test_name, test_description):
        struct = {'name': test_name,
                  'input_parameters': {'In': {'Value': None, 'validity': ParameterState.Valid()}},
                  'output_parameters': {'Out': {'UTL': '', 'LTL': '', 'Binning': {'bin': 10, 'result': Result.Fail()[1], 'context': ''}, 'validity': ParameterState.Valid()}},
                  'description': test_description,
                  'is_valid': True}
        parameters = self.project_info.get_test_table_content(self._extract_base_test_name(test_name), self.hardware.currentText(), self.base.currentText())

        inputs = self._generate_input_parameters(parameters)
        do_binning = test_name != test_description
        outputs = self._generate_output_parameters(parameters, do_binning)

        struct.update({'input_parameters': inputs})
        struct.update({'output_parameters': outputs})
        return struct

    def _generate_output_parameters(self, parameters, do_binning):
        outputs = {}
        for key, value in parameters['output_parameters'].items():
            # TODO: use update function, to only update the wanted fields and
            #       prevent overriding existing properties
            if do_binning:
                outputs.update(self._generate_output_dict(key, value['LTL'], value['UTL']))
                self.bin_counter += 1
            else:
                outputs[key] = {'LTL': value['LTL'], 'UTL': value['UTL']}

        return outputs

    def _generate_output_dict(self, param_name, ltl, utl):
        return {param_name: {'LTL': ltl, 'UTL': utl,
                'Binning': {'bin': self.bin_counter,
                            'result': Result.Fail()[1],
                            'context': ''},
                'validity': ParameterState.Valid()}}

    @staticmethod
    def _generate_input_dict(param_name, value):
        return {param_name: {'Value': value, 'validity': ParameterState.Valid()}}

    def _generate_input_parameters(self, parameters):
        inputs = {}
        for key, value in parameters['input_parameters'].items():
            inputs.update(self._generate_input_dict(key, value['Default']))

        return inputs

    def _update_selected_tests_parameters(self, type, parameter_name, value, limit=''):
        index = self.selectedTests.currentRow()
        if not limit:
            self.selected_tests[index][type][parameter_name]['Value'] = value
        else:
            self.selected_tests[index][type][parameter_name][limit] = value

    def _create_new_params(self, parameter_name, limit, type, index, value, limit_type=''):
        if not limit_type:
            self.selected_tests[index][type][parameter_name].update({'Value': value})
        else:
            self.selected_tests[index][type][parameter_name][limit] = value

    def _clear_test_list_table(self):
        if not self.selectedTests.rowCount():
            return

        for row in range(self.selectedTests.rowCount()):
            self.selectedTests.removeRow(row)

    def _is_test_valid(self, test):
        av_test = self._get_test(test['name'], self.available_tests)
        if av_test is None:
            return False

        if len(av_test['input_parameters']) < len(test['input_parameters']) \
           or len(av_test['input_parameters']) > len(test['input_parameters']):
            return False

        if len(av_test['output_parameters']) < len(test['output_parameters']) \
           or len(av_test['output_parameters']) > len(test['output_parameters']):
            return False

        if self._have_params_changed(av_test['input_parameters'], test['input_parameters']) \
           or self._have_params_changed(av_test['output_parameters'], test['output_parameters']):
            return False

        parameters = self._get_test_parameters(test['name'])
        if not self._are_input_parameters_valid(test['input_parameters'], parameters['input_parameters']) \
           or not self._are_output_parameters_valid(test['output_parameters'], parameters['output_parameters']):
            return False

        return True

    @staticmethod
    def _get_test(test_name, test_list):
        for test in test_list:
            if test_name != test['name']:
                continue

            return test

        return None

    @staticmethod
    def _are_input_parameters_valid(params, default_vals):
        for param_name, val in params.items():
            if val['Value'] < default_vals[param_name]['Min'] \
               or val['Value'] > default_vals[param_name]['Max']:
                return False

        return True

    @staticmethod
    def _are_output_parameters_valid(params, default_vals):
        for param_name, val in params.items():
            if val['LTL'] < default_vals[param_name]['LSL'] \
               or val['UTL'] > default_vals[param_name]['USL']:
                return False

        return True

    @staticmethod
    def _have_params_changed(av_test_input, test_input):
        for av_k, k in zip(sorted(av_test_input.keys()), sorted(test_input.keys())):
            if av_k != k:
                return True

        return False

    def _format_selected_list(self):
        for test in self.selected_tests:
            input_struct = self._generate_formatted_input_parameters(test['input_parameters'])
            output_struct = self._generate_formatted_output_parameters(test['output_parameters'])

            test.update(input_struct)
            test.update(output_struct)

    def _generate_formatted_output_parameters(self, output_params):
        output_struct = {'output_parameters': {}}
        for out_param, val in output_params.items():
            param = self._generate_output_dict(out_param, val['LTL'], val['UTL'])
            param[out_param]['Binning'].update(val['Binning'])
            output_struct['output_parameters'].update(param)

        return output_struct

    def _generate_formatted_input_parameters(self, input_params):
        input_struct = {'input_parameters': {}}
        for in_params, val in input_params.items():
            param = self._generate_input_dict(in_params, val)
            input_struct['input_parameters'].update(param)

        return input_struct

    def _update_test_list_table(self):
        self.is_valid_temperature = True
        self._clear_test_list_table()
        self.selectedTests.setRowCount(len(self.selected_tests))
        count = 0
        for test in self.selected_tests:
            item_name = self._generate_test_name_item(test['name'])
            item_description = self._generate_test_description_item(test['description'])
            which_range = self._is_temperature_in_range(self._extract_base_test_name(test['name']), self._get_temps())

            is_test_valid = self._is_test_valid(test)
            if which_range == Range.Out_Of_Range() or not is_test_valid:
                self._set_widget_color(item_name, RED)
                self._set_widget_color(item_description, RED)

            if which_range == Range.Limited_Range() and is_test_valid:
                self._set_widget_color(item_name, ORANGE)
                self._set_widget_color(item_description, ORANGE)

            self.selectedTests.setItem(count, 0, item_name)
            self.selectedTests.setItem(count, 1, item_description)
            count += 1

        self._set_parameter_validity()
        self._verify()

    def _set_parameter_validity(self):
        for test in self.selected_tests:
            av_test = self._get_test(test['name'], self.available_tests)
            if av_test is None:
                continue

            available_test = copy.deepcopy(av_test)
            self._validate_input_parameters(test, available_test)
            self._validate_output_parameters(test, available_test)

    def _validate_output_parameters(self, test, available_test):
        type = 'output_parameters'
        output_params = [out_param for out_param in available_test[type].keys()]
        self._do_mark_invalid_params(test[type], output_params)
        self._add_missing_output_parameters(test[type], output_params, available_test)

    def _validate_input_parameters(self, test, available_test):
        type = 'input_parameters'
        input_params = [in_param for in_param in available_test[type].keys()]
        self._do_mark_invalid_params(test[type], input_params)
        self._add_missing_input_parameters(test[type], input_params, available_test)

    @staticmethod
    def _generate_validity_dict(validity):
        return {'validity': validity}

    def _do_mark_invalid_params(self, parameter, available_params):
        for param_name in parameter.keys():
            valid_state = ParameterState.Valid() if param_name in available_params else ParameterState.Invalid()
            if parameter[param_name]['validity'] == ParameterState.New():
                continue
            parameter[param_name].update(self._generate_validity_dict(valid_state))

    @staticmethod
    def _add_missing_input_parameters(parameter, input_params, available_params):
        for param_name in input_params:
            if not parameter.get(param_name):
                parameter.update({param_name: available_params['input_parameters'][param_name]})
                parameter[param_name].update({'validity': ParameterState.New()})

    def _add_missing_output_parameters(self, parameter, output_params, available_params):
        for param_name in output_params:
            if not parameter.get(param_name):
                parameter.update({param_name: {'LTL': available_params['output_parameters'][param_name]['LTL'], 'UTL': available_params['output_parameters'][param_name]['UTL'],
                                               'Binning': {'bin': self.bin_counter,
                                                           'result': Result.Fail()[1],
                                                           'context': ''}, 'validity': ParameterState.New()}})
                self.bin_counter += 1

    def _get_temps(self):
        if self.sequencer_type == Sequencer.Static():
            if not len(self.temperature.text()):
                temps = []
            else:
                temps = [int(self.temperature.text())]
        else:
            temps = self._get_dynamic_temp(self.temperature.text())
            temps.sort()

        return temps

    def _generate_selected_test_name(self, test_name):
        count = 1
        for test in self.selected_tests:
            if test_name == test['name']:
                count += 1

        return f"{test_name}_{count}"

    def _add_test_tuple_items(self, test_name):
        indexed_test = self._generate_selected_test_name(test_name)
        self.selected_tests.append(self._generate_test_struct(test_name, indexed_test))

    def _insert_test_tuple_items(self, row, test_name, test_description):
        self.selectedTests.setItem(row, 0, self._generate_test_name_item(test_name))
        self.selectedTests.setItem(row, 1, self._generate_test_description_item(test_description))

    @staticmethod
    def _generate_test_description_item(text):
        description_item = QtWidgets.QTableWidgetItem(text)
        description_item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        return description_item

    @staticmethod
    def _generate_test_name_item(text):
        name_item = QtWidgets.QTableWidgetItem(text)
        # name should not be editable
        name_item.setFlags(QtCore.Qt.NoItemFlags | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        return name_item

    def _add_binning_item(self, description, out_params, parent):
        for key, value in out_params.items():
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, description + '_' + key)
            if not value.get('Binning'):
                value.update(self._generate_binning_structure(self.bin_counter, Result.Fail()[1], ''))

            item.setText(1, str(value['Binning']['bin']))
            item.setText(2, Result.Fail()[0] if value['Binning']['result'] == Result.Fail()[1] else Result.Pass()[0])
            item.setText(3, value['Binning']['context'])

            self._validate_tree_item(item, value['validity'])
            parent.addChild(item)

    def _validate_tree_item(self, item, validity):
        if validity == ParameterState.New():
            self._set_tree_item_color(item, GREEN)

        if validity == ParameterState.Invalid():
            self._set_tree_item_color(item, RED)

    def _set_tree_item_color(self, item, color):
        for col in range(self.binning_tree.columnCount()):
            item.setBackground(col, self._generate_color(color))
            item.setForeground(col, QtCore.Qt.black)

    def _populate_binning_tree(self):
        tests = [{'name': test['name'], 'description': test['description'], 'output_parameters': test['output_parameters']} for test in self.selected_tests]

        for test in tests:
            parent = QtWidgets.QTreeWidgetItem(self.binning_tree)
            parent.setExpanded(True)
            parent.setText(0, test['name'])
            self._add_binning_item(test['description'], test['output_parameters'], parent)

    def _get_configuration(self):
        configuration = {'name': '',
                         'hardware': self.hardware.currentText(),
                         'base': self.base.currentText(),
                         'target': self.target.currentText(),
                         'usertext': self.usertext.text(),
                         'sequencer_type': self.sequencer_type,

                         'temperature': self.temperature.text() if self.sequencer_type == Sequencer.Static()
                                 else self._get_dynamic_temp(self.temperature.text()),

                         'sample': self.sample.suffix()}

        definition = {'sequence': []}
        for test in self.selected_tests:
            test.pop('is_valid', None)

            self._prepare_parameters(test['input_parameters'])
            self._prepare_input_parameters(test['input_parameters'])

            self._prepare_parameters(test['output_parameters'])

            definition['sequence'].append(test)

        return configuration, definition

    @staticmethod
    def _prepare_parameters(params):
        invalids = []
        for param, val in params.items():
            if val['validity'] == ParameterState.Invalid():
                invalids.append(param)
                continue

            val.pop('validity')

        for invalid in invalids:
            params.pop(invalid)

    @staticmethod
    def _prepare_input_parameters(input_params):
        for in_param, val in input_params.items():
            input_params[in_param] = val['Value']

    def _save_configuration(self):
        configuration, definition = self._get_configuration()

        if configuration is None:
            return

        if not self.read_only and self.enable_edit:
            owner = f"{self.hardware.currentText()}_{self.base.currentText()}_{self.target.currentText()}_{self.owner}"
            count = self.project_info.get_program_owner_element_count(owner) + 1
            self.prog_name = f'{os.path.basename(self.project_info.project_directory)}_{owner}_{count}'

            self.target_prefix = f"{self.target.currentText()}_{self.owner}_{count}"

            self.project_info.insert_program(self.prog_name, configuration['hardware'], configuration['base'], configuration['target'],
                                             configuration['usertext'], configuration['sequencer_type'], configuration['temperature'],
                                             definition, owner, self.project_info.get_program_owner_element_count(owner), self.target_prefix)
        else:
            self.project_info.update_program(self.prog_name, configuration['hardware'], configuration['base'],
                                             configuration['target'], configuration['usertext'], configuration['sequencer_type'],
                                             configuration['temperature'], definition, self.owner, self._get_target_name())

        self.accept()

    def _get_target_name(self):
        owner_split = self.owner.split('_')
        index = -1
        for i, text in enumerate(owner_split):
            if not text == self.target.currentText():
                continue

            index = i
            break

        target_name = self.target.currentText()
        for i in range(index + 1, len(owner_split)):
            target_name += '_' + owner_split[i]

        target_name += '_' + self.prog_name[-1]

        return target_name

    def _cancel(self):
        self.reject()



def new_program_dialog(project_info, owner, parent):
    testProgramWizard = TestProgramWizard(project_info, owner, parent)
    testProgramWizard.exec_()
    del(testProgramWizard)
