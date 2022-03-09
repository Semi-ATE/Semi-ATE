
from abc import ABC, abstractmethod


class InterfaceSCT(ABC):
    def pulse_trigger_out(self, pulse_width_ms):
        # ToDo: Implement with actual hardware.
        print(f"MiniSCT: Pulse Trigger Out")

    @abstractmethod
    def get_sites_count(self):
        pass

    @abstractmethod
    def do_request(self, site_id: int, timeout: int) -> bool:
        pass

    @abstractmethod
    def test_in_progress(self, site_id: int):
        pass

    @abstractmethod
    def test_done(self, site_id: int, timeout: int):
        pass
