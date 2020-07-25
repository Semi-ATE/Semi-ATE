"""
ATE widget.
"""
# Standard library imports
import os
import sys

from qtpy.QtCore import Qt
from qtpy.QtCore import Signal
from qtpy.QtWidgets import QComboBox
from qtpy.QtWidgets import QLabel
from qtpy.QtWidgets import QTreeView
from qtpy.QtWidgets import QVBoxLayout
from qtpy.QtWidgets import QWidget
from spyder.api.translations import get_translation
from spyder.api.widgets import PluginMainWidget
from spyder.api.widgets.toolbars import ApplicationToolBar

from ATE.spyder.widgets.actions_on.project.ProjectWizard import NewProjectDialog
from ATE.spyder.widgets.navigation import ProjectNavigation
from ATE.spyder.widgets.toolbar_original import ToolBar
# Third party imports
#from PyQt5.QtCore import pyqtSignal
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

    def __init__(self, name=None, plugin=None, parent=None,
                 options=DEFAULT_OPTIONS):
        super().__init__(name, plugin, parent=parent, options=options)

        # Widgets
        self.tree = QTreeView()
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.context_menu_manager)

        # TODO: simplify the navigator to get ride of 'workspace_path'
        self.project_info = ProjectNavigation('', self)

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

    def setup(self, options):
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
        item = self.model.itemFromIndex(model_index)
        if item is None:
            return

        item.exec_context_menu()

    def set_tree(self):
        from ATE.spyder.widgets.actions_on.model.TreeModel import TreeModel
        self.model = TreeModel(self.project_info, parent=self)
        self.model.edit_file.connect(self.edit_test)
        self.model.delete_file.connect(self.delete_test)
        self.tree.setModel(self.model)
        self.tree.doubleClicked.connect(self.item_double_clicked)

    def item_double_clicked(self, index):
        try:
            item = self.tree.selectedIndexes()[0]
        except Exception:
            return

        model_item = item.model().itemFromIndex(index)
        from ATE.spyder.widgets.actions_on.tests.TestItem import TestItemChild
        if isinstance(model_item, TestItemChild):
            self.edit_test(model_item.path)

    def edit_test(self, path):
        """This method is called from ATE, and calls Spyder to open the file
        given by path"""
        self.sig_edit_goto_requested.emit(path, 1, "")

    def create_project(self, project_path):
        print(f"main_widget : Creating ATE project '{os.path.basename(project_path)}'")
        status, data = NewProjectDialog(self, os.path.basename(project_path))
        if status:  # OK button pressed
            self.project_info(project_path, data['quality'])
            self.set_tree()
            #self.toolbar(self.project_info)
        else:  # Cancel button pressed
            pass

    def open_project(self, project_path):
        print(f"main_widget : Opening ATE project '{os.path.basename(project_path)}'")
        self.project_info(project_path, self)
        self.toolbar(self.project_info)
        self.set_tree()

    def close_project(self):
        print(f"main_widget : Closing ATE project '{os.path.basename(self.project_info.project_directory)}'")

    def delete_test(self, path):
        selected_file = os.path.basename(path)
        index = self._get_tab_index(selected_file)
        if index == -1:
            return

        self.close_tab(index)
