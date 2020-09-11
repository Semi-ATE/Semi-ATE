import json
import aiomqtt
import logging
import asyncio
import sys
from typing import Optional

from ATE.TES.apps.handlerApp.handler_message_generator import MessageGenerator
from ATE.TES.apps.common.logger import Logger


class ConnectionHandler:
    def __init__(self, configuration: dict) -> None:
        self.__message_generator = MessageGenerator()
        self._broker_host = configuration["broker_host"]
        self._broker_port = configuration["broker_port"]
        self.device_id = configuration["device_id"]
        self._task = None
        self._client = None
        self._state: str = "Idle"
        self.log = Logger.get_logger()

        self._log = logging.getLogger()
        self._log.addHandler(logging.StreamHandler())
        self._log.setLevel(logging.DEBUG)

    def start_task(self) -> None:
        if self._task is not None:
            raise RuntimeError('task already started')

        self._task = asyncio.run(self._run_task())

    async def stop_task(self) -> None:
        if self._task is not None:
            self._task.cancel()
            await self._task

    def subscribe(self, topic: str) -> None:
        self.client.subscribe(topic)

    def publish(self, topic: str, payload, qos: int = 0, retain: bool = False) -> None:
        self.client.publish(topic, json.dumps(payload), qos=qos, retain=retain)

    def send_command(self, cmd_type: str, config: dict) -> bool:
        message = self.__message_generator.generate_command_msg(cmd_type, config)
        if message is None:
            self.log.warning(f"failed to send command from\
                             {sys._getframe().f_code.co_name} in\
                             {sys._getframe().f_code.co_filename}")
            return False

        topic = self.__generate_command_topic(self.device_id, cmd_type)
        self.publish(topic, message, qos=2)

        return True

    def __publish_state(self, state: str, retain: bool = False) -> None:
        topic = self.__generate_status_topic(self.device_id)
        payload = self.__message_generator.generate_status_msg(state)
        self.publish(topic, payload, qos=1, retain=retain)

    def __set_last_will(self) -> None:
        if self.client is None:
            raise RuntimeError('client not set yet')

        topic = self.__generate_status_topic(self.device_id)
        payload = self.__message_generator.generate_status_msg("crash")
        self.client.will_set(topic, json.dumps(payload), retain=True)

    def __generate_command_topic(self, device_id: str, cmd_type: str) -> str:
        return f'ate/{device_id}/Master/{cmd_type}'

    def __generate_status_topic(self, device_id: str) -> str:
        return f'ate/{device_id}/Handler/status'

    def __generate_Master_topic(self, site_id: Optional[str] = None) -> str:
        # TODO: should master have an explicit id
        # return f'ate/{device_id}/Master/status/site{site_id}'
        return f'ate/{self.device_id}/Master/status'

    async def _run_task(self) -> None:
        def on_connect(client, userdata, flags, rc) -> None:
            self._log.debug("connected")
            self.__publish_state(self._state)
            self.subscribe(self.__generate_Master_topic())

        def dispatch_masterapp_message(self, message) -> None:
            pass

        def on_message(client, userdata, message) -> None:
            self._log.debug(f"message: {message.topic} {message.payload}")
            if "Master" in message.topic:
                self.dispatch_masterapp_message(message)
            else:
                # TODO: should master be the only app who communication with the handler
                pass

        def on_disconnect(client, userdata, rc) -> None:
            self._log.debug("disconnected")

        self.client = aiomqtt.Client()
        self.__set_last_will()
        self.client.enable_logger()
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.on_disconnect = on_disconnect
        self.client.connect_async(self._broker_host, self._broker_port)
        self.client.loop_start()

        try:
            dummy_event_to_sleep_until_task_is_canceled = asyncio.Event()
            await dummy_event_to_sleep_until_task_is_canceled.wait()
        except asyncio.CancelledError:
            pass
        finally:
            self.client.disconnect()
            await self.client.loop_stop()
