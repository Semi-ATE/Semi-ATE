from abc import ABC, abstractmethod


class TesterInterface(ABC):
    SITE_COUNT = -1

    def get_sites_count(self):
        if self.SITE_COUNT == -1:
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

    @abstractmethod
    def do_init_state(self, site_id: int):
        pass

    def setup(self):
        pass

    def teardown(self):
        pass

    def run_pattern(self, pattern_name: str, start_label: str = '', stop_label: str = '', timeout: int = 1000):
        pass
