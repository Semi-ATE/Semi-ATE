from ate_common.logger import LogLevel
from aiohttp import web, WSMsgType, WSCloseCode
from pathlib import Path
import json
import time
import os
from enum import Enum
import uuid


class MessageTypes(Enum):
    TestResult = 'testresult'
    Status = 'status'
    UserSettings = 'usersettings'
    TestResults = 'testresults'
    Logs = 'logs'
    Logfile = 'logfile'
    Yield = 'yield'
    LotData = 'lotdata'
    BinTable = 'bintable'
    Configuration = 'masterconfiguration'

    def __call__(self):
        return self.value


class WebsocketCommunicationHandler:
    def __init__(self, app):
        self._app = app
        self._websockets = set()
        self._log = app['master_app'].log

    def get_current_master_state(self):
        master_app = self._app['master_app']
        return master_app.external_state

    def get_broker_from_master_config(self):
        master_app = self._app['master_app']
        return (master_app.configuration.get('broker_host'),
                master_app.configuration.get('broker_port'))

    def get_mqtt_handler(self):
        return self._app['mqtt_handler']

    async def send_message_to_all(self, data):
        self._discard_ws_connection_if_needed()
        for ws in self._websockets:
            await ws.send_json(data)

    async def send_message_to_client(self, client_id, data):
        self._discard_ws_connection_if_needed()
        for ws in self._websockets:
            if ws.get_connection_id() == client_id:
                await ws.send_json(data)

    async def send_status_to_all(self, state, description):
        status_message = self._create_status_message(state, description)
        await self.send_message_to_all(status_message)

    async def send_configuration(self, configuration, client_ws):
        configuration_message = self._create_configuration_message(configuration)
        await self.send_message_to_client(client_ws.connection_id, configuration_message)

    async def send_testresults_to_all(self, site_test_result):
        await self.send_message_to_all(site_test_result)

    async def send_testresults_to_client(self, testresults, connection_id):
        testresults_message = self._create_testresults_message(testresults)
        await self.send_message_to_client(connection_id, testresults_message)

    async def send_logs_to_all(self, logs):
        logs_message = self._create_logs_message(logs)
        await self.send_message_to_all(logs_message)

    async def send_logs(self, logs, connection_id):
        logs_message = self._create_logs_message(logs)
        await self.send_message_to_client(connection_id, logs_message)

    async def send_logfile(self, logfile_info, connection_id):
        logs_message = self._create_logfile_message(logfile_info)
        await self.send_message_to_client(connection_id, logs_message)

    async def send_user_settings(self, usersettings):
        testresults_message = self._create_usersettings_message(usersettings)
        await self.send_message_to_all(testresults_message)

    async def send_yields(self, yields):
        yields_message = self._create_yield_message(yields)
        await self.send_message_to_all(yields_message)

    async def send_lotdata(self, lotdata):
        lotdata_message = self._create_lotdata_message(lotdata)
        await self.send_message_to_all(lotdata_message)

    async def send_bin_table(self, bin_table):
        yields_message = self._create_bin_table_message(bin_table)
        await self.send_message_to_all(yields_message)

    async def _send_connection_id_to_ws(self, ws, connection_id):
        connection_id_message = self._create_connection_id_message(connection_id)
        await ws.send_json(connection_id_message)

    def _create_connection_id_message(self, connection_id):
        payload = {"connectionid": connection_id}
        return self._create_message("connectionid", payload)

    @staticmethod
    def _create_message(type, payload):
        return {'type': type, 'payload': payload}

    def _create_testresults_message(self, testresults):
        return self._create_message(MessageTypes.TestResults(), testresults)

    def _create_logs_message(self, logs):
        return self._create_message(MessageTypes.Logs(), logs)

    def _create_logfile_message(self, logfile_info):
        return self._create_message(MessageTypes.Logfile(), logfile_info)

    def _create_usersettings_message(self, user_settings):
        return self._create_message(MessageTypes.UserSettings(), user_settings)

    def _create_yield_message(self, yields):
        return self._create_message(MessageTypes.Yield(), yields)

    def _create_bin_table_message(self, bin_table: list):
        return self._create_message(MessageTypes.BinTable(), bin_table)

    def _create_lotdata_message(self, lotdata):
        return self._create_message(MessageTypes.LotData(), lotdata)

    def _create_status_message(self, state, error_message):
        payload = {'device_id': self._app['master_app'].device_id,
                   'systemTime': time.strftime("%b %d %Y %H:%M:%S"),
                   'sites': self._app['master_app'].configuredSites,
                   'state': state,
                   'error_message': error_message,
                   'env': self._app['master_app'].env,
                   'lot_number': self._app['master_app'].loaded_lot_number}

        return self._create_message(MessageTypes.Status(), payload)

    def _create_configuration_message(self, configuration):
        payload = {'broker_host': configuration['broker_host'],
                   'broker_port': configuration['broker_port'],
                   'device_id': self._app['master_app'].device_id,
                   'sites': self._app['master_app'].configuredSites,
                   'handler': configuration['Handler'],
                   'environment': configuration['environment'],
                   'jobsource': configuration['jobsource'],
                   'jobformat': configuration['jobformat'],
                   }

        return self._create_message(MessageTypes.Configuration(), payload)

    async def close_all(self):
        for ws in set(self._websockets):
            await ws.close(code=WSCloseCode.GOING_AWAY,
                           message='Server shutdown')

    async def receive(self, request):
        ws = web.WebSocketResponse(heartbeat=1.0)
        await ws.prepare(request)

        connection_id = str(uuid.uuid1())
        ws_connection = WebSocketConnection(ws, connection_id)
        self._websockets.add(ws_connection)

        await self._send_connection_id_to_ws(ws, connection_id)

        # master should propagate the available settings each time a page reloaded
        # or new websocket connection is required
        self.handle_new_connection(connection_id)
        await self.send_configuration(self._app['master_app'].configuration, ws_connection)

        self._log.log_message(LogLevel.Debug(), 'websocket connection opened.')

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    self.handle_client_message(msg.data)
                elif msg.type == WSMsgType.ERROR:
                    self._log.log_message(LogLevel.Error(), f'ws connection closed with exception: {ws.exception()}')
        finally:
            pass

        self._discard_ws_connection_if_needed()

    def _discard_ws_connection_if_needed(self):
        self._websockets = set([ws for ws in self._websockets if ws.is_alive()])

    def handle_new_connection(self, connection_id):
        self._app['master_app'].on_new_connection(connection_id)

    def handle_client_message(self, message_data: str):
        json_data = json.loads(message_data)
        self._log.log_message(LogLevel.Debug(), f'Server received message {json_data}')

        if json_data.get('type') == 'cmd':
            self._app["master_app"].dispatch_command(json_data)

    def is_ws_connection_established(self):
        return len(self._websockets) > 0


