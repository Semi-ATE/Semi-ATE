from threading import Event
import asyncio
import json

from ate_common.logger import LogLevel, Logger
from ate_apps_common.mqtt_connection import MqttConnection
from Common.utils import GPIOState


class ConnectionHandler:
    def __init__(self, host: str, port: int, event: Event, logger: Logger, parent) -> None:
        self._parent = parent
        self._mqtt = None
        self._log = logger

        self._client_id = f'tester_{self._parent.name}'
        self._host = host
        self._port = port
        self._event = event
        self._topicFactory = self._parent.factory

        self.is_running = True
        asyncio.run(self.start())

    async def start(self):
        self._mqtt = MqttConnection(self._host, self._port, self._client_id, self._log)
        self._log.set_mqtt_client(self._mqtt)
        self._mqtt.init_mqtt_client_callbacks(self._on_connect,
                                              self._on_disconnect)

        self._mqtt.register_route("Tester", lambda topic, payload: self.dispatch_tester_message(topic, self._mqtt.decode_payload(payload)))
        self._mqtt.register_route("TestApp", lambda topic, payload: self.dispatch_tester_message(topic, self._mqtt.decode_payload(payload)))

        self._mqtt.set_last_will(
            self._topicFactory.tester_status_topic(self._client_id),
            self._mqtt.create_message(
                self._topicFactory.tester_status_message('crash')))

        self._mqtt.start_loop()

        await self.do_for_ever()

    def subscribe(self, topic) -> None:
        self._mqtt.subscribe(topic)

    def publish(self, topic, payload, qos=2, retain=False) -> None:
        self._mqtt.publish(topic, json.dumps(payload), qos=qos, retain=retain)

    def publish_state(self, state) -> None:
        self.publish(self._topicFactory.tester_status_topic(self._client_id),
                     self._topicFactory.tester_status_message(state),
                     qos=2,
                     retain=False)

    def _on_connect(self, client, userdata, flags, rc) -> None:
        for topic in self._parent.get_topics():
            self.subscribe(topic)

        self.publish_state('running')

    def _on_disconnect(self, client, userdata, rc) -> None:
        self._log.log_message(LogLevel.Debug(), "disconnected")

    def dispatch_tester_message(self, topic, message) -> None:
        raise Exception('impl. me')

    def send_request_message(self, site_id: str, gpio_state: GPIOState):
        raise Exception('impl. me')

    def do_forever(self):
        raise Exception('impl. me')
