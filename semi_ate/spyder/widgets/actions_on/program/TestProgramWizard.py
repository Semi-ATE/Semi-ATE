from PyQt5 import QtGui, QtCore, QtWidgets
import sys
import os
import re
from enum import Enum
from ATE.org.actions_on.utils.BaseDialog import BaseDialog


ORANGE = (255, 127, 39)
RED = (237, 28, 36)


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

    def __call__(self):
        return self.value


DEFAULT_TEMPERATURE = '25'


class TestProgramWizard(BaseDialog):
    def __init__(self, project_info, owner, parent=None, read_only=False, edit_on=True, prog_name=''):
        super().__init__(__file__)
        self.project_info = project_info
        self.owner = owner

        self.available_tests = []
        self.selected_tests = []
        self.read_only = read_only
        self.edit_on = edit_on
        self.prog_name = prog_name

        self.current_selected_test = None
        self.result = None
        self._is_dynamic_range_valid = True

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

        from ATE.org.validation import valid_float_regex
        regx = QtCore.QRegExp(valid_float_regex)
        self.positive_float_validator = QtGui.QRegExpValidator(regx, self)

        from ATE.org.validation import valid_integer_regex
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

    def _table_clicked(self):
        if len(self.selectedTests.selectedItems()):
            return

        self._update_test_list_table()

    def _double_click_handler(self, item):
        if item.column() == 0:
            return

        from ATE.org.validation import valid_test_name_description_regex
        regx = QtCore.QRegExp(valid_test_name_description_regex)
        name_validator = QtGui.QRegExpValidator(regx, self)

        self._create_checkable_cell(item.text(), self.selectedTests, "description", item, name_validator)

    def _connect_event_handler(self):
        self.availableTests.itemClicked.connect(self._available_test_selected)

        self.parametersInput.itemDoubleClicked.connect(self._double_click_handler_input_param)
        self.parametersOutput.itemDoubleClicked.connect(self._double_click_handler_output_param)

        self.testAdd.clicked.connect(lambda: self._move_test(Action.Right()))
        self.moveTestDown.clicked.connect(lambda: self._move_test(Action.Down()))
        self.moveTestUp.clicked.connect(lambda: self._move_test(Action.Up()))
        self.testRemove.clicked.connect(lambda: self._move_test(Action.Left()))

        self.hardware.currentIndexChanged.connect(self._hardware_changed)
        self.base.currentIndexChanged.connect(self._base_changed)
        self.usertext.textChanged.connect(self._usertext_changed)

        self.sequencerType.currentIndexChanged.connect(self._sequencer_type_changed)
        self.temperature.textChanged.connect(self._verify_temperature)
        from ATE.org.validation import valid_user_text_name_regex
        user_text_reg_ex = QtCore.QRegExp(valid_user_text_name_regex)
        user_text_name_validator = QtGui.QRegExpValidator(user_text_reg_ex, self)
        self.usertext.setValidator(user_text_name_validator)

        self.OKButton.clicked.connect(self._save_configuration)
        self.CancelButton.clicked.connect(self._cancel)

    def _set_icon(self, button, icon_type):
        from ATE.org.actions_on.program.Actions import ACTIONS
        icon = QtGui.QIcon(ACTIONS[icon_type][0])
        button.setIcon(icon)
        button.setText("")

    def _resize_table(self, table, col_size):
        # resize cell columns
        for c in range(table.columnCount()):
            table.setColumnWidth(c, col_size)

        table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        table.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)

    def _view(self):
        self.existing_hardwares = self.project_info.get_active_hardware_names()
        self.hardware.addItems(self.existing_hardwares)
        current_hw_index = self.hardware.findText(self.project_info.active_hardware, QtCore.Qt.MatchExactly)
        self.hardware.setCurrentIndex(current_hw_index)

        current_base_index = self.base.findText(self.project_info.active_base, QtCore.Qt.MatchExactly)
        self.base.setCurrentIndex(current_base_index)

        self._update_target()

        self.sequencerType.addItems([Sequencer.Static(), Sequencer.Dynamic()])
        self.temperature.setText(DEFAULT_TEMPERATURE)

        self._update_test_list()
        self.Feedback.setText('')
        self.Feedback.setStyleSheet('color:orange')
        self.usertext_feedback.setStyleSheet('color:orange')
        self.temperature_feedback.setStyleSheet('color:orange')
        self.target_feedback.setStyleSheet('color:orange')
        self.usertext_feedback.setStyleSheet('color:orange')
        self._verify()

    def _update_target(self):
        self.target.clear()
        if self.base.currentText() == 'PR':
            existing_targets = self.project_info.get_active_die_names_for_hardware(self.hardware.currentText())
        else:
            existing_targets = self.project_info.get_active_device_names_for_hardware(self.hardware.currentText())

        self.target.addItems(existing_targets)
        current_target_index = self.target.findText(self.project_info.active_target, QtCore.Qt.MatchExactly)
        self.target.setCurrentIndex(current_target_index)

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

    @QtCore.pyqtSlot(int)
    def _sequencer_type_changed(self, index):
        if self.sequencerType.itemText(index) == Sequencer.Static():
            from ATE.org.validation import valid_integer_regex
            regx = QtCore.QRegExp(valid_integer_regex)
            integer_validator = QtGui.QRegExpValidator(regx, self)
            self.temperature.setValidator(integer_validator)
            self.temperature.setText(DEFAULT_TEMPERATURE)
            return

        from ATE.org.validation import valid_temp_sequence_regex
        regx = QtCore.QRegExp(valid_temp_sequence_regex)
        integer_validator = QtGui.QRegExpValidator(regx, self)
        self.temperature.setValidator(integer_validator)

        self.temperature.setText(f'{DEFAULT_TEMPERATURE},')

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def _available_test_selected(self, item):
        self.parametersInput.setEnabled(False)
        self.parametersOutput.setEnabled(False)

        self._update_tables_parameters(item.text(), item.text() + "_1", is_default=True)

    @QtCore.pyqtSlot(QtWidgets.QTableWidgetItem)
    def _test_selected(self, item):
        self.parametersInput.setEnabled(True)
        self.parametersOutput.setEnabled(True)

        row = item.row()
        self.selectedTests.item(row, 0).setSelected(True)
        self.selectedTests.item(row, 1).setSelected(True)

        self.selected_cell = item

        self._handle_selection(self.selectedTests, self.availableTests, item)

    def _handle_selection(self, selected_list, second_list, item):
        test_name = self.selectedTests.item(item.row(), 0).text()
        test_instance_name = self.selectedTests.item(item.row(), 1).text()
        self._deselect_items(second_list)
        self._update_tables_parameters(test_name, test_instance_name)

    def _deselect_items(self, selected_list):
        for index in range(selected_list.count()):
            selected_list.item(index).setSelected(False)

    def _deselect_table_items(self):
        for row in range(self.selectedTests.rowCount()):
            for col in range(self.selectedTests.columnCount()):
                self.selectedTests.item(row, col).setSelected(False)

    def _extract_base_test_name(self, indexed_test_name):
        # we assume that test name contains only one underscore
        return indexed_test_name.split('_')[0]

    def _extract_test_sequence(self, indexed_test_name):
        return indexed_test_name.split('_')[1]

    def _update_tables_parameters(self, the_test_name, test_instance_name, is_default=False):
        test_name = self._extract_base_test_name(the_test_name)
        self.current_selected_test = test_name
        parameters = self.project_info.get_test_table_content(test_name, self.hardware.currentText(), self.base.currentText())
        self.input_parameters = parameters['input_parameters']
        self.output_parameters = parameters['output_parameters']

        if not is_default:
            test_list = self.selected_tests
        else:
            test_list = self.available_tests

        # update table content if content changed
        for test in test_list:
            name = test['description']
            if name != test_instance_name:
                continue

            input_params = test['input_parameters'].items()
            for param in input_params:
                # hack to prevent using a key value that may not exists any more,
                # when we edit the parameter names for the respective test
                if not self.input_parameters.get(param[0]):
                    continue

                self.input_parameters[param[0]]['Default'] = param[1]

            output_params = test['output_parameters'].items()
            for param in output_params:
                # hack to prevent using a key value that may not exists any more,
                # when we edit the parameter names for the respective test
                if not self.output_parameters.get(param[0]):
                    continue

                self.output_parameters[param[0]]['LTL'], self.output_parameters[param[0]]['UTL'] = \
                    test['output_parameters'][param[0]]['LTL'], \
                    test['output_parameters'][param[0]]['UTL']
            break

        self._fill_input_parameter_table()
        self._fill_output_parameter_table()

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

    def _is_valid_temperature(self):
        if self.sequencer_type == Sequencer.Dynamic():
            return self._get_dynamic_temp(self.temperature.text())
        else:
            return self.temperature.text()

    @property
    def program_name(self):
        return f'Prog_{self.hardware.currentText()}_{self.base.currentText()}_{self.target.currentText()}_{self.usertext.text()}'

    @property
    def sequencer_type(self):
        return self.sequencerType.currentText()

    def _update_feedback(self, message):
        if not len(message) == 0:
            self.Feedback.setText(message)
            self.Feedback.setStyleSheet('color: orange')
            return

        self.Feedback.setStyleSheet('')
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
            return Range.Out_Of_Range()
        else:
            return Range.Limited_Range()

    def _generate_color(self, color):
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
                        item = self._generate_configurable_table_cell(value['Default'], fmt, 2)
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
                if parameter_name:
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
                    item = self._generate_configurable_table_cell(value['LTL'], fmt, 2)
                # TODO: should the nom be a part of the table
                # elif col == 3:
                #     item = QtWidgets.QTableWidgetItem(str(value['NOM']))
                elif col == 3:
                    item = self._generate_configurable_table_cell(value['UTL'], fmt, 3)
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

    def _generate_configurable_table_cell(self, value, fmt, cell):
        if isinstance(value, str) and not len(value):
            return
        text = str(self._get_text(value, fmt))
        item = QtWidgets.QTableWidgetItem(text)
        # QFontMetrics used to get the pixel size of the text which is used
        # to resizing of the cell
        font = QtGui.QFont()
        metric = QtGui.QFontMetrics(font)
        text_size = metric.boundingRect(text).width()
        colum_size = self.parametersInput.columnWidth(cell)
        self.parametersOutput.setColumnWidth(cell, text_size + colum_size)

        if self.read_only:
            item.setFlags(QtCore.Qt.NoItemFlags)

        return item

    def _double_click_handler_input_param(self, item):
        test_name = self.selectedTests.item(self.selectedTests.currentRow(), 0).text()
        self._create_checkable_cell(test_name, self.parametersInput, 'input', item, self.positive_float_validator)

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
            self.selectedTests.item(row, column).setText(str(checkable_widget.text()))
            self._update_test_description(row, checkable_widget.text())
            self._update_row(row)
        else:
            param_type = table.item(row, 0).text()
            value = float(checkable_widget.text())
            if table_type == 'input':
                self._validate_input_parameter(test_name, value, param_type)
            else:
                self._validate_output_parameter(test_name, value, param_type, column)

    def _update_test_description(self, test_row, new_description):
        self.selected_tests[test_row]['description'] = new_description

    def _update_row(self, row):
        test_name = self.selectedTests.item(row, 0).text()
        test_description = self.selectedTests.item(row, 1).text()

        self.selectedTests.removeRow(row)
        self.selectedTests.insertRow(row)
        self._insert_test_tuple_items(row, test_name, test_description)

    def _validate_output_parameter(self, test_name, value, param_type, column):
        limits = (self.output_parameters[param_type]['LSL'], self.output_parameters[param_type]['USL'])
        limit = 'LTL'
        if column == 3:
            limit = 'UTL'

        if not self._is_valid_value(value, limits) or \
           not self._is_valid_output_value(value, param_type, limit):
            self._fill_output_parameter_table()
            self._update_feedback(ErrorMessage.OutOfRange())
            return

        self._verify()
        self.output_parameters[param_type][limit] = value
        self._update_selected_tests_parameters(test_name,
                                               'output_parameters',
                                               param_type,
                                               value,
                                               limit)
        self._fill_output_parameter_table()

    def _is_valid_output_value(self, value, param_type, limit):
        import numpy as np

        if str(self.output_parameters[param_type]['UTL']) == str(np.nan) and limit != 'UTL' or \
           str(self.output_parameters[param_type]['LTL']) == str(np.nan) and limit != 'LTL':
            return True

        if limit == 'LTL':
            return self.output_parameters[param_type]['UTL'] > value

        if limit == 'UTL':
            return self.output_parameters[param_type]['LTL'] < value

    def _validate_input_parameter(self, test_name, value, param_type):
        limits = (self.input_parameters[param_type]['Min'], self.input_parameters[param_type]['Max'])
        if not self._is_valid_value(value, limits):
            self._fill_input_parameter_table()
            self._update_feedback(ErrorMessage.OutOfRange())
            return

        self._verify()
        self.input_parameters[param_type]['Default'] = value
        self._update_selected_tests_parameters(test_name,
                                               'input_parameters',
                                               param_type,
                                               value)
        self._fill_input_parameter_table()

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
        sturct = {'name': test_name, 'input_parameters': {'Value': None}, 'output_parameters': {'Out': {'UTL': '', 'LTL': ''}}, 'description': test_description, 'is_valid': True}
        parameters = self.project_info.get_test_table_content(self._extract_base_test_name(test_name), self.hardware.currentText(), self.base.currentText())
        inputs = {}
        outputs = {}
        for key, value in parameters['input_parameters'].items():
            inputs[key] = value['Default']

        for key, value in parameters['output_parameters'].items():
            outputs[key] = {'LTL': value['LTL'], 'UTL': value['UTL']}

        sturct.update({'input_parameters': inputs})
        sturct.update({'output_parameters': outputs})
        return sturct

    def _update_selected_tests_parameters(self, test_name, type, parameter_name, value, limit=''):
        index = self.selectedTests.currentRow()
        element = {}
        try:
            element = self.selected_tests[index][type][parameter_name]
        except KeyError:
            self._create_new_params(parameter_name, limit, type, index, test_name, value, limit)

        if not limit:
            element = value
        else:
            element[limit] = value

        self.selected_tests[index][type][parameter_name] = element

    def _create_new_params(self, parameter_name, limit, type, index, test_name, value, limit_type=''):
        if not limit_type:
            self.selected_tests[index][type][parameter_name] = value
        else:
            self.selected_tests[index][type][parameter_name] = {'UTL': '', 'LTL': ''}
            self.selected_tests[index][type][parameter_name][limit] = value

    def _clear_test_list_table(self):
        if not self.selectedTests.rowCount():
            return

        for row in range(self.selectedTests.rowCount()):
            self.selectedTests.removeRow(row)

    def _update_test_list_table(self):
        self._clear_test_list_table()
        self.selectedTests.setRowCount(len(self.selected_tests))
        count = 0
        for test in self.selected_tests:
            test_name = test['name']
            item_name = self._generate_test_name_item(test_name)
            item_description = self._generate_test_description_item(test['description'])
            temps = self._get_temps()
            which_range = self._is_temperature_in_range(self._extract_base_test_name(test_name), temps)
            if which_range == Range.Out_Of_Range():
                self._set_widget_color(item_name, RED)
                self._set_widget_color(item_description, RED)

            if which_range == Range.Limited_Range():
                self._set_widget_color(item_name, ORANGE)
                self._set_widget_color(item_description, ORANGE)

            self.selectedTests.setItem(count, 0, item_name)
            self.selectedTests.setItem(count, 1, item_description)
            count += 1

        self._verify()

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
            if test_name in test['name']:
                count += 1

        return f"{test_name}_{count}"

    def _add_test_tuple_items(self, test_name):
        indexed_test = self._generate_selected_test_name(test_name)
        self.selected_tests.append(self._generate_test_struct(test_name, indexed_test))

    def _insert_test_tuple_items(self, row, test_name, test_description):
        self.selectedTests.setItem(row, 0, self._generate_test_name_item(test_name))
        self.selectedTests.setItem(row, 1, self._generate_test_description_item(test_description))

    def _generate_test_description_item(self, text):
        description_item = QtWidgets.QTableWidgetItem(text)
        description_item.setFlags(QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        return description_item

    def _generate_test_name_item(self, text):
        name_item = QtWidgets.QTableWidgetItem(text)
        # name should not be editable
        name_item.setFlags(QtCore.Qt.NoItemFlags | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        return name_item

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
            # pop the "is_valid"-flag out, as it is not needed any more
            test.pop('is_valid', None)
            definition['sequence'].append(test)

        return configuration, definition

    def _save_configuration(self):
        configuration, definition = self._get_configuration()

        if configuration is None:
            return

        if not self.read_only and self.edit_on:
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

        self._generate_test_program(configuration, self.owner)

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

    def _generate_test_program(self, configuration, owner):
        from ATE.org.coding.generators import test_program_generator
        test_program_generator(self.prog_name, owner, self.project_info)


def new_program_dialog(project_info, owner, parent):
    testProgramWizard = TestProgramWizard(project_info, owner, parent)
    testProgramWizard.exec_()
    del(testProgramWizard)


if __name__ == '__main__':
    import qdarkstyle
    app = QtWidgets.QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_from_environment())

    with TestProgramWizard() as win:
        sys.exit(app.exec_())
