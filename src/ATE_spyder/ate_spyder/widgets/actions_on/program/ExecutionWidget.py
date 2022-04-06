from typing import List, TYPE_CHECKING

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMenu, QWidget, QTableWidgetItem

if TYPE_CHECKING:
    from ate_spyder.widgets.actions_on.program.TestProgramWizard import TestProgramWizard


class ExecutionWidget(QWidget):
    def __init__(self, parent: "TestProgramWizard") -> None:
        super().__init__(parent=parent)
        uic.loadUi(__file__.replace(".py", ".ui"), self)
        self.tp_wizard: TestProgramWizard = parent
        self._setup_ui()
        self._setup_handlers()
        self._init_table()

    def _setup_ui(self):
        self.default_brush = QTableWidgetItem('').background()

    def _setup_handlers(self):
        self.execution.cellClicked.connect(self._execution_cell_clicked)

    def _get_parallelism_names(self) -> List[str]:
        return list(
            self.tp_wizard.parallelism_store.get_all_matching_base(
                self.tp_wizard.project_info.active_base
            ).keys()
        )

    def _init_table(self):
        rows_text = self.tp_wizard._custom_parameter_handler.get_test_names()
        header_text = self._get_parallelism_names()
        self.execution.setRowCount(len(rows_text))
        self.execution.setVerticalHeaderLabels(rows_text)
        self.execution.setColumnCount(len(header_text))
        self.execution.setHorizontalHeaderLabels(header_text)

        for column_index in range(len(header_text)):
            config_names = self.tp_wizard.parallelism_store.get(header_text[column_index]).get_all_ping_pong_names()
            for row_index in range(len(rows_text)):
                item = QTableWidgetItem(config_names[0] if config_names else '')
                self.execution.setItem(row_index, column_index, item)

    def _set_execution_item_text(self, row, column, parallelism_name, new_ping_pong_id):
        execution_item = self.execution.item(row, column)
        if execution_item is None:
            execution_item = QTableWidgetItem()
            self.execution.setItem(row, column, execution_item)

        set_ping_pong = self.tp_wizard.parallelism_store.get(parallelism_name).get_ping_pong_by_id(new_ping_pong_id)
        if set_ping_pong is None:
            execution_item.setText("")
            execution_item.setBackground(Qt.red)
        else:
            execution_item.setText(set_ping_pong.name)
            execution_item.setBackground(self.default_brush)

    def _execution_cell_clicked(self, row, column):
        parallelism_name = self.execution.horizontalHeaderItem(column).text()
        menu = QMenu(self.tp_wizard)
        for ping_pong_name in self.tp_wizard.parallelism_store.get(parallelism_name).get_all_ping_pong_names():
            menu.addAction(ping_pong_name)

        sel_action = menu.exec_(QCursor.pos())
        if sel_action is None:
            return
        new_ping_pong_name = sel_action.text()
        row_name = self.execution.verticalHeaderItem(row).text()
        column_name = self.execution.horizontalHeaderItem(column).text()
        test, test_index = self.tp_wizard._custom_parameter_handler.get_test(row_name)
        assert row == test_index
        test.executions[column_name] = self.tp_wizard.parallelism_store.get(parallelism_name).get_ping_pong(new_ping_pong_name).id
        self._set_execution_item_text(row, column, column_name, test.executions[column_name])
        self.tp_wizard._verify()

    def update_rows_view(self):
        tests = self.tp_wizard._custom_parameter_handler.get_tests()
        rows_text = [test.get_test_name() for test in tests]
        header_text = self._get_parallelism_names()
        if not header_text:
            return
        self.execution.setRowCount(len(rows_text))
        self.execution.setVerticalHeaderLabels(rows_text)
        self.execution.setColumnCount(len(header_text))
        self.execution.setHorizontalHeaderLabels(header_text)

        for row_index in range(len(tests)):
            test = tests[row_index]
            assert self.execution.verticalHeaderItem(row_index).text() == test.get_test_name()
            for column_index, (expected_column_name, ping_pong_id) in enumerate(test.executions.items()):
                assert self.execution.horizontalHeaderItem(column_index).text() == expected_column_name
                self._set_execution_item_text(row_index, column_index, expected_column_name, ping_pong_id)
        self.execution.clearSelection()

    def ping_pong_remove_handler(self, parallelism_name: str, removed_ping_pong_id: int):
        for test in self.tp_wizard._custom_parameter_handler.get_tests():
            if removed_ping_pong_id in test.executions.values():
                test.executions[parallelism_name] = None
        self.update_rows_view()
        self.tp_wizard._verify()

    def verify_execution(self) -> bool:
        tests = self.tp_wizard._custom_parameter_handler.get_tests()
        for test in tests:
            if (
                None in test.executions.values()
                or len(test.executions) != self.tp_wizard.parallelism_store.get_count_matching_base(self.tp_wizard.project_info.active_base)
            ):
                return False
        return True
