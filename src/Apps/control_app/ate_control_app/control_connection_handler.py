import asyncio
import os
from pathlib import Path
import sys
from transitions import Machine
import json

from ate_apps_common.mqtt_connection import MqttConnection
from ate_common.logger import LogLevel


SOFTWARE_VERSION = 1
INTERFACE_VERSION = 1


class ControlAppMachine:
    states = ['idle', 'loading', 'busy', 'error', 'resetting']

    # multiple space code style "error" will be ignored for a better presentation of the possible state machine transitions
    transitions = [
        {'source': 'idle',      'dest': 'loading',   'trigger': 'load',                   'after': 'on_load'},                 # noqa: E241
        {'source': 'loading',   'dest': 'busy',      'trigger': 'testapp_active'},                                             # noqa: E241
        {'source': 'busy',      'dest': 'idle',      'trigger': 'testapp_exit',           'after': 'on_test_app_exit'},        # noqa: E241
        {'source': 'idle',      'dest': 'idle',      'trigger': 'testapp_exit',           'after': 'on_test_app_exit'},        # noqa: E241

        {'source': '*',         'dest': 'resetting', 'trigger': 'reset',                  'after': 'on_reset'},                # noqa: E241
        {'source': 'resetting', 'dest': 'idle',      'trigger': 'to_idle'},                                                    # noqa: E241

        {'source': '*',         'dest': 'error',     'trigger': 'load_error',             'after': 'on_error'},                 # noqa: E241
        {'source': '*',         'dest': 'error',     'trigger': 'test_app_error',         'after': 'on_error'},                 # noqa: E241
        {'source': '*',         'dest': 'error',     'trigger': 'error',                  'after': 'on_error'},                 # noqa: E241
    ]

    def __init__(self, conhandler):
        self._conhandler = conhandler
        self.log = conhandler.log
        self.prev_state = ''
        self._error_message = ''

        self.process = None
        self.stderr = None
        self.do_reset = False

        self.machine = Machine(model=self, states=self.states, transitions=self.transitions, initial='idle', after_state_change=self.publish_current_state)

    def publish_current_state(self, info: str):
        self._conhandler.publish_state(self.state, self._error_message)

        if self.prev_state != self.state:
            self.log.log_message(LogLevel.Info(), f'control state is: {self.state}')

        self.prev_state = self.state

    def on_master_state_changed(self, info: str):
        self.publish_current_state(info)

    async def _run_testapp_task(self, testapp_params: dict):
        try:
            args = [str(sys.executable), testapp_params['testapp_script_path'],
                    '--device_id', self._conhandler.device_id,
                    '--site_id', self._conhandler.site_id,
                    '--broker_host', self._conhandler.broker_host,
                    '--broker_port', str(self._conhandler.broker_port),
                    '--parent-pid', str(os.getpid()),  # TODO: this should be configurable in future: it will make the testapp kill itself if this parent process dies
                    '--strategytype', 'external',
                    # '--ptvsd-enable-attach',  # uncomment this to enable attaching the remote debugger
                    # '--ptvsd-wait-for-attach',  # uncomment this to enable attaching the remote debugger AND waiting for an remote debugger to be attached before initialization
                    *testapp_params.get('testapp_script_args', [])]

            os.environ[testapp_params['testapp_script_path'].split('.')[0]] = f"{testapp_params['bin_table']}"
            self.process = await asyncio.create_subprocess_exec(*args,
                                                                cwd=testapp_params.get('cwd'),
                                                                stdout=asyncio.subprocess.PIPE,
                                                                stderr=asyncio.subprocess.PIPE)
            self.testapp_active(self.process.pid)
            _, self.stderr = await self.process.communicate()
            self.testapp_exit(self.process.returncode)
        except asyncio.CancelledError:
            self._terminate()

    def on_error(self, message: str):
        self.log.log_message(LogLevel.Error(), f'{message}')

    def on_load(self, testapp_params: dict):
        self._error_message = ''
        self.log.log_message(LogLevel.Info(), f'test_program parameters: {str(testapp_params)}')
        if not self._does_test_program_exist(testapp_params):
            self.load_error(f'Test program could not be found: {testapp_params["cwd"]}/{testapp_params["testapp_script_path"]}')
            return

        _ = asyncio.create_task(self._run_testapp_task(testapp_params))

    @staticmethod
    def _does_test_program_exist(testapp_params: dict):
        path = Path(testapp_params.get('cwd'))
        if not path.joinpath(testapp_params['testapp_script_path']).exists():
            return False

        return True

    def on_test_app_exit(self, return_code: int):
        self.process = None

        # ignore testprogram cancellation if reset is required
        if self.do_reset:
            self.do_reset = False
            return

        if return_code != 0:
            self._error_message = self.stderr.decode('ascii')
            self.test_app_error(f'test program ends with an error:\n {self._error_message}')

    def on_reset(self, _):
        try:
            if self.process:
                self._terminate()
        except Exception as e:
            self.log.log_message(LogLevel.Error(), f"could not terminate testapp properly: {e}")

        self.do_reset = True
        self.to_idle(_)

    def _terminate(self):
        import platform
        if platform.system() == "Windows":
            self.process.terminate()
        else:
            self.process.kill()


