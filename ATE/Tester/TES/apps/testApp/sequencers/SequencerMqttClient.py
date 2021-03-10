from ATE.Tester.TES.apps.testApp.sequencers.SequencerBase import SequencerBase
from ATE.common.logger import LogLevel, Logger
import concurrent.futures

import logging
import os
import sys
import threading

from typing import Optional

from ATE.Tester.TES.apps.testApp.sequencers import Harness
from ATE.Tester.TES.apps.testApp.sequencers.CommandLineParser import CommandLineParser
from ATE.Tester.TES.apps.testApp.sequencers.ExecutionPolicy import SingleShotExecutionPolicy
from ATE.Tester.TES.apps.testApp.sequencers.MqttClient import MqttClient
from ATE.Tester.TES.apps.testApp.sequencers.TheTestAppMachine import TheTestAppMachine
from ATE.Tester.TES.apps.testApp.sequencers.TopicFactory import TopicFactory
from ATE.Tester.TES.apps.testApp.sequencers.TheTestAppStatusAlive import TheTestAppStatusAlive

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
        self.after_terminate_callback = None

    def set_logger(self, logger: Logger):
        self.logger = logger

    def apply_parameters(self, test_app_params: list):
        self.params = test_app_params if test_app_params is not None else CommandLineParser()

    @classmethod
    def run_from_command_line(cls, params: list):
        from ATE.Tester.TES.apps.testApp.sequencers.SequencerBase import SequencerBase
        the_sequencer = SequencerBase(None)
        testApp = SequencerMqttClient(params, the_sequencer)
        testApp.run()

    def run_from_command_line_with_sequencer(self):
        self.run()

    def init_mqtt_client(self, params: list, sequencer: SequencerBase):
        self._sequencer_instance = sequencer
        self._sequencer_instance.set_site_id(params.site_id)
        self.apply_parameters(params)
        self._init_app_components()

    def _init_app_components(self):
        topic_factory = TopicFactory(self.params.device_id,
                                     self.params.site_id)
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

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
                        self.logger.log_message(LogLevel.Error(), e)
                        self.logger.log_message(LogLevel.Error(), 'exception in mqtt callback')
                        self._statemachine.fail(str(e))
                    else:
                        raise

            # this is called in any thread, not necessarily in the executor
            def handle_uncaught_exceptions_from_executor(f):
                try:
                    f.result()
                except Exception:
                    self.logger.log_message(LogLevel.Error(), "executor exception")
                    # TODO: we probably don't want to keep running if any
                    #       exception escaped. using os._exit may not be
                    #       the best way to do this (because no cleanup/io
                    #       flushing at all)
                    os._exit(1)

            f = self.executor.submit(wrapped_callback)
            f.add_done_callback(handle_uncaught_exceptions_from_executor)

        self._mqtt = self._generate_mqtt_connection(topic_factory, submit_callback)
        self._statemachine = TheTestAppMachine(self._mqtt)

    def run(self):
        try:
            self._mqtt.loop_forever()
        except KeyboardInterrupt:
            pass
        self.executor.shutdown(wait=True)

    def _generate_mqtt_connection(self, topic_factory: TopicFactory, submit_callback: callable):
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

    def _on_disconnect(self):
        self._disconnected = True

    def _on_command(self, cmd: str, payload: dict):
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
        else:
            raise Exception(f'invalid command: "{cmd}"')

    def _execute_cmd_init(self):
        self.logger.log_message(LogLevel.Debug(), 'COMMAND: init')
        # ToDo: How should we perform the selftest?
        self.logger.log_message(LogLevel.Info(), 'running self test...')
        selftest_result = self._sequencer_instance.init()
        self.logger.log_message(LogLevel.Info(), f'self test completed: {selftest_result}')

        self.send_status("IDLE")

        # TODO: how to report positive init command results? we could also write the testresult
        # self.publish_result(selftest_result, "<insert init result data here>")
        # note that currently once "init" failed the status will not be restored to ALIVE
        if not selftest_result:
            self._mqtt.publish_status(TheTestAppStatusAlive.INITFAIL, {'state': self._statemachine.state, 'payload': {'state': self._statemachine.state, 'message': 'selftest is failed'}})

    def _execute_cmd_next(self, job_data: Optional[dict]):
        self.logger.log_message(LogLevel.Debug(), 'COMMAND: next')

        self.send_status("TESTING")
        result = self._sequencer_instance.run(self._execution_policy, job_data)
        self.send_status("IDLE")

        self.send_testresult(result)

    def _execute_cmd_setloglevel(self, level: LogLevel):
        self._sequencer_instance.set_logger_level(level)

    def send_testresult(self, stdfdata: object):
        self._mqtt.publish_result(stdfdata)

    def send_summary(self, summary: object):
        self._mqtt.publish_tests_summary(summary)

    def send_log(self, log: object):
        self._mqtt.publish_log_information(log)

    def send_status(self, status):
        # ToDo: This is done automatically by the statemachine here,
        # so we probably don't need the function anymore
        pass

    def _execute_cmd_terminate(self):
        self.logger.log_message(LogLevel.Debug(), "COMMAND: terminate")
        result = self._sequencer_instance.aggregate_tests_summary()
        self.send_summary(result)
        self.after_terminate_callback()

    def set_after_terminate_callback(self, callback: callable):
        self.after_terminate_callback = callback

    # Hack: Since we can only distribute the SequencerMqttClient to actuators, but they
    # need access to some sort of mqtt we reimplement this method as pass through here.
    def publish_with_reply(self, actuator_type: str, payload: object, response_timeout: int):
        request_topic = "ate/" + self.params.device_id + f"/TestApp/io-control/site{self.params.site_id}/request"
        response_topic = "ate/" + self.params.device_id + f"/Master/{actuator_type}/response"
        return self._mqtt.do_request_response(request_topic, response_topic, payload, response_timeout)

    def do_request_response(self, request_topic: str, response_topic: str, payload: object, timeout: int):
        return self._mqtt.do_request_response(request_topic, response_topic, payload, timeout)

    def register_route(self, route: str, callback: callable):
        self.router.register_route(route, callback)

    def subscribe_and_register(self, route: str, callback: callable):
        self.subscribe(route)
        self._router.register(route, callback)

    def unsubscribe(self, topic: str):
        self._mqtt.unsubscribe(topic)

    def unregister_route(self, route: str, callback: callable):
        self._router.unregister_route(route, callback)

    def subscribe(self, topic: str):
        self.mqtt_client.subscribe(topic)

    def publish(self, topic: str, payload: object = None, qos: int = 0, retain: bool = False):
        self.mqtt_client.publish(topic, payload, qos, retain)


def main():
    return SequencerMqttClient.run_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
