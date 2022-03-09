import asyncio
from DummyTester.TestersMaster.InterfaceSCT import InterfaceSCT


class MiniSCT(InterfaceSCT):
    def get_sites_count(self):
        return 1

    def release_test_execution(self, sites: list):
        pass

    async def get_site_states(self, timeout: int) -> list:
        await asyncio.sleep(0.0)
        return 16 * [1]

    def get_strategy_type(self):
        return 'simple'
