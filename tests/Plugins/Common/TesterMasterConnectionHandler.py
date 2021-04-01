from threading import Event
import asyncio
import json

from ATE.common.logger import Logger
from tests.Plugins.Common.ConnectionHandler import ConnectionHandler


class TesterConnectionHandler(ConnectionHandler):
    def __init__(self, host: str, port: int, event: Event, logger: Logger, parent) -> None:
        super().__init__(host, port, event, logger, parent)

    async def do_for_ever(self):
        while self.is_running:
            release = self._parent.get_release()
            if release is not None and release['is_released']:
                self.send_release_message(release['sites'])

            await asyncio.sleep(0.1)

    def dispatch_tester_message(self, topic, message) -> None:
        print(topic, message)

        if "test-request" in topic:
            self._parent.set_site_request(int(message['payload']['site']), int(message['payload']['state']), topic)
        elif "testApp":
            if message['command'] != 'terminate':
                return

            self.is_running = False
            self._parent.stop_execution()
        else:
            assert False

    def send_release_message(self, sites: list):
        for site in sites:
            self._mqtt.publish(self._parent.get_site_topic(site),
                               json.dumps(self._topicFactory.tester_release_message(site)),
                               2,
                               False)
