"""
    This class only runs under windows if the following line appears after the first import asncio :
        if sys.platform.startswith('win'):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
"""
import sys
import asyncio
import threading
import json
from time import sleep
from aiomqtt import Client, MqttError, Will
from ate_apps_common.mqtt_router import MqttRouter
from ate_common.logger import LogLevel, Logger


def ensure_asyncio_event_loop_compatibility_for_windows():
    """
    WindowsSelectorEventLoopPolicy is required for
    asyncio.create_subprocess_exec or it will fail with
    NotImplementedError.
    """
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class MqttConnection:
    def __init__(self, host: str, port: int, mqtt_client_id: str, logger: Logger):
        self.timeout = 5
        self.log = logger
        self.host = host
        self.port = port
        self.mqtt_client_id = mqtt_client_id
        self.router = MqttRouter()
        self.mqtt_client = None
        self._mqtt_client_cm = None
        self.listen_task = None
        self.on_disconnect = None
        self._last_will = None
        self.loop = asyncio.new_event_loop()

    async def connect(self):
        client_cm = Client(
            self.host,
            port=self.port,
            identifier=self.mqtt_client_id,
            will=self._last_will
            )
        self.mqtt_client = await asyncio.wait_for(client_cm.__aenter__(), timeout=self.timeout)
        self._mqtt_client_cm = client_cm
        self._connected = asyncio.Event()
        self.response_event = asyncio.Event()
        self._connected.set()

    async def disconnect(self):
        if self.mqtt_client and self._mqtt_client_cm:
            await self._mqtt_client_cm.__aexit__(None, None, None)
            self.mqtt_client = None
            self._mqtt_client_cm = None
            self._connected.clear()

    def start_loop(self, on_disconnect=None):
        self.on_disconnect = on_disconnect
        self._thread = threading.Thread(target=self._create_loop, daemon=True)
        self._thread.start()
        sleep(2)

    def _create_loop(self):
        asyncio.set_event_loop(self.loop)
        self.listen_task = self.loop.create_task(self._loop())
        self.loop.run_forever()

    async def _loop(self):
        try:
            await self.connect()
            async for message in self.mqtt_client.messages:
                await self._async__on_message_handler(message)
        except asyncio.TimeoutError:
            print(f"Connection to the MQTT broker {self.host}:{self.port} could not be established within {self.timeout} seconds.")
        except MqttError as e:
            print(f"MQTT-Client Error: {e}")
        except Exception as e:
            print(f"MQTT-Client unexpected Error: {e}")
        finally:
            await self.disconnect()
            print(f"MQTT-Client {self.host}:{self.port} closed.")
            if self.on_disconnect is not None:
                self.on_disconnect('disconnect')
        await asyncio.sleep(1)

    def stop_loop(self):
        if self.listen_task:
            fut_cancel = asyncio.run_coroutine_threadsafe(self._cancel_loop(), self.loop)
            fut_cancel.result()
        self.loop.call_soon_threadsafe(self.loop.stop)
        self._thread.join()

    async def _cancel_loop(self):
        if self.listen_task:
            self.listen_task.cancel()
            try:
                await self.listen_task
            except asyncio.CancelledError:
                pass
        await self.disconnect()

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
        self._last_will = Will(
           topic=topic,
           payload=msg,
           qos=2,
           retain=False)

    async def _async_subscribe(self, topic):
        await self._connected.wait()
        await self.mqtt_client.subscribe(topic)

    def subscribe(self, topic):
        return asyncio.run_coroutine_threadsafe(self._async_subscribe(topic), self.loop)

    async def _async_publish(self, topic, payload=None, qos=2, retain=False):
        await self._connected.wait()
        await self.mqtt_client.publish(topic, payload, qos, retain)

    def publish(self, topic, payload=None, qos=2, retain=False):
        return asyncio.run_coroutine_threadsafe(self._async_publish(topic, payload), self.loop)

    def register_route(self, route, callback):
        self.router.register_route(route, callback)

    async def subscribe_and_register(self, route, callback):
        await self.mqtt_client.subscribe(route)
        self.router.register_route(route, callback)

    async def unsubscribe(self, topic):
        await self.mqtt_client.unsubscribe(topic)

    def unregister_route(self, route):
        self.router.unregister_route(route)

    async def _async__on_message_handler(self, msg):
        self.router.inject_message(str(msg.topic), msg.payload)

    def _on_message_handler(self, msg):
        self.router.inject_message(str(msg.topic), msg.payload)

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
        await self.subscribe_and_register(response_topic, lambda topic, resp: self.response_received(topic, resp))
        await self.mqtt_client.publish(request_topic, data)
        await asyncio.wait_for(self.response_event.wait(), 5.0)
        await self.unsubscribe(response_topic)
        self.unregister_route(response_topic)
        return self.response_data
