""" master App """

# External imports
from aiohttp import web
from transitions.extensions import HierarchicalMachine as Machine
import asyncio
import mimetypes
import sys
import os

import base64
import io
from ATE.data.STDF.records import records_from_file
from typing import Callable, List, Optional


# Internal imports
from ATE.TES.apps.common.logger import Logger
from ATE.TES.apps.masterApp.master_connection_handler import MasterConnectionHandler
from ATE.TES.apps.masterApp.master_webservice import webservice_setup_app
from ATE.TES.apps.masterApp.parameter_parser import parser_factory
from ATE.TES.apps.masterApp.sequence_container import SequenceContainer
from ATE.TES.apps.masterApp.user_settings import UserSettings
from ATE.TES.apps.masterApp.stdf_aggregator import StdfTestResultAggregator
from ATE.TES.apps.masterApp.user_settings import UserSettings

INTERFACE_VERSION = 1


def assert_valid_system_mimetypes_config():
    """
    Perform sanity check for system/enfironment configuration and return
    result as boolean.

    Background info:

    aiohttp uses mimetypes.guess_type() to guess the content-type to be
    used in the http response headers when serving static files.

    If we serve javascript modules with "text/plain" instead
    of "application/javascript" the browser will not execute the file as
    javascript module and the angular frontend does not load.

    On windows mimetypes.init (called automatically by guess_type if not
    called before) will always read content types from registry in Python
    3.8.1 (e.g. "HKLM\\Software\\Classes\\.js\\Content Type"). The values
    stored there may not be standard because they have been changed on
    certain systems (reasons unknown).

    Apparently it was possible to avoid this in earlier python
    version by explicitly passing empty list to files, e.g.
    mimetypes.init(files=[]). But this does not work anymore in 3.8.1,
    where types from registry will always be loaded.
    """
    js_mime_type = mimetypes.guess_type('file.js')[0]
    if js_mime_type != 'application/javascript':
        print('FATAL ERROR: Invalid system configuration for .js type: '
              + 'expected "application/javascript" but got '
              + f'"{js_mime_type}".'
              + ' Please fix your systems mimetypes configuration.')
        sys.exit(1)


CONTROL_STATE_UNKNOWN = "unknown"
CONTROL_STATE_LOADING = "loading"
CONTROL_STATE_BUSY = "busy"
CONTROL_STATE_IDLE = "idle"
CONTROL_STATE_CRASH = "crash"

TEST_STATE_IDLE = "idle"
TEST_STATE_TESTING = "testing"
TEST_STATE_CRASH = "crash"
TEST_STATE_TERMINATED = "terminated"

STARTUP_TIMEOUT = 300
LOAD_TIMEOUT = 180
UNLOAD_TIMEOUT = 60
TEST_TIMEOUT = 30
RESET_TIMEOUT = 20

class TestingSiteMachine(Machine):
    states = ['inprogress', 'waiting_for_resource', 'waiting_for_testresult', 'waiting_for_idle', 'completed']

    def __init__(self, model):
        super().__init__(model=model, states=self.states, initial='inprogress', send_event=True)

        self.add_transition('resource_requested',       'inprogress',                               'waiting_for_resource',     before='set_requested_resource')        # noqa: E241
        self.add_transition('resource_ready',           'waiting_for_resource',                     'inprogress',               before='clear_requested_resource')      # noqa: E241

        self.add_transition('testresult_received',      ['inprogress', 'waiting_for_resource'],     'waiting_for_idle',         before='set_testresult')                # noqa: E241
        self.add_transition('status_idle',              ['inprogress', 'waiting_for_resource'],     'waiting_for_testresult')                                           # noqa: E241

        self.add_transition('testresult_received',      'waiting_for_testresult',                   'completed',                before='set_testresult')                # noqa: E241
        self.add_transition('status_idle',              'waiting_for_idle',                         'completed')                                                        # noqa: E241

        self.add_transition('reset',                    'completed',                                'inprogress',               before='clear_testresult')              # noqa: E241


class TestingSiteModel:
    site_id: str
    resource_request: Optional[dict]
    testresult: Optional[dict]

    def __init__(self, site_id: str):
        self.site_id = site_id
        self.resource_request = None
        self.testresult = None

    def set_requested_resource(self, event):
        self.resource_request = event.kwargs['resource_request']

    def clear_requested_resource(self, event):
        self.resource_request = None

    def set_testresult(self, event):
        self.testresult = event.kwargs['testresult']

    def clear_testresult(self, event):
        self.testresult = None


