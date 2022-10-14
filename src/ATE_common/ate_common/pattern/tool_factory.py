import platform
from ate_common.pattern.stil_tool_base import StilToolBase


def get_stil_tool() -> StilToolBase:
    if "linux" in platform.system().lower() and "aarch64" in platform.machine().lower():
        from ate_common.pattern.stil_tool import StilTool
        return StilTool()
    else:
        from ate_common.pattern.dummy_stil_tool import DummyStilTool
        return DummyStilTool()
