import pytest
import mock
from ate_master_app.master_application import MasterApplication
from ate_master_app.master_webservice import WebsocketCommunicationHandler


class TestWebsocketCommunicationHandler:

    def test_command_is_sent_to_app(self, mocker):
        config = {"sites": [0],
                  "device_id": "foobar",
                  "broker_host": "192.168.0.1",
                  "broker_port": "4000",
                  "environment": "SCT_1",
                  "Handler": "abc",
                  "tester_type": "Semi-ATE Master Parallel Tester",
                  "enable_timeouts": True}
        mocker.patch.object(MasterApplication, "get_strategy_type", return_value='default')
        mocker.patch.object(MasterApplication, "get_tester", return_value=None)
        mocker.patch.object(MasterApplication, "set_execution_strategy_configuration", return_value=None)
        mocker.patch.object(MasterApplication, "dispatch_command")
        self.masterApp = MasterApplication(config)
        self.webservice = WebsocketCommunicationHandler({'mqtt_handler': None, 'master_app': self.masterApp})
        data = "{\"type\" : \"cmd\", \"command\" : \"load\" }"
        self.webservice.handle_client_message(data)
        MasterApplication.dispatch_command.assert_called_once()
