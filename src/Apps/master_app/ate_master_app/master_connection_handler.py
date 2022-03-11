from ate_apps_common.mqtt_connection import MqttConnection
from ate_common.logger import LogLevel
import json
import re
from typing import List, Optional

TOPIC_CONTROLSTATUS = "Control/status"
TOPIC_CONTROLLOG = "Control/log"
SUBTOPIC_HANDLER = "Handler/status"

INTERFACE_VERSION = 1


class MasterConnectionHandler:

    """ handle commands """

    def __init__(self, host, port, sites, device_id, handler_id, status_consumer):
        mqtt_client_id = f'masterapp.{device_id}'
        self.status_consumer = status_consumer
        self.log = status_consumer.log
        self.mqtt = MqttConnection(host, port, mqtt_client_id, self.log)
        self.mqtt.init_mqtt_client_callbacks(self._on_connect_handler,
                                             self._on_disconnect_handler)
        self.sites = sites
        self.device_id = device_id
        self.connected_flag = False
        self.handler_id = handler_id

        self.mqtt.register_route("Control", lambda topic, payload: self.dispatch_control_message(topic, self.mqtt.decode_payload(payload)))
        self.mqtt.register_route("TestApp", lambda topic, payload: self.dispatch_testapp_message(topic, self.mqtt.decode_payload(payload)))
        self.mqtt.register_route("Master/cmd", lambda topic, payload: self.dispatch_handler_message(topic, self.mqtt.decode_payload(payload)))
        self.mqtt.register_route("Handler", lambda topic, payload: self.dispatch_handler_message(topic, self.mqtt.decode_payload(payload)))

    def start(self):
        self.mqtt.set_last_will(
            self._generate_base_topic_status(),
            self.mqtt.create_message(
                self._generate_status_message('crash')))
        self.mqtt.start_loop()

    async def stop(self):
        await self.mqtt.stop_loop()

    def publish_state(self, state, statedict=None):
        self.mqtt.publish(self._generate_base_topic_status(),
                          self.mqtt.create_message(self._generate_status_message(state, statedict)),
                          qos=2,
                          retain=False)

    def send_load_test_to_all_sites(self, testapp_params):
        topic = f'ate/{self.device_id}/Control/cmd'
        params = {
            'type': 'cmd',
            'command': 'loadTest',
            'testapp_params': testapp_params,
            'sites': self.sites,
        }
        self.log.log_message(LogLevel.Info(), 'Send LoadLot to sites...')
        self.mqtt.publish(topic, json.dumps(params), 2, False)

    def send_next_to_all_sites(self, job_data: Optional[dict] = None):
        topic = f'ate/{self.device_id}/TestApp/cmd'
        params = self._generate_command_message('next', job_data['sites'])

        if job_data is not None:
            params['job_data'] = job_data
            job_data.pop('sites')
        self.mqtt.publish(topic, json.dumps(params), 2, False)

    def send_terminate_to_all_sites(self):
        topic = f'ate/{self.device_id}/TestApp/cmd'
        self.mqtt.publish(topic, json.dumps(self._generate_command_message('terminate')))

    def send_test_results(self, test_results):
        topic = f'ate/{self.device_id}/Master/response'
        self.mqtt.publish(topic, json.dumps(self._generate_test_results_message(test_results)))

    def send_identification(self):
        topic = f'ate/{self.device_id}/Master/response'
        self.mqtt.publish(topic, json.dumps(self._generate_identification_message()))

    def send_host_info(self, host: str, port: int):
        topic = f'ate/{self.device_id}/Master/response'
        self.mqtt.publish(topic, json.dumps(self._generate_host_message(host, port)))

    def send_state(self, state, message):
        topic = f'ate/{self.device_id}/Master/response'
        self.mqtt.publish(topic, json.dumps(self._generate_state_message(state, message)))

    def send_reset_to_all_sites(self):
        control_topic = f'ate/{self.device_id}/Control/cmd'
        self.mqtt.publish(control_topic, json.dumps(self._generate_command_message('reset')))

        # hack: this make sure to terminate any zombie test application that do not have a parent process(control)
        testApp_topic = f'ate/{self.device_id}/TestApp/cmd'
        self.mqtt.publish(testApp_topic, json.dumps(self._generate_command_message('reset')))

    def send_set_log_level(self, level):
        topics = [f'ate/{self.device_id}/TestApp/cmd', f'ate/{self.device_id}/Control/cmd']
        default_message = self._generate_command_message('setloglevel')
        default_message.update({'level': level})
        for topic in topics:
            self.mqtt.publish(topic, json.dumps(default_message))

    def send_set_new_hbin(self, sbin: int, hbin: int):
        testApp_topic = f'ate/{self.device_id}/TestApp/cmd'
        message = self._generate_command_message('sethbin')
        message.update({'sbin': sbin})
        message.update({'hbin': hbin})

        self.mqtt.publish(testApp_topic, json.dumps(message))

    def send_handler_get_temperature_command(self):
        message = self._generate_message('temperature', {})
        self.send_handler_command(message)

    def send_handler_command(self, message):
        topic = f'ate/{self.device_id}/Handler/command'
        self.mqtt.publish(topic, json.dumps(message))

    def send_get_execution_strategy_command(self, layout):
        topic = f'ate/{self.device_id}/TestApp/cmd'
        message = self._generate_command_message('getexecutionstrategy')
        message.update({'layout': layout})
        self.mqtt.publish(topic, json.dumps(message))

    def _generate_command_message(self, command: str, sites: List[str] = None):
        return {'type': 'cmd',
                'command': command,
                'sites': self.sites if sites is None else sites,
                }

    def _generate_test_results_message(self, test_results):
        return self._generate_message('next', {'sites': test_results})

    def _generate_identification_message(self):
        return self._generate_message('identify', {'name': self.device_id})

    def _generate_host_message(self, host: str, port: int):
        return self._generate_message('get-host', {'host': host, 'port': port})

    def _generate_state_message(self, state, message):
        return self._generate_message('get-state', {'state': state, 'message': message})

    @staticmethod
    def _generate_message(type, payload):
        return {'type': type, 'payload': payload}

    def on_cmd_message(self, message):
        payload = self.decode_message(message)

        to_exec_command = self.commands.get(payload.get("value"))
        if to_exec_command is None:
            self.log.log_message(LogLevel.Warning(), 'received command not found')
            return False

        return to_exec_command()

    def _on_connect_handler(self, client, userdata, flags, conect_res):
        self.log.log_message(LogLevel.Info(), 'mqtt connected')
        self.connected_flag = True

        self.mqtt.subscribe(f"ate/{self.device_id}/Master/#")
        self.mqtt.subscribe(f"ate/{self.device_id}/TestApp/#")
        self.mqtt.subscribe(f"ate/{self.device_id}/Control/#")
        self.mqtt.subscribe(f"ate/{self.handler_id}/{SUBTOPIC_HANDLER}")
        self.mqtt.subscribe(f"ate/{self.device_id}/+/log/#")

        self.status_consumer.startup_done()
        self.send_reset_to_all_sites()

    def _on_disconnect_handler(self, client, userdata, distc_res):
        self.log.log_message(LogLevel.Info(), f'mqtt disconnected (rc: {distc_res})')
        self.connected_flag = False

    def _generate_status_message(self, state, message=''):
        message = {
            "type": "status",
            "interface_version": INTERFACE_VERSION,
            "state": state,
            "payload": {"state": state, "message": message}
        }
        return message

    def _generate_base_topic_status(self):
        return "ate/" + str(self.device_id) + "/Master/status"

    def __generate_ioctl_response_topic(self, resource_request):
        return f"ate/{self.device_id}/Master/{resource_request['periphery_type']}/response"

    def publish_ioctl_response(self, resource_request, result):
        response_topic = self.__generate_ioctl_response_topic(resource_request)
        self.mqtt.publish(response_topic, result, 2)

    def publish_ioctl_timeout(self, resource_request):
        response_topic = self.__generate_ioctl_response_topic(resource_request)
        message = {
            "type": "io-control-response",
            "ioctl_name": resource_request["ioctl_name"],
            "result": "Timeout"
        }
        self.mqtt.publish(response_topic, json.dumps(message), 2)

    def _generate_usersettings_message(self, usersettings: dict):
        message = {
            "type": "usersettings",
        }
        message.update(usersettings)
        return message

    def __extract_siteid_from_control_topic(self, topic):
        pats = [rf'ate/{self.device_id}/{TOPIC_CONTROLSTATUS}/site(.+)$',
                rf'ate/{self.device_id}/{TOPIC_CONTROLLOG}/site(.+)$']

        for pat in pats:
            m = re.match(pat, topic)
            if m:
                return m.group(1)

    def __extract_siteid_from_testapp_topic(self, topic):
        patterns = [rf'ate/{self.device_id}/TestApp/(?:status|testresult)/site(.+)$',
                    rf'ate/{self.device_id}/TestApp/(?:status|testsummary|log|execution_strategy)/site(.+)$',
                    rf'ate/{self.device_id}/TestApp/io-control/site(.+)/request$',
                    rf'ate/{self.device_id}/TestApp/binsettings/site(.+)$']
        for pattern in patterns:
            m = re.match(pattern, topic)
            if m:
                return m.group(1)

    def dispatch_control_message(self, topic, msg):
        siteid = self.__extract_siteid_from_control_topic(topic)
        if siteid is None:
            # Hacky: To limit the number of routs we subscribed to # on control, thus we get served
            # the messages in cmd as well, which don't have a siteid in the topicname. To avoid
            # confusing logmessage we return early in that case:
            if "cmd" in topic:
                return
            self.log.log_message(LogLevel.Warning(), f'unexpected message on control topic {topic}: extracting siteid failed')
            return

        if "status" in topic:
            self.status_consumer.on_control_status_changed(siteid, msg)
        elif "log" in topic:
            self.status_consumer.on_log_message(siteid, msg)
        else:
            assert False

    def dispatch_testapp_message(self, topic, msg):
        siteid = self.__extract_siteid_from_testapp_topic(topic)
        if siteid is None:
            # Hacky: To limit the number of routs we subscribed to # on control, thus we get served
            # the messages in cmd as well, which don't have a siteid in the topicname. To avoid
            # confusing logmessage we return early in that case:
            if "cmd" in topic:
                return
            self.log.log_message(LogLevel.Warning(), f'unexpected message on testapp topic {topic}: extracting siteid failed')
            return

        if "testresult" in topic:
            self.status_consumer.on_testapp_testresult_changed(siteid, msg)
        elif "testsummary" in topic:
            self.status_consumer.on_testapp_testsummary_changed(msg)
        elif "io-control" in topic:
            assert 'type' in msg
            assert msg['type'] == 'io-control-request'
            assert 'periphery_type' in msg
            assert 'ioctl_name' in msg
            assert 'parameters' in msg
            self.status_consumer.on_testapp_resource_changed(siteid, msg)
        elif "status" in topic:
            self.status_consumer.on_testapp_status_changed(siteid, msg)
        elif "log" in topic:
            self.status_consumer.on_log_message(siteid, msg)
        elif "execution_strategy":
            self.status_consumer.on_execution_strategy_message(siteid, msg['payload'])
        else:
            assert False

    def dispatch_handler_message(self, topic, msg):
        if "status" in topic:
            self.status_consumer.on_handler_status_changed(msg["payload"])
        elif "cmd" in topic:
            self.status_consumer.on_handler_command_message(msg)
        elif "response" in topic:
            self.status_consumer.on_handler_response_message(msg)
        else:
            assert False
