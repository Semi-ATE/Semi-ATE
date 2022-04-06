from enum import Enum
import json
import paho.mqtt.client as mqtt
import argparse
import sys
import time
from transitions import Machine
import concurrent.futures
import logging
import os
import threading
from typing import Optional
from ate_test_app import thetestzip_mock
import queue


logger = logging.getLogger(__name__)

RESOURCE_CONFIG_REQUEST_TIMEOUT = 30  # TODO: reduce, it's temporarily large for manual mqtt messaging


# source: https://stackoverflow.com/a/23587108
def start_parent_process_death_watchdog_win32(parent_pid):
    from ctypes import WinDLL
    from ctypes.wintypes import DWORD, BOOL, HANDLE
    # Magic value from http://msdn.microsoft.com/en-us/library/ms684880.aspx
    SYNCHRONIZE = 0x00100000
    kernel32 = WinDLL("kernel32.dll")
    kernel32.OpenProcess.argtypes = (DWORD, BOOL, DWORD)
    kernel32.OpenProcess.restype = HANDLE
    parent_handle = kernel32.OpenProcess(SYNCHRONIZE, False, parent_pid)

    def _threadproc(parent_handle):
        try:
            os.waitpid(parent_handle, 0)
        finally:
            print(f"PARENT PROCESS WATCHDOG TRIGGERED: process with pid {parent_pid} has died. killing this process ({os.getpid()}) as well...",
                  file=sys.stderr, flush=True)
            os._exit(1)

    t = threading.Thread(target=_threadproc,
                         args=(parent_handle,),
                         daemon=True)
    t.start()


# def start_parent_process_death_watchdog_linux(parent_pid):

#     def _threadproc(parent_pid):
#         try:
#             # unix behavior of os.waitpid: "If pid is less than -1, status is requested for any process in the process group -pid (the absolute value of pid)"
#             # TODO: does not work, os.waitpid can probably not be used, because 'any process' in the progress group includes this one !?
#             # os.waitpid(-parent_pid, 0)
#             while True:
#                 print('getppid: ', os.getppid())
#                 print('getpgrp: ', os.getpgrp())
#                 print(f'getpgid({parent_pid}): ', os.getpgid(parent_pid))
#                 time.sleep(1)
#         finally:
#             os._exit(1)

#     t = threading.Thread(target=_threadproc,
#                          args=(parent_pid,),
#                          daemon=True)
#     t.start()


class TheTestAppStatusAlive(Enum):
    DEAD = 0      # error/crash
    ALIVE = 1
    SHUTDOWN = 2  # graceful shutdown
    INITFAIL = 3  # init failed


class TheTestAppParameters:
    __slots__ = ["broker_host", "broker_port", "device_id", "site_id", "thetestzip_name"]

    def __init__(self):
        self.broker_host = "10.9.1.6"
        self.broker_port = 1883
        self.device_id = "pebkac_device"
        self.site_id = "0"
        self.thetestzip_name = "sleepmock"

    def to_json(self):
        return {key: getattr(self, key, None) for key in self.__slots__}

    def update_from_json(self, json_str: str):
        for key, v in json.loads(json_str).items():
            if key in self.__slots__:
                setattr(self, key, v)

    def update_from_kwargs(self, **kwargs):
        for key, v in kwargs.items():
            if key in self.__slots__ and v is not None:
                setattr(self, key, v)

    def update_from_file(self, filename):
        with open(filename, 'r') as infile:
            self.update_from_json(infile.read())

    def update_from_parsed_argparse_args(self, args):  # args = argparse.ArgumentParser().parse_args()
        self.update_from_kwargs(**vars(args))

    @classmethod
    def add_argparse_arguments(cls, parser: argparse.ArgumentParser):
        for key in cls.__slots__:
            parser.add_argument('--' + key)


