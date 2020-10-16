from ATE.common.logger import LogLevel
from abc import ABC, abstractmethod
import asyncio


MAX_ERROR_COUNT = 3
AVAILABE_STATUS = {'-99': 'command not implemented',
                   '-64': 'unrecoverable error',
                   '-10': 'checksum error',
                   '-1': 'error',
                   '1': 'busy',
                   '0': 'ok'}


class ICommunication(ABC):
    @abstractmethod
    async def read(self):
        pass

    @abstractmethod
    def write(self, message):
        pass


class Geringer(ICommunication):
    def __init__(self, serial, log):
        super().__init__()
        self.serial = serial
        self._log = log
        self.error_count = 0

    async def read(self):
        await asyncio.sleep(0.0)
        message = self.serial.read()
        return self._dispatch_message(message.decode('ASCII').rstrip())

    def write(self, message):
        self.serial.write(self._add_checksum_to_message(message).encode('ASCII'))
        self.serial.write(b'\n')
        self.serial.flush()

    def _add_checksum_to_message(self, message):
        check_sum = self._calculate_checksum(message)
        check_sum = str(check_sum).zfill(3)
        return f"{message}|{check_sum}"

    @staticmethod
    def _calculate_checksum(message):
        return sum([ord(char) for char in str(message)]) & 0xff

    def _dispatch_message(self, message):
        if not message:
            return None

        data_splits = message.split('|')
        if len(data_splits) <= 1:
            self._log.log_message(LogLevel.Warning(), 'message is not valid')
            return None

        header_type = data_splits[0]

        if not self._is_check_sum_valid(message) \
           or (not self._is_command(header_type) and not self._is_response(header_type)):
            self.error_count += 1

            if self.error_count == MAX_ERROR_COUNT:
                raise Exception('max error count is reached')

            return None

        self.error_count = 0
        if self._is_command(header_type):
            return self._dispatch_command(data_splits)
        else:
            return self._dispatch_response(data_splits)

    def _is_check_sum_valid(self, message):
        message_without_checksum = message[:len(message) - 3]
        message_checksum = message[-3:]

        checksum = self._calculate_checksum(message_without_checksum)
        return checksum == int(message_checksum)

    @staticmethod
    def _is_command(header_tpye):
        return header_tpye in ['LL', 'ST', 'LE', 'ID?', 'TS?']

    @staticmethod
    def _is_response(header_tpye):
        return header_tpye in ['TE', 'HS', 'ID']

    def _dispatch_command(self, data):
        try:
            message = {'LL': lambda: self._load_lot(data),
                       'ST': lambda: self._start_test(data),
                       'LE': lambda: self._lot_end(),
                       'ID?': lambda: self._get_tester_name(),
                       'TS?': lambda: self._get_tester_state(),
                       }[data[0]]()
            return message
        except KeyError:
            raise Exception('command is not supported')

    def _dispatch_response(self, data):
        try:
            response = {'TE': lambda: self._handle_temperature(data),
                        'HS': lambda: self._handle_state(data),
                        'ID': lambda: self._handle_name(data)
                        }[data[0]]()

            return response
        except KeyError:
            raise Exception('response is not supported')

    @staticmethod
    def _load_lot(data):
        return {'type': 'load_lot',
                'payload': {'lotnumber': data[1],
                            'devicetype': data[2],
                            'temperature': data[3]}}

    def _start_test(self, data):
        sites = self._extract_sites_information(data)
        return {'type': 'next',
                'payload': {'sites': sites}}

    @staticmethod
    def _extract_sites_information(data):
        sites = []
        num_sites = int(data[1])
        start_index = 3
        is_site_enabled_index = 2
        for site_num in range(num_sites):
            if data[is_site_enabled_index] == '1':
                sites.append({'siteid': site_num,
                              'deviceid': int(data[start_index]),
                              'binning': int(data[start_index + 1]),
                              'logflag': data[start_index + 2],
                              'additionalinfo': int(data[start_index + 3])})

            start_index += 5
            is_site_enabled_index += 5

        return sites

    @staticmethod
    def _lot_end():
        return {'type': 'terminate',
                'payload': {}}

    @staticmethod
    def _get_tester_name():
        return {'type': 'identify',
                'payload': {}}

    @staticmethod
    def _get_tester_state():
        return {'type': 'get_state',
                'payload': {}}

    @staticmethod
    def _handle_temperature(data):
        return {'type': 'temperature',
                'payload': {'temperature': float(data[1])}}

    @staticmethod
    def _handle_state(data):
        try:
            status_info = AVAILABE_STATUS[data[1]]
        except KeyError:
            status_info = 'no status available'

        return {'type': 'state',
                'payload': {'state': int(data[1]),
                            'message': status_info}}

    @staticmethod
    def _handle_name(data):
        return {'type': 'name',
                'payload': {'name': data[1]}}
