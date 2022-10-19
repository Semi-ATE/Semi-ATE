from ate_common.pattern.stil_tool_base import StilToolBase


class DummyStilTool(StilToolBase):
    def _load_patterns_impl(self, compiled_patterns: dict):
        print('the environment doesn\'t support loading patterns')
