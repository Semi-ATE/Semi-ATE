import asyncio
from enum import Enum

from transitions.core import MachineError
from ATE.common.logger import LogLevel
from ATE.Tester.TES.apps.common.sequence_container import SequenceContainer


STARTUP_TIMEOUT = 300
TOREADY_TIMEOUT = 15
TOINITIALIZED_TIMEOUT = 15


class MasterStates(Enum):
    unknown = 'unknown'
    connecting = 'connecting'
    initialized = 'initialized'
    loading = 'loading'
    ready = 'ready'
    testing = 'testing'
    unloading = 'unloading'
    error = 'softerror'
    crash = 'crash'

    def __call__(self):
        return self.value


class MultiSitesMasterHandler:
    def __init__(self, device_ids):
        self.master_list = {master_id: MasterStates.unknown() for master_id in device_ids}

    def on_master_state_changed(self, master_id, master_state):
        try:
            self.master_list[master_id] = master_state
        except KeyError:
            raise Exception(f'master: {master_id} was not configured')


class HandlerApplication(MultiSitesMasterHandler):
    def __init__(self, machine, device_ids, log):
        super().__init__(device_ids)
        self._machine = machine
        self._device_ids = device_ids
        self._enable_timeouts = True
        self._timeout_handle = None
        self._log = log
        self.prev_master_state = None

        self.pending_transition_master = SequenceContainer([MasterStates.initialized()], self._device_ids, lambda: self._all_testers_detected(),
                                                           lambda master, state: self._on_unexpected_master_state(master, state))
        self.arm_timeout(STARTUP_TIMEOUT, lambda: self.on_error('master(s) could not be recognized'))

    def on_master_state_changed(self, master_id, state):
        self._handle_master_state(state)
        self.prev_master_state = state

        try:
            self.pending_transition_master.trigger_transition(master_id, state, must_match_transition=self.state == MasterStates.connecting())
        except KeyError:
            self._machine.model.on_error(f'unconfigured master_id: {master_id}')

    def _handle_master_state(self, state):
        # ignore connecting state
        if state == MasterStates.connecting():
            return

        if state in (MasterStates.crash(), MasterStates.error()) and self.prev_master_state is not None:
            self.on_error(f'master changes state from "{self.prev_master_state}" to {state}')

        if state == MasterStates.initialized() and self.state == MasterStates.ready():
            self.pending_transition_master = SequenceContainer([MasterStates.initialized()], self._device_ids, lambda: self._all_testers_initialized(),
                                                               lambda master, state: self._on_unexpected_master_state(master, state))
            self.arm_timeout(TOINITIALIZED_TIMEOUT, lambda: self.on_error('master(s) could not be recognized'))

    def startup_done(self, message):
        self._machine.model.startup_done(message)

    def on_error(self, message):
        self._machine.model.on_error(message + ' ' + self.prev_master_state)
        self._log.log_message(LogLevel.Error(), message)
        self.pending_transition_master = SequenceContainer([MasterStates.initialized()], self._device_ids, lambda: self._all_testers_detected(),
                                                           lambda master, state: self._on_unexpected_master_state(master, state))
        self.arm_timeout(STARTUP_TIMEOUT, lambda: self.on_error('master(s) could not be recognized'))

    def _all_testers_detected(self):
        self._machine.model.master_connected('')
        self.disarm_timeout()

    def _on_unexpected_master_state(self, master_id, state):
        self.on_error(f'Master {master_id} reported state {state} while state {MasterStates.initialized()} is expected')

    @property
    def state(self):
        return self._machine.model.state

    def disarm_timeout(self):
        if self._enable_timeouts:
            if self._timeout_handle is not None:
                self._timeout_handle.cancel()
                self._timeout_handle = None

    def arm_timeout(self, timeout_in_seconds: float, callback):
        if self._enable_timeouts:
            self.disarm_timeout()
            self._timeout_handle = asyncio.get_event_loop().call_later(timeout_in_seconds, callback)

    def set_mqtt_client(self, mqtt_client):
        self._log.set_mqtt_client(mqtt_client)

    def handle_message(self, message):
        message_type = message['type']
        try:
            expected_master_state = {'load': lambda: self._on_load_command_issued(),
                                     'next': lambda: self._on_next_command_issued(),
                                     'unload': lambda: self._on_unload_command_issued()}[message_type]()
        except KeyError:
            expected_master_state = [MasterStates.unknown()]
        except MachineError:
            self._log.log_message(LogLevel.Warning(), f'cannot trigger command "{message_type}" from state {self.state}')
            return self._get_error_message(message_type)
        finally:
            self._log.log_message(LogLevel.Info(), f'Handler reports message: {message}')

        if expected_master_state[0] == MasterStates.unknown():
            return {}

        self.pending_transition_master = SequenceContainer(expected_master_state, self._device_ids, lambda: self._get_call_back(expected_master_state[0]),
                                                           lambda site, state: self._on_unexpected_master_state(site, state))

        return {}

    def _get_error_message(self, message_type):
        if self.state in (MasterStates.initialized()) and message_type in ('next', 'load', 'unload'):
            return self._generate_response(message_type, 'notlot')
        if self.state == MasterStates.ready() and message_type in ('load'):
            return self._generate_response(message_type, 'havelot')
        if self.state == MasterStates.testing() and message_type in ('load', 'next', 'unload'):
            return self._generate_response(message_type, 'busy')
        if self.state in (MasterStates.connecting()) and message_type in ('next', 'load', 'unload'):
            return self._generate_response(message_type, 'error', 'No Tester is available')

        return self._generate_response(message_type, 'error')

    def _generate_response(self, command_type, response_type, message=None):
        return {'type': 'error', 'state': self.state, 'command_type': command_type, 'response_type': response_type, 'message': message}

    def _on_load_command_issued(self):
        self._machine.model.master_loading('')
        return [MasterStates.ready()]

    def _on_next_command_issued(self):
        self._machine.model.master_testing('')
        return [MasterStates.ready()]

    def _on_unload_command_issued(self):
        self._machine.model.master_unload('')
        return [MasterStates.initialized()]

    def _get_call_back(self, type):
        try:
            call_back = {MasterStates.ready(): lambda: self._all_testers_ready(),
                         MasterStates.initialized(): lambda: self._all_testers_initialized(),
                         }[type]
            return call_back()
        except KeyError:
            raise Exception(f'callback type: "{type}" is not support')

    def _all_testers_ready(self):
        self._machine.model.master_ready('')
        self.disarm_timeout()

    def _all_testers_initialized(self):
        self._machine.model.master_initialized('')
        self.disarm_timeout()