async def index_handler(request):
    static_file_path = request.app['static_file_path']
    return web.FileResponse(os.path.join(static_file_path, 'index.html'))


async def webservice_init(app):
    static_file_path = app['static_file_path']
    ws_comm_handler = WebsocketCommunicationHandler(app)
    if Path(static_file_path, 'index.html').exists() == False:
        async def index(request: web.Request) -> web.Response:
            text = '''
            Please configure the JSON-key "webui_root_path" in file "master_config_file.json" in such a way
            that it points to a web-root folder, i.e. a folder containing some index.html and restart the
            master application.        
            '''
            return web.Response(text=text)
        global index_handler
        index_handler = index
    app.add_routes([web.get('/', index_handler),
                    web.get('/information', index_handler),
                    web.get('/control', index_handler),
                    web.get('/records', index_handler),
                    web.get('/logging', index_handler),
                    web.get('/bin', index_handler),
                    web.get('/ws', ws_comm_handler.receive)])
    # From the aiohttp documentation it is known to use
    # add_static only when developing things
    # normally static content should be processed by
    # webservers like (nginx or apache)
    # In the case of Single Tester it is okay to use add_static
    app.router.add_static('/', path=static_file_path, name='static')
    app['ws_comm_handler'] = ws_comm_handler


async def webservice_cleanup(app):
    ws_comm_handler = app['ws_comm_handler']
    if ws_comm_handler is not None:
        await ws_comm_handler.close_all()
        app['ws_comm_handler'] = None


def webservice_setup_app(app: web.Application, static_file_path: str):
    if not os.path.isdir(static_file_path):
        raise ValueError(f'static_file_path is not an existing directory: {static_file_path}')
    
    app['static_file_path'] = static_file_path
    app.on_startup.append(webservice_init)
    app.on_cleanup.append(webservice_cleanup)


class WebSocketConnection:
    def __init__(self, ws_connection, connection_id):
        self.ws_connection = ws_connection
        self.connection_id = connection_id

    def is_alive(self):
        return not (self.ws_connection.closed or self.ws_connection.close_code is not None)

    def close(self, code, message):
        self.ws_connection.close(code=code, message=message)

    def get_connection_id(self):
        return self.connection_id

    async def send_json(self, data):
        await self.ws_connection.send_json(data)