class ControlConnectionHandler:

    """ handle connection """

    def __init__(self, host, port, site_id, device_id, logger):
        self.broker_host = host
        self.broker_port = port
        self.site_id = site_id
        self.device_id = device_id
        self.log = logger
        mqtt_client_id = f'controlapp.{device_id}.{site_id}'
        self.mqtt = MqttConnection(host, port, mqtt_client_id, self.log)
        self.log.set_mqtt_client(self)
        self.mqtt.init_mqtt_client_callbacks(self._on_connect_handler,
                                             self._on_disconnect_handler)

        self.mqtt.register_route(self._generate_base_topic_cmd(), lambda topic, payload: self.on_message_handler(topic, payload))
        self.mqtt.register_route(self._generate_base_topic_status_master(), lambda topic, payload: self.on_message_handler(topic, payload))

        self.commands = {
            "loadTest": self.__load_test_program,
            "reset": self.__reset_after_error,
            "setloglevel": self.__set_log_level,
        }
        self._statemachine = ControlAppMachine(self)

    def start(self):
        self.mqtt.set_last_will(
            self._generate_base_topic_status(),
            self.mqtt.create_message(
                self._generate_status_message('crash', '')))
        self.mqtt.start_loop()

    async def stop(self):
        await self.mqtt.stop_loop()

    def publish_state(self, state, error_message, statedict=None):
        self.mqtt.publish(self._generate_base_topic_status(),
                          self.mqtt.create_message(
                              self._generate_status_message(state, error_message, statedict)),
                          retain=False)

    def publish_log_information(self, log):
        self.mqtt.publish(
            topic=self._generate_log_topic(),
            payload=json.dumps(self.log_payload(log)),
            qos=0,
            retain=False),

    def send_log(self, log):
        self.publish_log_information(log)

    def __set_log_level(self, cmd_payload: dict):
        level = cmd_payload['level']
        self.log.set_logger_level(level)

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
            data = json.loads(message.decode('utf-8'))
            assert data['type'] == 'cmd'
            cmd = data['command']
            sites = data['sites']

            self.log.log_message(LogLevel.Debug(), f'received command: {cmd}')

            if self.site_id not in sites:
                self.log.log_message(LogLevel.Warning(), f'ignoring TestApp cmd for other sites {sites} (current site_id is {self.site_id})')
                return

            to_exec_command = self.commands.get(cmd)
            if to_exec_command is None:
                self.log.log_message(LogLevel.Warning(), 'received command not found')
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

    def on_message_handler(self, topic, payload):
        if "Master" in topic:
            self._statemachine.on_master_state_changed(payload)
            return
        if "status" in topic:
            self.on_status_message(payload)
        elif "cmd" in topic:
            self.on_cmd_message(payload)
        else:
            return

    def _on_disconnect_handler(self, client, userdata, distc_res):
        self.log.log_message(LogLevel.Info(), f'mqtt disconnected (rc: {distc_res})')

    def _generate_status_message(self, state, error_message, statedict=None):
        message = {
            "type": "status",
            "interface_version": INTERFACE_VERSION,
            "software_version": SOFTWARE_VERSION,
            "payload": {"state": state, "error_message": error_message}
        }
        if statedict is not None:
            message.update(statedict)
        return message

    def _generate_base_topic_status(self) -> str:
        return "ate/" + self.device_id + "/Control/status/site" + self.site_id

    def _generate_log_topic(self) -> str:
        return "ate/" + self.device_id + "/Control/log/site" + self.site_id

    def _generate_base_topic_cmd(self) -> str:
        return "ate/" + self.device_id + "/Control/cmd"

    def _generate_base_topic_status_master(self) -> str:
        return "ate/" + self.device_id + "/Master/status"

    @staticmethod
    def log_payload(log_info):
        return {
            "type": "log",
            "payload": log_info
        }
