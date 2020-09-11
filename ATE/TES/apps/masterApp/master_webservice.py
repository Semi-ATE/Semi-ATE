from aiohttp import web, WSMsgType, WSCloseCode
import json
import time
import os
import weakref
from enum import Enum


class MessageTypes(Enum):
    TestResult = 'testresult'
    Status = 'status'
    UserSettings = 'usersettings'
    TestResults = 'testresults'
    Logs = 'logs'
    Logfile = 'logfile'

    def __call__(self):
        return self.value


class WebsocketCommunicationHandler:
    def __init__(self, app):
        self._app = app
        self._websockets = weakref.WeakSet()
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
        for ws in set(self._websockets):
            await ws.send_json(data)

    async def send_status_to_all(self, state, description):
        status_message = self._create_status_message(state, description)
        await self.send_message_to_all(status_message)

    async def send_testresults_to_all(self, site_test_result):
        await self.send_message_to_all(site_test_result)

    async def send_testresults_from_all_site(self, testresults):
        testresults_message = self._create_testresults_message(testresults)
        await self.send_message_to_all(testresults_message)

    async def send_logs(self, logs):
        logs_message = self._create_logs_message(logs)
        await self.send_message_to_all(logs_message)

    async def send_logfile(self, logfile_info):
        logs_message = self._create_logfile_message(logfile_info)
        await self.send_message_to_all(logs_message)

    async def send_user_settings(self, usersettings):
        testresults_message = self._create_usersettings_message(usersettings)
        await self.send_message_to_all(testresults_message)

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

    def _create_status_message(self, state, error_message):
        payload = {'device_id': self._app['master_app'].device_id,
                   'systemTime': time.strftime("%b %d %Y %H:%M:%S"),
                   'sites': self._app['master_app'].configuredSites,
                   'state': state,
                   'error_message': error_message,
                   'env': self._app['master_app'].env,
                   'lot_number': self._app['master_app'].loaded_lot_number}

        return self._create_message(MessageTypes.Status(), payload)

    async def close_all(self):
        for ws in set(self._websockets):
            await ws.close(code=WSCloseCode.GOING_AWAY,
                           message='Server shutdown')

    async def receive(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        # master should propagate the available settings each time a page reloaded
        # or new websocket connection is required
        self.handle_new_connection()
        self._log.log_message('debug', 'websocket connection opened.')

        self._websockets.add(ws)
        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    response_message = self.handle_client_message(msg.data)
                    if response_message:
                        await ws.send_json(response_message)
                elif msg.type == WSMsgType.ERROR:
                    self._log.log_message('error', f'ws connection closed with exception: {ws.exception()}')
        finally:
            self._websockets.discard(ws)

        self._log.log_message('debug', 'websocket connection closed.')

    def handle_new_connection(self):
        self._app['master_app'].on_new_connection()

    def handle_client_message(self, message_data: str):
        json_data = json.loads(message_data)
        self._log.log_message('debug', f'Server received message {json_data}')

        if json_data.get('type') == 'cmd':
            self._app["master_app"].dispatch_command(json_data)


async def index_handler(request):
    static_file_path = request.app['static_file_path']
    return web.FileResponse(os.path.join(static_file_path, 'index.html'))


async def webservice_init(app):
    static_file_path = app['static_file_path']
    ws_comm_handler = WebsocketCommunicationHandler(app)
    app.add_routes([web.get('/', index_handler),
                    web.get('/information', index_handler),
                    web.get('/control', index_handler),
                    web.get('/results', index_handler),
                    web.get('/logging', index_handler),
                    web.get('/ws', ws_comm_handler.receive)])
    # From the aiohttp documentation it is known to use
    # add_static only when developing things
    # normally static content should be processed by
    # webservers like (nginx or apache)
    # In the case of MiniSCT it is okay to use add_static
    app.router.add_static('/', path=static_file_path, name='static')
    app['ws_comm_handler'] = ws_comm_handler


async def webservice_cleanup(app):
    ws_comm_handler = app['ws_comm_handler']
    if ws_comm_handler is not None:
        await ws_comm_handler.close_all()
        app['ws_comm_handler'] = None


def webservice_setup_app(app, static_file_path):
    if not os.path.isdir(static_file_path):
        raise ValueError(f'static_file_path is not an existing directory: {static_file_path}')
    app['static_file_path'] = static_file_path
    app.on_startup.append(webservice_init)
    app.on_cleanup.append(webservice_cleanup)
