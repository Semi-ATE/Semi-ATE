"""
ATE widget.
"""

# Standard library imports
import sys

# Third party imports
from qtpy.QtWidgets import QWidget, QVBoxLayout

# Local imports
from spyder.api.translations import get_translation
from spyder.api.widgets import PluginMainWidget


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
        self.tree = QWidget()

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
        pass

    def on_option_update(self, option, value):
        pass

    def update_actions(self):
        pass
