from semi_ate_testers.testers.tester_interface import TesterInterface

class DummySingleTester(TesterInterface):
    def pulse_trigger_out(self, pulse_width_ms):
        # ToDo: Implement with actual hardware.
        print(f"Single Tester: Pulse Trigger Out")

    def get_sites_count(self):
        return 1

    def do_request(self, site_id: int, timeout: int) -> bool:
        return True

    def test_in_progress(self, site_id: int):
        pass

    def test_done(self, site_id: int, timeout: int):
        pass

    def do_init_state(self, site_id: int):
        pass
