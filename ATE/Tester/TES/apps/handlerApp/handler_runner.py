import asyncio
import serial
from ATE.Tester.TES.apps.handlerApp.handler_application import HandlerApplication
from ATE.Tester.TES.apps.handlerApp.handler_connection_handler import HandlerConnectionHandler
from ATE.Tester.TES.apps.handlerApp.handler_statemachine import HandlerStateMachine
from ATE.Tester.TES.apps.handlerApp.handler_serial_com_handler import SerialCommunicationHandler
from ATE.common.logger import (Logger, LogLevel)


class HandlerRunner:
    def __init__(self, configuration, args):
        self._log = Logger('handler', None)
        loglevel = LogLevel.Warning() if configuration.get('loglevel') is None else configuration['loglevel']
        self._log.set_logger_level(loglevel)
        self._get_configuration(configuration)
        self.args = args

        self._machine = HandlerStateMachine()
        self._app = HandlerApplication(self._machine)
        self._connection_handler = HandlerConnectionHandler(self.broker,
                                                            self.broker_port,
                                                            self.handler_id,
                                                            self.device_ids,
                                                            self._log,
                                                            self._app)

    def _get_configuration(self, configuration):
        try:
            self.handler_id = configuration['handler_id']
            self.device_ids = configuration['device_ids']
            self.broker = configuration['broker_host']
            self.broker_port = configuration['broker_port']
        except KeyError as e:
            self._log.log_message(LogLevel.Error(), f'Handler got invalid configuration: {e}')
            raise

    async def _run_task(self):
        self._machine.after_state_change(lambda: self._connection_handler.publish_state(self._machine.model.state, ''))
        self._serial_communication = SerialCommunicationHandler(self._generate_serial_object(self.args), self._log)
        self._serial_communication.start()
        self._connection_handler.start()
        try:
            while True:
                command = await self._serial_communication.get_message()
                if command:
                    self._handle_command(command)
        except asyncio.CancelledError:
            await self._connection_handler.stop()
            self._serial_communication.stop()

    def _generate_serial_object(self, args):
        return serial.Serial(args.port, baudrate=args.baudrate, bytesize=args.bytesize,
                             parity=args.parity, stopbits=args.stopbits, timeout=args.timeout)

    def run(self):
        try:
            asyncio.run(self._run_task())
        except KeyboardInterrupt:
            pass

    def _handle_command(self, command):
        pass
