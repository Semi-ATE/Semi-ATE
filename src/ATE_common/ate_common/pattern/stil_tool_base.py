from typing import Any
from abc import ABC, abstractmethod


class StilToolBase(ABC):
    @abstractmethod
    def _load_patterns(self, compiled_patterns: dict):
        pass

    @abstractmethod
    def run_pattern(self, pattern_name: str):
        pass
