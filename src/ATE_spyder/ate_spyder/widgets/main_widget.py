"""
ATE widget.
"""
# Standard library imports
import os
import os.path as osp
from pathlib import Path
import shutil
import logging

# Local imports
from ate_spyder.widgets.constants import ATEActions
from ate_spyder.widgets.actions_on.project.ProjectWizard import new_project_dialog
from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.toolbar import ToolBar
from ate_spyder.widgets.statusbar import ATEStatusBar
from ate_spyder.widgets.actions_on.tests.TestItems.TestItemChild import (TestItemChild, TestItemChildTarget)
from ate_spyder.project import ATEProject

# Third party imports
import zmq
from qtpy.QtCore import Qt, Signal, QProcess, QSocketNotifier
from qtpy.QtWidgets import QTreeView, QVBoxLayout, QDialog
from spyder.api.translations import get_translation
from spyder.api.widgets.main_widget import PluginMainWidget


# Localization
_ = get_translation('spyder')
logger = logging.getLogger(__name__)


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
    sig_update_statusbar = Signal(str)

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

    # --- PluginMainWidget API
    # ------------------------------------------------------------------------
    def get_title(self):
        return _('ATE')

    def get_focus_widget(self):
        return self.tree

    def setup(self):
        self.model = None
        self.stil_process = None
        self.stil_process_running = False

        self.zmq_context = zmq.Context.instance()
        self.stil_sock = self.zmq_context.socket(zmq.PULL)
        self.stil_port = self.stil_sock.bind_to_random_port('tcp://127.0.0.1')

        fid = self.stil_sock.getsockopt(zmq.FD)
        self.notifier = QSocketNotifier(fid, QSocketNotifier.Read, self)
        self.notifier.activated.connect(self.on_stil_msg_received)

        self.statusbar = ATEStatusBar(self)
        self.sig_update_statusbar.connect(self.statusbar.sig_update_value)

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

        self.run_stil_action = self.create_action(
            ATEActions.RunStil, _('Compile STIL files'),
            self.create_icon('run_again'), tip=_('Compile STIL files'),
            triggered=self.compile_stil
        )

        self.run_stil_action.setEnabled(False)

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
        project_loaded = False
        if not os.path.exists(project_path):
            # hack: make sure to re-open with a valid project name
            # while creating a new project spyder do not validate the project name the way semi-ate plugin is expecting it
            # so we make spyder-ide load a project only if Semi-ATE Plugin approved it
            if not self.project_info.project_directory:
                # spyder ide may not recognize path changes done by semi-ate plugin
                # so we clear up the interface by closing the project for both the plugin and spyder
                parent_instance.close_project()
                self.close_project()

            parent_instance.open_project(path=self.project_info.project_directory)
            project_loaded = True
        else:
            # in case the project exist we only reload the project navigator with the new project path
            # but we still need to make sure that the project type is 'Semi-ATE Project'

            # extract project type from workspace.ini inside .spydrproject folder
            default_spyder_project_configuration_file_relative_path = '.spyproject/config/workspace.ini'
            config_file_path = Path(project_path).joinpath(default_spyder_project_configuration_file_relative_path)
            if not config_file_path.exists:
                print("could not find configuration file 'workspace.init' ")

            if self._is_semi_ate_project(config_file_path):
                self.project_info(project_path)

                self.toolbar(self.project_info)
                self.set_tree()
                self.init_done.emit()
                project_loaded = True

        self.run_stil_action.setEnabled(project_loaded)
        return project_loaded

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

    def compile_stil(self):
        if self.stil_process_running:
            self.stil_process.kill()
            return

        self.stil_process = QProcess(self)
        # self.stil_process.errorOccurred.connect(self.stil_process_failed)
        self.stil_process.finished.connect(self.stil_process_finished)

        # TODO: Determine STIL file location adequately
        project_path = self.project_info.project_directory
        cwd = os.path.join(project_path, 'patterns')
        env = self.stil_process.processEnvironment()

        for var in os.environ:
            env.insert(var, os.environ[var])

        self.stil_process.setProcessEnvironment(env)
        self.stil_process.setWorkingDirectory(cwd)

        # TODO: Determine which STIL file to run
        stil_file_location = osp.join(cwd, 'test_atpg_1.stil')
        args = ['sscl', '-c', '-i', stil_file_location, '--port',
                str(self.stil_port)]

        self.stil_process.setProcessChannelMode(QProcess.ForwardedChannels)
        self.stil_process.start(args[0], args[1:])
        self.stil_process_running = True
        self.run_stil_action.setIcon(self.create_icon('stop'))

    def stil_process_finished(self, exit_code, exit_status):
        self.stil_process_running = False
        self.stil_process = None
        self.run_stil_action.setIcon(self.create_icon('run_again'))

    def on_stil_msg_received(self):
        try:
            response = self.stil_sock.recv_json(flags=zmq.NOBLOCK)
        except zmq.ZMQError:
            return

        if response['kind'] == 'info':
            payload = response['payload']
            message = payload['message']
            logger.info(message)
            self.sig_update_statusbar.emit(message)
