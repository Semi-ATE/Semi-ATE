from typing import Dict, List
import paho.mqtt.client as mqtt
import json
import queue
import threading
import logging

from ate_test_app.sequencers.TopicFactory import TopicFactory
from ate_test_app.sequencers.TheTestAppStatusAlive import TheTestAppStatusAlive
from ate_apps_common.mqtt_router import MqttRouter

logger = logging.getLogger(__name__)


class MqttClient():
    _client: mqtt.Client
    _topic_factory: TopicFactory
    _resource_msg_queue: queue.Queue

    def __init__(self, broker_host: str, broker_port: str, topic_factory: TopicFactory):
        self._topic_factory = topic_factory
        self._client = self._create_mqtt_client(topic_factory)
        self._client.connect_async(broker_host, int(broker_port), 60)
        self.submit_callback = None
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

    def publish_status(self, alive: TheTestAppStatusAlive, statedict: dict) -> mqtt.MQTTMessageInfo:
        payload = self._topic_factory.test_status_payload(alive)
        payload.update(statedict)
        return self._publish(self._topic_factory.test_status_topic(), json.dumps(payload))

    def publish_result(self, testdata: object) -> mqtt.MQTTMessageInfo:
        return self._publish(self._topic_factory.test_result_topic(), json.dumps(self._topic_factory.test_result_payload(testdata)))

    def publish_tests_summary(self, tests_summary: object) -> mqtt.MQTTMessageInfo:
        return self._publish(self._topic_factory.tests_summary_topic(), json.dumps(self._topic_factory.test_result_payload(tests_summary)))

    def publish_stdf_part(self, blob: bytes) -> mqtt.MQTTMessageInfo:
        return self._publish(self._topic_factory.test_stdf_topic(), blob)

    def publish_resource_request(self, resource_id: str, config: dict) -> mqtt.MQTTMessageInfo:
        return self._publish(self._topic_factory.test_resource_topic(resource_id), self._topic_factory.test_resource_payload(resource_id, config))

    def publish_log_information(self, log: str) -> mqtt.MQTTMessageInfo:
        return self._publish(self._topic_factory.test_log_topic(), json.dumps(self._topic_factory.test_log_payload(log)))

    def publish_execution_strategy(self, execution_strategy: List[List[str]]) -> mqtt.MQTTMessageInfo:
        return self._publish(self._topic_factory.test_execution_strategy_topic(), json.dumps(self._topic_factory.test_execution_strategy_payload(execution_strategy)))

    def _publish(self, topic: str, payload: Dict[str, str]):
        return self._client.publish(
            topic=topic,
            payload=payload,
            qos=2,
            retain=False)

    def _create_mqtt_client(self, topic_factory: TopicFactory) -> mqtt.Client:
        mqttc = mqtt.Client(client_id=topic_factory.mqtt_client_id)

        mqttc.on_connect = self._on_connect_callback
        mqttc.on_disconnect = self._on_disconnect_callback
        mqttc.on_message = self._on_message_callback

        mqttc.message_callback_add(self._topic_factory.test_cmd_topic(),
                                   self._on_message_cmd_callback)
        mqttc.message_callback_add(self._topic_factory.master_resource_topic(),
                                   self._on_message_resource_callback)
        mqttc.message_callback_add(self._topic_factory.generic_resource_response(),
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
            (self._topic_factory.master_resource_topic(resource_id=None), 2),
            (self._topic_factory.generic_resource_response(), 2)
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
        data = json.loads(message.payload.decode('utf-8'))
        self.response_data = data
        self.response_topic = message.topic
        self.event.set()

    def do_request_response(self, request_topic: str, response_topic: str, payload: dict, timeout: int):
        self.event.clear()
        self._client.publish(request_topic, payload, 2)

        while (self.event.wait(timeout)):
            if self.response_topic == response_topic:
                return False, self.response_data

        return True, None
