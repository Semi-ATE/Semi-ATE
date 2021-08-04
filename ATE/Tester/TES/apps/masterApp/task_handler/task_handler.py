from aiohttp import web

import asyncio
import os
from enum import Enum

from ATE.Tester.TES.apps.masterApp.master_connection_handler import MasterConnectionHandler
from ATE.Tester.TES.apps.masterApp.master_webservice import webservice_setup_app


class TaskType(Enum):
    Websocket = 'websocket'
    Request = 'request'
    Mqtt = 'mqtt'

    def __call__(self):
        return self.value


class TaskHandler:
    def __init__(self, parent: object, configuration: dict, connection_handler: MasterConnectionHandler, request_callback: callable, websocket_callback: callable):
        self._connection_handler = connection_handler
        self._request_handler = request_callback
        self._websocket_handler = websocket_callback
        self._configuration = configuration
        self.parent = parent
        self.app = web.Application()
        self.app['master_app'] = self.parent

    @staticmethod
    def _create_task_callback(callback: callable) -> callable:
        async def task_ctx(app):
            task = asyncio.create_task(callback(app))

            yield

            task.cancel()
            await task

        return lambda app: task_ctx(app)

    @staticmethod
    def _run_task_callback(callback: callable) -> callable:
        async def task_ctx(app):
            callback.start()

            yield

            await callback.stop()

        return lambda app: task_ctx(app)

    def run(self):
        root_path_to_ui = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        import pathlib
        webui_static_path = os.path.join(root_path_to_ui, 'ui/angular/mini-sct-gui/')
        webui_static_path = pathlib.Path(webui_static_path)

        webservice_setup_app(self.app, str(webui_static_path))
        self.app.cleanup_ctx.append(self._run_task_callback(self._connection_handler))
        self.app.cleanup_ctx.append(self._create_task_callback(lambda app: self._websocket_handler(app)))
        self.app.cleanup_ctx.append(self._create_task_callback(lambda app: self._request_handler(app)))
        host = self._configuration.get('webui_host', 'localhost')
        port = self._configuration.get('webui_port', 8081)
        web.run_app(self.app, host=host, port=port)
