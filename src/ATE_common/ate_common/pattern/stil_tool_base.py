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

        # patterns could be assigned for multiple tests
        # retrieve all the patterns so they appear only once in the list
        compiled_pattern_list = list(set(compiled_patterns.values()))
        # make sure compiled patterns exists
        for compiled_pattern in compiled_pattern_list:
            if not Path(compiled_pattern).exists():
                raise Exception(f'pattern binary file: \'{compiled_pattern}\' is missing, make sure to compile all required pattern files')

        self._load_patterns_impl(compiled_pattern_list)

    @abstractmethod
    def _load_patterns_impl(self, compiled_patterns: list):
        pass

    def _get_pattern_name(self, pattern_virtual_name: str):
        if not self._compiled_patterns:
            raise Exception('no patterns are loaded')

        if not self._compiled_patterns.get(pattern_virtual_name):
            raise Exception(f'pattern: \'{pattern_virtual_name}\' is not loaded')

        return Path(self._compiled_patterns[pattern_virtual_name]).stem
