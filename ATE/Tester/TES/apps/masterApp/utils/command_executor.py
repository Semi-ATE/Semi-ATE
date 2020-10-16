import threading


class NonBlockingCall(threading.Thread):
    def __init__(self, callback):
        super().__init__(target=callback)
        self.start()


class NonBlockingCommand:
    def __init__(self, connection_id, obj):
        self._is_ready = False
        self.connection_id = connection_id
        NonBlockingCall(lambda: self.acquire_data(obj))

    def acquire_data(self, obj):
        self.acquire_data_impl(obj)
        self._is_ready = True

    def is_data_ready(self):
        return self._is_ready

    async def execute(self, ws_conn_handler):
        raise Exception("Implement me")

    def acquire_data_impl(self, data):
        raise Exception("Implement me")


class GetLogFileCommand(NonBlockingCommand):
    async def execute(self, ws_comm_handler):
        await ws_comm_handler.send_logfile(self._reply, self.connection_id)

    def acquire_data_impl(self, obj):
        self._reply = obj.get_log_file_information()


class GetTestResultsCommand(NonBlockingCommand):
    async def execute(self, ws_comm_handler):
        await ws_comm_handler.send_testresults_to_client(self._reply, self.connection_id)

    def acquire_data_impl(self, data):
        self._reply = list(data.get_data())


class GetLogsCommand(NonBlockingCommand):
    async def execute(self, ws_comm_handler):
        await ws_comm_handler.send_logs(self._reply, self.connection_id)

    def acquire_data_impl(self, data):
        self._reply = data.get_logs()
