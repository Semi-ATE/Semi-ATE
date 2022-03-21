from threading import Thread, Event
import os
import time
from typing import List
import random

from Common.TopicFactory import TopicFactory
from Common.TesterConnectionHandler import TesterConnectionHandler
from Common.utils import GPIOState

from DummyTester.Testers.InterfaceSCT import InterfaceSCT
from ate_common.logger import Logger


def get_broker_address():
    return os.getenv('ATE_INTEGRATION_TESTENV_BROKER_HOST', '127.0.0.1')


PORT = 1883


class MaxiSCT(InterfaceSCT):
    def __init__(self):
        self.name = f'tester_{str(time.time())}_{random.randint(1, 10000000)}'
        self._log = Logger('tester')
        self.event = Event()
        self.requests = []
        self.request = self._generate_request_flag()
        self.factory = TopicFactory()

        th = Thread(target=TesterConnectionHandler, args=(get_broker_address(), PORT, self.event, self._log, self), daemon=True)
        th.start()

    def get_sites_count(self):
        return 16

    def do_request(self, site_id: int, timeout: int) -> bool:
        self.event.clear()
        self.requests.append(self._generate_request_flag(is_requested=True, site_id=site_id, state=GPIOState.ON))
        return self.event.wait(timeout)

    def test_in_progress(self, site_id: int):
        self.requests.append(self._generate_request_flag(is_requested=True, site_id=site_id, state=GPIOState.OFF))

    def test_done(self, site_id: int):
        self.requests.append(self._generate_request_flag(is_requested=True, site_id=site_id, state=GPIOState.ON))

    def do_init_state(self, site_id: int):
        self.requests.append(self._generate_request_flag(is_requested=True, site_id=site_id, state=GPIOState.OFF))

    # help functions to simulate Tester to Tester connection
    def reset_request(self):
        self.request.update({'is_requested': False})

    def get_request(self):
        return self.requests.pop() if len(self.requests) else None

    @staticmethod
    def _generate_request_flag(is_requested: bool = False, site_id: int = -1, state: GPIOState = GPIOState.OFF):
        return {'is_requested': is_requested, 'site_id': site_id, 'state': state}

    def get_topics(self) -> List[str]:
        return [self.factory.tester_release_topic(f'tester_{self.name}'), self.factory.tester_terminate_topic()]

    def stop_execution(self):
        import sys
        sys.exit(0)
