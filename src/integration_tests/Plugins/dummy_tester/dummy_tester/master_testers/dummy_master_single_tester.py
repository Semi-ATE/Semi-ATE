import asyncio
from dummy_tester.master_testers.master_tester_interface import MasterTesterInterface


class MiniSCT(MasterTesterInterface):
    def get_sites_count(self):
        return 1

    def release_test_execution(self, sites: list):
        pass

    async def get_site_states(self, timeout: int) -> list:
        await asyncio.sleep(0.0)
        return 16 * [1]

    def get_strategy_type(self):
        return 'simple'
