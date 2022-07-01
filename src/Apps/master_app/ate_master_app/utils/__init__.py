from dataclasses import dataclass


@dataclass
class ControlState:
    Unknown = "unknown"
    Loading = "loading"
    Busy = "busy"
    Idle = "idle"
    Crash = "crash"


@dataclass
class TestState:
    Idle = "idle"
    Testing = "testing"
    Crash = "crash"
    Terminated = "terminated"

