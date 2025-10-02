from ate_common.pattern.stil_tool_base import StilToolBase


def get_stil_tool() -> StilToolBase:
    try:
        from ate_common.pattern.stil_tool import StilTool
        return StilTool()
    except Exception:
        from ate_common.pattern.dummy_stil_tool import DummyStilTool
        return DummyStilTool()
