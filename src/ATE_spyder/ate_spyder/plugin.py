"""
ATE Plugin.
"""
# Standard library imports
import logging
import os
from typing import Type

# Third party imports
from qtpy.QtCore import Signal
from qtpy.QtGui import QIcon
from spyder.api.plugins import Plugins, SpyderDockablePlugin
from spyder.api.translations import get_translation
from spyder.api.plugin_registration.decorators import (
    on_plugin_available, on_plugin_teardown)

# Local imports
from ate_spyder.project import ATEProject, ATEPluginProject
from ate_spyder.widgets.main_widget import ATEWidget
from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.vcs import VCSInitializationProvider
from ate_spyder.widgets.constants import ATEToolbars
from spyder import __version__ as spyder_version

# Localization
_ = get_translation('spyder')

# Logging
logger = logging.getLogger(__name__)


# --- Plugin
# ----------------------------------------------------------------------------
class ATE(SpyderDockablePlugin):
    """
    Breakpoint list Plugin.
    """
    NAME = 'ate'
    REQUIRES = [Plugins.Toolbar, Plugins.Projects, Plugins.Editor, Plugins.IPythonConsole]   # TODO: fix crash  (Plugins.Editor)
    OPTIONAL = [Plugins.StatusBar]
    TABIFY = [Plugins.Projects]
    WIDGET_CLASS = ATEWidget
    CONF_SECTION = NAME

    sig_edit_goto_requested = Signal(str, int, str)
    sig_close_file = Signal(str)
    sig_save_all = Signal()
    sig_exception_occurred = Signal(dict)
    sig_ate_project_changed = Signal(bool)
    """
    Signal that indicates if an ATE project gets loaded or not.

    Parameters
    ----------
    ate_project_loaded: bool
        True if an ATE project was loaded, False otherwise.
    """

    sig_compile_pattern = Signal(list, str)
    """
    Compile STIL pattern

    Parameters
    ---------
    stil_path: List[str]
        List containing all the full paths to the STIL patterns to compile.
    """

    sig_ate_project_created = Signal()
    sig_ate_project_loaded = Signal()

    sig_run_cell = Signal()
    sig_debug_cell = Signal()
    sig_stop_debugging = Signal()
    sig_ate_progname = Signal(str)

    sig_test_tree_update = Signal()
    # --- SpyderDockablePlugin API
    # ------------------------------------------------------------------------
    @staticmethod
    def get_name():
        return _("ATE")

    def get_description(self):
        return _("Automatic test equipment.")

    def get_icon(self):
        return QIcon()

    def on_initialize(self):
        logger.debug("ATE_spyder:on_initialize")
        widget = self.get_widget()
        widget.sig_edit_goto_requested.connect(self.sig_edit_goto_requested)

        widget.sig_run_cell.connect(self.sig_run_cell)
        widget.sig_debug_cell.connect(self.sig_debug_cell)

        widget.sig_edit_goto_requested.connect(self.sig_edit_goto_requested)
        widget.sig_ate_progname.connect(self.sig_ate_progname)

        widget.sig_close_file.connect(self.sig_close_file)
        widget.sig_exception_occurred.connect(self.sig_exception_occurred)

        widget.sig_ate_project_changed.connect(self.sig_ate_project_changed)
        widget.sig_compile_pattern.connect(self.sig_compile_pattern)
        widget.sig_project_created.connect(self.project_created)
        widget.sig_project_created.connect(self.sig_ate_project_created)
        widget.sig_project_loaded.connect(self.sig_ate_project_loaded)
        widget.sig_test_tree_update.connect(self.sig_test_tree_update)
        logger.debug("ATE_spyder:on_initialize done")

    @on_plugin_available(plugin=Plugins.Toolbar)
    def on_toolbar_available(self):
        logger.debug("ATE_spyder:on_toolbar_available start")
        widget = self.get_widget()
        toolbar = self.get_plugin(Plugins.Toolbar)

        # extend semi-ate toolbar with labml extension (written by Zlin526F)
        lab_ml_package_name = 'labml-adjutancy'

        from importlib.metadata import version, PackageNotFoundError

        try:
            version(lab_ml_package_name)  # wirft PackageNotFoundError wenn nicht installiert
            from labml_adjutancy.ctrl.toolbar import ControlToolBar
            control_toolbar = ControlToolBar(widget, "ATE Plugin control toolbar")
            widget.toolbar.add_external_toolbar_item(control_toolbar.get_items())
        except PackageNotFoundError:
            pass  # Paket ist nicht installiert → nichts tun
        except Exception as ex:
            logger.error(f"ATE_spyder:on_toolbar_available Exception: {ex}")

        toolbar.add_application_toolbar(widget.toolbar)
        widget.toolbar.build()
        logger.debug("ATE_spyder:on_toolbar_available done.")

    @on_plugin_available(plugin=Plugins.Projects)
    def on_projects_available(self):
        logger.debug("ATE_spyder:on_projects_available")
        projects = self.get_plugin(Plugins.Projects)
        projects.register_project_type(self, ATEProject)
        projects.register_project_type(self, ATEPluginProject)
        projects.sig_project_loaded.connect(self.open_project)
        projects.sig_project_closed.connect(self.close_project)
        logger.debug("ATE_spyder:on_projects_available done.")

    @on_plugin_available(plugin=Plugins.Editor)
    def on_editor_available(self):
        logger.debug("ATE_spyder:on_editor_available")
        widget = self.get_widget()
        editor = self.get_plugin(Plugins.Editor)
        self.sig_edit_goto_requested.connect(editor.load)

        if spyder_version == "5.5.6":
            self.sig_run_cell.connect(editor.run_cell)
            self.sig_debug_cell.connect(editor.debug_cell)

        self.sig_close_file.connect(lambda path: self.close_file(path, editor))
        widget.sig_save_all.connect(editor.save_all)
        logger.debug("ATE_spyder:on_editor_available done.")
 
    # new connection for Spyder 6 to the IPythonConsole Plugin instead the Editor
    @on_plugin_available(plugin=Plugins.IPythonConsole)
    def on_ipython_console_available(self):
        """Connect run_cell and debug_cell to IPythonConsole"""
        logger.debug("ATE_spyder:on_ipython_console_available")
        if spyder_version > "5.5.6":
            self.sig_run_cell.connect(self.run_cell_in_console)
            self.sig_debug_cell.connect(self.debug_cell_in_console)
        logger.debug("ATE_spyder:on_ipython_console_available done.")

    def run_cell_in_console(self):
        logger.debug("ATE_spyder:run_cell_in_console start.")
        editor = self.get_plugin(Plugins.Editor)
        console = self.get_plugin(Plugins.IPythonConsole)
        editorstack = editor.get_current_editorstack()
        codeeditor = editorstack.get_current_editor()
        filename = codeeditor.filename
        wdir = os.path.dirname(filename)

        console.run_script(filename, wdir=wdir)
        logger.debug(f"ATE_spyder:run_cell_in_console done: {filename}")
        
    def debug_cell_in_console(self):
        logger.debug("Debug ist not supported, continue with run_cell_in_console")
        self.run_cell_in_console()

    @on_plugin_teardown(plugin=Plugins.Toolbar)
    def on_toolbar_teardown(self):
        logger.debug("ATE_spyder:on_toolbar_teardown")
        toolbar = self.get_plugin(Plugins.Toolbar)
        toolbar.remove_application_toolbar(ATEToolbars.ATE)
        logger.debug("ATE_spyder:on_toolbar_teardown done")

    def on_mainwindow_visible(self):
        # Hide by default the first time the plugin is loaded.
        if self.get_conf('first_time_shown', True):
            self.get_widget().toggle_view(False)
            self.set_conf('first_time_shown', False)

    # --- ATE Plugin API
    # ------------------------------------------------------------------------
    def create_project(self, project_root):
        self.project_root = project_root
        self.get_widget().create_project(project_root)

    def project_created(self):
        logger.debug("Plugin : project_created,  Creating ATE project "
              f"'{os.path.basename(self.project_root)}'")

    def open_project(self, project_root):
        logger.debug(f"ATE_spyder:open_project {project_root}")
        self.project_root = project_root
        projects = self.get_plugin(Plugins.Projects)
        # hide semi-ate toolbar if opening the project was not successful
        if not self.get_widget().open_project(project_root, projects):
            self.get_widget().hide()
            self.get_widget().toolbar.hide()
        else:
            self.get_widget().show()
            self.get_widget().toolbar.show()

        logger.debug(f"Plugin : Opening ATE project '{os.path.basename(project_root)}'")

    def close_project(self):
        logger.debug(f"Plugin : Closing ATE project '{os.path.basename(self.project_root)}'")
        self.get_widget().close_project()

    def get_project_navigation(self) -> ProjectNavigation:
        return self.get_widget().get_project_navigation()

    def add_item_to_toolbar(self, item):
        widget = self.get_widget()
        widget.toolbar.add_item(item)

    def register_version_control_provider(
            self, VCSProviderClass: Type[VCSInitializationProvider]):
        """
        Register a new version control system (VCS) provider.

        Parameters
        ----------
        VCSProviderClass: Type[VCSInitializationProvider]
            The class that implements the `VCSInitializationProvider`
            interface to be registered.
        """
        self.get_widget().register_version_control_provider(VCSProviderClass)

    @staticmethod
    def close_file(path, editor):
        if not editor.is_file_opened(path):
            return

        editor.close_file_in_all_editorstacks(str(id(editor)), path)
