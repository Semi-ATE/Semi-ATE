""" master App """

from ate_master_app.master_application import MasterApplication
from ate_master_app.utils.master_configuration import MasterConfiguration
from ate_master_app.utils import TestState
from ate_apps_common.sequence_container import SequenceContainer
from ate_apps_common.stdf_aggregator import StdfTestResultAggregator

from transitions.extensions import HierarchicalMachine as Machine

DEVELOP_MODE_DEVICE_ID = 'developmode'


class MasterApplicationDevMode(MasterApplication):
    debug_transtitons = [
        {'source': 'connecting', 'dest': 'loading', 'trigger': "develop_mode_ready", 'after': "on_developer_mode_ready"},               # noqa: E241
        {'source': 'softerror',  'dest': 'loading', 'trigger': 'develop_mode_ready', 'after': 'on_developer_mode_ready'},               # noqa: E241
        {'source': 'unloading',  'dest': 'loading', 'trigger': 'develop_mode_ready', 'after': 'on_developer_mode_ready'},               # noqa: E241
    ]

    def __init__(self, master_configuration: MasterConfiguration):
        self.transitions.extend(self.debug_transtitons)

        master_configuration.device_id = DEVELOP_MODE_DEVICE_ID
        super().__init__(master_configuration)

    def _setup_machine(self, model: 'MasterApplication', states: list, transitions: list, initial: str, after_state_change: str):
        self.fsm = Machine(model=model,
                           states=states,
                           transitions=transitions,
                           initial=initial,
                           after_state_change=after_state_change)

        self.is_initialized = False

    def init(self):
        self.timeoutHandle = None
        self.init_user_settings()
        self.pendingTransitionsTest = SequenceContainer([TestState.Idle], self.configuredSites, lambda: self.all_siteloads_complete(),
                                                        lambda site, state: self.on_unexpected_testapp_state(site, state))

    def on_startup_done(self):
        self.repost_state_if_connecting()
        self.develop_mode_ready()

    def on_reset_received(self, _: dict):
        self.pendingTransitionsTest = SequenceContainer([TestState.Idle], self.configuredSites, lambda: self.all_siteloads_complete(),
                                                        lambda site, state: self.on_unexpected_testapp_state(site, state))
        self.connectionHandler.send_reset_to_all_sites()
        self.develop_mode_ready()

    def on_allsiteloads_complete(self):
        super().on_allsiteloads_complete()
        self.on_developer_mode_ready()

    def on_developer_mode_ready(self):
        if not self.is_initialized:
            self._stdf_aggregator = StdfTestResultAggregator(self.device_id + ".Master", self.sites)
            self.is_initialized = True

    def on_testapp_status_changed(self, siteid: str, status_msg: dict):
        newstatus = status_msg['state']

        if self.pendingTransitionsTest:
            self.pendingTransitionsTest.trigger_transition(siteid, newstatus)

        if self.state == 'softerror':
            self.develop_mode_ready()

    def on_unload_command_issued(self, _: dict):
        self.pendingTransitionsTest = SequenceContainer([TestState.Terminated, TestState.Idle], self.configuredSites, lambda: self.all_siteloads_complete(),
                                                        lambda site, state: self.on_unexpected_testapp_state(site, state))
        self.error_message = ''
        self._first_part_tested = False
        self.connectionHandler.send_terminate_to_all_sites()
        self.handle_reset_command()

        self.develop_mode_ready()
        self.is_initialized = False

    def on_unexpected_testapp_state(self, site: str, state: str):
        self.on_error(f'test app on site: {site} report an unexpected state: {state}')

    def on_error_occurred(self, message):
        super().on_error_occurred(message)
        self.pendingTransitionsTest = SequenceContainer([TestState.Idle], self.configuredSites, lambda: self.all_siteloads_complete(),
                                                        lambda site, state: self.on_unexpected_testapp_state(site, state))

    def on_timeout(self, message):
        super().on_timeout(message)
        self.pendingTransitionsTest = SequenceContainer([TestState.Idle], self.configuredSites, lambda: self.all_siteloads_complete(),
                                                        lambda site, state: self.on_unexpected_testapp_state(site, state))
        self.develop_mode_ready()

    def on_test_app_response_to_next_command(self):
        self.disarm_timeout()
        self.pendingTransitionsTest = SequenceContainer([TestState.Idle], self.configuredSites, lambda: None,
                                                        lambda site, state: self.on_error(f"Bad statetransition of testapp {site} during testing to state: '{state}'"))
        self.testing_event.set()