class TopicFactory:

    def __init__(self, device_id, site_id):
        self._device_id = device_id
        self._site_id = site_id

    def master_status_topic(self):
        return f'ate/{self._device_id}/Master/status'

    def master_resource_topic(self, resource_id: Optional[str] = None):
        if resource_id is None:
            resource_id = '+'
        return f'ate/{self._device_id}/Master/resource/{resource_id}'

    def control_status_topic(self):
        return f'ate/{self._device_id}/ControlApp/status/site{self._site_id}'

    def test_status_topic(self):
        return f'ate/{self._device_id}/TestApp/status/site{self._site_id}'

    def test_cmd_topic(self):
        return f'ate/{self._device_id}/TestApp/cmd'

    def test_result_topic(self):
        return f'ate/{self._device_id}/TestApp/testresult/site{self._site_id}'

    def test_stdf_topic(self):
        return f'ate/{self._device_id}/TestApp/stdf/site{self._site_id}'

    def test_resource_topic(self, resource_id: str):
        return f'ate/{self._device_id}/TestApp/resource/{resource_id}/site{self._site_id}'

    def test_status_payload(self, alive: TheTestAppStatusAlive):
        return {
            "type": "status",
            "framework_version": FRAMEWORK_VERSION,
            "test_version": "N/A",
            "payload": {}
        }

    def test_result_payload(self, ispass: bool, testdata: object):
        return {
            "type": "testresult",
            "pass": 1 if ispass else 0,
            "testdata": testdata  # any json serializable thing for now
        }

    def test_resource_payload(self, resource_id: str, config: dict) -> dict:
        return {
            "type": "resource-config-request",
            "resource_id": resource_id,
            "config": config
        }

    @property
    def site_id(self):
        return self._site_id

    @property
    def mqtt_client_id(self):
        return f'testapp.{self._device_id}.{self._site_id}'


class TheTestAppMachine:

    def __init__(self, mqtt):
        self._mqtt = mqtt

        states = ['starting', 'idle', 'testing', 'selftesting', 'terminated', 'error']

        transitions = [
            {'trigger': 'startup_done', 'source': 'starting', 'dest': 'idle', 'before': 'on_startup_done'},
            {'trigger': 'cmd_init', 'source': 'idle', 'dest': 'selftesting', 'before': 'on_cmd_init'},
            {'trigger': 'cmd_next', 'source': 'idle', 'dest': 'testing', 'before': 'on_cmd_next'},
            {'trigger': 'cmd_terminate', 'source': 'idle', 'dest': 'terminated', 'before': 'on_cmd_terminate'},
            {'trigger': 'cmd_done', 'source': ['testing', 'selftesting'], 'dest': 'idle', 'before': 'on_cmd_done'},
            {'trigger': 'fail', 'source': '*', 'dest': 'error', 'before': 'on_fail'},
        ]

        self.machine = Machine(model=self, states=states, transitions=transitions, initial='starting', after_state_change=self.after_state_change)

    def after_state_change(self, whatever=None):
        logger.debug('publish_current_state: %s', self.state)

        if self.is_error() or self.is_terminated():
            dodisconnect = True
            alive = TheTestAppStatusAlive.DEAD
        else:
            dodisconnect = False
            alive = TheTestAppStatusAlive.ALIVE

        msginfo = self._mqtt.publish_status(alive, {'state': self.state})
        msginfo.wait_for_publish()

        # workaround: handle state after publishing status (which is done
        # in after_state_change, so we cannot put this logic into
        # before/after_transition or on_state handler)
        if dodisconnect:
            self._mqtt.disconnect()

    def on_startup_done(self):
        logger.debug('on_startup_done')

    def on_cmd_init(self):
        logger.debug('on_cmd_init')

    def on_cmd_next(self):
        logger.debug('on_cmd_next')

    def on_cmd_terminate(self):
        logger.debug('on_cmd_terminate')

    def on_cmd_done(self):
        logger.debug('on_cmd_done')

    def on_fail(self, info):
        logger.error('on_fail: %s', info)


