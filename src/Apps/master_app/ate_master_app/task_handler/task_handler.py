from aiohttp import web
import asyncio
from enum import Enum
from ate_master_app.master_connection_handler import MasterConnectionHandler
from ate_master_app.master_webservice import webservice_setup_app

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
        web_root_path = self._configuration.get('webui_root_path')
        webservice_setup_app(self.app, web_root_path)
        self.app.cleanup_ctx.append(self._run_task_callback(self._connection_handler))
        self.app.cleanup_ctx.append(self._create_task_callback(lambda app: self._websocket_handler(app)))
        self.app.cleanup_ctx.append(self._create_task_callback(lambda app: self._request_handler(app)))
        host = self._configuration.get('webui_host', 'localhost')
        port = self._configuration.get('webui_port', 8081)
        web.run_app(self.app, host=host, port=port)
