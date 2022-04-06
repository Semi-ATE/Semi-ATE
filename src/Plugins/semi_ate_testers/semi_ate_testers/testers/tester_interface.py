from abc import ABC, abstractmethod

class TesterInterface(ABC):
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

    @abstractmethod
    def do_init_state(self, site_id: int):
        pass
