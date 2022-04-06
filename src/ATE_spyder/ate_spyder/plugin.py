"""
ATE Plugin.
"""
# Standard library imports
import os

from qtpy.QtCore import Signal
from qtpy.QtGui import QIcon
from spyder.api.plugins import Plugins
from spyder.api.plugins import SpyderDockablePlugin
from spyder.api.translations import get_translation
from spyder.api.plugin_registration.decorators import on_plugin_available

from ate_spyder.project import ATEPluginProject
from ate_spyder.project import ATEProject
from ate_spyder.widgets.main_widget import ATEWidget
# Third party imports
# Local imports

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
    TABIFY = [Plugins.Projects]
    WIDGET_CLASS = ATEWidget
    CONF_SECTION = NAME

    sig_edit_goto_requested = Signal(str, int, str)
    sig_close_file = Signal(str)
    sig_save_all = Signal()
    sig_exception_occurred = Signal(dict)

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
        widget.sig_close_file.connect(self.sig_close_file)
        widget.sig_exception_occurred.connect(self.sig_exception_occurred)

    @on_plugin_available(plugin=Plugins.Toolbar)
    def on_toolbar_available(self):
        widget = self.get_widget()
        toolbar = self.get_plugin(Plugins.Toolbar)
        toolbar.add_application_toolbar(widget.toolbar)
        widget.toolbar.hide()

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
        self.sig_close_file.connect(lambda path: self.close_file(path, editor))
        widget.sig_save_all.connect(editor.save_all)

    def on_mainwindow_visible(self):
        # Hide by default the first time the plugin is loaded.
        if self.get_conf('first_time_shown', True):
            self.get_widget().toggle_view(False)
            self.set_conf('first_time_shown', False)

    # --- ATE Plugin API
    # ------------------------------------------------------------------------
    def create_project(self, project_root):
        print(f"Plugin : Creating ATE project '{os.path.basename(project_root)}'")
        self.project_root = project_root
        self.get_widget().create_project(project_root)

    def open_project(self, project_root):
        print(f"Plugin : Opening ATE project '{os.path.basename(project_root)}'")
        self.project_root = project_root
        self.get_widget().open_project(project_root)

    def close_project(self):
        print("Plugin : Closing ATE project '{os.path.basename(self.project_root)}'")
        self.get_widget().close_project()

    @staticmethod
    def close_file(path, editor):
        if not editor.is_file_opened(path):
            return

        editor.close_file_in_all_editorstacks(str(id(editor)), path)
