
from abc import ABC, abstractmethod


class InterfaceSCT(ABC):
    @abstractmethod
    def get_sites_count(self):
        pass
