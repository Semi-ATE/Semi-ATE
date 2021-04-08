from asyncio.queues import Queue, QueueEmpty
import json
from typing import List, Tuple

from ATE.common.logger import LogLevel
from ATE.Tester.TES.apps.common.mqtt_connection import MqttConnection

INVISIBLE_TESTER_STATES = ['connecting', 'loading', 'unloading', 'waitingforbintable']


class HandlerConnectionHandler:
    def __init__(self, host, port, _handler_id, _device_ids, log, app, event) -> None:
        self._mqtt = None
        self._app = app
        self._log = log
        self.event = None
        self.command = None

        self._client_id = f'handler.{_handler_id}'
        self._host = host
        self._port = port
        self._device_ids = _device_ids
        self._handler_id = _handler_id
        self._event = event
        self._message_queue = Queue()

    def start(self):
        self._mqtt = MqttConnection(self._host, self._port, self._client_id, self._log)
        self._log.set_mqtt_client(self._mqtt)
        self._mqtt.init_mqtt_client_callbacks(self._on_connect,
                                              self._on_disconnect)

        self._mqtt.register_route("Master", lambda topic, payload: self.dispatch_masterapp_message(topic, self._mqtt.decode_payload(payload)))
        self._mqtt.register_route("Handler", lambda topic, payload: self.dispatch_masterapp_message(topic, self._mqtt.decode_payload(payload)))

        self._mqtt.set_last_will(
            self._generate_handler_status_topic(),
            self._mqtt.create_message(
                self._generate_status_message('crash', '')))
        self._mqtt.start_loop()

    async def stop(self) -> None:
        await self._mqtt.stop_loop()

    def subscribe(self, topic) -> None:
        self._mqtt.subscribe(topic)

    def publish(self, topic, payload, qos=2, retain=False) -> None:
        self._mqtt.publish(topic, json.dumps(payload), qos=qos, retain=retain)

    def publish_state(self, state, message) -> None:
        self._log.log_message(LogLevel.Info(), f'Handler state: {state}')
        self.publish(self._generate_handler_status_topic(),
                     self._generate_status_message(state, message),
                     qos=1,
                     retain=False)

    def _on_connect(self, client, userdata, flags, rc) -> None:
        self._app.startup_done('connection to broker is established')

        for device_id in self._device_ids:
            self.subscribe(self._generate_master_status_topic(device_id))
            self.subscribe(self._generate_command_topic(device_id))
            self.subscribe(self._generate_response_topic(device_id))

    def _on_disconnect(self, client, userdata, rc) -> None:
        self._log.log_message(LogLevel.Debug(), "disconnected")

    def dispatch_masterapp_message(self, topic, message) -> None:
        master_id = topic.split('/')[1]
        if "status" in topic:
            master_state = message['state']
            self._app.on_master_state_changed(master_id, master_state)
            self._handle_master_state(message)
        elif "command" in topic or\
             "response" in topic:
            self._put_message(message)
        else:
            assert False

    def _handle_master_state(self, message):
        if message['state'] in INVISIBLE_TESTER_STATES:
            return

        if not self.command:
            return

        self._put_message(message)

    def _put_message(self, message):
        self._message_queue.put_nowait(message)
        self._event.set()

    def get_message(self):
        try:
            return self._message_queue.get_nowait()
        except QueueEmpty:
            return None

    def get_mqtt_client(self):
        return self._mqtt

    def send_command_message(self, message):
        for device_id in self._device_ids:
            self._mqtt.publish(self._generate_master_command_topic(device_id),
                               self._mqtt.create_message(message),
                               False)

    def publish_head_layout(self, layout: List[Tuple[int]]):
        message = self._generate_layout_message(layout)
        self.send_command_message(message)

    def send_response_message(self, message):
        self._mqtt.publish(self._generate_handler_response_topic(),
                           self._mqtt.create_message(message),
                           False)

    def handle_message(self, message):
        response = self._app.handle_message(message)
        if len(response):
            self._message_queue.put_nowait(response)
            self._event.set()
            return

        if message['type'] == 'temperature':
            self.send_response_message(message)
        else:
            self.send_command_message(message)
            self.command = message['type']

    @staticmethod
    def _generate_message(type, payload):
        return {'type': type, 'payload': payload}

    def _generate_status_message(self, state, message):
        payload = {'state': state, 'message': message}
        return self._generate_message('status', payload)

    def _generate_layout_message(self, layout):
        payload = {'sites': layout}
        return self._generate_message('site-layout', payload)

    @staticmethod
    def _generate_command_topic(device_id):
        return f"ate/{device_id}/Handler/command"

    @staticmethod
    def _generate_response_topic(device_id):
        return f"ate/{device_id}/Master/response"

    @staticmethod
    def _generate_log_message(log_message):
        return {"type": "log",
                "payload": log_message}

    def _handler_log_topic(self):
        return f'ate/{self._handler_id}/Handler/log/'

    def _generate_handler_status_topic(self):
        return f'ate/{self._handler_id}/Handler/status'

    def _generate_handler_response_topic(self):
        return f'ate/{self._handler_id}/Handler/response'

    @staticmethod
    def _generate_master_status_topic(device_id):
        return f'ate/{device_id}/Master/status'

    @staticmethod
    def _generate_master_command_topic(device_id):
        return f"ate/{device_id}/Master/cmd"
