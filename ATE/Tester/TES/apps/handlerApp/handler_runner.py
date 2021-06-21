import asyncio
from ATE.Tester.TES.apps.handlerApp.handler_application import HandlerApplication
from ATE.Tester.TES.apps.handlerApp.handler_connection_handler import HandlerConnectionHandler
from ATE.Tester.TES.apps.handlerApp.handler_serial_com_handler import SerialCommunicationHandler
from ATE.Tester.TES.apps.handlerApp.statemachine.handler_statemachine import HandlerStateMachine
from ATE.common.logger import (Logger, LogLevel)


class HandlerRunner:
    def __init__(self, configuration, comm):
        self._mqtt = None
        self._log = Logger('handler', self._mqtt)
        loglevel = LogLevel.Warning() if configuration.get('loglevel') is None else configuration['loglevel']
        self._log.set_logger_level(loglevel)
        self.comm = comm
        self._serial_communication = None

        self._get_configuration(configuration)
        self._machine = HandlerStateMachine()

    def _get_configuration(self, configuration):
        try:
            self.handler_type = configuration['handler_type']
            self.handler_id = configuration['handler_id']
            self.device_ids = configuration['device_ids']
            self.broker = configuration['broker_host']
            self.broker_port = configuration['broker_port']
            self.site_layout = configuration['site_layout']
        except KeyError as e:
            self._log.log_message(LogLevel.Error(), f'Handler got invalid configuration: {e}')
            raise

    async def _run_task(self):
        self._app = HandlerApplication(self._machine, self.device_ids, self._log)
        event = asyncio.Event()
        self._serial_communication = SerialCommunicationHandler(self.comm, self._log, event, self.handler_type)
        self._connection_handler = HandlerConnectionHandler(self.broker,
                                                            self.broker_port,
                                                            self.handler_id,
                                                            self.device_ids,
                                                            self._log,
                                                            self._app,
                                                            event)

        self._machine.set_send_layout_callback(lambda: self._connection_handler.publish_head_layout(self.site_layout))
        self._machine.after_state_change(lambda message: self._connection_handler.publish_state(self._machine.model.state, message))
        self._serial_communication.start()
        self._connection_handler.start()
        try:
            while True:
                await event.wait()
                event.clear()
                self._handle_message_from_mqtt()
                self._handle_message_from_serial()
        except asyncio.CancelledError:
            await self._connection_handler.stop()
            await self._serial_communication.stop()
            raise

    def run(self):
        try:
            asyncio.run(self._run_task())
        except KeyboardInterrupt:
            pass

    def start(self):
        self.task = asyncio.create_task(self._run_task())

    async def stop(self):
        await self._serial_communication.stop()
        await self._connection_handler.stop()

    def _handle_message_from_serial(self):
        while(True):
            message = self._serial_communication.get_message()
            if not message:
                return

            self._connection_handler.handle_message(message)

    def _handle_message_from_mqtt(self):
        while(True):
            message = self._connection_handler.get_message()
            if not message:
                break

            self._serial_communication.handle_message(message)