class MultiSiteTestingMachine(Machine):

    def __init__(self, model=None):
        states = ['inprogress', 'waiting_for_resource', 'completed']
        super().__init__(model=model, states=states, initial='inprogress'),

        self.add_transition('all_sites_waiting_for_resource',       'inprogress',              'waiting_for_resource')      # noqa: E241
        self.add_transition('resource_config_applied',              'waiting_for_resource',    'inprogress')                # noqa: E241
        self.add_transition('all_sites_completed',                  '*',                       'completed')                 # noqa: E241


class MultiSiteTestingModel:
    def __init__(self, site_ids: List[str], parent_model=None):
        self._site_models = {site_id: TestingSiteModel(site_id) for site_id in site_ids}
        self._site_machines = {site_id: TestingSiteMachine(self._site_models[site_id]) for site_id in site_ids}
        self._parent_model = parent_model if parent_model is not None else self

    def handle_reset(self):
        for site in self._site_models.values():
            if site.is_completed():
                site.reset()

    def handle_resource_request(self, site_id: str, resource_request: dict):
        self._site_models[site_id].resource_requested(resource_request=resource_request)

        for site in self._site_models.values():
            if site.resource_request is not None and site.resource_request != resource_request:
                raise RuntimeError(f'mismatch in resource request from site "{site_id}": previous request of site "{site.site_id}" differs')

        self._check_for_all_remaing_sites_waiting_for_resource()

    def _on_resource_config_applied(self):
        if not self.is_waiting_for_resource():
            return  # ignore late callback if we already left the state

        self.resource_config_applied()
        for site in self._site_models.values():
            if site.is_waiting_for_resource():
                site.resource_ready()

    def handle_testresult(self, site_id: str, testresult: dict):
        self._site_models[site_id].testresult_received(testresult=testresult)
        if not self._check_for_all_sites_completed():
            self._check_for_all_remaing_sites_waiting_for_resource()

    def handle_status_idle(self, site_id: str):
        self._site_models[site_id].status_idle()
        if not self._check_for_all_sites_completed():
            self._check_for_all_remaing_sites_waiting_for_resource()

    def _check_for_all_sites_completed(self):
        if all(site.is_completed() for site in self._site_models.values()):
            self.all_sites_completed()
            self._parent_model.all_sitetests_complete()
            return True
        return False

    def _check_for_all_remaing_sites_waiting_for_resource(self):
        if self.is_waiting_for_resource():
            return  # already transitioned to state

        if any(site.is_inprogress() for site in self._site_models.values()):
            return  # at least one site is still busy

        sites_waiting = [site for site in self._site_models.values() if site.is_waiting_for_resource()]
        if not sites_waiting:
            return  # no site is waiting for resource

        self.all_sites_waiting_for_resource()
        resource_request = sites_waiting[0].resource_request  # all sites have same request
        self._parent_model.apply_resource_config(resource_request, lambda: self._on_resource_config_applied())  # Callable[[dict, Callable], None]

    def is_waiting_for_resource(self):
        # HACK: referencing the parent state by name sucks, but apparently we do not get
        # a monkey patched self.waiting_for_resource() to check if we are in 'our' nested state
        return self.state == 'testing_waiting_for_resource'


