import asyncio
import os
import sys
from transitions import Machine
import json

from ATE.TES.apps.common.connection_handler import ConnectionHandler
from ATE.TES.apps.common.Utils import LogLevel


DEAD = 0
ALIVE = 1
SOFTWARE_VERSION = 1
INTERFACE_VERSION = 1


class ControlAppMachine:
    states = ['idle', 'loading', 'busy', 'error', 'resetting']

    # multiple space code style "error" will be ignored for a better presentation of the possible state machine transitions
    transitions = [
        {'source': 'idle',      'dest': 'loading',   'trigger': 'load',                   'after': 'on_load'},            # noqa: E241
        {'source': 'loading',   'dest': 'busy',      'trigger': 'testapp_active',         'before': 'testapp_before_active'},  # noqa: E241
        {'source': 'busy',      'dest': 'idle',      'trigger': 'testapp_exit',           'after': 'on_test_app_exit'},        # noqa: E241

        {'source': '*',         'dest': 'resetting', 'trigger': 'reset',                  'after': 'on_reset'},     # noqa: E241
        {'source': 'resetting', 'dest': 'idle',      'trigger': 'to_idle'},                                                    # noqa: E241

        {'source': 'idle',      'dest': 'idle',      'trigger': 'reset'},                                                      # noqa: E241

        {'source': '*',         'dest': 'error',     'trigger': 'load_error',            'after': 'on_error'},                 # noqa: E241
        {'source': '*',         'dest': 'error',     'trigger': 'test_app_error',        'after': 'on_error'},                 # noqa: E241
    ]

    def __init__(self, conhandler):
        self._conhandler = conhandler
        self._task = None
        self.log = conhandler.log
        self.prev_state = ''
        self._error_message = ''

        self._process = None
        self.stderr = None

        self.machine = Machine(model=self, states=self.states, transitions=self.transitions, initial='idle', after_state_change=self.publish_current_state)

    def publish_current_state(self, info):
        self._conhandler.publish_state(self.state, self._error_message)

        if self.prev_state != self.state:
            self.log.log_message(LogLevel.Info(), f'publish_current_state: {self.state}')

        self.prev_state = self.state

    def on_master_state_changed(self, info):
        self.publish_current_state(info)

    async def _run_testapp_task(self, testapp_params: dict):
        args = [str(sys.executable), testapp_params['testapp_script_path'],
                '--device_id', self._conhandler.device_id,
                '--site_id', self._conhandler.site_id,
                '--broker_host', self._conhandler.broker_host,
                '--broker_port', str(self._conhandler.broker_port),
                '--parent-pid', str(os.getpid()),  # TODO: this should be configurable in future: it will make the testapp kill itself if this parent process dies
                # '--ptvsd-enable-attach',  # uncomment this to enable attaching the remote debugger
                # '--ptvsd-wait-for-attach',  # uncomment this to enable attaching the remote debugger AND waiting for an remote debugger to be attached before initialization
                *testapp_params.get('testapp_script_args', [])]

        self.process = await asyncio.create_subprocess_exec(*args,
                                                            cwd=testapp_params.get('cwd'),
                                                            stdout=asyncio.subprocess.PIPE,
                                                            stderr=asyncio.subprocess.PIPE)
        self.testapp_active(self.process.pid)
        _, self.stderr = await self.process.communicate()
        self.testapp_exit(self.process.returncode)

    def on_error(self, message):
        self.log.log_message(LogLevel.Error(), f'{message}')

    def on_load(self, testapp_params: dict):
        self._error_message = ''
        self.log.log_message(LogLevel.Info(), f'test_program parameters: {str(testapp_params)}')
        if not self._do_test_program_exists(testapp_params):
            self.load_error('Test program could not be found')
            return

        self._task = asyncio.create_task(self._run_testapp_task(testapp_params))

    def _do_test_program_exists(self, testapp_params):
        if not os.path.exists(os.path.join(testapp_params.get('cwd'), testapp_params['testapp_script_path'])):
            return False

        return True

    def on_test_app_exit(self, return_code):
        self.process = None

        if return_code != 0:
            self._error_message = self.stderr.decode('ascii')
            self.test_app_error(f'Test Program ends with an error:\n {self._error_message}')

    def testapp_before_active(self, pid):
        print('testapp_active: ', pid)

    def on_reset(self):
        if self.process:
            self.process.terminate()

        self.to_idle()

    def before_error(self, info):
        self.log.log_message('error', f'{info}')

        if self._task is not None:
            self._task.cancel()

    def before_reset(self, info):
        print('reset')


