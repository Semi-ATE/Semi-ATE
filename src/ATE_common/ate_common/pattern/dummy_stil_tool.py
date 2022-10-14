from ate_common.pattern.stil_tool_base import StilToolBase


class DummyStilTool(StilToolBase):
    def load_pattern(self, compiled_patterns: dict):
        print('the environment doesn\'t support loading pattern')

    def run_pattern(self, pattern_name: str):
        print('the environment doesn\'t support running pattern')
