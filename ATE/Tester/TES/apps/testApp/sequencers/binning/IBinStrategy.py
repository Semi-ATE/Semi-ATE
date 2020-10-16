from abc import ABC, abstractmethod


class IBinStrategy(ABC):
    @abstractmethod
    def get_binning_table(self, sbins=None):
        pass
