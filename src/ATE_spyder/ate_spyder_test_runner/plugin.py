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
from spyder.api.plugin_registration.decorators import (
    on_plugin_available, on_plugin_teardown)
from spyder.plugins.toolbar.plugin import Toolbar

# Local imports
from ate_spyder_test_runner.widgets.main_widget import TestRunner
from ate_spyder.plugin import ATE

# Localization
_ = get_translation("spyder")


class TestRunnerPlugin(SpyderDockablePlugin):
    """Test Runner dockable plugin."""

    NAME = 'test_runner'
    WIDGET_CLASS = TestRunner
    CONF_SECTION = NAME
    REQUIRES = [ATE.NAME]
    OPTIONAL = [Plugins.Toolbar, Plugins.StatusBar, Plugins.MainMenu]
    CONF_FILE = False
    TABIFY = [Plugins.Help]

    # --- SpyderDockablePlugin API
    # ------------------------------------------------------------------------

    @staticmethod
    def get_name() -> str:
        return _('TEST_RUNNER')

    def get_description(self) -> str:
        return _('Test Runner integration')

    def get_icon(self):
        return self.create_icon('mdi.chip')

    def on_initialize(self):
        pass

    def update_font(self):
        pass

    # -------------------- Plugin initialization ------------------------------
    @on_plugin_available(plugin=ATE.NAME)
    def on_ate_available(self):
        ate: ATE = self.get_plugin(ATE.NAME)
        ate.sig_ate_project_loaded.connect(self._setup_test_runner_widget)

    def _setup_test_runner_widget(self):
        widget: TestRunner = self.get_widget()
        ate: ATE = self.get_plugin(ATE.NAME)
        project_info = ate.get_project_navigation()
        widget.setup_widget(project_info)

    # ----------------------- Plugin teardown ---------------------------------

    @on_plugin_teardown(plugin=ATE.NAME)
    def on_ate_teardown(self):
        widget: TestRunner = self.get_widget()
        ate: ATE = self.get_plugin(ATE.NAME)

        widget.set_project_information(None)
        ate.sig_ate_project_changed.disconnect(widget.notify_project_status)

    def compile_patterns(self, patterns: list[str]):
        self.get_container().compile_patterns(patterns)
