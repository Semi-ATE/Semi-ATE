import asyncio

from TDKMicronas.TestersMaster.InterfaceSCT import InterfaceSCT


class MaxiSCT(InterfaceSCT):
    def get_sites_count(self):
        # TODO: temporary value for 16
        return 16

    def get_site_states(self) -> list:
        pass

    async def get_site_states(self, timeout: int) -> list:
        await asyncio.sleep(0.0)
        return 16 * [1]

    def release_test_execution(self, sites: list):
        pass

    def get_strategy_type(self):
        return "simple"
