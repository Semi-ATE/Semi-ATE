"""
ATE widget.
"""
# Standard library imports
import os

from qtpy.QtCore import Qt
from qtpy.QtCore import Signal
from qtpy.QtWidgets import QTreeView
from qtpy.QtWidgets import QVBoxLayout
from spyder.api.translations import get_translation
from spyder.api.widgets.main_widget import PluginMainWidget

from ate_spyder.widgets.actions_on.project.ProjectWizard import new_project_dialog
from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.toolbar import ToolBar
from ate_spyder.widgets.actions_on.tests.TestItems.TestItemChild import (TestItemChild, TestItemChildTarget)
# Third party imports
# Local imports

# Localization
_ = get_translation('spyder')


class ATEWidget(PluginMainWidget):
    """
    ATE widget.
    """

    DEFAULT_OPTIONS = {}

    # --- Signals
    # ------------------------------------------------------------------------
    sig_edit_goto_requested = Signal(str, int, str)
    sig_close_file = Signal(str)
    sig_save_all = Signal()
    sig_exception_occurred = Signal(dict)

    database_changed = Signal(int)
    toolbar_changed = Signal(str, str, str)
    active_project_changed = Signal()
    hardware_added = Signal(str)
    hardware_activated = Signal(str)
    hardware_removed = Signal(str)
    update_target = Signal()
    select_target = Signal(str)
    select_base = Signal(str)
    select_hardware = Signal(str)
    update_settings = Signal(str, str, str)
    test_target_deleted = Signal(str, str)
    group_state_changed = Signal()
    group_added = Signal(str)
    group_removed = Signal(str)
    groups_update = Signal(str, list)

    def __init__(self, name=None, plugin=None, parent=None):
        super().__init__(name, plugin, parent=parent)

        # Widgets
        self.model = None
        self.tree = QTreeView()
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.context_menu_manager)

        # TODO: simplify the navigator to get ride of 'workspace_path'
        homedir = os.path.expanduser("~")
        self.project_info = ProjectNavigation('', homedir, self)

        self.toolbar = ToolBar(self.project_info, self, "ATE Plugin toolbar")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        self.setLayout(layout)

        # Signals

    # --- PluginMainWidget API
    # ------------------------------------------------------------------------
    def get_title(self):
        return _('ATE')

    def get_focus_widget(self):
        return self.tree

    def setup(self):
        return

    def on_option_update(self, option, value):
        pass

    def update_actions(self):
        pass

    # --- PluginMainWidget API
    # ------------------------------------------------------------------------
    def run_ate_project(self):
        """For now the run of an ATE project is not integrated in the global
        run button yet"""
        pass

    def context_menu_manager(self, point):
        # https://riverbankcomputing.com/pipermail/pyqt/2009-April/022668.html
        # https://doc.qt.io/qt-5/qtreewidget-members.html
        # https://www.qtcentre.org/threads/18929-QTreeWidgetItem-have-contextMenu
        # https://cdn.materialdesignicons.com/4.9.95/
        indexes = self.tree.selectedIndexes()
        if indexes is None:
            return

        model_index = self.tree.indexAt(point)

        if not self.model:
            return

        item = self.model.itemFromIndex(model_index)
        if item is None:
            return

        item.exec_context_menu()

    def set_tree(self):
        from ate_spyder.widgets.actions_on.model.TreeModel import TreeModel
        self.model = TreeModel(self.project_info, parent=self)
        self.model.edit_file.connect(self.open_test_file)
        self.model.delete_file.connect(self.delete_test)
        self.model.edit_test_params.connect(self.edit_test)
        self.tree.setModel(self.model)
        self.tree.doubleClicked.connect(self.item_double_clicked)

    def item_double_clicked(self, index):
        try:
            item = self.tree.selectedIndexes()[0]
        except Exception:
            return

        model_item = item.model().itemFromIndex(index)
        if isinstance(model_item, TestItemChild):
            self.open_test_file(model_item.path)

        if isinstance(model_item, TestItemChildTarget):
            self.open_test_file(model_item.get_path())

    def open_test_file(self, path):
        """This method is called from ATE, and calls Spyder to open the file
        given by path"""
        self.sig_edit_goto_requested.emit(path, 1, "")

    def edit_test(self):
        # save all pending changes before editing any test, it doesn't matter if it is open !
        # to make sure that any changes provoke new code generation do not override the own code
        self.sig_save_all.emit()

    def create_project(self, project_path):
        print(f"main_widget : Creating ATE project '{os.path.basename(project_path)}'")
        self.project_info(project_path)
        new_project_dialog(self.project_info)
        self.set_tree()

    def open_project(self, project_path):
        print(f"main_widget : Opening ATE project '{os.path.basename(project_path)}'")
        self.project_info(project_path)
        self.toolbar(self.project_info)
        self.set_tree()

    def close_project(self):
        print(f"main_widget : Closing ATE project '{os.path.basename(self.project_info.project_directory)}'")
        self.toolbar.clean_up()
        self.project_info.project_name = ''
        self.tree.setModel(None)

    def delete_test(self, path):
        from pathlib import Path
        import os
        self.sig_close_file.emit(os.fspath(Path(path)))