class TheTestAppMqttClient:
    _client: mqtt.Client
    _topic_factory: TopicFactory
    _resource_msg_queue: queue.Queue

    def __init__(self, broker_host, broker_port, topic_factory: TopicFactory, submit_callback):
        self._topic_factory = topic_factory
        self._client = self._create_mqtt_client(topic_factory)
        self._client.connect_async(broker_host, int(broker_port), 60)
        self.submit_callback = submit_callback

        # mqtt callbacks, excecuted in executor
        self.on_connect = None        # on_connect()        (only called when succcesfully (re-)connected)
        self.on_disconnect = None     # on_disconnect()     (only called after successful disconnect())
        self.on_message = None        # on_message(message: mqtt.MQTTMessageInfo)
        self.on_command = None        # on_command(cmd:string, payload: dict)

        # queue to process resource messages anywhere (without callbacks)
        self._resource_msg_queue = queue.Queue()

    def loop_forever(self):
        self._client.loop_forever()

    def disconnect(self):
        # note: disconnecting with will message (reasoncode=4) is MQTT5 only
        # in MQTT311 disconnect always tells the broker to discard the will message
        self._client.disconnect()

    def publish_status(self, alive: TheTestAppStatusAlive, statedict) -> mqtt.MQTTMessageInfo:
        payload = self._topic_factory.test_status_payload(alive)
        if statedict is not None:
            payload["payload"].update(statedict)
        return self._client.publish(
            topic=self._topic_factory.test_status_topic(),
            payload=json.dumps(payload),
            qos=2,
            retain=False)

    def publish_result(self, ispass: bool, testdata: object) -> mqtt.MQTTMessageInfo:
        return self._client.publish(
            topic=self._topic_factory.test_result_topic(),
            payload=json.dumps(
                self._topic_factory.test_result_payload(ispass, testdata)),
            qos=2,
            retain=False)

    def publish_stdf_part(self, blob: bytes) -> mqtt.MQTTMessageInfo:
        return self._client.publish(
            topic=self._topic_factory.test_stdf_topic(),
            payload=blob,
            qos=2,
            retain=False)

    def publish_resource_request(self, resource_id: str, config: dict) -> mqtt.MQTTMessageInfo:
        return self._client.publish(
            topic=self._topic_factory.test_resource_topic(resource_id),
            payload=json.dumps(self._topic_factory.test_resource_payload(resource_id, config)),
            qos=2,
            retain=False),

    def _create_mqtt_client(self, topic_factory: TopicFactory) -> mqtt.Client:
        mqttc = mqtt.Client(client_id=topic_factory.mqtt_client_id)

        mqttc.on_connect = self._on_connect_callback
        mqttc.on_disconnect = self._on_disconnect_callback
        mqttc.on_message = self._on_message_callback

        mqttc.message_callback_add(self._topic_factory.test_cmd_topic(),
                                   self._on_message_cmd_callback)
        mqttc.message_callback_add(self._topic_factory.master_resource_topic(),
                                   self._on_message_resource_callback)

        payload = self._topic_factory.test_status_payload(TheTestAppStatusAlive.DEAD)
        payload.update({'state': 'crash'})
        mqttc.will_set(
            topic=topic_factory.test_status_topic(),
            payload=json.dumps(payload),
            qos=2,
            retain=False)

        return mqttc

    def _on_connect_callback(self, client, userdata, flags, rc):
        if rc != 0:
            logger.error(f"mqtt connect error: {rc}")
            return

        logger.info("mqtt connected")

        self._client.subscribe([
            (self._topic_factory.test_cmd_topic(), 2),
            # subscribe to all resources of master, since we currently
            # don't know in advance which resources a loaded test is
            # interested in
            (self._topic_factory.master_resource_topic(resource_id=None), 2)
        ])

        self.submit_callback(self.on_connect)

    def _on_disconnect_callback(self, client, userdata, rc):
        if rc != 0:
            logger.error(f"mqtt unexpected disconnect: {rc}")
            return

        logger.info("mqtt disconnected")

        self.submit_callback(self.on_disconnect)

    def _on_message_callback(self, client, userdata, message: mqtt.MQTTMessage):
        logger.info(f'mqtt message for topic {message.topic}')

        self.submit_callback(self.on_message, message)

    def _on_message_cmd_callback(self, client, userdata, message: mqtt.MQTTMessage):
        logger.info(f'mqtt message for topic {message.topic}')

        # there is no exception handling here, because any exceptions
        # in paho main loop should be handled there
        data = json.loads(message.payload.decode('utf-8'))
        assert data['type'] == 'cmd'
        cmd = data['command']
        sites = data['sites']

        if self._topic_factory.site_id not in sites:
            logger.warning(f'ignoring TestApp cmd for other sites {sites} (current site_id is {self._topic_factory.site_id})')
            return

        self.submit_callback(self.on_command, cmd, data)

    def _on_message_resource_callback(self, client, userdata, message: mqtt.MQTTMessage):
        logger.info(f'mqtt message for topic {message.topic}')

        resource_id = message.topic.rpartition('/')[2]
        if not resource_id:
            logger.warning(f'ignoring unexpected Master resource message without resource_id')
            return

        # {
        #   "type": "resource-config",
        #   "resource_id": "myresourceid",
        #   "config": {}
        # }
        data = json.loads(message.payload.decode('utf-8'))
        assert data['type'] == 'resource-config'
        assert data['resource_id'] == resource_id
        assert isinstance(data['config'], dict)
        self._resource_msg_queue.put(data)

    def wait_for_resource_with_config(self, resource_id: str, config: dict, timeout=None):
        end_time = time.time() + timeout if timeout is not None else None
        adjusted_timeout = timeout
        try:
            while True:
                data = self._resource_msg_queue.get(block=True, timeout=adjusted_timeout)
                # TODO: we probably want a way to indicate an error, such as a resource does not even exist (which we should check earlier, but there should be a way to avoid waiting for the timeout)
                if data['resource_id'] == resource_id and data['config'] == config:
                    return data
                if end_time is not None:
                    # only timeout=None means "wait forever", <= 0 will not block
                    adjusted_timeout = end_time - time.time()
        except queue.Empty:
            raise TimeoutError(f'timeout while waiting for resource "{resource_id}" with config: {config}')


