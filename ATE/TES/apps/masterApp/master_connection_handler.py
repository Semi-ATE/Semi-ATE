from ATE.TES.apps.common.connection_handler import ConnectionHandler
from ATE.TES.apps.common.logger import Logger
import json
import re
from typing import Optional

TOPIC_COMMAND = "Master/cmd"
TOPIC_TESTSTATUS = "TestApp/status"
TOPIC_TESTRESULT = "TestApp/testresult"
TOPIC_TESTSUMMARY = "TestApp/testsummary"
TOPIC_TESTRESOURCE = "TestApp/resource"
TOPIC_CONTROLSTATUS = "Control/status"
INTERFACE_VERSION = 1
DEAD = 0
ALIVE = 1


class MasterConnectionHandler:

    """ handle commands """

    def __init__(self, host, port, sites, device_id, status_consumer):
        mqtt_client_id = f'masterapp.{device_id}'
        self.mqtt = ConnectionHandler(host, port, mqtt_client_id)
        self.mqtt.init_mqtt_client_callbacks(self._on_connect_handler,
                                             self._on_message_handler,
                                             self._on_disconnect_handler)
        self.sites = sites
        self.device_id = device_id
        self.log = Logger.get_logger()
        self.connected_flag = False
        self.status_consumer = status_consumer

    def start(self):
        self.mqtt.set_last_will(
            self._generate_base_topic_status(),
            self.mqtt.create_message(
                self._generate_status_message(DEAD, 'crash')))
        self.mqtt.start_loop()

    async def stop(self):
        await self.mqtt.stop_loop()

    def publish_state(self, state, statedict=None):
        self.mqtt.publish(self._generate_base_topic_status(),
                          self.mqtt.create_message(
                          self._generate_status_message(ALIVE, state, statedict)),
                          False)

    def publish_resource_config(self, resource_id: str, config: dict):
        self.mqtt.publish(self._generate_resource_config_topic(resource_id),
                          self.mqtt.create_message(
                              self._generate_resource_config_message(resource_id, config)),
                          False)

    def send_load_test_to_all_sites(self, testapp_params):
        topic = f'ate/{self.device_id}/Control/cmd'
        params = {
            'type': 'cmd',
            'command': 'loadTest',
            'testapp_params': testapp_params,
            'sites': self.sites,
        }
        self.log.info("Send LoadLot to sites...")
        self.mqtt.publish(topic, json.dumps(params), 0, False)

    def send_next_to_all_sites(self, job_data: Optional[dict] = None):
        topic = f'ate/{self.device_id}/TestApp/cmd'
        params = {
            'type': 'cmd',
            'command': 'next',
            'sites': self.sites,
        }
        if job_data is not None:
            params['job_data'] = job_data
        self.mqtt.publish(topic, json.dumps(params), 0, False)

    def send_terminate_to_all_sites(self):
        topic = f'ate/{self.device_id}/TestApp/cmd'
        params = {
            'type': 'cmd',
            'command': 'terminate',
            'sites': self.sites,
        }
        self.mqtt.publish(topic, json.dumps(params), 0, False)

    def send_reset_to_all_sites(self):
        topic = f'ate/{self.device_id}/Control/cmd'
        params = {
            'type': 'cmd',
            'command': 'reset',
            'sites': self.sites,
        }
        self.mqtt.publish(topic, json.dumps(params), 0, False)

    def send_load_command(self):
        self.log.info("send load test command")
        return True

    def send_terminate_command(self):
        self.log.info("send terminate command")
        return True

    def send_start_next_test_command(self):
        self.log.info("send start next test command")
        return True

    def on_cmd_message(self, message):
        payload = self.decode_message(message)

        to_exec_command = self.commands.get(payload.get("value"))
        if to_exec_command is None:
            self.log.warning("received command not found")
            return False

        return to_exec_command()

    def _on_connect_handler(self, client, userdata, flags, conect_res):
        self.log.info("mqtt connected")
        self.connected_flag = True

        self.mqtt.subscribe(self._generate_base_topic_cmd())
        self.mqtt.subscribe(self.__generate_sub_topic(TOPIC_CONTROLSTATUS))
        self.mqtt.subscribe(self.__generate_sub_topic(TOPIC_TESTRESULT))
        self.mqtt.subscribe(self.__generate_sub_topic(TOPIC_TESTSTATUS))
        self.mqtt.subscribe(self.__generate_sub_topic(TOPIC_TESTRESOURCE))
        self.mqtt.subscribe(self.__generate_sub_topic(TOPIC_TESTSUMMARY))
        self.status_consumer.startup_done()

    def _on_disconnect_handler(self, client, userdata, distc_res):
        self.log.info("mqtt disconnected (rc: %s)", distc_res)
        self.connected_flag = False

    def _generate_status_message(self, alive, state, statedict=None):
        message = {
            "type": "status",
            "alive": alive,
            "interface_version": INTERFACE_VERSION,
            "state": state,
        }
        if statedict is not None:
            message.update(statedict)
        return message

    def _generate_base_topic_status(self):
        return "ate/" + str(self.device_id) + "/Master/status"

    def _generate_resource_config_message(self, resource_id: str, config: dict):
        message = {
            'type': 'resource-config',
            'resource_id': resource_id,
            'config': config
        }
        return message

    def _generate_resource_config_topic(self, resource_id: str):
        return "ate/" + str(self.device_id) + "/Master/resource/" + resource_id

    def _generate_usersettings_message(self, usersettings: dict):
        message = {
            "type": "usersettings",
        }
        message.update(usersettings)
        return message

    def _generate_topic_usersettings(self):
        return "ate/" + str(self.device_id) + "/Master/usersettings"

    def __generate_sub_topic(self, topic):
        return "ate/" + str(self.device_id) + "/" + topic + "/#"

    def _generate_base_topic_cmd(self):
        return "ate/" + str(self.device_id) + "/Master/cmd"

    def __extract_siteid_from_control_topic(self, topic):
        pat = rf'ate/{self.device_id}/{TOPIC_CONTROLSTATUS}/site(.+)$'
        m = re.match(pat, topic)
        if m:
            return m.group(1)

    def __extract_siteid_from_testapp_topic(self, topic):
        pat1 = rf'ate/{self.device_id}/TestApp/(?:status|testsummary)/site(.+)$'
        m = re.match(pat1, topic)
        if m:
            return m.group(1)
        pat = rf'ate/{self.device_id}/TestApp/(?:status|testresult)/site(.+)$'
        m = re.match(pat, topic)
        if m:
            return m.group(1)
        pat2 = rf'ate/{self.device_id}/TestApp/resource/.+?/site(.+)$'
        m = re.match(pat2, topic)
        if m:
            return m.group(1)

    def dispatch_control_message(self, client, topic, msg):
        siteid = self.__extract_siteid_from_control_topic(topic)
        if siteid is None:
            self.log.warning('unexpected message on control topic '
                             + f'"{topic}": extracting siteid failed')
            return

        if "status" in topic:
            self.status_consumer.on_control_status_changed(siteid, msg)
        else:
            assert(False)

    def dispatch_testapp_message(self, client, topic, msg):
        siteid = self.__extract_siteid_from_testapp_topic(topic)
        if siteid is None:
            self.log.warning('unexpected message on testapp topic ' /
                             + f'"{topic}": extracting siteid failed')
            return

        if "testresult" in topic:
            self.status_consumer.on_testapp_testresult_changed(siteid, msg)
        elif "testsummary" in topic:
            self.status_consumer.on_testapp_testsummary_changed(msg)
        elif "resource" in topic:
            assert 'type' in msg
            assert msg['type'] == 'resource-config-request'
            assert 'resource_id' in msg
            assert 'config' in msg
            self.status_consumer.on_testapp_resource_changed(siteid, msg)
        elif "status" in topic:
            self.status_consumer.on_testapp_status_changed(siteid, msg)
        else:
            assert False

    def _on_message_handler(self, client, userdata, msg):
        payload = self.mqtt.decode_message(msg)
        if "Control" in msg.topic:
            self.dispatch_control_message(client, msg.topic, payload)
        elif "TestApp" in msg.topic:
            self.dispatch_testapp_message(client, msg.topic, payload)
        else:
            assert False
