from pathlib import Path
from abc import ABC, abstractmethod


class StilToolBase(ABC):
    def __init__(self):
        self._compiled_patterns = None

    def _load_patterns(self, compiled_patterns: dict):
        self._compiled_patterns = compiled_patterns

        if not self._compiled_patterns:
            print('-------- there is no pattern to load ---------')
            return

        self._load_patterns_impl(compiled_patterns)

    @abstractmethod
    def _load_patterns_impl(self, compiled_patterns: dict):
        pass

    def _get_pattern_name(self, pattern_virtual_name: str):
        if not self._compiled_patterns:
            raise Exception('no patterns are loaded')

        if not self._compiled_patterns.get(pattern_virtual_name):
            raise Exception(f'pattern: \'{pattern_virtual_name}\' is not loaded')

        return Path(self._compiled_patterns[pattern_virtual_name]).stem
