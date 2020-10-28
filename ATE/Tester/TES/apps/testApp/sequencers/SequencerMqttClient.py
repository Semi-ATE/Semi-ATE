import concurrent.futures
import json
import logging
import os
import queue
import sys
import threading
from enum import Enum
from typing import Optional

import paho.mqtt.client as mqtt
from transitions import Machine

from ATE.Tester.TES.apps.testApp.sequencers import Harness
from ATE.Tester.TES.apps.testApp.sequencers.CommandLineParser import CommandLineParser
from ATE.Tester.TES.apps.testApp.sequencers.ExecutionPolicy import SingleShotExecutionPolicy

from ATE.utils.mqtt_router import MqttRouter

FRAMEWORK_VERSION = 1

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


class TopicFactory:

    def __init__(self, device_id, site_id):
        self._device_id = device_id
        self._site_id = site_id

    def master_status_topic(self):
        return f'ate/{self._device_id}/Master/status'

    def master_resource_topic(self, resource_id: Optional[str] = None):
        if resource_id is None:
            resource_id = '+'
        return f'ate/{self._device_id}/Master/peripherystate/{resource_id}'

    def generic_resource_response(self):
        # Evil hack: We want to see the responsetopics of all actuators here.
        return f'ate/{self._device_id}/+/response'

    def control_status_topic(self):
        return f'ate/{self._device_id}/ControlApp/status/site{self._site_id}'

    def test_status_topic(self):
        return f'ate/{self._device_id}/TestApp/status/site{self._site_id}'

    def test_cmd_topic(self):
        return f'ate/{self._device_id}/TestApp/cmd'

    def test_result_topic(self):
        return f'ate/{self._device_id}/TestApp/testresult/site{self._site_id}'

    def tests_summary_topic(self):
        return f'ate/{self._device_id}/TestApp/testsummary/site{self._site_id}'

    def test_stdf_topic(self):
        return f'ate/{self._device_id}/TestApp/stdf/site{self._site_id}'

    def test_resource_topic(self, resource_id: str):
        return f'ate/{self._device_id}/TestApp/peripherystate/{resource_id}/site{self._site_id}/request'

    def test_log_topic(self):
        return f'ate/{self._device_id}/TestApp/log/site{self._site_id}'

    def test_bin_settings(self):
        return f'ate/{self._device_id}/TestApp/binsettings/site{self._site_id}'

    def test_status_payload(self, alive: TheTestAppStatusAlive):
        return {
            "type": "status",
            "alive": alive.value,
            "framework_version": FRAMEWORK_VERSION,
            "test_version": "N/A"
        }

    @staticmethod
    def test_result_payload(testdata: object):
        return {
            "type": "testresult",
            "payload": testdata
        }

    @staticmethod
    def test_resource_payload(resource_id: str, config: dict) -> dict:
        return {
            "type": "resource-config-request",
            "resource_id": resource_id,
            "config": config
        }

    @staticmethod
    def test_log_payload(testdata: str):
        return {
            "type": "log",
            "payload": testdata
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

        msginfo = self._mqtt.publish_status(alive, {'state': self.state, 'payload': {'state': self.state, 'message': ''}})
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


class MqttClient():
    _client: mqtt.Client
    _topic_factory: TopicFactory
    _resource_msg_queue: queue.Queue

    def __init__(self, broker_host, broker_port, topic_factory: TopicFactory, submit_callback):
        self._topic_factory = topic_factory
        self._client = self._create_mqtt_client(topic_factory)
        self._client.connect_async(broker_host, int(broker_port), 60)
        self._submit_callback = submit_callback
        self._router = MqttRouter()

        # mqtt callbacks, excecuted in executor
        self.on_connect = None        # on_connect()        (only called when succcesfully (re-)connected)
        self.on_disconnect = None     # on_disconnect()     (only called after successful disconnect())
        self.on_message = None        # on_message(message: mqtt.MQTTMessageInfo)
        self.on_command = None        # on_command(cmd:string, payload: dict)

        # queue to process resource messages anywhere (without callbacks)
        self._resource_msg_queue = queue.Queue()
        self.event = threading.Event()

    def loop_forever(self):
        self._client.loop_forever()

    def disconnect(self):
        # note: disconnecting with will message (reasoncode=4) is MQTT5 only
        # in MQTT311 disconnect always tells the broker to discard the will message
        self._client.disconnect()

    def publish_status(self, alive: TheTestAppStatusAlive, statedict) -> mqtt.MQTTMessageInfo:
        payload = self._topic_factory.test_status_payload(alive)
        payload.update(statedict)
        return self._client.publish(
            topic=self._topic_factory.test_status_topic(),
            payload=json.dumps(payload),
            qos=2,
            retain=False)

    def publish_result(self, testdata: object) -> mqtt.MQTTMessageInfo:
        _topic = self._topic_factory.test_result_topic()
        _payload = json.dumps(self._topic_factory.test_result_payload(testdata))
        return self._client.publish(
            topic=_topic,
            payload=_payload,
            qos=2,
            retain=False)

    def publish_tests_summary(self, tests_summary: object) -> mqtt.MQTTMessageInfo:
        _topic = self._topic_factory.tests_summary_topic()
        _payload = json.dumps(self._topic_factory.test_result_payload(tests_summary))
        return self._client.publish(
            topic=_topic,
            payload=_payload,
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

    def publish_log_information(self, log: str) -> mqtt.MQTTMessageInfo:
        return self._client.publish(
            topic=self._topic_factory.test_log_topic(),
            payload=json.dumps(self._topic_factory.test_log_payload(log)),
            qos=2,
            retain=False),

    def publish_bin_settings(self, bin_settings) -> mqtt.MQTTMessageInfo:
        return self._client.publish(
            topic=self._topic_factory.test_bin_settings(),
            payload=json.dumps(bin_settings),
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
        mqttc.message_callback_add(self._topic_factory.generic_resource_response(), self._on_message_resource_callback)

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
            (self._topic_factory.master_resource_topic(resource_id=None), 2),
            (self._topic_factory.generic_resource_response(), 2)
        ])

        self._submit_callback(self.on_connect)

    def _on_disconnect_callback(self, client, userdata, rc):
        if rc != 0:
            logger.error(f"mqtt unexpected disconnect: {rc}")
            return

        logger.info("mqtt disconnected")

        self._submit_callback(self.on_disconnect)

    def _on_message_callback(self, client, userdata, message: mqtt.MQTTMessage):
        logger.info(f'mqtt message for topic {message.topic}')

        self._submit_callback(self.on_message, message)

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

        self._submit_callback(self.on_command, cmd, data)

    def _on_message_resource_callback(self, client, userdata, message: mqtt.MQTTMessage):
        data = json.loads(message.payload.decode('utf-8'))
        self.response_data = data
        self.response_topic = message.topic
        self.event.set()

    def do_request_response(self, request_topic, response_topic, payload, timeout):
        self.event.clear()
        self._client.publish(request_topic, payload, 2)

        while (self.event.wait(timeout)):
            if self.response_topic == response_topic:
                return False, self.response_data

        return True, None


class SequencerMqttClient(Harness.Harness):
    _statemachine: Optional[TheTestAppMachine]
    _mqtt: Optional[MqttClient]

    def __init__(self):
        self._statemachine = None
        self._mqtt = None
        self._disconnected = False
        self._sequencer_instance = None
        # TODO: execution policy should not be hard coded
        self._execution_policy = SingleShotExecutionPolicy()
        self.logger = None
        self._bin_settings = None

    def set_logger(self, logger):
        self.logger = logger

    def apply_parameters(self, test_app_params):
        self.params = test_app_params if test_app_params is not None else CommandLineParser()

    @classmethod
    def run_from_command_line(cls, params):
        from ATE.Tester.sequencers.SequencerBase import SequencerBase
        the_sequencer = SequencerBase(None)
        testApp = SequencerMqttClient(params, the_sequencer)
        testApp.run()

    def run_from_command_line_with_sequencer(self, bin_setting):
        self._bin_settings = bin_setting
        self.run()

    def init_mqtt_client(self, params, sequencer):
        self._sequencer_instance = sequencer
        self._sequencer_instance.set_site_id(params.site_id)
        self.apply_parameters(params)

    def run(self):
        topic_factory = TopicFactory(self.params.device_id,
                                     self.params.site_id)
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

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
                        self.logger.error(e)
                        self.logger.error('exception in mqtt callback')
                        self._statemachine.fail(str(e))
                    else:
                        raise

            # this is called in any thread, not necessarily in the executor
            def handle_uncaught_exceptions_from_executor(f):
                try:
                    f.result()
                except Exception:
                    self.logger.error("executor exception")
                    # TODO: we probably don't want to keep running if any
                    #       exception escaped. using os._exit may not be
                    #       the best way to do this (because no cleanup/io
                    #       flushing at all)
                    os._exit(1)

            f = executor.submit(wrapped_callback)
            f.add_done_callback(handle_uncaught_exceptions_from_executor)

        self._mqtt = self._generate_mqtt_connection(topic_factory, submit_callback)
        self._statemachine = TheTestAppMachine(self._mqtt)

        try:
            self._mqtt.loop_forever()
        except KeyboardInterrupt:
            pass
        executor.shutdown(wait=True)

    def _generate_mqtt_connection(self, topic_factory, submit_callback):
        mqtt = MqttClient(self.params.broker_host,
                          self.params.broker_port,
                          topic_factory,
                          submit_callback)
        mqtt.on_connect = self._on_connect
        mqtt.on_disconnect = self._on_disconnect
        mqtt.on_command = self._on_command

        return mqtt

    def _on_connect(self):
        # transition to idle state on first connect
        # TODO: subsequent connects are currently not really handled here and
        #       and unexpected disconnects should probably be an error (?)
        if self._statemachine.is_starting():
            self._statemachine.startup_done()
        else:
            # TODO: else is here to avoid publishing the initial idle state
            #       twice (which however should not be a problem eventually
            #       after fixing problems in subsribers)
            self._mqtt.publish_status(TheTestAppStatusAlive.ALIVE, {'state': self._statemachine.state, 'payload': {'state': self._statemachine.state, 'message': ''}})

    def _send_bin_settings(self):
        if not self._bin_settings:
            self.logger.error('bin settings are not set yet')
            raise Exception

        self._mqtt.publish_bin_settings(self._bin_settings)

    def _on_disconnect(self):
        self._disconnected = True

    def _on_command(self, cmd, payload):
        self._execute_command(cmd, payload)

    def _execute_command(self, cmd: str, payload: dict):
        if cmd == 'init':
            self._statemachine.cmd_init()
            self._execute_cmd_init()
            self._statemachine.cmd_done()
        elif cmd == 'next':
            self._statemachine.cmd_next()
            self._execute_cmd_next(payload.get('job_data'))
            self._statemachine.cmd_done()
        elif cmd == 'terminate':
            self._execute_cmd_terminate()
            self._statemachine.cmd_terminate()
        elif cmd == 'reset':
            self._statemachine.cmd_terminate()
        elif cmd == 'setloglevel':
            self._execute_cmd_setloglevel(payload['level'])
        elif cmd == 'setting':
            self._execute_cmd_setting(payload['name'])
        else:
            raise Exception(f'invalid command: "{cmd}"')

    def _execute_cmd_init(self):
        self.logger.debug('COMMAND: init')
        # ToDo: How should we perform the selftest?
        self.logger.info('running self test...')
        selftest_result = self._sequencer_instance.init()
        self.logger.info(f'self test completed: {selftest_result}')

        self.send_status("IDLE")

        # TODO: how to report positive init command results? we could also write the testresult
        # self.publish_result(selftest_result, "<insert init result data here>")
        # note that currently once "init" failed the status will not be restored to ALIVE
        if not selftest_result:
            self._mqtt.publish_status(TheTestAppStatusAlive.INITFAIL, {'state': self._statemachine.state, 'payload': {'state': self._statemachine.state, 'message': 'selftest is failed'}})

    def _execute_cmd_next(self, job_data: Optional[dict]):
        self.logger.debug('COMMAND: next')

        self.send_status("TESTING")
        result = self._sequencer_instance.run(self._execution_policy, job_data)
        self.send_status("IDLE")

        self.send_testresult(result)

    def _execute_cmd_setloglevel(self, level):
        self._sequencer_instance.set_logger_level(level)

    def _execute_cmd_setting(self, name):
        try:
            {
                'binsettings': lambda: self._send_bin_settings(),
            }[name]()
        except Exception:
            self.log.warning(f'setting {name} is not supported')

    def send_testresult(self, stdfdata):
        self._mqtt.publish_result(stdfdata)

    def send_summary(self, summary):
        self._mqtt.publish_tests_summary(summary)

    def send_log(self, log):
        self._mqtt.publish_log_information(log)

    def send_status(self, status):
        # ToDo: This is done automatically by the statemachine here,
        # so we probably don't need the function anymore
        pass

    def _execute_cmd_terminate(self):
        self.logger.debug('COMMAND: terminate')
        result = self._sequencer_instance.aggregate_tests_summary()
        self.send_summary(result)

    # Hack: Since we can only distribute the SequencerMqttClient to actuators, but they
    # need access to some sort of mqtt we reimplement this method as pass through here.
    def publish_with_reply(self, topic_base, payload, response_timeout):
        request_topic = "ate/" + self.params.device_id + f"/TestApp/{topic_base}/site{self.params.site_id}/request"
        response_topic = "ate/" + self.params.device_id + "/Master/" + topic_base + "/response"
        return self._mqtt.do_request_response(request_topic, response_topic, payload, response_timeout)

    def do_request_response(self, request_topic, response_topic, payload, timeout):
        return self._mqtt.do_request_response(request_topic, response_topic, payload, timeout)

    def register_route(self, route, callback):
        self.router.register_route(route, callback)

    def subscribe_and_register(self, route, callback):
        self.subscribe(route)
        self._router.register(route, callback)

    def unsubscribe(self, topic):
        self._mqtt.unsubscribe(topic)

    def unregister_route(self, route, callback):
        self._router.unregister_route(route, callback)

    def subscribe(self, topic):
        self.mqtt_client.subscribe(topic)

    def publish(self, topic, payload=None, qos=0, retain=False):
        self.mqtt_client.publish(topic, payload, qos, retain)


def main():
    return SequencerMqttClient.run_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
