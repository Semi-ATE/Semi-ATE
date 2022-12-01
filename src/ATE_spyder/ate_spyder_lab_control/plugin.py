# -*- coding: utf-8 -*-
#
# Copyright © Semi-ATE
# Licensed under the terms of the GPLv2 License
# (see LICENSE.txt for more details)


# Standard library imports

# Third-party imports

# Spyder imports
from spyder.api.plugins import SpyderDockablePlugin
from spyder.api.plugins import Plugins, SpyderDockablePlugin
from spyder.api.translations import get_translation
from spyder.api.plugin_registration.decorators import on_plugin_available, on_plugin_teardown

from qtpy.QtCore import Signal

# Local imports
from ate_spyder_lab_control.widgets.main_widget import LabControl
from ate_spyder.plugin import ATE

# Localization
_ = get_translation("spyder")


class LabControlPlugin(SpyderDockablePlugin):
    """Labo Control dockable plugin."""

    NAME = 'lab_control'
    WIDGET_CLASS = LabControl
    CONF_SECTION = NAME
    REQUIRES = [ATE.NAME]
    OPTIONAL = [Plugins.MainMenu, Plugins.Editor, Plugins.Projects]
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
        return _('Lab_CONTROL')

    def get_description(self) -> str:
        return _('Lab Control integration')

    def get_icon(self):
        return self.create_icon('mdi.chip')

    def on_initialize(self):
        pass

    def update_font(self):
        pass

    # -------------------- Plugin initialization ------------------------------
    @on_plugin_available(plugin=ATE.NAME)
    def on_ate_available(self):
        widget: LabControl = self.get_widget()
        ate: ATE = self.get_plugin(ATE.NAME)
        ate.sig_ate_project_loaded.connect(self._setup_test_runner_widget)
        ate.sig_ate_progname.connect(self.runflow_changed)
        ate.sig_stop_debugging.connect(widget.debug_stop)

    def _setup_test_runner_widget(self):
        widget: LabControl = self.get_widget()
        ate: ATE = self.get_plugin(ATE.NAME)
        project_info = ate.get_project_navigation()
        widget.setup_widget(project_info)

    @on_plugin_available(plugin=Plugins.Projects)
    def on_projects_available(self):
        projects = self.get_plugin(Plugins.Projects)
        projects.sig_project_closed.connect(self.project_closed)

    def project_closed(self):
        pass

    @on_plugin_available(plugin=Plugins.Editor)
    def on_editor_available(self):
        editor = self.get_plugin(Plugins.Editor)
        self.sig_edit_goto_requested.connect(editor.load)

        self.sig_run_cell.connect(editor.run_cell)
        self.sig_debug_cell.connect(editor.debug_cell)
        self.sig_stop_debugging.connect(editor.stop_debugging)

    def runflow_changed(self, progname: str):
        widget: LabControl = self.get_widget()
        widget.update_control(progname)

    # ----------------------- Plugin teardown ---------------------------------

    @on_plugin_teardown(plugin=ATE.NAME)
    def on_ate_teardown(self):
        widget: LabControl = self.get_widget()
        ate: ATE = self.get_plugin(ATE.NAME)

        widget.set_project_information(None)
        ate.sig_ate_project_changed.disconnect(widget.notify_project_status)

    def compile_patterns(self, patterns: list[str]):
        self.get_container().compile_patterns(patterns)