class TheTestZip_Callbacks(thetestzip_mock.TheTestZip_CallbackInterface):
    def __init__(self, mqtt: TheTestAppMqttClient):
        self._mqtt = mqtt
        super().__init__()

    def publish_stdf_part(self, stdf_blob: bytes):
        self._mqtt.publish_stdf_part(stdf_blob)

    def request_resource_config(self, resource_id: str, config: dict):
        logger.info('requesting resource "%s" with config: %s', resource_id, config)
        self._mqtt.publish_resource_request(resource_id, config)
        _ = self._mqtt.wait_for_resource_with_config(resource_id, config, timeout=RESOURCE_CONFIG_REQUEST_TIMEOUT)  # TODO: what timeout should we use? how to handle timeout at all? should it abort the whole dut test or just the individual test that uses the resource? probably the former because the environment is not in a sane state?
        return "additionalinfofromresourceorwhatever"


class TheTestAppApplication:
    _statemachine: Optional[TheTestAppMachine]
    _mqtt: Optional[TheTestAppMqttClient]
    _thetestzip_instance: Optional[thetestzip_mock.TheTestZip_InstanceInterface]

    def __init__(self, params: TheTestAppParameters = None):
        self.params = params if params is not None else TheTestAppParameters()
        self._statemachine = None
        self._mqtt = None
        self._disconnected = False
        self._thetestzip_instance = None

    @staticmethod
    def init_from_command_line(argv):
        parser = argparse.ArgumentParser(prog=argv[0], formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        TheTestAppParameters.add_argparse_arguments(parser)
        parser.add_argument('config_file', metavar='config-file', nargs='?')
        parser.add_argument("-v", "--verbose",
                            help="increase output verbosity",
                            action="store_true")
        parser.add_argument('--parent-pid')
        parser.add_argument('--ptvsd-host', nargs='?', default='0.0.0.0', type=str,
                            help="remote debugger list ip address")
        parser.add_argument('--ptvsd-port', nargs='?', default=5678, type=int,
                            help="remote debugger list port")
        parser.add_argument('--ptvsd-enable-attach', action="store_true",
                            help="enable remote debugger attach")
        parser.add_argument('--ptvsd-wait-for-attach', action="store_true",
                            help="wait for remote debugger attach before start (implies --ptvsd-enable-attach)")
        args = parser.parse_args(argv[1:])

        if args.verbose:
            logger.addHandler(logging.StreamHandler())
            logger.setLevel(logging.DEBUG)

        if args.ptvsd_enable_attach or args.ptvsd_wait_for_attach:
            import ptvsd
            ptvsd.enable_attach(address=(args.ptvsd_host, args.ptvsd_port))
            if args.ptvsd_wait_for_attach:
                ptvsd.wait_for_attach()

        # kill this process when the parent dies
        # this is mostly a temporary solution to get rid of
        # zombie processes when the control app dies
        if args.parent_pid is not None:
            if sys.platform == 'win32':
                logger.warning('PARENT PROCESS WATCHDOG enabled for pid %s', args.parent_pid)
                start_parent_process_death_watchdog_win32(int(args.parent_pid))
            else:
                logger.warning('PARENT PROCESS WATCHDOG should be enabled for pid %s, but this is not yet implemented for non-win32 hosts (currently unclear if required or not)', args.parent_pid)

        params = TheTestAppParameters()
        # note: values specified on command line always override values loaded
        #       from config file, no matter where the config_file option is
        if args.config_file is not None:
            params.update_from_file(args.config_file)

        params.update_from_parsed_argparse_args(args)

        return params

    @classmethod
    def run_from_command_line(cls, argv):
        params = cls.init_from_command_line(argv)
        testApp = TheTestAppApplication(params)
        testApp.run()

    def run(self):
        topic_factory = TopicFactory(self.params.device_id,
                                     self.params.site_id)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

        def submit_callback(cb, *args, **kwargs):
            # ignore unbound callbacks
            if cb is None:
                return

            # handle exceptions in all callbacks
            def wrapped_callback():
                try:
                    cb(*args, **kwargs)
                except Exception as e:
                    if self._statemachine is not None:
                        logger.exception('exception in mqtt callback')
                        self._statemachine.fail(str(e))
                    else:
                        raise

            # this is called in any thread, not necessarily in the executor
            def handle_uncaught_exceptions_from_executor(f):
                try:
                    f.result()
                except Exception:
                    logger.exception("executor exception")
                    # TODO: we probably don't want to keep running if any
                    #       exception escapesed. using os._exit may not be
                    #       the best way to do this (because no cleanup/io
                    #       flushing at all)
                    os._exit(1)

            f = executor.submit(wrapped_callback)
            f.add_done_callback(handle_uncaught_exceptions_from_executor)

        mqtt = TheTestAppMqttClient(self.params.broker_host,
                                    self.params.broker_port,
                                    topic_factory,
                                    submit_callback)
        mqtt.on_connect = self._on_connect
        mqtt.on_disconnect = self._on_disconnect
        mqtt.on_command = self._on_command

        self._mqtt = mqtt
        self._statemachine = TheTestAppMachine(mqtt)

        try:
            self._mqtt.loop_forever()
        except KeyboardInterrupt:
            pass
        executor.shutdown(wait=True)

    def _on_connect(self):
        # transition to idle state on first connect
        # TODO: subsequent connects are currently not really handled here and
        #       and unexpected disconnects should probably be an error (?)
        if self._statemachine.is_starting():
            self._thetestzip_init()
            self._statemachine.startup_done()
        else:
            # TODO: else is here to avoid publishing the initial idle state
            #       twice (which howver should not be a problem eventually
            #       after fixing problems in subsribers)
            self._mqtt.publish_status(TheTestAppStatusAlive.ALIVE, {'payload': {'state': self._statemachine.state, 'message': ''}})

    def _on_disconnect(self):
        self._disconnected = True

    def _on_command(self, cmd, payload):
        self._execute_command(cmd, payload)

    def _execute_command(self, cmd: str, payload: dict):
        if cmd == 'init':
            self._statemachine.cmd_init()
            self._execute_cmd_init(payload.get('mock_result', True),
                                   payload.get('mock_duration_secs', 1.5))
            self._statemachine.cmd_done()
        elif cmd == 'next':
            self._statemachine.cmd_next()
            self._execute_cmd_next(payload.get('mock_result', True),
                                   payload.get('mock_duration_secs', 2.5),
                                   payload.get('job_data'))
            self._statemachine.cmd_done()
        elif cmd == 'terminate':
            self._thetestzip_teardown()
            self._statemachine.cmd_terminate()
            self._execute_cmd_terminate()
        else:
            raise Exception(f'invalid command: "{cmd}"')

    def _execute_cmd_init(self, mock_result: bool, mock_duration_secs: int):
        logger.debug('COMMAND: init')

        logger.info('running self test...')
        time.sleep(mock_duration_secs)
        selftest_result = mock_result
        logger.info(f'self test completed: {selftest_result}')

        # TODO: how to report positive init command results? we could also write the testresult
        # self.publish_result(selftest_result, "<insert init result data here>")
        # note that currently once "init" failed the status will not be restored to ALIVE
        if not selftest_result:
            self._mqtt.publish_status(TheTestAppStatusAlive.INITFAIL, {'payload': {'state': self._statemachine.state, 'message': ''}})

    def _execute_cmd_next(self, mock_result: bool, mock_duration_secs: int, job_data: Optional[dict]):
        logger.debug('COMMAND: next')

        # TODO: remove this block later. for now er TEMPORAILRY create job_data (for backward compatibility until master has it implemented)
        if job_data is None:
            job_data = {}
        job_data.setdefault('mock_result', mock_result)
        job_data.setdefault('mock_duration_secs', mock_duration_secs)

        job_data['testzipmock.current_site_id'] = self.params.site_id
        job_data.setdefault('testzipmock.custom_sequence', [{'result_ispass': True}, {'result_ispass': False}, {'result_ispass': True}])

        test_result, testdata = self._thetestzip_instance.execute_dut_tests(job_data)

        self._mqtt.publish_result(test_result, testdata)

    def _execute_cmd_terminate(self):
        logger.debug('COMMAND: terminate')

        # TODO: code commented: this is currently done in state matching
        # logger.info('publishing shutdown status...')
        # msginfo = self._mqtt.publish_status(TheTestAppStatusAlive.SHUTDOWN)
        # msginfo.wait_for_publish()
        # logger.info('shutdown status published!')
        # logger.info('disconnecting and shutting down...')
        # self._mqtt.disconnect()  # loop_forever() will return after this call

    def _thetestzip_init(self):
        if self._thetestzip_instance is not None:
            raise ValueError('_thetestzip_instance already initialized')

        # TODO: use job related info here (e.g. from Master/job topic or passed in some other way with the loadTest command)
        thetestzip_name = self.params.thetestzip_name
        logger.info('initializing thetestzip %s', thetestzip_name)

        self._thetestzip_instance = thetestzip_mock.create_thetestzipmock_instance(thetestzip_name, TheTestZip_Callbacks(self._mqtt))
        self._thetestzip_instance.setup()

    def _thetestzip_teardown(self):
        if self._thetestzip_instance is None:
            raise ValueError('_thetestzip_instance not initialized')

        logger.info('unloading thetestzip')

        self._thetestzip_instance.teardown()
        self._thetestzip_instance = None


def main():
    return TheTestAppApplication.run_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
