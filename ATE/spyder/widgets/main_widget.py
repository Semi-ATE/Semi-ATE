"""
ATE widget.
"""

# Standard library imports
import os
import sys

# Third party imports
from qtpy.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QTreeView
from qtpy.QtCore import Qt

# Local imports
from spyder.api.translations import get_translation
from spyder.api.widgets import PluginMainWidget
from spyder.api.widgets.toolbars import ApplicationToolBar

from ATE.spyder.widgets.navigation import ProjectNavigation
from ATE.spyder.widgets.actions_on.project.ProjectWizard import NewProjectDialog

# Localization
_ = get_translation('spyder')


class ATEWidget(PluginMainWidget):
    """
    ATE widget.
    """

    DEFAULT_OPTIONS = {}

    # --- Signals
    # ------------------------------------------------------------------------

    def __init__(self, name=None, plugin=None, parent=None,
                 options=DEFAULT_OPTIONS):
        super().__init__(name, plugin, parent=parent, options=options)

        # Widgets
        self.tree = QTreeView()
        self.tree.setHeaderHidden(True)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.context_menu_manager)

        self.toolbar = ApplicationToolBar(self, "ATE Plugin toolbar")
        self.label_hardware = QLabel("Hardware")
        self.label_base = QLabel("Base")
        self.label_target = QLabel("Target")
        self.combo_hardware = QComboBox(parent=self)
        self.combo_base = QComboBox(parent=self)
        self.combo_target = QComboBox(parent=self)

        # TODO: simplify the navigator to get ride of 'workspace_path'
        self.project_info = ProjectNavigation('', '')

        # TODO: Temporary workaround
        self.label_hardware.setStyleSheet("background-color: transparent;")
        self.label_base.setStyleSheet("background-color: transparent;")
        self.label_target.setStyleSheet("background-color: transparent;")

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

        run_action = self.create_action(
            name="run_ate",
            text="Run",
            icon=self.create_icon("run"),
            triggered=self.run_ate_project,
        )

        # Add items to toolbar
        for item in [run_action, self.label_hardware,
                     self.combo_hardware, self.label_base, self.combo_base,
                     self.label_target, self.combo_target]:
            self.add_item_to_toolbar(
                item,
                self.toolbar,
                "run",
            )

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
        print("implement call to spyder API")

    def create_project(self, project_path):
        print(f"main_widget : Creating ATE project '{os.path.basename(project_path)}'")

        new_project_name, new_project_quality = NewProjectDialog(self, os.path.basename(project_path), self.project_info)
        if not new_project_name:
            return

        self.toolbar(self.project_info)
        self.set_tree()

    def open_project(self, project_path):
        print(f"main_widget : Opening ATE project '{os.path.basename(project_path)}'")

    def close_project(self):
        print(f"main_widget : Closing ATE project '{os.path.basename(project_path)}'")
