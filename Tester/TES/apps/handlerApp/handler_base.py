from abc import ABC, abstractmethod
from ATE.common.logger import LogLevel


class HandlerBase(ABC):
    def __init__(self, log):
        self._log = log

    @abstractmethod
    async def read(self):
        pass

    @abstractmethod
    def write(self, message):
        pass

    def _generate_command_from_message(self, message):
        try:
            command = {'identify': lambda: self._generate_get_handler_name_command(),
                       'get-state': lambda: self._generate_get_handler_state_command()
                       }[message['type']]()
            return command
        except KeyError:
            self._log.log_message(LogLevel.Warning(), f'master command type could not be recognized: {message["type"]}')
            return None

    def _generate_response_from_message(self, message):
        try:
            response = {'status': lambda: self._generate_status_response(message),  # TODO: define a share state interface between handle and master
                        'identify': lambda: self._generate_test_name_response(message),
                        'next': lambda: self._generate_end_test_response(message),
                        'get-state': lambda: self._generate_tester_status_response(message),
                        'error': lambda: self._generate_error_message(message)
                        }[message['type']]()
            return response
        except KeyError:
            self._log.log_message(LogLevel.Warning(), f'master response type could not be recognized: {message["type"]}"')

    def handle_message(self, message):
        if message['type'] in ('identify', 'get-state') and \
           not message['payload']:
            msg = self._generate_command_from_message(message)
        else:
            msg = self._generate_response_from_message(message)

        if not msg:
            return

        self.write(msg)

    @abstractmethod
    def _generate_get_handler_name_command() -> str:
        pass

    @abstractmethod
    def _generate_get_handler_state_command() -> str:
        pass

    @abstractmethod
    def _generate_status_response() -> str:
        pass

    @abstractmethod
    def _generate_test_name_response() -> str:
        pass

    @abstractmethod
    def _generate_end_test_response() -> str:
        pass

    @abstractmethod
    def _generate_tester_status_response() -> str:
        pass

    @abstractmethod
    def _generate_error_message() -> str:
        pass
