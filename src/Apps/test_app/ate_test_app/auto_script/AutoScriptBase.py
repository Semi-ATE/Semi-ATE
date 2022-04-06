from abc import ABC, abstractmethod
from ate_common.logger import Logger


class AutoScriptBase(ABC):
    @abstractmethod
    def after_cycle_teardown(self):
        pass

    @abstractmethod
    def after_terminate_teardown(self):
        pass

    @abstractmethod
    def after_exception_teardown(self, source: str, exception: Exception):
        pass

    def set_logger(self, logger: Logger):
        self.logger = logger

    def set_context(self, context: object):
        self.context = context
