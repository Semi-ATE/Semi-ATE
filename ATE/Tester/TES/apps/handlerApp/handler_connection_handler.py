import json
import sys

from ATE.Tester.TES.apps.handlerApp.handler_message_generator import MessageGenerator
from ATE.Tester.TES.apps.common.connection_handler import ConnectionHandler


class HandlerConnectionHandler:
    def __init__(self, host, port, handler_id, device_ids, log, app) -> None:
        self._mqtt = None
        self._app = app
        self._log = log
        self._log.set_mqtt_client(self._mqtt)

        self.__message_generator = MessageGenerator(self._log)
        self.client_id = f'handler.{handler_id}'
        self.host = host
        self.port = port
        self.device_ids = device_ids
        self.handler_id = handler_id

    def start(self):
        self._mqtt = ConnectionHandler(self.host, self.port, self.client_id, self._log)
        self._mqtt.init_mqtt_client_callbacks(self._on_connect,
                                              self._on_message,
                                              self._on_disconnect)

        self._mqtt.register_route("Master", lambda topic, payload: self.dispatch_masterapp_message(topic, self._mqtt.decode_payload(payload)))

        self._mqtt.set_last_will(
            self.__generate_handler_status_topic(),
            self._mqtt.create_message(
                self.__message_generator.generate_status_msg('crash', '')))
        self._mqtt.start_loop()

    async def stop(self) -> None:
        await self._mqtt.stop_loop()

    def subscribe(self, topic: str) -> None:
        self._mqtt.subscribe(topic)

    def publish(self, topic: str, payload, qos: int = 0, retain: bool = False) -> None:
        self._mqtt.publish(topic, json.dumps(payload), qos=qos, retain=retain)

    def send_command(self, cmd_type: str, config: dict) -> bool:
        message = self.__message_generator.generate_command_msg(cmd_type, config)
        if message is None:
            self._log.warning(f"failed to send command from\
                             {sys._getframe().f_code.co_name} in\
                             {sys._getframe().f_code.co_filename}")
            return False

        raise Exception('fix me!!')
        topic = self.__generate_command_topic(self.device_id)
        self.publish(topic, message, qos=2)

        return True

    def publish_state(self, state: str, message: str) -> None:
        topic = self.__generate_handler_status_topic()
        payload = self.__message_generator.generate_status_msg(state, message)
        self.publish(topic, payload, qos=1, retain=False)

    def __generate_handler_status_topic(self) -> str:
        return f'ate/{self.handler_id}/Handler/status'

    @staticmethod
    def __generate_master_status_topic(device_id) -> str:
        return f'ate/{device_id}/Master/status'

    @staticmethod
    def __command_topic(device_id):
        return f"ate/{device_id}/Handler/command"

    def _on_connect(self, client, userdata, flags, rc) -> None:
        self._app.startup_done()
        self._log.debug("connected")

        self.publish_state(self._app.state, '')

        for device_id in self.device_ids:
            self.subscribe(self.__generate_master_status_topic(device_id['device_id']))
            self.subscribe(self.__command_topic(device_id['device_id']))

    def dispatch_masterapp_message(self, topic, message) -> None:
        if "status" in topic:
            self._app.on_master_state_changed(message)
        elif "command" in topic:
            print("COMMAND FROM MASTER: Impl. ME")
        elif "response" in topic:
            print("RESPONSE FROM MASTER: Impl. ME")
        else:
            assert False

    def _on_message(self, client, userdata, message) -> None:
        self._mqtt.router.inject_message(message.topic, message.payload)

    def _on_disconnect(self, client, userdata, rc) -> None:
        self._log.debug("disconnected")
