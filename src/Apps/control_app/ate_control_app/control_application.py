""" control App """
from ate_control_app.control_connection_handler import ControlConnectionHandler
from ate_common.logger import LogLevel, Logger
import sys
import asyncio


def ensure_asyncio_event_loop_compatibility_for_windows():
    """
    WindowsSelectorEventLoopPolicy is required for
    asyncio.create_subprocess_exec or it will fail with
    NotImplementedError.
    """
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


class ControlApplication:

    """ ControlApplication """

    def __init__(self, configuration):
        self.site_id = configuration['site_id']
        self.device_id = configuration['device_id']
        self.broker_host = configuration["broker_host"]
        self.broker_port = configuration["broker_port"]
        self.configuration = configuration
        self.log = Logger(f'control {self.site_id}')
        self.log_level = LogLevel.Warning() if configuration.get('loglevel') is None else configuration['loglevel']
        self.log.set_logger_level(self.log_level)

    async def _run_task(self):
        self.connection_handler = ControlConnectionHandler(
            self.broker_host,
            self.broker_port,
            self.site_id,
            self.device_id,
            self.log)
        self.connection_handler.start()
        while True:
            await asyncio.sleep(1)

    def run(self):
        try:
            asyncio.run(self._run_task())
        except KeyboardInterrupt:
            pass
