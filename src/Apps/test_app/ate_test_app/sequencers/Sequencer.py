import concurrent.futures

import logging
import os
import sys
import threading

from typing import Dict, List, Optional, Tuple

from ate_common.logger import LogLevel, Logger
from ate_test_app.sequencers.SequencerBase import SequencerBase
from ate_test_app.sequencers import Harness
from ate_test_app.sequencers.CommandLineParser import CommandLineParser
from ate_test_app.sequencers.ExecutionPolicy import get_execution_policy, ExecutionType
from ate_test_app.sequencers.TheTestAppMachine import TheTestAppMachine
from ate_test_app.sequencers.TheTestAppStatusAlive import TheTestAppStatusAlive
from ate_test_app.stages_sequence_generator.stages_sequence_generator import StagesSequenceGenerator
from ate_test_app.sequencers.mqtt.MqttConnection import MqttConnection

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


class Sequencer:
    _statemachine: Optional[TheTestAppMachine]

    def __init__(
            self,
            sequencer: SequencerBase,
            params: dict,
            execution_strategy: StagesSequenceGenerator,
            mqtt_connection: MqttConnection,
            harness: Harness):
        self._statemachine = None
        self._disconnected = False
        self._sequencer_instance = sequencer

        self._sequencer_instance.set_harness(harness)

        self._sequencer_instance.set_site_id(params.site_id)
        self.params = params if params is not None else CommandLineParser()
        self._execution_strategy = execution_strategy

        self._harness = harness

        self._execution_policy = get_execution_policy(ExecutionType.SingleShot())
        self.logger = None
        self.after_terminate_callback = None

        self._mqtt_connection = mqtt_connection
        self._mqtt = self._mqtt_connection.get_mqtt_client()
        self._statemachine = TheTestAppMachine(self._mqtt)

        self._mqtt_connection.set_callbacks(self._on_connect, self._on_disconnect, self._execute_command, self.submit_callback)

    def set_logger(self, logger: Logger):
        self.logger = logger
        self._mqtt_connection.set_logger(logger)

    def submit_callback(self, cb, *args, **kwargs):
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)
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

    def run(self):
        try:
            self._mqtt.loop_forever()
        except KeyboardInterrupt:
            pass
        self.executor.shutdown(wait=True)

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

    def _execute_command(self, cmd: str, payload: dict):
        if cmd == 'init':
            self._statemachine.cmd_init()
            self._execute_cmd_init()
            self._statemachine.cmd_done()
        elif cmd == 'next':
            self._statemachine.cmd_next()
            self._execute_cmd_next(payload.get('job_data'))
        elif cmd == 'terminate':
            self._execute_cmd_terminate()
            self._statemachine.cmd_terminate()
        elif cmd == 'reset':
            self._statemachine.cmd_terminate()
        elif cmd == 'setloglevel':
            self._execute_cmd_setloglevel(payload['level'])
        elif cmd == 'getexecutionstrategy':
            self._execute_cmd_get_execution_strategy(payload['layout'])
        elif cmd == 'sethbin':
            self._execute_cmd_set_hbin(payload['sbin'], payload['hbin'])
        elif cmd == 'setparameter':
            self._execute_cmd_set_parameter(payload['parameters'])
        else:
            raise Exception(f'invalid command: "{cmd}"')

    def _execute_cmd_set_parameter(self, payload: list):
        self._sequencer_instance.set_input_parameter(payload)

    def _execute_cmd_set_hbin(self, sbin: str, hbin: str):
        self._sequencer_instance.set_new_hbin_for_sbin(sbin, hbin)

    def _execute_cmd_init(self):
        self.logger.log_message(LogLevel.Debug(), 'COMMAND: init')
        # ToDo: How should we perform the selftest?
        self.logger.log_message(LogLevel.Info(), 'running self test...')
        selftest_result = self._sequencer_instance.init()
        self.logger.log_message(LogLevel.Info(), f'self test completed: {selftest_result}')

        # TODO: how to report positive init command results? we could also write the testresult
        # self.publish_result(selftest_result, "<insert init result data here>")
        # note that currently once "init" failed the status will not be restored to ALIVE
        if not selftest_result:
            self._mqtt.publish_status(TheTestAppStatusAlive.INITFAIL, {'state': self._statemachine.state, 'payload': {'state': self._statemachine.state, 'message': 'selftest is failed'}})

    def _execute_cmd_next(self, job_data: Optional[dict]):
        self.logger.log_message(LogLevel.Debug(), 'COMMAND: next')

        self._harness.next()

        result = self._sequencer_instance.run(self._execution_policy, job_data)
        self._statemachine.cmd_done()

        self._harness.send_testresult(result)

    def _execute_cmd_setloglevel(self, level: LogLevel):
        self._sequencer_instance.set_logger_level(level)

    def _execute_cmd_get_execution_strategy(self, layout: Dict[str, Tuple[int, int]]):
        self._mqtt.publish_execution_strategy(self._execution_strategy.get_execution_strategy(layout))

    def send_log(self, log: object):
        self._mqtt.publish_log_information(log)

    def send_execution_strategy(self, execution_strategy: List[List[str]]):
        self._mqtt.publish_execution_strategy(execution_strategy)

    def _execute_cmd_terminate(self):
        self.logger.log_message(LogLevel.Debug(), "COMMAND: terminate")
        result = self._sequencer_instance.aggregate_tests_summary()

        self._harness.send_summary(result)

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

    def publish(self, topic: str, payload: object = None, qos: int = 2, retain: bool = False):
        self.mqtt_client.publish(topic, payload, qos, retain)


def main():
    return Sequencer.run_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
