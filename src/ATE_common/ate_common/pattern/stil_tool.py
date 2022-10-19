from ate_common.pattern.stil_tool_base import StilToolBase
from STIL_Tools.sc_loader import SLoader


OUTPUT_DIR = '/tmp/mem'


class StilTool(StilToolBase):
    def __init__(self):
        self._loader = SLoader()

    def _load_patterns_impl(self, compiled_patterns: list):
        self._loader.load(compiled_patterns, OUTPUT_DIR)
