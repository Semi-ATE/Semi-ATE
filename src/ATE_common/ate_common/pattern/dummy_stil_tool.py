from ate_common.pattern.stil_tool_base import StilToolBase


class DummyStilTool(StilToolBase):
    def _load_patterns_impl(self, compiled_patterns: dict, sig2chan=None):
        print('Stil Tool not available, the environment doesn\'t support loading patterns')
        print('   There is an example on https://github.com/Semi-ATE/STIL showing how you can integrate a style parser.')
