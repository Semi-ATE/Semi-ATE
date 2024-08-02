from ate_common.pattern.stil_tool_base import StilToolBase
from stil_tools.sc_loader import SLoader

# stil tool use this path to do the loading work
OUTPUT_DIR = '/tmp/mem'


class StilTool(StilToolBase):
    def __init__(self):
        self._loader = SLoader()
        self.pattern_withpath = False if not hasattr(self._loader, 'pattern_withpath') else self._loader.pattern_withpath

    def _load_patterns_impl(self, compiled_patterns: list):
        self._loader.load(compiled_patterns, OUTPUT_DIR)
