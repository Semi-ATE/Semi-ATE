""" master App """

# External imports
from aiohttp import web
from transitions.core import MachineError
from transitions.extensions import HierarchicalMachine as Machine
from queue import Empty, Full, Queue
import asyncio
import mimetypes
import sys
import os

from typing import Callable

from ATE.common.logger import Logger, LogLevel
from ATE.Tester.TES.apps.common.sequence_container import SequenceContainer
from ATE.Tester.TES.apps.masterApp.master_connection_handler import MasterConnectionHandler
from ATE.Tester.TES.apps.masterApp.master_webservice import webservice_setup_app
from ATE.Tester.TES.apps.masterApp.parameter_parser import parser_factory
from ATE.Tester.TES.apps.masterApp.user_settings import UserSettings
from ATE.Tester.TES.apps.masterApp.utils.command_executor import (GetLogFileCommand, GetLogsCommand, GetLotData, GetTestResultsCommand, GetUserSettings, GetYields, GetBinTable)

from ATE.Tester.TES.apps.masterApp.resulthandling.stdf_aggregator import StdfTestResultAggregator
from ATE.Tester.TES.apps.masterApp.resulthandling.result_collection_handler import ResultsCollector
from ATE.Tester.TES.apps.masterApp.utils.result_Information_handler import ResultInformationHandler

from ATE.Tester.TES.apps.masterApp.peripheral_controller import PeripheralController

from ATE.Tester.TES.apps.masterApp.statemachines.MultiSite import (MultiSiteTestingModel, MultiSiteTestingMachine)


