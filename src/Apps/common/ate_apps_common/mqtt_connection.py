import aiomqtt
import asyncio
import json

from ate_apps_common.mqtt_router import MqttRouter
from ate_common.logger import LogLevel, Logger


class MqttConnection:
    def __init__(self, host: str, port: int, mqtt_client_id: str, logger: Logger):
        self.mqtt_client = aiomqtt.Client(client_id=mqtt_client_id)
        self.mqtt_client.reconnect_delay_set(10, 15)
        self.log = logger
        self.host = host
        self.port = port
        self.router = MqttRouter()
        self.response_event = asyncio.Event()

    def init_mqtt_client_callbacks(self, on_connect, on_disconnect):
        self.mqtt_client.on_connect = on_connect
        self.mqtt_client.on_disconnect = on_disconnect
        self.mqtt_client.on_message = self._on_message_handler

    def start_loop(self):
        self.mqtt_client.connect_async(self.host, self.port)
        self.mqtt_client.loop_start()

    async def stop_loop(self):
        await self.mqtt_client.loop_stop()

    def create_message(self, msg):
        return json.dumps(msg)

    def decode_message(self, message):
        return self.decode_payload(message.payload)

    def decode_payload(self, payload_bytes):
        try:
            payload = json.loads(payload_bytes)
            return payload
        except json.JSONDecodeError as error:
            self.log.log_message(LogLevel.Error(), f'{error}')

        return None

    def set_last_will(self, topic, msg):
        self.mqtt_client.will_set(topic, msg, 2, False)

    def subscribe(self, topic):
        self.mqtt_client.subscribe(topic)

    def publish(self, topic, payload=None, qos=2, retain=False):
        self.mqtt_client.publish(topic, payload, qos, retain)

    def register_route(self, route, callback):
        self.router.register_route(route, callback)

    def subscribe_and_register(self, route, callback):
        self.subscribe(route)
        self.router.register_route(route, callback)

    def unsubscribe(self, topic):
        self.mqtt_client.unsubscribe(topic)

    def unregister_route(self, route):
        self.router.unregister_route(route)

    def _on_message_handler(self, client, userdata, msg):
        self.router.inject_message(msg.topic, msg.payload)

    @staticmethod
    def send_log(_):
        pass

    def response_received(self, topic, data):
        self.response_data = data
        self.response_event.set()

    async def publish_with_response(self, topic_base, data):
        response_topic = f"{topic_base}/response"
        request_topic = f"{topic_base}/request"
        self.response_data = None
        self.response_event.clear()
        self.subscribe_and_register(response_topic, lambda topic, resp: self.response_received(topic, resp))
        self.mqtt_client.publish(request_topic, data)
        await asyncio.wait_for(self.response_event.wait(), 5.0)
        self.unsubscribe(response_topic)
        self.unregister_route(response_topic)
        return self.response_data
