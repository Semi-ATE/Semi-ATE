"""
ATE Plugin.
"""

# Standard library imports
import os

# Third party imports
from qtpy.QtCore import Signal
from qtpy.QtGui import QIcon

# Local imports
from spyder.api.plugins import ApplicationMenus, Plugins, SpyderDockablePlugin
from spyder.api.translations import get_translation
from ATE.spyder.project import ATEProject
from ATE.spyder.widgets.main_widget import ATEWidget

# Localization
_ = get_translation('spyder')


# --- Plugin
# ----------------------------------------------------------------------------
class ATE(SpyderDockablePlugin):
    """
    Breakpoint list Plugin.
    """
    NAME = 'ate'
    REQUIRES = []
    TABIFY = [Plugins.Projects]
    WIDGET_CLASS = ATEWidget
    CONF_SECTION = NAME

    # --- Signals
    # ------------------------------------------------------------------------

    # --- SpyderDockablePlugin API
    # ------------------------------------------------------------------------
    def get_name(self):
        return _("ATE")

    def get_description(self):
        return _("Automatic test equipment.")

    def get_icon(self):
        return QIcon()

    def register(self):
        widget = self.get_widget()

        # Add toolbar
        self.add_application_toolbar('ate_toolbar', widget.toolbar)
        widget.toolbar.hide()

        # Register a new project type
        # TODO: Temporal fix
        projects = self._main._PLUGINS["project_explorer"]
        projects.register_project_type(ATEProject)

        # Register a new action to create consoles on the IPythonConsole
        # TODO: Temporal fix
        zconf_action = self.create_action(
            name="show_zconf_dialog",
            text="Select kernel from Zero Conf",
            tip="",
            icon=self.create_icon("run"),
            triggered=self.show_zero_conf_dialog,
        )
        ipython = self._main._PLUGINS["ipython_console"]
        # menu = ipython.get_main_menu()
        # self.add_item_to_menu(
        #     zconf_action,
        #     menu,
        #     "top",
        # )

    # --- ATE Plugin API
    # ------------------------------------------------------------------------
    def show_zero_conf_dialog(self):
        print("something!")
