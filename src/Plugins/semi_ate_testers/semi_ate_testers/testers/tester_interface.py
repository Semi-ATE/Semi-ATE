from abc import ABC, abstractmethod
from ate_common.logger import LogLevel


class TesterInterface(ABC):
    SITE_COUNT = -1
    
    def __init__(self, logger=None):
        self.logger = logger

    def get_sites_count(self):
        if self.SITE_COUNT == -1:
            raise Exception('make sure to override the static class variable `SITE_COUNT` with the correct site number supported by the tester inside the derived class')

        return self.SITE_COUNT

    @abstractmethod
    def do_request(self, site_id: int, timeout: int) -> bool:
        pass

    @abstractmethod
    def test_in_progress(self, site_id: int):
        pass

    @abstractmethod
    def test_done(self, site_id: int, timeout: int):
        self.log_info('tester.test_done() only dummy function')
        pass

    @abstractmethod
    def do_init_state(self, site_id: int):
        self.log_info('tester.do_init_state() only dummy function')
        pass

    def setup(self):
        self.log_info('tester.setup() only dummy function')
        pass

    def teardown(self):
        self.log_info('tester: teardown() only dummy function')
        pass

    def run_pattern(self, pattern_name: str, start_label: str = '', stop_label: str = '', timeout: int = 1000):
        pass

    def log_info(self, message: str):
        if self.logger is not None:
            self.logger.log_message(LogLevel.Info(), message)
        else:
            print(f'Info: {message}')

    def log_debug(self, message: str):
        if self.logger is not None:
            self.logger.log_message(LogLevel.Debug(), message)
        else:
            print(f'Debug: {message}')

    def log_warning(self, message: str):
        if self.logger is not None:
            self.logger.log_message(LogLevel.Warning(), message)
        else:
            print(f'Warning: {message}')

    def log_error(self, message: str):
        if self.logger is not None:
            self.logger.log_message(LogLevel.Error(), message)
        else:
            print(f'Error: {message}')

    def log_measure(self, message: str):
        if self.logger is not None:
            self.logger.log_message(LogLevel.Measure(), message)
        else:
            print(f'Measure: {message}')