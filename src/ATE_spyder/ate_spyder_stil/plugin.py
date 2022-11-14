# -*- coding: utf-8 -*-
#
# Copyright © Semi-ATE
# Licensed under the terms of the GPLv2 License
# (see LICENSE.txt for more details)

"""ATE STIL (IEEE 1450) plugin."""

# Standard library imports

# Third-party imports
from qtpy.QtCore import Qt, Signal

# Spyder imports
from spyder.api.plugins import SpyderDockablePlugin
from spyder.api.exceptions import SpyderAPIError
from spyder.api.plugins import Plugins, SpyderDockablePlugin
from spyder.api.translations import get_translation
from spyder.api.plugin_registration.decorators import (
    on_plugin_available, on_plugin_teardown)
from spyder.plugins.toolbar.plugin import Toolbar

# Local imports
from ate_spyder_stil.api import STILActions
from ate_spyder_stil.widgets.main_widget import STILContainer
from ate_spyder.plugin import ATE
from ate_spyder.widgets.constants import ATEToolbars

# Localization
_ = get_translation("spyder")



class STIL(SpyderDockablePlugin):
    """STIL dockable plugin."""

    NAME = 'stil'
    WIDGET_CLASS = STILContainer
    CONF_SECTION = NAME
    REQUIRES = [ATE.NAME]
    OPTIONAL = [Plugins.Toolbar, Plugins.StatusBar, Plugins.MainMenu,
                Plugins.Editor]
    CONF_FILE = False
    TABIFY = [Plugins.Help]

    # Signals
    sig_stil_compilation_started = Signal()
    """
    This signal indicates if the STIL compiler was invoked and is running.
    """

    sig_stil_compilation_stopped = Signal(bool)
    """
    This signal indicated if the STIL compiler has finished.

    Arguments
    ---------
    success: bool
        True if the compiler finished successfully. False otherwise.
    """

    sig_open_file = Signal(str, int, int)
    """
    This signal is emitted whenever a STIL file should be opened.

    Arguments
    ---------
    filename: str
        Path to the file to open.
    line: int
        Line number to focus when the file is opened.
    column: int
        Column number to focus when the file is opened.
    """

    # --- SpyderDockablePlugin API
    # ------------------------------------------------------------------------

    @staticmethod
    def get_name() -> str:
        return _('STIL')

    def get_description(self) -> str:
        return _('STIL tools integration')

    def get_icon(self):
        return self.create_icon('mdi.chip')

    def on_initialize(self):
        widget: STILContainer = self.get_widget()
        widget.sig_stil_compilation_started.connect(
            self.sig_stil_compilation_started)
        widget.sig_stil_compilation_stopped.connect(
            self.sig_stil_compilation_stopped)
        widget.sig_edit_goto_requested.connect(self.sig_open_file)

    def update_font(self):
        color_scheme = self.get_color_scheme()
        font = self.get_font()
        self.get_widget().update_font(font, color_scheme)

    # -------------------- Plugin initialization ------------------------------

    @on_plugin_available(plugin=ATE.NAME)
    def on_ate_available(self):
        widget: STILContainer = self.get_widget()
        ate: ATE = self.get_plugin(ATE.NAME)

        project_info = ate.get_project_navigation()
        widget.set_project_information(project_info)
        ate.sig_ate_project_changed.connect(widget.notify_project_status)

        ate.sig_compile_pattern.connect(self.compile_patterns)

        stil_action = self.get_action(STILActions.RunSTIL)
        ate.add_item_to_toolbar(stil_action)

    @on_plugin_available(plugin=Plugins.Editor)
    def on_editor_available(self):
        editor = self.get_plugin(Plugins.Editor)
        self.partial_editor_call = lambda file, line, col: editor.load(
            [file], line, start_column=col)
        self.sig_open_file.connect(self.partial_editor_call)

    @on_plugin_available(plugin=Plugins.Toolbar)
    def on_toolbar_available(self):
        pass

    @on_plugin_available(plugin=Plugins.StatusBar)
    def on_statusbar_available(self):
        pass

    @on_plugin_available(plugin=Plugins.MainMenu)
    def on_mainmenu_available(self):
        pass

    # ----------------------- Plugin teardown ---------------------------------

    @on_plugin_teardown(plugin=ATE.NAME)
    def on_ate_teardown(self):
        widget: STILContainer = self.get_widget()
        ate: ATE = self.get_plugin(ATE.NAME)

        widget.set_project_information(None)
        ate.sig_ate_project_changed.disconnect(widget.notify_project_status)

    @on_plugin_teardown(plugin=Plugins.Toolbar)
    def on_toolbar_teardown(self):
        toolbar: Toolbar = self.get_plugin(Plugins.Toolbar)

        toolbar.remove_item_from_application_toolbar(
            STILActions.RunSTIL, ATEToolbars.ATE)

    @on_plugin_teardown(plugin=Plugins.Editor)
    def on_editor_teardown(self):
        self.sig_open_file.disconnect(self.partial_editor_call)
        self.partial_editor_call = None

    @on_plugin_teardown(plugin=Plugins.StatusBar)
    def on_statusbar_teardown(self):
        pass

    @on_plugin_teardown(plugin=Plugins.MainMenu)
    def on_mainmenu_teardown(self):
        pass

    def compile_patterns(self, patterns: list[str], sig_to_chan_path: str):
        self.get_container().compile_stil(patterns, sig_to_chan_path)
