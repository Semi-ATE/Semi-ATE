
from abc import ABC, abstractmethod


class TesterInterface(ABC):
    SITE_COUNT = -1

    def get_sites_count(self):
        if not hasattr(self, 'SITE_COUNT') or self.SITE_COUNT == -1:
            raise Exception('make sure to override the static class variable `SITE_COUNT` with the correct site number supported by the tester inside the derived class')

        return self.SITE_COUNT

    @abstractmethod
    def do_request(self, site_id: int, timeout: int) -> bool:
        pass

    @abstractmethod
    def test_in_progress(self, site_id: int):
        pass

    @abstractmethod
    def test_done(self, site_id: int, timeout: int):
        pass

    def pulse_trigger_out(self, pulse_width_ms):
        # ToDo: Implement with actual hardware.
        print("Tester: Pulse Trigger Out")

    def setup(self):
        pass

    def teardown(self):
        pass
