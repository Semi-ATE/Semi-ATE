# -*- coding: utf-8 -*-
#
# Copyright © Semi-ATE
# Licensed under the terms of the GPLv2 License
# (see LICENSE.txt for more details)

"""ATE STIL (IEEE 1450) plugin."""

# Standard library imports
import logging

# Third-party imports
from qtpy.QtCore import Signal

# Spyder imports
from spyder.api.plugins import SpyderDockablePlugin
from spyder.api.plugins import Plugins
from spyder.api.translations import get_translation
from spyder.api.plugin_registration.decorators import (
    on_plugin_available, on_plugin_teardown)
from spyder.plugins.toolbar.plugin import Toolbar
from spyder.api.fonts import SpyderFontType
from spyder import __version__ as spyder_version

# Local imports
from ate_spyder_stil.api import STILActions
from ate_spyder_stil.widgets.main_widget import STILContainer
from ate_spyder.plugin import ATE
from ate_spyder.widgets.constants import ATEToolbars

# Logging
logger = logging.getLogger(__name__)

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
        logger.debug("STIL:on_initialize start")
        widget: STILContainer = self.get_widget()
        widget.sig_stil_compilation_started.connect(
            self.sig_stil_compilation_started)
        widget.sig_stil_compilation_stopped.connect(
            self.sig_stil_compilation_stopped)
        widget.sig_edit_goto_requested.connect(self.sig_open_file)
        logger.debug("STIL:on_initialize done")

    def update_font(self):
        logger.debug("STIL:update_font start")
        color_scheme = self.get_color_scheme()
        if spyder_version == "5.5.6":
            font = self.get_font()
        else:
            font = self.get_font(font_type=SpyderFontType.Monospace)           # oder 'interface', 'console'
        self.get_widget().update_font(font, color_scheme)
        logger.debug("STIL:update_font done")

    # -------------------- Plugin initialization ------------------------------

    @on_plugin_available(plugin=ATE.NAME)
    def on_ate_available(self):
        logger.debug("STIL:on_ate_available start")
        widget: STILContainer = self.get_widget()
        ate: ATE = self.get_plugin(ATE.NAME)

        project_info = ate.get_project_navigation()
        widget.set_project_information(project_info)
        ate.sig_ate_project_changed.connect(widget.notify_project_status)

        ate.sig_compile_pattern.connect(self.compile_patterns)

        stil_action = self.get_action(STILActions.RunSTIL)
        ate.add_item_to_toolbar(stil_action)
        logger.debug("STIL:on_ate_available done")

    @on_plugin_available(plugin=Plugins.Editor)
    def on_editor_available(self):
        logger.debug("STIL:on_editor_available start")
        editor = self.get_plugin(Plugins.Editor)
        if editor is None:
            logger.error("STIL:on_editor_available Editor plugin is None!")
            return
        self.partial_editor_call = lambda file, line, col: editor.load(
            [file], line, start_column=col)
        self.sig_open_file.connect(self.partial_editor_call)
        logger.debug("STIL:on_editor_available done")

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
        logger.debug("STIL:on_ate_teardown start")
        widget: STILContainer = self.get_widget()
        ate: ATE = self.get_plugin(ATE.NAME)

        widget.set_project_information(None)
        ate.sig_ate_project_changed.disconnect(widget.notify_project_status)
        logger.debug("STIL:on_ate_teardown done")

    @on_plugin_teardown(plugin=Plugins.Toolbar)
    def on_toolbar_teardown(self):
        logger.debug("STIL:on_toolbar_teardown start")
        toolbar: Toolbar = self.get_plugin(Plugins.Toolbar)

        toolbar.remove_item_from_application_toolbar(
            STILActions.RunSTIL, ATEToolbars.ATE)
        logger.debug("STIL:on_toolbar_teardown done")

    @on_plugin_teardown(plugin=Plugins.Editor)
    def on_editor_teardown(self):
        logger.debug("STIL:on_editor_teardown start")
        self.sig_open_file.disconnect(self.partial_editor_call)
        self.partial_editor_call = None
        logger.debug("STIL:on_editor_teardown done")

    @on_plugin_teardown(plugin=Plugins.StatusBar)
    def on_statusbar_teardown(self):
        pass

    @on_plugin_teardown(plugin=Plugins.MainMenu)
    def on_mainmenu_teardown(self):
        pass

    def compile_patterns(self, patterns: list[str], sig_to_chan_path: str):
        logger.debug(f"STIL:compile_patterns {patterns}, {sig_to_chan_path}")
        self.get_container().compile_stil(patterns, sig_to_chan_path)
        logger.debug("STIL:compile_patterns done")
