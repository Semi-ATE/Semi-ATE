import aiomqtt
from paho.mqtt.client import MQTTMessage
import asyncio


class MqttWsProxy:
    def __init__(self, ws, broker_host, broker_port):
        self._ws = ws
        self._broker_host = broker_host
        self._broker_port = broker_port
        self._subs = []
        self._client = None
        self._task = None
        self._log = Logger.get_logger()

    def start_task(self):
        if self._task is not None:
            raise RuntimeError('task already started')
        self._task_stop_event = asyncio.Event()
        self._task = asyncio.create_task(self._run_task(self._task_stop_event))

    def stop_task(self):
        if self._task is not None:
            self._task_stop_event.set()

    def sub(self, topic):
        self._subs.append(topic)
        if self._client is not None:
            self._client.subscribe(topic)

    def pub(self, topic, payload, qos=0, retain=False):
        if self._client is not None:
            self._client.publish(
                topic, payload=payload, qos=qos, retain=retain)
        else:
            self._log.warning('MqttWsProxy ignore publish request because not connected')

    def _send_initial_subs(self, c):
        for topic in self._subs:
            c.subscribe(topic)

    def _message_payload_to_json_value(self, payload):
        # only forward payloads that can be encoded as utf-8 without errors
        if isinstance(payload, bytes):
            return payload.decode('utf-8')
        elif isinstance(payload, str):
            return payload
        raise ValueError(type(payload).__name__)

    def _create_onmessage_message_for_ws(self, message: MQTTMessage):
        return {
            'type': 'mqtt.onmessage',
            'payload': {
                'topic': message.topic,
                'payload': self._message_payload_to_json_value(message.payload),
                'qos': message.qos,
                'retain': message.retain,
            }
        }

    async def _run_task(self, stop_event: asyncio.Event):
        def on_connect(client, userdata, flags, rc):
            self._log.debug("MqttWsProxy connected!")
            self._send_initial_subs(client)
            self._client = client

        def on_subscribe(client, userdata, mid, granted_qos):
            self._log.debug("MqttWsProxy subscribed!")

        def on_message(client, userdata, message):
            self._log.debug("MqttWsProxy message: %s %s", message.topic, message.payload)

            try:
                ws_msg = self._create_onmessage_message_for_ws(message)
            except Exception:
                self._log.warning("MqttWsProxy ignoring unsupported mqtt message payload (possibly binary): %s %s", message.topic, message.payload)
                return

            asyncio.create_task(self._ws.send_json(ws_msg))

        def on_disconnect(client, userdata, rc):
            self._log.debug("MqttWsProxy disconnected!")

        self._log.debug(f"MqttWsProxy task start ({self._broker_host}:{self._broker_port})")

        c = aiomqtt.Client()
        c.on_connect = on_connect
        c.on_subscribe = on_subscribe
        c.on_message = on_message
        c.on_disconnect = on_disconnect
        c.loop_start()
        c.connect_async(self._broker_host, self._broker_port)
        self._client = c

        try:
            await stop_event.wait()
        finally:
            self._client = None

        c.disconnect()
        await c.loop_stop()

        self._log.debug("MqttWsProxy task end")

