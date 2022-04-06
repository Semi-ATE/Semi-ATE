
from abc import ABC, abstractmethod


class MasterTesterInterface(ABC):
    @abstractmethod
    def get_sites_count(self):
        pass

    @abstractmethod
    def get_site_states(self) -> list:
        pass

    @abstractmethod
    def release_test_execution(self, sites: list):
        pass

    @abstractmethod
    def get_strategy_type(self):
        return "default"
