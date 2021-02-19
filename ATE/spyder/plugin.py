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

from ATE.spyder.project import ATEPluginProject
from ATE.spyder.project import ATEProject
from ATE.spyder.widgets.main_widget import ATEWidget
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
    REQUIRES = [Plugins.Toolbar]   # TODO: fix crash  (Plugins.Editor)
    TABIFY = [Plugins.Projects]
    WIDGET_CLASS = ATEWidget
    CONF_SECTION = NAME

    sig_edit_goto_requested = Signal(str, int, str)
    sig_close_file = Signal(str)
    sig_save_all = Signal()
    sig_exception_occurred = Signal(dict)

    # --- SpyderDockablePlugin API
    # ------------------------------------------------------------------------
    def get_name(self):
        return _("ATE")

    def get_description(self):
        return _("Automatic test equipment.")

    def get_icon(self):
        return QIcon()

    def register(self):
        toolbar = self.get_plugin(Plugins.Toolbar)
        widget = self.get_widget()

        widget.sig_edit_goto_requested.connect(self.sig_edit_goto_requested)
        widget.sig_close_file.connect(self.sig_close_file)
        widget.sig_exception_occurred.connect(self.sig_exception_occurred)

        # Add toolbar
        toolbar.add_application_toolbar(widget.toolbar)
        widget.toolbar.hide()

        # Register a new project type
        # TODO: Temporal fix
        projects = self._main._PLUGINS["project_explorer"]
        projects.register_project_type(self, ATEProject)
        projects.register_project_type(self, ATEPluginProject)

        editor = self._main._PLUGINS["editor"]
        self.sig_edit_goto_requested.connect(editor.load)
        self.sig_close_file.connect(lambda path: self.close_file(path, editor))
        widget.sig_save_all.connect(editor.save_all)

        # Register a new action to create consoles on the IPythonConsole
        # TODO: Temporal fix
        # zconf_action = self.create_action(
        #     name="show_zconf_dialog",
        #     text="Select kernel from Zero Conf",
        #     tip="",
        #     icon=self.create_icon("run"),
        #     triggered=self.show_zero_conf_dialog,
        # )
        ipython = self._main._PLUGINS["ipython_console"]
        # menu = ipython.get_main_menu()
        # self.add_item_to_menu(
        #     zconf_action,
        #     menu,
        #     "top",
        # )

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
