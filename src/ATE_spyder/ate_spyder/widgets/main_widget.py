"""
ATE widget.
"""
# Standard library imports
from qtpy.QtCore import Qt
from qtpy.QtCore import Signal
from qtpy.QtWidgets import QTreeView
from qtpy.QtWidgets import QVBoxLayout
from qtpy.QtWidgets import QDialog

import os
from pathlib import Path
import shutil

# Local imports
from ate_spyder.widgets.actions_on.project.ProjectWizard import new_project_dialog
from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.toolbar import ToolBar
from ate_spyder.widgets.actions_on.tests.TestItems.TestItemChild import (TestItemChild, TestItemChildTarget)
from ate_spyder.widgets.actions_on.patterns.PatternItem import PatternItemChild
from ate_spyder.project import ATEProject

# Third party imports
from spyder.api.translations import get_translation
from spyder.api.widgets.main_widget import PluginMainWidget


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
    init_done = Signal()

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

        if isinstance(model_item, PatternItemChild):
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

    def create_project(self, project_path) -> bool:
        status = new_project_dialog(self.project_info, project_path)

        # hack: as spyder automatically create an empty project even before semi-ate project validation done
        # we need to clean up after canceling creating the project
        if status == QDialog.DialogCode.Rejected:
            shutil.rmtree(project_path)
            return False

        print(f"main_widget : Creating ATE project '{os.path.basename(project_path)}'")
        return True

    def open_project(self, project_path, parent_instance) -> bool:
        if not os.path.exists(project_path):
            # hack: make sure to re-open with a valid project name
            # while creating a new project spyder do not validate the project name the way semi-ate plugin is expecting it
            # so we make spyder-ide load a project only if Semi-ATE Plugin approved it
            if not self.project_info.project_directory:
                # spyder ide may not recognize path changes done by semi-ate plugin
                # so we clear up the interface by closing the project for both the plugin and spyder
                parent_instance.close_project()
                self.close_project()
                return False

            parent_instance.open_project(path=self.project_info.project_directory)
            return True
        else:
            # in case the project exist we only reload the project navigator with the new project path
            # but we still need to make sure that the project type is 'Semi-ATE Project'

            # extract project type from workspace.ini inside .spydrproject folder
            default_spyder_project_configuration_file_relative_path = '.spyproject/config/workspace.ini'
            config_file_path = Path(project_path).joinpath(default_spyder_project_configuration_file_relative_path)
            if not config_file_path.exists:
                print("could not find configuration file 'workspace.init' ")
                return False

            if self._is_semi_ate_project(config_file_path):
                self.project_info(project_path)

                from ate_projectdatabase import latest_semi_ate_project_db_version
                project_version = self.project_info.get_version()
                if (project_version != latest_semi_ate_project_db_version):
                    try:
                        raise Exception(f'''\n
Migration required:\n
Project version: '{project_version}' differs from Semi-ATE Plugin version: '{latest_semi_ate_project_db_version}'\n
To prevent any inconsistencies the project must be migrated\n
Execute the following commands inside the project root\n
$ sammy migrate\n
Running the generate all command shall refresh the generated code based on the template files\n
$ sammy generate all\n
                    ''')
                    except Exception as e:
                        from ate_spyder.widgets.actions_on.utils.ExceptionHandler import report_exception
                        report_exception(self.project_info.parent, "migration required")
                        self.close_project()
                        return False

                self.toolbar(self.project_info)
                self.set_tree()
                self.init_done.emit()
                return True
            else:
                print(f'project type is not: {ATEProject.ID}')

        return False

    def _is_semi_ate_project(self, config_file_path: Path) -> bool:
        with open(config_file_path, 'r') as file:
            for line in file.readlines():
                # the 'project_type' key is valid in the current version of spyder(5.3.1)
                # but any changes to the 'workspace.ini' file structure will break this check and
                # we will never be able to open a Semi-ATE project!!
                # (so maybe propagate this issue to spyder organization)
                if 'project_type' in line and ATEProject.ID in line:
                    return True
        return False

    def close_project(self):
        print(f"main_widget : Closing ATE project '{os.path.basename(self.project_info.project_directory)}'")
        self.toolbar.clean_up()
        self.project_info.project_name = ''
        self.project_info.project_directory = ''
        self.tree.setModel(None)

    def delete_test(self, path):
        from pathlib import Path
        import os
        self.sig_close_file.emit(os.fspath(Path(path)))
