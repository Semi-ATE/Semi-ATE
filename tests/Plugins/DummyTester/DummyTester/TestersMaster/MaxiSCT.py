import asyncio
from threading import Thread, Event
from typing import List
import random

from ATE.common.logger import Logger
from tests.Plugins.Common.utils import GPIOState
from tests.Plugins.Common.TopicFactory import TopicFactory
from tests.Plugins.Common.TesterMasterConnectionHandler import TesterConnectionHandler

from DummyTester.TestersMaster.InterfaceSCT import InterfaceSCT


PORT = 1883


def get_broker_address():
    import os
    return os.getenv('ATE_INTEGRATION_TESTENV_BROKER_HOST', '127.0.0.1')


class MaxiSCT(InterfaceSCT):
    def __init__(self):
        self.name = f'master_{random.randint(0, 10000)}'
        self._log = Logger('tester')
        self.event = Event()
        self.sites = []
        for _ in range(16):
            site_info = {'state': 1, 'topic': ''}
            self.sites.append(site_info)

        self.releases = []
        self.release = self._generate_release_flag()
        self.factory = TopicFactory()
        self.sites_event = asyncio.Event()

        th = Thread(target=TesterConnectionHandler, args=(get_broker_address(), PORT, self.event, self._log, self), daemon=True)
        th.start()

    def get_strategy_type(self):
        return "default"

    def get_sites_count(self):
        return 16

    async def get_site_states(self, timeout: int) -> list:
        import contextlib
        with contextlib.suppress(asyncio.TimeoutError):
            await asyncio.wait_for(self.sites_event.wait(), timeout)

        self.sites_event.clear()
        return [site['state'] for site in self.sites]

    def release_test_execution(self, sites: list):
        self.releases.append(self._generate_release_flag(is_release=True, sites=sites))
        self.sites_event.clear()

    def get_release(self):
        return self.releases.pop() if len(self.releases) else None

    def set_site_request(self, site_id: int, state: int, topic: str):
        topic = topic.replace('test-request', 'test-release')
        self.sites[int(site_id)] = {'state': state, 'topic': topic}
        self.sites_event.set()

    @staticmethod
    def _generate_release_flag(is_release: bool = False, sites: list = []):
        return {'is_released': is_release, 'sites': sites}

    def get_site_topic(self, site_id: str) -> str:
        return self.sites[int(site_id)]['topic']

    def get_topics(self) -> List[str]:
        return [self.factory.master_subscription_topic()]

    def stop_execution(self):
        import sys
        sys.exit(0)
