"""
ATE widget.
"""

# Standard library imports
import sys

# Third party imports
from qtpy.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel

# Local imports
from spyder.api.translations import get_translation
from spyder.api.widgets import PluginMainWidget
from spyder.api.widgets.toolbars import ApplicationToolBar


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
        self.toolbar = ApplicationToolBar(self, "ATE Plugin toolbar")
        self.label_hardware = QLabel("Hardware")
        self.label_base = QLabel("Base")
        self.label_target = QLabel("Target")
        self.combo_hardware = QComboBox(parent=self)
        self.combo_base = QComboBox(parent=self)
        self.combo_target = QComboBox(parent=self)

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
        refresh_action = self.create_action(
            name="refresh_ate",
            text="Refresh",
            icon=self.create_icon("refresh"),
            triggered=self.refresh_ate,
        )

        run_action = self.create_action(
            name="run_ate",
            text="Run",
            icon=self.create_icon("run"),
            triggered=self.run_ate_project,
        )

        # Add items to toolbar
        for item in [refresh_action, run_action, self.label_hardware,
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
        pass

    def refresh_ate(self):
        pass
