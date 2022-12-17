
"""ATE injection plugin to dispatch events when an IPython kernel is idle."""

# Qt imports
from qtpy.QtCore import Qt, Signal

# Spyder imports
from spyder.api.translations import get_translation
from spyder.api.plugins import SpyderPluginV2, Plugins
from spyder.api.plugin_registration.decorators import (
    on_plugin_available, on_plugin_teardown)

# Third-party imports
from ate_dispatcher import ATEDispatcher

# Local imports
from ate_spyder_debug_display.dispatch import ATEProducer, ATEResultListener

# Localization
_ = get_translation("spyder")


class DebugDisplay(SpyderPluginV2):
    NAME = 'ate_debug_display'
    REQUIRES = [Plugins.IPythonConsole]

    sig_debug_state_changed = Signal(bool, dict)

    # ----------- Required methods -----------------
    @staticmethod
    def get_name():
        return _('ATE debug display')

    def get_description(self):
        return _('This plugin is used to display debug and state information '
                 'in the IPython console whenever it is idle.')

    def get_icon(self):
        return self.create_icon('mdi.eye')

    def on_initialize(self):
        self.prev_state = {}
        self.dispatcher = ATEDispatcher()
        self.producer = ATEProducer()
        self.listener = ATEResultListener(self)

        self.dispatcher.start()
        self.producer.start()
        self.listener.start()

        self.dispatcher.register_result_producer(self.producer, 'debug_ate')
        self.dispatcher.register_result_listener(self.listener, 'debug_ate')
        self.sig_debug_state_changed.connect(self.debugger_state_changed)

    # ------------- Optional methods --------------------
    def on_close(self, cancelable=False):
        self.dispatcher.deregister_result_producer(self.producer, 'debug_ate')
        self.dispatcher.deregister_result_listener(self.listener, 'debug_ate')

        self.producer.stop()
        self.listener.stop()
        self.dispatcher.stop()

    # ------------ Plugin registration/teardown ----------
    @on_plugin_available(plugin=Plugins.IPythonConsole)
    def on_ipython_console_available(self):
        ipython = self.get_plugin(Plugins.IPythonConsole)
        ipython.sig_pdb_state_changed.connect(self.sig_debug_state_changed)

    @on_plugin_teardown(plugin=Plugins.IPythonConsole)
    def on_ipython_console_teardown(self):
        ipython = self.get_plugin(Plugins.IPythonConsole)
        ipython.sig_pdb_state_changed.disconnect(self.sig_debug_state_changed)

    # ---------------- Private API --------------------
    def debugger_state_changed(self, is_waiting: bool, last_step: dict):
        if is_waiting and self.prev_state != last_step:
            self.dispatcher.send_request('debug_ate')

        self.prev_state = last_step

    def relay_dispatcher_result(self, response: str):
        ipython = self.get_plugin(Plugins.IPythonConsole)
        if ipython is not None:
            ipython.execute_code(response)
