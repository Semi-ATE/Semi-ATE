from ate_master_app.master_webservice import WebSocketConnection, WebsocketCommunicationHandler
import threading


class NonBlockingCall(threading.Thread):
    def __init__(self, callback):
        super().__init__(target=callback)
        self.start()


class NonBlockingCommand:
    def __init__(self, obj, connection_id=None):
        self._is_ready = False
        self.connection_id = connection_id
        self._reply = None
        NonBlockingCall(lambda: self.acquire_data(obj))

    def acquire_data(self, obj):
        self.acquire_data_impl(obj)
        self._is_ready = True

    def is_data_ready(self):
        return self._is_ready

    async def execute(self, ws_conn_handler: WebSocketConnection):
        if not self._reply:
            # skip executing if rely not read yet
            return

        await self.execute_impl(ws_conn_handler)

    async def execute_impl(self, ws_conn_handler: WebSocketConnection):
        raise Exception("Implement me")

    def acquire_data_impl(self, data):
        raise Exception("Implement me")


class GetLogFileCommand(NonBlockingCommand):
    async def execute_impl(self, ws_comm_handler):
        await ws_comm_handler.send_logfile(self._reply, self.connection_id)

    def acquire_data_impl(self, obj):
        self._reply = obj.get_log_file_information()


class GetTestResultsCommand(NonBlockingCommand):
    async def execute_impl(self, ws_comm_handler):
        await ws_comm_handler.send_testresults_to_client(self._reply, self.connection_id)

    def acquire_data_impl(self, data):
        self._reply = list(data.get_data())


class GetLogsCommand(NonBlockingCommand):
    async def execute_impl(self, ws_comm_handler):
        await ws_comm_handler.send_logs(self._reply, self.connection_id)

    def acquire_data_impl(self, data):
        self._reply = data.get_logs()


class GetUserSettings(NonBlockingCommand):
    async def execute_impl(self, ws_comm_handler):
        await ws_comm_handler.send_user_settings(self._reply)

    def acquire_data_impl(self, get_user_settings_call_back):
        self._reply = get_user_settings_call_back()


class GetYields(NonBlockingCommand):
    async def execute_impl(self, ws_comm_handler):
        await ws_comm_handler.send_yields(self._reply)

    def acquire_data_impl(self, get_yield_call_back):
        self._reply = get_yield_call_back()


class GetLotData(NonBlockingCommand):
    async def execute_impl(self, ws_comm_handler: WebsocketCommunicationHandler):
        await ws_comm_handler.send_lotdata(self._reply)

    def acquire_data_impl(self, get_lotdata_call_back: callable):
        self._reply = get_lotdata_call_back()


class GetBinTable(NonBlockingCommand):
    async def execute_impl(self, ws_comm_handler: WebsocketCommunicationHandler):
        await ws_comm_handler.send_bin_table(self._reply)

    def acquire_data_impl(self, get_lotdata_call_back: callable):
        self._reply = get_lotdata_call_back()
