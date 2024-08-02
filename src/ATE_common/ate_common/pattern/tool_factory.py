import platform
from ate_common.pattern.stil_tool_base import StilToolBase


def get_stil_tool() -> StilToolBase:
    if "linux" in platform.system().lower() and "aarch64" in platform.machine().lower():
        from ate_common.pattern.stil_tool import StilTool
        return StilTool()
    elif "windows" in platform.system().lower():
        try:
            from ate_common.pattern.stil_tool import StilTool
            return StilTool()
        except Exception:
            from ate_common.pattern.dummy_stil_tool import DummyStilTool
            return DummyStilTool()
    else:
        from ate_common.pattern.dummy_stil_tool import DummyStilTool
        return DummyStilTool()
