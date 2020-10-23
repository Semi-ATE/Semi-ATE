from ATE.common.logger import LogLevel
import asyncio
from asyncio.queues import QueueEmpty, QueueFull
from ATE.Tester.TES.apps.handlerApp.handlers.geringer_PTO92UT import Geringer
from asyncio import Queue


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
        asyncio.run_coroutine_threadsafe(self._communicate(), asyncio.get_event_loop())

    def stop(self):
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
