# -*- coding: utf-8 -*-
#
# Copyright © Semi-ATE
# Licensed under the terms of the GPLv2 License
# (see LICENSE.txt for more details)


# Standard library imports

# Third-party imports

# Spyder imports
from spyder.api.plugins import Plugins, SpyderDockablePlugin
from spyder.api.translations import get_translation
from spyder.api.plugin_registration.decorators import on_plugin_available, on_plugin_teardown

from qtpy.QtCore import Signal

# Local imports
from ate_spyder_lab_control.widgets.gui_widget import LabGui
from ate_spyder.plugin import ATE

# Localization
_ = get_translation("spyder")


class LabGuiPlugin(SpyderDockablePlugin):
    """Labor Gui dockable plugin."""

    NAME = 'lab_gui'
    WIDGET_CLASS = LabGui
    CONF_SECTION = NAME
    REQUIRES = [ATE.NAME]
    OPTIONAL = [Plugins.MainMenu, Plugins.Projects]
    CONF_FILE = False
    TABIFY = [Plugins.Help]

    sig_edit_goto_requested = Signal(str, int, str)
    sig_run_cell = Signal()
    sig_debug_cell = Signal()
    sig_stop_debugging = Signal()

    # --- SpyderDockablePlugin API
    # ------------------------------------------------------------------------

    @staticmethod
    def get_name() -> str:
        return _('Lab_GUI')

    def get_description(self) -> str:
        return _('Lab Gui integration')

    def get_icon(self):
        return self.create_icon('mdi.chip')

    def on_initialize(self):
        pass
        # widget = self.get_widget()

    def update_font(self):
        pass

    # -------------------- Plugin initialization ------------------------------
    @on_plugin_available(plugin=ATE.NAME)
    def on_ate_available(self):
        widget: LabGui = self.get_widget()
        ate: ATE = self.get_plugin(ATE.NAME)
        ate.sig_ate_project_loaded.connect(self._setup_test_runner_widget)
        ate.sig_ate_progname.connect(self.runflow_changed)
        ate.sig_test_tree_update.connect(self.update_actions)
        ate.sig_stop_debugging.connect(widget.debug_stop)

    def _setup_test_runner_widget(self):
        widget: LabGui = self.get_widget()
        ate: ATE = self.get_plugin(ATE.NAME)
        project_info = ate.get_project_navigation()
        widget.setup_widget(project_info)

    @on_plugin_available(plugin=Plugins.Projects)
    def on_projects_available(self):
        projects = self.get_plugin(Plugins.Projects)
        projects.sig_project_closed.connect(self.project_closed)

    def project_closed(self):
        pass

    def runflow_changed(self, progname: str):
        widget: LabGui = self.get_widget()
        widget.update_labgui(progname)

    def update_actions(self):
        widget: LabGui = self.get_widget()
        widget.update_actions()

    # ----------------------- Plugin teardown ---------------------------------

    @on_plugin_teardown(plugin=ATE.NAME)
    def on_ate_teardown(self):
        widget: LabGui = self.get_widget()
        ate: ATE = self.get_plugin(ATE.NAME)

        widget.set_project_information(None)
        ate.sig_ate_project_changed.disconnect(widget.notify_project_status)
