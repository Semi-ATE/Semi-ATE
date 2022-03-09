from ate_common.logger import Logger
from ate_test_app.sequencers.TopicFactory import TopicFactory
from ate_test_app.sequencers.TheTestAppMachine import TheTestAppMachine
from ate_test_app.sequencers.MqttClient import MqttClient

from typing import Optional


class MqttConnection:
    _statemachine: Optional[TheTestAppMachine]
    _mqtt: Optional[MqttClient]

    def __init__(self, params: object) -> None:
        self._statemachine = None
        self._mqtt = None
        self._logger = None
        self._params = params
        self._init_app_components()

    def set_logger(self, logger: Logger):
        self._logger = logger

    def get_mqtt_client(self) -> MqttClient:
        return self._mqtt

    def _init_app_components(self):
        topic_factory = TopicFactory(self._params.device_id,
                                     self._params.site_id)
        self._mqtt = MqttClient(self._params.broker_host,
                                self._params.broker_port,
                                topic_factory)

    def run(self):
        try:
            self._mqtt.loop_forever()
        except KeyboardInterrupt:
            pass
        self.executor.shutdown(wait=True)

    def set_callbacks(self, on_connect: callable, on_disconnect: callable, execute_command: callable, submit_callback: callable):
        self._mqtt.on_connect = on_connect
        self._mqtt.on_disconnect = on_disconnect
        self._mqtt.on_command = execute_command
        self._mqtt.submit_callback = submit_callback