class ControlConnectionHandler:

    """ handle connection """

    def __init__(self, host, port, site_id, device_id, logger):
        self.broker_host = host
        self.broker_port = port
        self.site_id = site_id
        self.device_id = device_id
        self.log = logger
        mqtt_client_id = f'controlapp.{device_id}.{site_id}'
        self.mqtt = ConnectionHandler(host, port, mqtt_client_id, self.log)
        self.mqtt.init_mqtt_client_callbacks(self._on_connect_handler,
                                             self._on_message_handler,
                                             self._on_disconnect_handler)

        self.commands = {
            "loadTest": self.__load_test_program,
            "reset": self.__reset_after_error,
        }
        self._statemachine = ControlAppMachine(self)

    def start(self):
        self.mqtt.set_last_will(
            self._generate_base_topic_status(),
            self.mqtt.create_message(
                self._generate_status_message(DEAD, 'crash', '')))
        self.mqtt.start_loop()

    async def stop(self):
        await self.mqtt.stop_loop()

    def publish_state(self, state, error_message, statedict=None):
        self.mqtt.publish(self._generate_base_topic_status(),
                          self.mqtt.create_message(
                              self._generate_status_message(ALIVE, state, error_message, statedict)),
                          retain=False)

    def __load_test_program(self, cmd_payload: dict):
        testapp_params = cmd_payload['testapp_params']
        try:
            self._statemachine.load(testapp_params)
        except Exception as e:
            self._statemachine.error(str(e))
        return True

    def __reset_after_error(self, cmd_payload):
        try:
            self._statemachine.reset(None)
        except Exception as e:
            self._statemachine.error(str(e))
        return True

    def on_cmd_message(self, message):
        try:
            data = json.loads(message.payload.decode('utf-8'))
            assert data['type'] == 'cmd'
            cmd = data['command']
            sites = data['sites']

            self.log.log_message('debug', f'received command: {cmd}')

            if self.site_id not in sites:
                self.log.log_message('warning', f'ignoring TestApp cmd for other sites {sites} (current site_id is {self.site_id})')
                return

            to_exec_command = self.commands.get(cmd)
            if to_exec_command is None:
                self.log.log_message('warning', 'received command not found')
                return

            to_exec_command(data)

        except Exception as e:
            self._statemachine.error(str(e))

    def on_status_message(self, message):
        # TODO: handle status messages
        return

    def _on_connect_handler(self, client, userdata, flags, conect_res):
        self.log.log_message(LogLevel.Info(), 'mqtt connected')

        self.mqtt.subscribe(self._generate_base_topic_cmd())
        self.mqtt.subscribe(self._generate_base_topic_status_master())
        self._statemachine.publish_current_state(None)

    def _on_message_handler(self, client, userdata, message):
        if "Master" in message.topic:
            self._statemachine.on_master_state_changed(message)
            return
        if "status" in message.topic:
            self.on_status_message(message)
        elif "cmd" in message.topic:
            self.on_cmd_message(message)
        else:
            return

    def _on_disconnect_handler(self, client, userdata, distc_res):
        self.log.log_message(LogLevel.Info(), f'mqtt disconnected (rc: {distc_res})')

    def _generate_status_message(self, alive, state, error_message, statedict=None):
        message = {
            "type": "status",
            "alive": alive,
            "interface_version": INTERFACE_VERSION,
            "software_version": SOFTWARE_VERSION,
            "state": state,
            "error_message": error_message
        }
        if statedict is not None:
            message.update(statedict)
        return message

    def _generate_base_topic_status(self) -> str:
        return "ate/" + self.device_id + "/Control/status/site" + self.site_id

    def _generate_base_topic_cmd(self) -> str:
        return "ate/" + self.device_id + "/Control/cmd"

    def _generate_base_topic_status_master(self) -> str:
        return "ate/" + self.device_id + "/Master/status"
