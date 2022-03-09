from asyncio.queues import Queue, QueueEmpty, QueueFull


class DummySerialGeringer:
    port = ""

    def __init__(self):
        self._message_queue = Queue()
        self._site_num = None

    def put(self, command, site_num=None):
        try:
            self._site_num = site_num
            self._message_queue.put_nowait(self._generate_command_message(command))
        except QueueFull:
            raise Exception('message queue is full')

    def _generate_command_message(self, command):
        try:
            return {'load': lambda: self._generate_load_command(),
                    'next': lambda: self._generate_next_command(),
                    'unload': lambda: self._generate_unload_command(),
                    'identify': lambda: self._generate_identify_command(),
                    'get-state': lambda: self._generate_get_state_command(),
                    'temperature': lambda: self._generate_temperature_response()}[command]()
        except KeyError:
            raise Exception('command is not supported')

    @staticmethod
    def _generate_load_command():
        return b'LL|306426.001|814A|120|237\n'

    def _generate_next_command(self):
        assert self._site_num
        check_sum = 152 + self._site_num

        message = f'ST|0{self._site_num}|1|12345|-01|002|000|1|12346|-01|002|000|{check_sum}\n'
        return message.encode('ASCII')

    @staticmethod
    def _generate_unload_command():
        return b'LE|13\n'

    @staticmethod
    def _generate_identify_command():
        return b'ID?|72\n'

    @staticmethod
    def _generate_get_state_command():
        return b'TS?|98\n'

    @staticmethod
    def _generate_temperature_response():
        return b'TE|169.5|148\n'

    def readline(self):
        try:
            return self._message_queue.get_nowait()
        except QueueEmpty:
            return b''

    def write(self, message):
        pass

    def flush(self):
        pass
