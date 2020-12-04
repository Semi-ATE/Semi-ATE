from enum import Enum


class TheTestAppStatusAlive(Enum):
    DEAD = 0      # error/crash
    ALIVE = 1
    SHUTDOWN = 2  # graceful shutdown
    INITFAIL = 3  # init failed