INTERFACE_VERSION = 1
MAX_NUM_OF_TEST_PROGRAM_RESULTS = 1000


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
RESPONSE_TIMEOUT = 10


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
              'softerror',
              'waitingforbintable']

    # multiple space code style "error" will be ignored for a better presentation of the possible state machine transitions
    transitions = [
        {'source': 'startup',            'dest': 'connecting',  'trigger': "startup_done",                'after': "on_startup_done"},               # noqa: E241
        {'source': 'connecting',         'dest': 'initialized', 'trigger': 'all_sites_detected',          'after': "on_allsitesdetected"},           # noqa: E241
        {'source': 'connecting',         'dest': 'error',       'trigger': 'bad_interface_version'},                                                 # noqa: E241

        {'source': 'initialized',        'dest': 'loading',     'trigger': 'load_command',                'after': 'on_loadcommand_issued'},         # noqa: E241
        {'source': 'loading',            'dest': 'ready',       'trigger': 'all_siteloads_complete',      'after': 'on_allsiteloads_complete'},      # noqa: E241
        {'source': 'loading',            'dest': 'initialized', 'trigger': 'load_error',                             'after': 'on_load_error'},                 # noqa: E241

        # TODO: properly limit source states to valid states where usersettings are allowed to be modified
        #       ATE-104 says it should not be possible while testing in case of stop-on-fail,
        #       but this constraint may not be required here and could be done in UI)
        {'source': ['initialized', 'ready'], 'dest': '=', 'trigger': 'usersettings_command',                       'after': 'on_usersettings_command_issued'},  # noqa: E241

        {'source': 'ready',              'dest': 'testing',                'trigger': 'next',                      'after': 'on_next_command_issued'},          # noqa: E241
        {'source': 'ready',              'dest': 'unloading',              'trigger': 'unload',                    'after': 'on_unload_command_issued'},        # noqa: E241
        {'source': 'testing_completed',  'dest': 'ready',                  'trigger': 'all_sitetests_complete',    'after': "on_allsitetestscomplete"},         # noqa: E241
        {'source': 'unloading',          'dest': 'initialized',            'trigger': 'all_siteunloads_complete',  'after': "on_allsiteunloadscomplete"},       # noqa: E241

        {'source': 'ready',              'dest': '=',                      'trigger': 'getresults',                'after': 'on_getresults_command'},           # noqa: E241
        {'source': '*',                  'dest': '=',                      'trigger': 'getlogs',                   'after': 'on_getlogs_command'},              # noqa: E241
        {'source': '*',                  'dest': '=',                      'trigger': 'getlogfile',                'after': 'on_getlogfile_command'},           # noqa: E241
        {'source': '*',                  'dest': '=',                      'trigger': 'setloglevel',               'after': 'on_setloglevel_command'},          # noqa: E241

        {'source': '*',                  'dest': 'softerror',              'trigger': 'testapp_disconnected',      'after': 'on_disconnect_error'},             # noqa: E241
        {'source': '*',                  'dest': 'softerror',              'trigger': 'timeout',                   'after': 'on_timeout'},                      # noqa: E241
        {'source': '*',                  'dest': 'softerror',              'trigger': 'on_error',                  'after': 'on_error_occurred'},               # noqa: E241
        {'source': 'softerror',          'dest': 'connecting',             'trigger': 'reset',                     'after': 'on_reset_received'}                # noqa: E241

    ]

    """ MasterApplication """

    def __init__(self, configuration):
        self.sites = configuration['sites']
        super().__init__(self.sites)
        self.fsm = Machine(model=self,
                           states=MasterApplication.states,
                           transitions=MasterApplication.transitions,
                           initial="startup",
                           after_state_change='publish_state')
        self.configuration = configuration
        self.log = Logger('master')
        self.loglevel = LogLevel.Warning() if configuration.get('loglevel') is None else configuration['loglevel']
        self.log.set_logger_level(self.loglevel)
        self.apply_configuration(configuration)
        self.init()
        self.connectionHandler = MasterConnectionHandler(self.broker_host, self.broker_port, self.configuredSites, self.device_id, self.handler_id, self)
        self.peripheral_controller = PeripheralController(self.connectionHandler.mqtt, self.device_id)

        self.received_site_test_results = []
        self.received_sites_test_results = ResultsCollector(MAX_NUM_OF_TEST_PROGRAM_RESULTS)

        self.loaded_jobname = ""
        self.loaded_lot_number = ""
        self.error_message = ''

        self.prev_state = ''
        self.summary_counter = 0
        self.tsr_messages = []
        self.sites_to_test = []

        self.command_queue = Queue(maxsize=50)
        self._result_info_handler = ResultInformationHandler(self.sites)

        self.test_results = []

        self.dummy_partid = 1
        self._first_part_tested = False
        self._stdf_aggregator = None

    def init(self):
        self.siteStates = {site_id: CONTROL_STATE_UNKNOWN for site_id in self.configuredSites}
        self.pendingTransitionsControl = SequenceContainer([CONTROL_STATE_IDLE], self.configuredSites, lambda: self.all_sites_detected(),
                                                           lambda site, state: self.on_unexpected_control_state(site, state))
        self.pendingTransitionsTest = SequenceContainer([TEST_STATE_IDLE], self.configuredSites, lambda: self.all_siteloads_complete(),
                                                        lambda site, state: self.on_unexpected_testapp_state(site, state))
        self.init_user_settings()

        self.timeoutHandle = None
        self.arm_timeout(STARTUP_TIMEOUT, lambda: self.timeout("Not all sites connected."))

    def apply_configuration(self, configuration: dict):
        try:
            self.configuredSites = configuration['sites']
            # Sanity check for bad configurations:
            if len(self.configuredSites) == 0:
                self.log.log_message(LogLevel.Error(), 'Master got no sites assigned')
                sys.exit()

            self.device_id = configuration['device_id']
            self.broker_host = configuration['broker_host']
            self.broker_port = configuration['broker_port']
            self.enableTimeouts = configuration['enable_timeouts']
            self.handler_id = configuration['Handler']
            self.env = configuration['environment']
        except KeyError as e:
            self.log.log_message(LogLevel.Error(), f'Master got invalid configuration: {e}')
            sys.exit()

    @property
    def user_settings_filepath(self):
        return self.configuration.get("user_settings_filepath")

    @property
    def persistent_user_settings_enabled(self):
        return self.user_settings_filepath is not None

    def init_user_settings(self):
        self.user_settings = self._load_usersettings()

    def _load_usersettings(self):
        if self.persistent_user_settings_enabled:
            try:
                user_settings = UserSettings.load_from_file(self.user_settings_filepath)
            except FileNotFoundError:
                user_settings = UserSettings.get_defaults()

            # always update file with hardcoded defaults (and create it if it does not exist)
            UserSettings.save_to_file(self.user_settings_filepath, user_settings, add_defaults=True)
        else:
            user_settings = UserSettings.get_defaults()

        return user_settings

    def modify_user_settings(self, settings):
        self.user_settings.update(self._extract_settings(settings))
        if self.persistent_user_settings_enabled:
            UserSettings.save_to_file(self.user_settings_filepath, self.user_settings, add_defaults=True)

        self.command_queue.put_nowait(GetUserSettings(lambda: self._generate_usersettings_message(self.user_settings)))

    def _store_user_settings(self, settings):
        UserSettings.save_to_file(self.user_settings_filepath, settings, add_defaults=True)
        self.user_settings = settings
        self.command_queue.put_nowait(GetUserSettings(lambda: self._generate_usersettings_message(self.user_settings)))

    def on_usersettings_command_issued(self, param_data: dict):
        settings = param_data['payload']
        self.modify_user_settings(settings)

    @staticmethod
    def _extract_settings(settings):
        modified_settings = UserSettings.get_defaults()
        for setting in settings:
            field = {setting['name']: {'active': setting['active'], 'value': int(setting['value']) if setting.get('value') else -1}}
            modified_settings.update(field)

        return modified_settings

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
        # TODO: no reason to keep this ??
        if self.state == "connecting":
            self.publish_state()
            asyncio.get_event_loop().call_later(1, lambda: self.repost_state_if_connecting())

    def on_startup_done(self):
        self.repost_state_if_connecting()

    def on_timeout(self, message):
        self.error_message = message
        self.log.log_message(LogLevel.Error(), message)

    def on_disconnect_error(self, site_id, data):
        self.log.log_message(LogLevel.Error(), f'Master entered state error due to disconnect of site {site_id}')

    def on_unexpected_control_state(self, site_id, state):
        self.log.log_message(LogLevel.Warning(), f'Site {site_id} reported state {state}. This state is ignored during startup.')
        self.error_message = f'Site {site_id} reported state {state}'

        if self.state == 'connecting' and state == 'busy':
            self.on_error(f"master can't handle control {site_id}'s state 'busy' during statup")

    def on_unexpected_testapp_state(self, site_id, state):
        self.log.log_message(LogLevel.Warning(), f'TestApp for site {site_id} reported state {state}. This state is ignored during startup.')
        self.error_message = f'TestApp for site {site_id} reported state {state}'

        if self.state == 'connecting' and state == 'idle':
            self.on_error(f"master can't handle testApp {site_id}'s state 'idle' during statup")

    def on_error_occurred(self, message):
        self.log.log_message(LogLevel.Error(), f'Master entered state error, reason: {message}')
        self.error_message = message

    def on_load_error(self):
        self.log.log_message(LogLevel.Warning(), self.error_message)

    def on_allsitesdetected(self):
        # Trap any controls that misbehave and move out of the idle state.
        # In this case we want to move to error as well
        self.pendingTransitionsControl = SequenceContainer([CONTROL_STATE_IDLE], self.configuredSites, lambda: None,
                                                           lambda site, state: self.on_error(f"Bad statetransition of control {site} during sync to {state}"))

        self.error_message = ''
        self.disarm_timeout()

    def publish_state(self, site_id=None, param_data=None):
        if self.prev_state == self.state:
            return

        self.prev_state = self.state
        self.log.log_message(LogLevel.Info(), f'Master state is {self.state}')
        self.connectionHandler.publish_state(self.external_state)

    def on_loadcommand_issued(self, param_data: dict):
        self._result_info_handler.clear_all()

        jobname = param_data['lot_number']
        # TODO: see no difference !!
        self.loaded_jobname = str(jobname)
        self.loaded_lot_number = str(jobname)

        jobformat = self.configuration.get('jobformat')
        parser = parser_factory.CreateParser(jobformat)
        source = parser_factory.CreateDataSource(jobname,
                                                 self.configuration,
                                                 parser,
                                                 self.log)

        if self.configuration.get('skip_jobdata_verification', False):
            self._test_program_data = {"DEBUG_OPTION": "no content because skip_jobdata_verification enabled"}
        else:
            param_data = source.retrieve_data()
            if param_data is None:
                self.error_message = "Failed to execute load command"
                self.load_error()
                return

            if not source.verify_data(param_data):
                self.error_message = "Malformed jobfile"
                self.load_error()
                return

            self._test_program_data = source.get_test_information(param_data)
            bin_table = source.get_bin_table(self._test_program_data)
            self._result_info_handler.set_bin_settings(bin_table)

            # used to reduce the size of data to be transferred to the TP
            self._test_program_data['BINTABLE'] = source.get_binning_tuple(bin_table)

            self.log.log_message(LogLevel.Debug(), f'testprogram information: {self._test_program_data}')

        self.arm_timeout(LOAD_TIMEOUT, lambda: self.timeout("not all sites loaded the testprogram"))
        self.pendingTransitionsControl = SequenceContainer([CONTROL_STATE_LOADING, CONTROL_STATE_BUSY], self.configuredSites, lambda: None,
                                                           lambda site, state: self.on_error(f"Bad statetransition of control {site} during load to {state}"))
        self.pendingTransitionsTest = SequenceContainer([TEST_STATE_IDLE], self.configuredSites, lambda: self.all_siteloads_complete(),
                                                        lambda site, state: self.on_error(f"Bad statetransition of testapp {site} during load to {state}"))
        self.error_message = ''

        self.connectionHandler.send_load_test_to_all_sites(self.get_test_parameters(self._test_program_data))
        self._store_user_settings(UserSettings.get_defaults())

        self.command_queue.put_nowait(GetBinTable(lambda: self._generate_bin_table_message()))

    @staticmethod
    def get_test_parameters(data):
        # TODO: workaround until we specify the connection to the server or even mount the project locally
        from pathlib import Path
        import os
        return {
            'testapp_script_path': os.path.join(os.path.basename(os.fspath(Path(data['PROGRAM_DIR'])))),
            'testapp_script_args': ['--verbose'],
            'cwd': os.path.dirname(data['PROGRAM_DIR']),
            'bin_table': data['BINTABLE']                                                           # optional/unused for now
        }

    def on_allsiteloads_complete(self, paramData=None):
        self.error_message = ''
        self.disarm_timeout()

        self._stdf_aggregator = StdfTestResultAggregator(self.device_id + ".Master", self.loaded_lot_number, self.loaded_jobname, self.sites)
        self._stdf_aggregator.set_test_program_data(self._test_program_data)
        self._send_set_log_level()

    def _send_set_log_level(self):
        level = {
            LogLevel.Debug(): 'Debug',
            LogLevel.Info(): 'Info',
            LogLevel.Warning(): 'Warning',
            LogLevel.Error(): 'Error',
        }[self.loglevel]

        self.log.log_message(LogLevel.Info(), f'set loglevel to {level}')
        self.connectionHandler.send_set_log_level(self.loglevel)

    def on_next_command_issued(self, param_data: dict):
        if not self._first_part_tested:
            self._stdf_aggregator.write_header_records()
            self._first_part_tested = True
            self.command_queue.put_nowait(GetLotData(lambda: self._generate_lot_data_message()))

        self.received_site_test_results = []
        self.arm_timeout(TEST_TIMEOUT, lambda: self.timeout("not all sites completed the active test"))
        self.pendingTransitionsTest = SequenceContainer([TEST_STATE_TESTING, TEST_STATE_IDLE], self.configuredSites, lambda: None,
                                                        lambda site, state: self.on_error(f"Bad statetransition of testapp {site} during test to {state}"))
        self.error_message = ''

        settings = self.user_settings.copy()
        settings.update(self._extract_sites_information(param_data))
        self.connectionHandler.send_next_to_all_sites(settings)

    def _extract_sites_information(self, parameters):
        try:
            sites_info = parameters['sites']
            self.sites_to_test = [site['siteid'] for site in sites_info]
            self.sites_to_test.sort()
            self.sites.sort()

            if not (self.sites_to_test == self.sites):
                self.log.log_message(LogLevel.Error(), f'Master do not support site(s): {set(self.sites_to_test) - set(self.sites)}')
                self.on_error('"next command", handler requiers not configured site(s)')
            return self._generate_sites_message(self.sites_to_test, sites_info)
        except Exception:
            return self._generate_default_sites_configuration()

    def _generate_default_sites_configuration(self):
        sites_info = []
        self.sites_to_test = self.sites
        for index in range(len(self.sites)):
            sites_info.append({'siteid': str(index), 'partid': str(self.dummy_partid), 'binning': -1})
            self.dummy_partid += 1

        return self._generate_sites_message(self.sites, sites_info)

    @staticmethod
    def _generate_sites_message(sites, sites_info):
        return {'sites': sites, 'sites_info': sites_info}

    def on_unload_command_issued(self, param_data: dict):
        self.arm_timeout(UNLOAD_TIMEOUT, lambda: self.timeout("not all sites unloaded the testprogram"))
        self.pendingTransitionsControl = SequenceContainer([CONTROL_STATE_IDLE], self.configuredSites, lambda: self.all_siteunloads_complete(),
                                                           lambda site, state: self.on_error(f"Bad statetransition of control {site} during unload to {state}"))
        self.pendingTransitionsTest = SequenceContainer([TEST_STATE_TERMINATED], self.configuredSites, lambda: None, lambda site, state: None)
        self.error_message = ''
        self.connectionHandler.send_terminate_to_all_sites()
        self._first_part_tested = False

    def on_reset_received(self, param_data: dict):
        self.arm_timeout(UNLOAD_TIMEOUT, lambda: self.timeout("not all sites do report state idle after reset"))
        self.pendingTransitionsControl = SequenceContainer([CONTROL_STATE_IDLE], self.configuredSites, lambda: self.all_sites_detected(),
                                                           lambda site, state: self.on_unexpected_control_state(site, state))

        self.pendingTransitionsTest = None
        self.connectionHandler.send_reset_to_all_sites()

        # set a virtual control state to make sure that any responce from control would be caught and handeled
        for site in self.configuredSites:
            self.siteStates[site] = 'resetting'

    def on_allsiteunloadscomplete(self):
        self.disarm_timeout()

        self.received_sites_test_results.clear()
        self.loaded_lot_number = ''

    def on_allsitetestscomplete(self):
        self._send_test_results()
        self.test_results = []
        self.disarm_timeout()
        self.handle_reset()

    def _send_test_results(self):
        self.connectionHandler.send_test_results(self.test_results)

    def on_site_test_result_received(self, site_id, param_data):
        payload = param_data['payload']
        self._write_stdf_data(payload)

        prr_record = None
        # hack: (-)inf could not be parsed into a json object, so we cast it to string
        for index, rec in enumerate(payload):
            for key, value in rec.items():
                if str(value) in ('inf', '-inf'):
                    payload[index][key] = str(value)

            if rec['type'] == 'PRR':
                prr_record = rec

        assert prr_record

        self.received_sites_test_results.append(payload)
        self.received_site_test_results.append(param_data)
        success, msg = self._result_info_handler.handle_result(prr_record)

        if not success:
            self.on_error(msg)

        self.test_results.append(self._result_info_handler.get_site_result_response(prr_record))

    def _write_stdf_data(self, stdf_data):
        self._stdf_aggregator.append_test_results(stdf_data)

    def on_control_status_changed(self, siteid: str, status_msg: dict):
        if self.external_state == 'softerror':
            return

        newstatus = status_msg['payload']['state']

        if(status_msg['interface_version'] != INTERFACE_VERSION):
            self.log.log_message(LogLevel.Error(), f'Bad interface version on site {siteid}')
            self.bad_interface_version()

        try:
            if(self.siteStates[siteid] != newstatus):
                self.log.log_message(LogLevel.Info(), f'Control {siteid} state is {newstatus}')
                self.siteStates[siteid] = newstatus
                self.pendingTransitionsControl.trigger_transition(siteid, newstatus)
        except KeyError:
            self.on_error(f"Site id received: {siteid} is not configured")

    def on_testapp_status_changed(self, siteid: str, status_msg: dict):
        if self.external_state == 'softerror':
            return

        newstatus = status_msg['payload']['state']
        self.log.log_message(LogLevel.Info(), f'Testapp {siteid} state is {newstatus}')
        if self.is_testing(allow_substates=True) and newstatus == TEST_STATE_IDLE:
            self.handle_status_idle(siteid)

        if self.pendingTransitionsTest:
            self.pendingTransitionsTest.trigger_transition(siteid, newstatus)

    def on_log_message(self, siteid: str, log_msg: dict):
        self.log.append_log(log_msg['payload'])

    def on_testapp_testresult_changed(self, siteid: str, status_msg: dict):
        if self.is_testing(allow_substates=True):
            self.handle_testresult(siteid, status_msg)
            self.on_site_test_result_received(siteid, status_msg)
        else:
            self.on_error(f"Received unexpected testresult from site {siteid}")

    def on_testapp_testsummary_changed(self, message: dict):
        self.summary_counter += 1
        self.tsr_messages.extend(message['payload'])

        if self.summary_counter == len(self.configuredSites):
            self._stdf_aggregator.finalize()

            self._stdf_aggregator.append_soft_and_hard_bin_record(self._result_info_handler.get_hbin_soft_bin_report())
            self._stdf_aggregator.append_test_summary(self.tsr_messages)
            self._stdf_aggregator.append_part_count_infos(self._result_info_handler.get_part_count_infos())

            self._stdf_aggregator.write_footer_records()
            self._stdf_aggregator = None
            self.summary_counter = 0
            self.tsr_messages.clear()

    def on_testapp_resource_changed(self, siteid: str, resource_request_msg: dict):
        self.handle_resource_request(siteid, resource_request_msg)

    def on_peripheral_response_received(self, response):
        self.peripheral_controller.on_response_received(response)

    def on_handler_status_changed(self, msg: dict):
        if self.external_state == 'softerror':
            return

        if msg['state'] == 'connecting':
            self.connectionHandler.publish_state(self.state)

        # TODO: how to handle status crash or error
        if msg['state'] in ('error', 'crash'):
            return

    def on_handler_response_message(self, msg):
        res = msg.get('type')
        payload = msg.get('payload')
        try:
            {
                'temperature': lambda: self._handle_handler_temperature(payload),
            }[res]()
        except KeyError:
            self.log.log_message(LogLevel.Error(), f'Failed to execute response: {res}')
        except MachineError:
            self.on_error(f'cannot trigger command "{res}" from state "{self.fsm.model.state}"')

    def _handle_handler_temperature(self, param_data):
        self.log.log_message(LogLevel.Info(), f'handler temperature is : {param_data["temperature"]}')

    def on_handler_command_message(self, msg: dict):
        cmd = msg.get('type')
        payload = msg.get('payload')
        try:
            {
                'load': lambda param_data: self.load_command(param_data),
                'next': lambda param_data: self.next(param_data),
                'unload': lambda param_data: self.unload(param_data),
                'reset': lambda param_data: self.reset(param_data),
                'identify': lambda param_data: self._send_tester_identification(param_data),
                'get-state': lambda param_data: self._send_tester_state(param_data),
            }[cmd](payload)
        except KeyError:
            self.log.log_message(LogLevel.Error(), f'Failed to execute command: {cmd}')
        except MachineError:
            self.on_error(f'cannot trigger command "{cmd}" from state "{self.fsm.model.state}"')

    def _send_tester_identification(self, _):
        self.connectionHandler.send_identification()

    def _send_tester_state(self, _):
        self.connectionHandler.send_state(self.external_state, self.error_message)

    def send_handler_get_temperature_command(self):
        self.connectionHandler.send_handler_get_temperature_command()

    def apply_resource_config(self, resource_request: dict, on_resource_config_applied_callback: Callable):
        resource_id = resource_request['periphery_type']

        async def periphery_io_control_task():
            try:
                result = await self.periphery_io_control(resource_request)
                on_resource_config_applied_callback()
                self.connectionHandler.publish_ioctl_response(resource_request, result)
            except asyncio.TimeoutError:
                # Applying the resource configuration ran into a timeout.
                # We err-out in this case.
                self.connectionHandler.publish_ioctl_timeout(resource_request)
                # TBD: Dunno if this is actually that much of a good idea,
                # as nothing is wrong with the tester per se here.
                self.on_error(f"Failed to control resource {resource_id}. Reason: Timeout.")

        asyncio.get_event_loop().create_task(periphery_io_control_task())

    async def periphery_io_control(self, resource_request):
        resource_id = resource_request['periphery_type']
        ioctl_name = resource_request['ioctl_name']
        parameters = resource_request['parameters']
        return await self.peripheral_controller.device_io_control(resource_id, ioctl_name, parameters)

    def dispatch_command(self, json_data):
        cmd = json_data.get('command')
        try:
            {
                'load': lambda param_data: self.load_command(param_data),
                'next': lambda param_data: self.next(param_data),
                'unload': lambda param_data: self.unload(param_data),
                'reset': lambda param_data: self.reset(param_data),
                'usersettings': lambda param_data: self.usersettings_command(param_data),
                'getresults': lambda param_data: self._handle_command_with_response(param_data),
                'getlogs': lambda param_data: self._handle_command_with_response(param_data),
                'getlogfile': lambda param_data: self._handle_command_with_response(param_data),
                'setloglevel': lambda param_data: self.setloglevel(param_data),
            }[cmd](json_data)
        except Exception as e:
            self.log.log_message(LogLevel.Error(), f'Failed to execute command {cmd}: {e}')

    def on_setloglevel_command(self, param_data):
        loglevel = param_data['level']
        self.loglevel = loglevel
        self.log.set_logger_level(loglevel)
        self._send_set_log_level()
        self.command_queue.put_nowait(GetUserSettings(lambda: self._generate_usersettings_message(self.user_settings)))

    def _handle_command_with_response(self, data):
        cmd = data.get('command')
        connection_id = data.get('connectionid')
        try:
            obj = {'getlogs': lambda: GetLogsCommand(self.log, connection_id),
                   'getlogfile': lambda: GetLogFileCommand(self.log, connection_id),
                   'getresults': lambda: GetTestResultsCommand(self.received_sites_test_results, connection_id),
                   }[cmd]()
            try:
                self.command_queue.put_nowait(obj)
            except Full:
                pass

        except KeyError:
            pass

    async def _mqtt_loop_ctx(self, app):
        self.connectionHandler.start()
        # ToDo Get rid of this, propably no longer needed!
        app['mqtt_handler'] = self.connectionHandler

        yield

        app['mqtt_handler'] = None
        await self.connectionHandler.stop()

    def on_new_connection(self, connection_id):
        self.command_queue.put_nowait(GetUserSettings(lambda: self._generate_usersettings_message(self.user_settings)))
        self.command_queue.put_nowait(GetTestResultsCommand(self.received_sites_test_results, connection_id))
        self.command_queue.put_nowait(GetYields(lambda: self._generate_yield_message(), connection_id))
        self.command_queue.put_nowait(GetBinTable(lambda: self._generate_bin_table_message(), connection_id))

        if self._stdf_aggregator:
            self.command_queue.put_nowait(GetLotData(lambda: self._generate_lot_data_message(), connection_id))

    async def _master_background_task(self, app):
        try:
            while True:
                ws_comm_handler = app['ws_comm_handler']
                if ws_comm_handler is None:
                    await asyncio.sleep(1)
                    continue

                if not ws_comm_handler.is_ws_connection_established():
                    self.log.clear_logs()

                await self._handle_sending_data(ws_comm_handler)
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            pass

    async def _execute_commands(self, ws_comm_handler):
        while True:
            try:
                command = self.command_queue.get_nowait()
            except Empty:
                break

            if not command.is_data_ready():
                try:
                    self.command_queue.put_nowait(command)
                except Full:
                    continue

            await command.execute(ws_comm_handler)

    async def _handle_sending_data(self, ws_comm_handler):
        # TODO: used to update front-end's clock, do we need to do this anyway
        await ws_comm_handler.send_status_to_all(self.external_state, self.error_message)

        # TODO: ATE-227, sync with UI Team
        for test_result in self.received_site_test_results:
            await ws_comm_handler.send_testresults_to_all(test_result)
            await ws_comm_handler.send_yields(self._generate_yield_message())
            await ws_comm_handler.send_bin_table(self._generate_bin_table_message())

        self.received_site_test_results = []

        await self._execute_commands(ws_comm_handler)

        available_logs = self.log.get_current_logs()
        if len(available_logs) > 0:
            await ws_comm_handler.send_logs_to_all(available_logs)

    def _generate_yield_message(self):
        return self._result_info_handler.get_yield_messages()

    def _generate_bin_table_message(self):
        return self._result_info_handler.get_bin_table()

    def _generate_usersettings_message(self, usersettings):
        settings = []

        for usersetting, value in usersettings.items():
            settings.append({'name': usersetting, 'active': value['active'], 'value': int(value['value'])})

        test_options = {'testoptions': settings}
        log_level = {'loglevel': self.loglevel}
        usersetting = {}
        usersetting.update(test_options)
        usersetting.update(log_level)

        return usersetting

    def _generate_lot_data_message(self):
        return self._stdf_aggregator.get_MIR_dict()

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

        host = self.configuration.get('webui_host', 'localhost')
        port = self.configuration.get('webui_port', 8081)
        web.run_app(app, host=host, port=port)
