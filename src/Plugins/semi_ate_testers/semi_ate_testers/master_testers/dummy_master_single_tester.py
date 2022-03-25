import asyncio
from semi_ate_testers.master_testers.tester_master_interface import MasterTesterInterface


class DummyMasterSingleTester(MasterTesterInterface):
    def pulse_trigger_out(self, pulse_width_ms):
        # ToDo: Implement with actual hardware.
        print(f"Single Tester: Pulse Trigger Out")

    def get_sites_count(self):
        return 1

    async def get_site_states(self, timeout: int) -> list:
        await asyncio.sleep(0.0)
        return 16 * [1]

    def release_test_execution(self, sites: list):
        pass

    def get_strategy_type(self):
        return "simple"
