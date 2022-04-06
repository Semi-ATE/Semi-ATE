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
from ate_spyder.widgets.main_widget import ATEWidget

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
    # ------------------------------------------------------------------------:

    # --- SpyderDockablePlugin API
    # ------------------------------------------------------------------------
    def get_name(self):
        return _("ATE")

    def get_description(self):
        return _("Automatic test equipment.")

    def get_icon(self):
        return QIcon()

    def on_initialize(self):
        widget = self.get_widget()
        self.add_application_toolbar('ate_toolbar', widget.toolbar)
