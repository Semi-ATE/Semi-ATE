from threading import Event
import asyncio

from ate_common.logger import Logger
from Common.utils import GPIOState
from Common.ConnectionHandler import ConnectionHandler


class TesterConnectionHandler(ConnectionHandler):
    def __init__(self, host: str, port: int, event: Event, logger: Logger, parent):
        super().__init__(host, port, event, logger, parent)

    async def do_for_ever(self):
        while self.is_running:
            request = self._parent.get_request()
            if request is not None and request['is_requested']:
                self.send_request_message(request['site_id'], request['state'])

            await asyncio.sleep(0.1)

    def dispatch_tester_message(self, topic, message):
        print(topic, message)

        if "test-release" in topic:
            self._event.set()
        elif "testApp":
            if message['command'] != 'terminate':
                return

            self.is_running = False
            self._parent.stop_execution()
        else:
            assert False

    def send_request_message(self, site_id: str, gpio_state: GPIOState):
        import json
        self._mqtt.publish(self._topicFactory.tester_request_topic(self._client_id),
                           json.dumps(self._topicFactory.tester_request_message(site_id, gpio_state)),
                           2,
                           False)
