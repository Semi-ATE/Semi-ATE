
from TDKMicronas.Testers.InterfaceSCT import InterfaceSCT


class MiniSCT(InterfaceSCT):
    def pulse_trigger_out(self, pulse_width_ms):
        # ToDo: Implement with actual hardware.
        print(f"MiniSCT: Pulse Trigger Out")

    def get_sites_count(self):
        return 1

    def do_request(self, site_id: int, timeout: int) -> bool:
        return True

    def test_in_progress(site_id: int):
        pass

    def test_done(site_id: int, timeout: int):
        pass

    def do_init_state(site_id: int):
        pass
