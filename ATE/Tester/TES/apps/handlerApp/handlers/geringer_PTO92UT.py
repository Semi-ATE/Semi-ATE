import asyncio
from enum import Enum
from ATE.common.logger import LogLevel
from ATE.Tester.TES.apps.handlerApp.handler_base import HandlerBase


MAX_ERROR_COUNT = 3


class TesterStateTypes(Enum):
    Busy = '3'
    Lot = '2'
    Init = '1'
    Ok = '0'
    Err = '-1'
    NotImplemented = '-99'
    InvalidLot = '-98'
    NoLot = '-68'
    HaveLot = '-67'
    UndefinedErr = '-64'

    def __call__(self):
        return self.value


AVAILABLE_STATUS = {'-99': 'command not implemented',
                    '-64': 'unrecoverable error',
                    '-10': 'checksum error',
                    '-1': 'error',
                    '1': 'busy',
                    '0': 'ok'}

RESPONSE_MESSAGE = {'notlot': (TesterStateTypes.NoLot(), 'No Lot was Started'),
                    'havelot': (TesterStateTypes.Lot(), 'Lot is Already Active'),
                    'busy': (TesterStateTypes.Busy(), 'Busy Testing'),
                    'error': (TesterStateTypes.Err(), 'Error'),
                    'ok': (TesterStateTypes.Ok(), 'OK'),
                    'lot': (TesterStateTypes.Lot(), 'Lot is Loaded, Test start is awaited')}


class Geringer(HandlerBase):
    def __init__(self, serial, log):
        super().__init__(log)
        self.serial = serial
        self.error_count = 0
        self._error = None
        self._is_command_received = False
        self.command = []

    async def read(self):
        await asyncio.sleep(0.0)
        message = self.serial.readline()

        return self._dispatch_message(message.decode('ASCII').rstrip())

    def write(self, message):
        self.serial.write(self._add_checksum_to_message(message).encode('ASCII'))
        self.serial.write(b'\n')
        self.serial.flush()

    def _add_checksum_to_message(self, message):
        check_sum = self._calculate_checksum(message)
        check_sum = str(check_sum).zfill(3)
        return f"{message}{check_sum}"

    @staticmethod
    def _calculate_checksum(message):
        return sum([ord(char) for char in str(message)]) & 0xff

    def _dispatch_message(self, message):
        if not message:
            return None

        data_splits = message.split('|')
        header_type = data_splits[0]
        if len(data_splits) <= 1:
            self._log.log_message(LogLevel.Warning(), 'message is not valid')
            return None

        success = self._is_message_valid(message, header_type)

        if not success:
            self.error_count += 1

            if self.error_count == MAX_ERROR_COUNT:
                raise Exception('max error count is reached')

            self._log.log_message(LogLevel.Warning(), f'message: "{message}" could not be parsed')

            return None

        self.error_count = 0
        if self._is_command(header_type):
            return self._dispatch_command(data_splits)
        else:
            return self._dispatch_response(data_splits)

    def _is_message_valid(self, message, header_type):
        if not self._is_check_sum_valid(message):
            self._error = ''
            return False

        if (not self._is_command(header_type) and not self._is_response(header_type)):
            self._error = ''
            return False

        return True

    def _is_check_sum_valid(self, message):
        message_limit = message.rfind('|') + 1
        message_without_checksum = message[:message_limit]
        message_checksum = message[message_limit:len(message)]

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

            self.command.append(message['type'])
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
        return {'type': 'load',
                'payload': {'lot_number': data[1],
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
                sites.append({'siteid': str(site_num),
                              'partid': str(data[start_index]),
                              'binning': int(data[start_index + 1]),
                              'logflag': int(data[start_index + 2]),
                              'additionalinfo': data[start_index + 3]})

            start_index += 5
            is_site_enabled_index += 5

        return sites

    @staticmethod
    def _lot_end():
        return {'type': 'unload',
                'payload': {}}

    @staticmethod
    def _get_tester_name():
        return {'type': 'identify',
                'payload': {}}

    @staticmethod
    def _get_tester_state():
        return {'type': 'get-state',
                'payload': {}}

    @staticmethod
    def _handle_temperature(data):
        return {'type': 'temperature',
                'payload': {'temperature': float(data[1])}}

    @staticmethod
    def _handle_state(data):
        try:
            status_info = AVAILABLE_STATUS[data[1]]
        except KeyError:
            status_info = 'no status available'

        return {'type': 'state',
                'payload': {'state': int(data[1]),
                            'message': status_info}}

    @staticmethod
    def _handle_name(data):
        return {'type': 'identify',
                'payload': {'name': data[1]}}

    def _generate_error_message(self, message):
        try:
            command_index = self.command.index(message['command_type'])
            self.command.pop(command_index)
            msg = RESPONSE_MESSAGE[message['response_type']]

            if message['message']:
                msg = (TesterStateTypes.Err(), message['message'])
        except KeyError:
            msg = RESPONSE_MESSAGE['error']
        except ValueError:
            return

        return self._generate_status_message_response(msg[0], msg[1])

    def _generate_status_response(self, message):
        if not self.command:
            return

        msg = None
        state = message['state']

        command_index = -1
        if state == 'softerror':
            msg = RESPONSE_MESSAGE['error']

        if 'load' in self.command and state == 'ready':
            command_index = self.command.index('load')
            msg = RESPONSE_MESSAGE['lot']
        if 'unload' in self.command and state == 'initialized':
            command_index = self.command.index('unload')
            msg = RESPONSE_MESSAGE['ok']
        if 'next' in self.command and state in ('testing', 'ready'):
            # response need some time
            return None

        if not msg:
            return None

        self.command.pop(command_index)
        return self._generate_status_message_response(msg[0], msg[1])

    @staticmethod
    def _generate_status_message_response(state, message):
        return f'TS|{state}|{message}|'

    def _generate_tester_status_response(self, message):
        msg = RESPONSE_MESSAGE['ok']

        if message['payload']['state'] == 'softerror':
            msg = TesterStateTypes.Err(), message['message']

        return f'TS|{msg[0]}|{msg[1]}|'

    def _generate_end_test_response(self, message):
        sites = message['payload']['sites']
        response_message = f'ET|{len(sites)}|'
        for site in sites:
            response_message += f'{site["partid"]}|{site["binning"]}|{site["logflag"]}|{site["additionalinfo"]}|'

        self.command.pop(self.command.index(message['type']))
        return response_message

    def _generate_test_name_response(self, message):
        if message['type'] not in self.command:
            return None

        self.command.pop(self.command.index(message['type']))
        name = message['payload']['name']
        return f'ID|{name}|'

    @staticmethod
    def _generate_get_handler_name_command():
        return 'ID?|'

    @staticmethod
    def _generate_get_handler_state_command():
        return 'HS?|'
