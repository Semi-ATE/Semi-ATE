class DummyTester:
    def do_request(self, site_id: int, timeout: int) -> bool:
        return True

    def pulse_trigger_out(self, pulse_width_ms):
        pass

    def test_in_progress(self, site_id: int):
        pass

    def test_done(self, site_id: int):
        pass
