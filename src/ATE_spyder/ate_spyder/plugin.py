"""
ATE Plugin.
"""
# Standard library imports
import os
from typing import Type
from ate_spyder.widgets.navigation import ProjectNavigation

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
from ate_spyder.widgets.constants import ATEActions, ATEToolbars, ATEStatusBars

# Localization
_ = get_translation('spyder')


# --- Plugin
# ----------------------------------------------------------------------------
class ATE(SpyderDockablePlugin):
    """
    Breakpoint list Plugin.
    """
    NAME = 'ate'
    REQUIRES = [Plugins.Toolbar, Plugins.Projects, Plugins.Editor]   # TODO: fix crash  (Plugins.Editor)
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

    @on_plugin_available(plugin=Plugins.Toolbar)
    def on_toolbar_available(self):
        widget = self.get_widget()
        toolbar = self.get_plugin(Plugins.Toolbar)

        # extend semi-ate toolbar with labml extension (written by Zlin526F)
        lab_ml_package_name = 'labml-adjutancy'
        import pkg_resources
        packages = [pkg.key for pkg in pkg_resources.working_set]
        if lab_ml_package_name in packages:
            from labml_adjutancy.ctrl.toolbar import ControlToolBar
            control_toolbar = ControlToolBar(widget, "ATE Plugin control toolbar")
            widget.toolbar.add_external_toolbar_item(control_toolbar.get_items())

        toolbar.add_application_toolbar(widget.toolbar)
        widget.toolbar.build()

    @on_plugin_available(plugin=Plugins.Projects)
    def on_projects_available(self):
        projects = self.get_plugin(Plugins.Projects)
        projects.register_project_type(self, ATEProject)
        projects.register_project_type(self, ATEPluginProject)
        projects.sig_project_loaded.connect(self.open_project)
        projects.sig_project_closed.connect(self.close_project)

    @on_plugin_available(plugin=Plugins.Editor)
    def on_editor_available(self):
        widget = self.get_widget()
        editor = self.get_plugin(Plugins.Editor)
        self.sig_edit_goto_requested.connect(editor.load)

        self.sig_run_cell.connect(editor.run_cell)
        self.sig_debug_cell.connect(editor.debug_cell)

        self.sig_close_file.connect(lambda path: self.close_file(path, editor))
        widget.sig_save_all.connect(editor.save_all)

    @on_plugin_teardown(plugin=Plugins.Toolbar)
    def on_toolbar_teardown(self):
        toolbar = self.get_plugin(Plugins.Toolbar)
        toolbar.remove_application_toolbar(ATEToolbars.ATE)

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
        print("Plugin : Creating ATE project "
              f"'{os.path.basename(self.project_root)}'")

    def open_project(self, project_root):
        self.project_root = project_root
        projects = self.get_plugin(Plugins.Projects)
        # hide semi-ate toolbar if opening the project was not successful
        if not self.get_widget().open_project(project_root, projects):
            self.get_widget().hide()
            self.get_widget().toolbar.hide()
        else:
            self.get_widget().show()
            self.get_widget().toolbar.show()

        print(f"Plugin : Opening ATE project '{os.path.basename(project_root)}'")

    def close_project(self):
        print(f"Plugin : Closing ATE project '{os.path.basename(self.project_root)}'")
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

    def get_project_navigation(self) -> ProjectNavigation:
        return self.get_widget().get_project_navigation()
