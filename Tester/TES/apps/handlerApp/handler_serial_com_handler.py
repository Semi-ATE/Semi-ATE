import asyncio
from asyncio.queues import QueueEmpty, QueueFull
from asyncio import Queue
from ATE.Tester.TES.apps.handlerApp.handlers.geringer_PTO92UT import Geringer
from ATE.common.logger import LogLevel


def get_handler(handler_type, serial, log):
    if handler_type == 'geringer':
        return Geringer(serial, log)
    else:
        raise Exception(f'handler type: "{handler_type}" is not supported')


class SerialCommunicationHandler:
    def __init__(self, serial, log, event, handler_type):
        self._message_queue = Queue()
        self.serial = serial
        self._log = log
        self._event = event
        self._handler = get_handler(handler_type, self.serial, self._log)

    def start(self):
        self.task = asyncio.create_task(self._communicate())

    async def stop(self):
        self.task.cancel()
        try:
            await self.task
        except asyncio.CancelledError:
            pass

    async def _communicate(self):
        while True:
            command = await self._handler.read()
            if not command:
                continue

            try:
                self._message_queue.put_nowait(command)
                self._event.set()
            except QueueFull:
                self._log.log_message(LogLevel.Warning(), 'communication handler cannot handle commands any more, queue is full!')

    def get_message(self):
        try:
            return self._message_queue.get_nowait()
        except QueueEmpty:
            return None

    def handle_message(self, message):
        self._handler.handle_message(message)
