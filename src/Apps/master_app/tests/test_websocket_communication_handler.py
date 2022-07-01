from ate_master_app.utils.master_configuration import MasterConfiguration
import pytest
import mock
from ate_master_app.master_application import MasterApplication
from ate_master_app.master_webservice import WebsocketCommunicationHandler
from tests.test_masterapp import default_configuration


class TestWebsocketCommunicationHandler:

    def test_command_is_sent_to_app(self, mocker):
        config = default_configuration()
        config['sites'] = ['0']
        config['device_id'] = "foobar"
        config['broker_host'] = "192.168.0.1"
        config['broker_port'] = "4000"
        config['environment'] = "SCT_1"
        config['Handler'] = "abc"
        config['test_type'] = "Semi-ATE Master Parallel Tester"
        config['enable_timeouts'] = True

        mocker.patch.object(MasterApplication, "get_strategy_type", return_value='default')
        mocker.patch.object(MasterApplication, "get_tester", return_value=None)
        mocker.patch.object(MasterApplication, "set_execution_strategy_configuration", return_value=None)
        mocker.patch.object(MasterApplication, "dispatch_command")
        self.masterApp = MasterApplication(MasterConfiguration(**config))
        self.webservice = WebsocketCommunicationHandler({'mqtt_handler': None, 'master_app': self.masterApp})
        data = "{\"type\" : \"cmd\", \"command\" : \"load\" }"
        self.webservice.handle_client_message(data)
        MasterApplication.dispatch_command.assert_called_once()
