import asyncio
from asyncio.queues import QueueFull
from ATE.Tester.TES.apps.handlerApp.handlers.geringer_PTO92UT import Geringer
from asyncio import Queue


def get_handler(handler_type, serial, log):
    if handler_type == 'geringer':
        return Geringer(serial, log)


class SerialCommunicationHandler:
    def __init__(self, serial, log):
        self.command_queue = Queue()
        self.serial = serial
        self._log = log
        self._handler = get_handler('geringer', self.serial, self._log)

    def start(self):
        asyncio.run_coroutine_threadsafe(self._communicate(), asyncio.get_event_loop())

    def stop(self):
        pass

    async def _communicate(self):
        while True:
            command = await self._handler.read()
            try:
                self.command_queue.put_nowait(command)
            except QueueFull:
                pass

    async def get_message(self):
        return await self.command_queue.get()
