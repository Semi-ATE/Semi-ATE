import asyncio
import json
from aiomqtt import Client

from ate_apps_common.mqtt_router import MqttRouter
from ate_common.logger import LogLevel, Logger


class MqttConnection:
    def __init__(self, host: str, port: int, mqtt_client_id: str, logger: Logger):
        self.host = host
        self.port = port
        self.mqtt_client_id = mqtt_client_id
        self.log = logger
        self.router = MqttRouter()
        self.response_event = asyncio.Event()
        self.response_data = None
        self.mqtt_client = None
        self.last_will = {}
        self.__aenter__()

    async def __aenter__(self):
        self.mqtt_client = Client(hostname=self.host, port=self.port, client_id=self.mqtt_client_id, **self.last_will)
        await self.mqtt_client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.mqtt_client.__aexit__(exc_type, exc, tb)

    async def subscribe(self, topic):
        await self.mqtt_client.subscribe(topic)

    async def unsubscribe(self, topic):
        await self.client.unsubscribe(topic)

    async def publish(self, topic, payload=None, qos=2, retain=False):
        await self.client.publish(topic, payload, qos=qos, retain=retain)

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

    def register_route(self, route, callback):
        self.router.register_route(route, callback)

    def unregister_route(self, route):
        self.router.unregister_route(route)

    async def subscribe_and_register(self, route, callback):
        await self.subscribe(route)
        self.router.register_route(route, callback)

    @staticmethod
    def send_log(_):
        pass

    async def publish_with_response(self, topic_base, data):
        response_topic = f"{topic_base}/response"
        request_topic = f"{topic_base}/request"
        self.response_data = None
        self.response_event.clear()
        await self.subscribe_and_register(response_topic, lambda topic, resp: self.response_received(topic, resp))
        await self.publish(request_topic, data)
        await asyncio.wait_for(self.response_event.wait(), 5.0)
        await self.unsubscribe(response_topic)
        self.unregister_route(response_topic)
        return self.response_data

    async def message_loop(self):
        async with self.client.messages() as messages:
            async for message in messages:
                topic = message.topic
                payload = message.payload
                self.router.inject_message(topic, payload)

    def set_last_will(self, topic, msg):
        if self.mqtt_client is not None:
            print(f"set_last_will({topic}, {msg}) after connection to the client is not possible")
        self.last_will = {
            "last_will_topic": topic,
            "last_will_payload": msg,
            "last_will_qos": 2,
            "last_will_retain": False
        }

    # CJ mit der neuen aiomqtt muss das geändert werden, es gibt kein on_connect, on_disconnect, on_message mehr!!
    def init_mqtt_client_callbacks(self, on_connect, on_disconnect):
        #self.mqtt_client.on_connect = on_connect
        #self.mqtt_client.on_disconnect = on_disconnect
        #self.mqtt_client.on_message = self._on_message_handler
        print("init_mqtt_client_callbacks not necessary....")

    def _on_message_handler(self, client, userdata, msg):
        self.router.inject_message(msg.topic, msg.payload)


# CJ: braucht man das noch so?????
    def start_loop(self):
        self.mqtt_client.connect_async(self.host, self.port)
        self.mqtt_client.loop_start()

    async def stop_loop(self):
        await self.mqtt_client.loop_stop()

    def response_received(self, topic, data):
        self.response_data = data
        self.response_event.set()