class MasterApplication(MultiSiteTestingModel):

    states = ['startup',
              'connecting',
              'initialized',
              'loading',
              'ready',
              {'name': 'testing', 'children': MultiSiteTestingMachine()},  # , 'remap': {'completed': 'ready'}
              'finished',
              'unloading',
              'error',
              'softerror']

    # multipe space code style "error" will be ignored for a better presentation of the possible state machine transitions
    transitions = [
        {'source': 'startup',           'dest': 'connecting',  'trigger': "startup_done",                'after': "on_startup_done"},               # noqa: E241
        {'source': 'connecting',        'dest': 'initialized', 'trigger': 'all_sites_detected',          'after': "on_allsitesdetected"},           # noqa: E241
        {'source': 'connecting',        'dest': 'error',       'trigger': 'bad_interface_version'},                                                 # noqa: E241

        {'source': 'initialized',       'dest': 'loading',     'trigger': 'load_command',                'after': 'on_loadcommand_issued'},         # noqa: E241
        {'source': 'loading',           'dest': 'ready',       'trigger': 'all_siteloads_complete',      'after': 'on_allsiteloads_complete'},     # noqa: E241

        # TODO: properly limit source states to valid states where usersettings are allowed to be modified
        #       ATE-104 says it should not be possible while testing in case of stop-on-fail, but this constraint may not be required here and could be done in UI)
        {'source': ['initialized', 'ready'], 'dest': '=', 'trigger': 'usersettings_command',       'after': 'on_usersettings_command_issued'},  # noqa: E241

        # TODO: properly limit source states to valid states where usersettings are allowed to be modified
        #       ATE-104 says it should not be possible while testing in case of stop-on-fail, but this constraint may not be required here and could be done in UI)
        {'source': ['initialized', 'ready'], 'dest': '=', 'trigger': 'usersettings_command',       'after': 'on_usersettings_command_issued'},  # noqa: E241

        {'source': 'ready',             'dest': 'testing',     'trigger': 'next',                        'after': 'on_next_command_issued'},        # noqa: E241
        {'source': 'ready',             'dest': 'unloading',   'trigger': 'unload',                      'after': 'on_unload_command_issued'},      # noqa: E241
        {'source': 'testing_completed', 'dest': 'ready',       'trigger': 'all_sitetests_complete',      'after': "on_allsitetestscomplete"},       # noqa: E241
        {'source': 'unloading',         'dest': 'initialized', 'trigger': 'all_siteunloads_complete',    'after': "on_allsiteunloadscomplete"},     # noqa: E241

        {'source': '*',                 'dest': 'softerror',   'trigger': 'testapp_disconnected',        'after': 'on_disconnect_error'},           # noqa: E241
        {'source': '*',                 'dest': 'softerror',   'trigger': 'timeout',                     'after': 'on_timeout'},                    # noqa: E241
        {'source': '*',                 'dest': 'softerror',   'trigger': 'on_error',                    'after': 'on_error_occured'},              # noqa: E241
        {'source': 'softerror',         'dest': 'connecting',  'trigger': 'reset',                       'after': 'on_reset_received'}              # noqa: E241
    ]

    """ MasterApplication """

    def __init__(self, configuration):
        super().__init__(configuration['sites'])
        self.fsm = Machine(model=self,
                           states=MasterApplication.states,
                           transitions=MasterApplication.transitions,
                           initial="startup",
                           after_state_change='publish_state')
        self.configuration = configuration
        self.log = Logger.get_logger()
        self.init(configuration)

        self.receivedSiteTestResults = {}  # key: site_id, value: [testresult topic payload dicts]
        self.loaded_jobname = ""
        self.loaded_lot_number = ""

    def init(self, configuration: dict):
        self.__get_configuration(configuration)
        self.create_handler(self.broker_host, self.broker_port)

        self.receivedSiteTestResults = {}  # key: site_id, value: [testresult topic payload dicts]

        self.error_message = ''

        self.siteStates = {site_id: CONTROL_STATE_UNKNOWN for site_id in self.configuredSites}
        self.pendingTransitionsControl = SequenceContainer([CONTROL_STATE_IDLE], self.configuredSites, lambda: self.all_sites_detected(),
                                                           lambda site, state: self.on_unexpected_control_state(site, state))
        self.pendingTransitionsTest = SequenceContainer([TEST_STATE_IDLE], self.configuredSites, lambda: self.all_siteloads_complete(),
                                                        lambda site, state: self.on_unexpected_testapp_state(site, state))
        self.init_user_settings()

        self.timeoutHandle = None
        self.arm_timeout(STARTUP_TIMEOUT, lambda: self.timeout("Not all sites connected."))

    def __get_configuration(self, configuration: dict):
        try:
            self.configuredSites = configuration['sites']
            # Sanity check for bad configurations:
            if len(self.configuredSites) == 0:
                self.log.error(f"no sites assigned")
                sys.exit()

            self.device_id = configuration['device_id']
            self.broker_host = configuration['broker_host']
            self.broker_port = configuration['broker_port']
            self.enableTimeouts = configuration['enable_timeouts']
            self.env = configuration['environment']
        except KeyError as e:
            self.log.error(f"invalid configuration: {e}")
            sys.exit()

    @property
    def user_settings_filepath(self):
        return self.configuration.get("user_settings_filepath")

    @property
    def persistent_user_settings_enabled(self):
        return self.user_settings_filepath is not None

    def init_user_settings(self):
        if self.persistent_user_settings_enabled:
            try:
                user_settings = UserSettings.load_from_file(self.user_settings_filepath)
            except FileNotFoundError:
                user_settings = UserSettings.get_defaults()

            # always update file with hardcoded defaults (and create it if it does not exist)
            UserSettings.save_to_file(self.user_settings_filepath, user_settings, add_defaults=True)
        else:
            user_settings = UserSettings.get_defaults()

        self.user_settings = user_settings

    def modify_user_settings(self, modified_settings):
        self.user_settings.update(modified_settings)
        self.publish_usersettings()
        if self.persistent_user_settings_enabled:
            UserSettings.save_to_file(self.user_settings_filepath, self.user_settings, add_defaults=True)

    def on_usersettings_command_issued(self, param_data: dict):
        settings = param_data['settings']
        self.modify_user_settings(settings)

    def publish_usersettings(self):
        self.log.info("Master usersettings are: " + str(self.user_settings))
        self.connectionHandler.publish_usersettings(self.user_settings)
        # TODO: notify UI of changes/initial settings. Should we send individual messages to all connected websockets or should we rely on mqtt proxy usages (UI just has to subscribe to Master/usersettings topic)?

    @property
    def external_state(self):
        return 'testing' if self.is_testing(allow_substates=True) else self.state

    def disarm_timeout(self):
        if self.enableTimeouts:
            if self.timeoutHandle is not None:
                self.timeoutHandle.cancel()
                self.timeoutHandle = None

    def arm_timeout(self, timeout_in_seconds: float, callback: Callable):
        if self.enableTimeouts:
            self.disarm_timeout()
            self.timeoutHandle = asyncio.get_event_loop().call_later(timeout_in_seconds, callback)

    def repost_state_if_connecting(self):
        if self.state == "connecting":
            self.publish_state()
            asyncio.get_event_loop().call_later(1, lambda: self.repost_state_if_connecting())

    def on_startup_done(self):
        self.repost_state_if_connecting()
        self.publish_usersettings()

    def on_timeout(self, message):
        self.error_message = message
        self.log.error(message)

    def on_disconnect_error(self, site_id, data):
        self.log.error(f"Entered state error due to disconnect of site {site_id}")

    def on_unexpected_control_state(self, site_id, state):
        self.log.warning(f"Site {site_id} reported state {state}. This state is ignored during startup.")
        self.error_message = f'Site {site_id} reported state {state}'

    def on_unexpected_testapp_state(self, site_id, state):
        self.log.warning(f"TestApp for site {site_id} reported state {state}. This state is ignored during startup.")
        self.error_message = f'TestApp for site {site_id} reported state {state}'

    def on_error_occured(self, message):
        self.log.error(f"Entered state error, reason: {message}")
        self.error_message = message

    def on_allsitesdetected(self):
        # Trap any controls that misbehave and move out of the idle state.
        # In this case we want to move to error as well
        self.pendingTransitionsControl = SequenceContainer([CONTROL_STATE_IDLE], self.configuredSites, lambda: None,
                                                           lambda site, state: self.on_error(f"Bad statetransition of control {site} during sync to {state}"))

        self.error_message = ''
        self.disarm_timeout()

    def publish_state(self, site_id=None, param_data=None):
        self.log.info("Master state is " + self.state)
        self.connectionHandler.publish_state(self.external_state)

    def on_loadcommand_issued(self, param_data: dict):
        jobname = param_data['lot_number']
        self.loaded_jobname = str(jobname)

        # TODO: HACK for quick testing/development: allow to specify the
        # testappzip mock variant with the lot number, and use hardcoded variant by default,
        # so we dont have to modify the XML for now
        thetestzipname = 'sleepmock'  # use trivial zip mock implementation by default
        if isinstance(jobname, str) and '|' in jobname:
            jobname, thetestzipname = jobname.split('|')

        self.loaded_lot_number = str(jobname)

        jobformat = self.configuration.get('jobformat')
        parser = parser_factory.CreateParser(jobformat)
        source = parser_factory.CreateDataSource(jobname,
                                                 self.configuration,
                                                 parser)

        if self.configuration.get('skip_jobdata_verification', False):
            data = {"DEBUG_OPTION": "no content because skip_jobdata_verification enabled"}
        else:
            param_data = source.retrieve_data()
            if param_data is None:
                # TODO: report error: file could not be loaded (currently only logged)
                return

            if not source.verify_data(param_data):
                # TODO: report error: file was loaded but contains invalid data (currently only logged)
                return

            data = source.get_test_information(param_data)
            self.log.debug(data)

        self.arm_timeout(LOAD_TIMEOUT, lambda: self.timeout("not all sites loaded the testprogram"))
        self.pendingTransitionsControl = SequenceContainer([CONTROL_STATE_LOADING, CONTROL_STATE_BUSY], self.configuredSites, lambda: None,
                                                           lambda site, state: self.on_error(f"Bad statetransition of control {site} during load to {state}"))
        self.pendingTransitionsTest = SequenceContainer([TEST_STATE_IDLE], self.configuredSites, lambda: self.all_siteloads_complete(),
                                                        lambda site, state: self.on_error(f"Bad statetransition of testapp {site} during load to {state}"))
        self.error_message = ''

        self.connectionHandler.send_load_test_to_all_sites(self.get_test_parameters(data))

    def get_test_parameters(self, data):
        # TODO: workaround until we specify the connection to the server or even mount the project locally
        return {
            'testapp_script_path': os.path.join(os.path.basename(data['PROGRAM_DIR'])),
            'testapp_script_args': ['--verbose', '--thetestzip_name', 'example1'],
            'cwd': os.path.dirname(data['PROGRAM_DIR']),
            'XML': data                                                                 # optional/unused for now
        }

    def on_allsiteloads_complete(self, paramData=None):
        self.error_message = ''
        self.disarm_timeout()

        self._stdf_aggregator = StdfTestResultAggregator()
        self._stdf_aggregator.init(self.device_id + ".Master", self.loaded_lot_number, self.loaded_jobname)

    def on_next_command_issued(self, paramData: dict):
        self.receivedSiteTestResults = {}
        self.arm_timeout(TEST_TIMEOUT, lambda: self.timeout("not all sites completed the active test"))
        self.pendingTransitionsTest = SequenceContainer([TEST_STATE_TESTING, TEST_STATE_IDLE], self.configuredSites, lambda: None,
                                                        lambda site, state: self.on_error(f"Bad statetransition of testapp during test"))
        self.error_message = ''
        job_data = {
            'duttest.stop_on_fail': self.user_settings['duttest.stop_on_fail'],
        }
        self.connectionHandler.send_next_to_all_sites(job_data)

    def on_unload_command_issued(self, param_data: dict):
        self.arm_timeout(UNLOAD_TIMEOUT, lambda: self.timeout("not all sites unloaded the testprogram"))
        self.pendingTransitionsControl = SequenceContainer([CONTROL_STATE_IDLE], self.configuredSites, lambda: self.all_siteunloads_complete(),
                                                           lambda site, state: self.on_error(f"Bad statetransition of control {site} during unload to {state}"))
        self.pendingTransitionsTest = SequenceContainer([TEST_STATE_TERMINATED], self.configuredSites, lambda: None, lambda site, state: None)
        self.error_message = ''
        self.connectionHandler.send_terminate_to_all_sites()

    def on_reset_received(self, param_data: dict):
        self.arm_timeout(RESET_TIMEOUT, lambda: self.timeout("not all sites unloaded the testprogram"))
        self.pendingTransitionsControl = SequenceContainer([CONTROL_STATE_IDLE], self.configuredSites, lambda: self.all_sites_detected(),
                                                           lambda site, state: self.on_unexpected_control_state(site, state))
        self.error_message = ''
        self.connectionHandler.send_reset_to_all_sites()

    def on_allsiteunloadscomplete(self):
        self.disarm_timeout()

        self._stdf_aggregator.finalize()
        self._stdf_aggregator.write_to_file('temp_final_stdf_file_on_unload.stdf')
        self._stdf_aggregator = None

    def _collect_testresults_from_completed_sites(self):
        # TODO: we do nothing with test-results until we have a specification how the results look like (json or base64 ??)
        return
        # TODO: all sorts of error handling (but how do we handle sites from which we cannot process test results, whatever the reason may be)?
        for site_num, (site_id, site) in enumerate(self._site_models.items()):
            if site.is_completed():
                try:
                    testdata = site.testresult['testdata']
                    ispass = site.testresult['pass'] == 1
                    if testdata is not None:
                        stdf_blob = base64.b64decode(testdata)
                        records = self._stdf_aggregator.parse_parttest_stdf_blob(stdf_blob)
                        self._stdf_aggregator.add_parttest_records(records, ispass, site_num)  # TODO: this sucks: we need an integer for site number, the id is not guaranteed to be an integer! need other way of configurable lookup for remapping
                except Exception:
                    self.log.exception("exception while processing test results from site %s", site_id)
                    raise
        self._stdf_aggregator.write_to_file('temp_stdf_file_after_last_duttest_complete.stdf')

    def on_allsitetestscomplete(self):
        self.disarm_timeout()
        self._collect_testresults_from_completed_sites()
        self.handle_reset()

    def on_site_test_result_received(self, site_id: str, param_data: dict):
        # simply store testresult so it can be forwarded to UI on the next tick
        self.receivedSiteTestResults.setdefault(site_id, []).append(param_data)

    def create_handler(self, host, port):
        self.connectionHandler = MasterConnectionHandler(host, port, self.configuredSites, self.device_id, self)

    def on_control_status_changed(self, siteid: str, status_msg: dict):
        print(f'control app status packet: {status_msg}')
        newstatus = status_msg['state']

        if(status_msg['interface_version'] != INTERFACE_VERSION):
            self.bad_interface_version({'reason': f'Bad interfaceversion on site {siteid}'})

        if(self.siteStates[siteid] != newstatus):
            self.siteStates[siteid] = newstatus
            self.pendingTransitionsControl.trigger_transition(siteid, newstatus)

    def on_testapp_status_changed(self, siteid: str, status_msg: dict):
        print(f'test app status packet: {status_msg}')
        newstatus = status_msg['state']
        if self.is_testing(allow_substates=True) and newstatus == TEST_STATE_IDLE:
            self.handle_status_idle(siteid)

        self.pendingTransitionsTest.trigger_transition(siteid, newstatus)

    def on_testapp_testresult_changed(self, siteid: str, status_msg: dict):
        if self.is_testing(allow_substates=True):
            self.handle_testresult(siteid, status_msg)
            self.on_site_test_result_received(siteid, status_msg)
        else:
            self.on_error(f"received unexpected testresult from site {siteid}")

    def on_testapp_resource_changed(self, siteid: str, resource_request_msg: dict):
        self.handle_resource_request(siteid, resource_request_msg)

    def apply_resource_config(self, resource_request: dict, on_resource_config_applied_callback: Callable):
        resource_id = resource_request['resource_id']
        config = resource_request['config']

        # simulate async callback after resource has been configured (always successful currently)
        # TODO: we probably need to check again if we are still in valid state. an error may occurred by now. also resource configuration may fail.
        def _delayed_callback_after_resource_config_has_actually_been_applied():
            self.connectionHandler.publish_resource_config(resource_id, config)
            on_resource_config_applied_callback()

        asyncio.get_event_loop().call_later(0.1, _delayed_callback_after_resource_config_has_actually_been_applied)

    def dispatch_command(self, json_data):
        cmd = json_data.get('command')
        try:
            {
                'load': lambda param_data: self.load_command(param_data),
                'next': lambda param_data: self.next(param_data),
                'unload': lambda param_data: self.unload(param_data),
                'reset': lambda param_data: self.reset(param_data),
                'usersettings': lambda param_data: self.usersettings_command(param_data)
            }[cmd](json_data)
        except Exception as e:
            self.log.error(f'Failed to execute command {cmd}: {e}')

    async def _mqtt_loop_ctx(self, app):
        self.connectionHandler.start()
        app['mqtt_handler'] = self.connectionHandler  # TODO: temporarily exposed so websocket can publish

        yield

        app['mqtt_handler'] = None
        await self.connectionHandler.stop()

    # HACK: parse testdata json to be sent to frontend: this is a quick hack to show the raw STDF data in frontend for now
    #       * we should not pass this data as base64 for performance reasons
    #       * the code for processing and eventually merging/aggregating stdf data from all sites should be in its own module/file
    def _try_convert_stdf_data_in_testresult_payload_to_dict_for_json(self, testresult_payload: dict):
        # TODO: we do nothing with test-results until we have a specification how the results look like (json or base64 ??)
        return
        try:
            testdata = testresult_payload['testdata']
            if testdata is not None:
                stdf_blob = base64.b64decode(testdata)

                # iterate records here and return record as dict (with readable record type as key and fields-dict as value)
                with io.BytesIO(stdf_blob) as stream:
                    return [[record.id, record.to_dict()]
                            for _, _, _, record in records_from_file(stream, unpack=True)]

        except Exception:
            self.log.exception(f'Error while converting stdf data in testresult (this is ignored for now, no stdf data will be generated for frontend)')
        return None

    # example usage of exacting data from the stdf data reported from a dut test
    def _try_extract_bin_from_testresults_stdf(self, testresult_payload: dict):
        # TODO: we do nothing with test-results until we have a specification how the results look like (json or base64 ??)
        return
        try:
            testdata = testresult_payload['testdata']
            if testdata is not None:
                stdf_blob = base64.b64decode(testdata)

                with io.BytesIO(stdf_blob) as stream:
                    prr_records = [record for _, _, _, record in records_from_file(stream, unpack=True, of_interest=['PRR'])]
                    if len(prr_records) != 1:
                        raise ValueError(f'stdf data in testresults does not contain exactly one PRR record (found: {len(prr_records)})')
                    return prr_records[0].get_value('HARD_BIN')
        except Exception:
            self.log.exception(f'Error while extracting info from stdf data in testresult (this is ignored for now, no stdf data will be generated for frontend)')
        return None

    def _try_add_stdf_data_to_testresults_for_frontend(self):
        for _, testresult_payloads in self.receivedSiteTestResults.items():
            for testresult_payload in testresult_payloads:
                stdf_data = self._try_convert_stdf_data_in_testresult_payload_to_dict_for_json(testresult_payload)
                if stdf_data is not None:
                    testresult_payload['stdf'] = stdf_data
                bin_from_stdf = self._try_extract_bin_from_testresults_stdf(testresult_payload)
                if bin_from_stdf is not None:
                    testresult_payload['bin'] = bin_from_stdf

    async def _master_background_task(self, app):
        try:
            while True:
                # push state change via ui/websocket
                ws_comm_handler = app['ws_comm_handler']
                if ws_comm_handler is not None:
                    await ws_comm_handler.send_status_to_all(self.external_state, self.error_message)

                if len(self.receivedSiteTestResults) != 0:
                    self._try_add_stdf_data_to_testresults_for_frontend()
                    ws_comm_handler = app['ws_comm_handler']
                    if ws_comm_handler is not None:
                        await ws_comm_handler.send_testresults_to_all(
                            self.receivedSiteTestResults)
                    self.receivedSiteTestResults = {}

                await asyncio.sleep(1)

        except asyncio.CancelledError:
            if self.connectionHandler is not None:
                self.connectionHandler.mqtt.publish('TEST/tick', 'dead')
                # TODO: would we need wait for on_published here to ensure the mqqt loop is not stopped?

    async def _master_background_task_ctx(self, app):
        task = asyncio.create_task(self._master_background_task(app))

        yield

        task.cancel()
        await task

    def run(self):
        app = web.Application()
        app['master_app'] = self

        # initialize static file path from config (relative paths are interpreted
        # relative to the current working directory).
        # TODO: the default value of the static file path (here and config template) should
        #       not be based on the development folder structure and simply be './mini-sct-gui'.
        webui_static_path = self.configuration.get('webui_static_path', './src/ATE/ui/angular/mini-sct-gui/dist/mini-sct-gui')
        static_file_path = os.path.realpath(webui_static_path)

        webservice_setup_app(app, static_file_path)
        app.cleanup_ctx.append(self._mqtt_loop_ctx)
        app.cleanup_ctx.append(self._master_background_task_ctx)

        host = self.configuration.get('webui_host', "localhost")
        port = self.configuration.get('webui_port', 8081)
        web.run_app(app, host=host, port=port)
