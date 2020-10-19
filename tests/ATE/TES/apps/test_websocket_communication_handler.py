from ATE.Tester.TES.apps.masterApp.master_application import MasterApplication
from ATE.Tester.TES.apps.masterApp.master_webservice import WebsocketCommunicationHandler


class TestWebsocketCommunicationHandler:

    def setup_method(self):
        config = {"sites": [0],
                  "device_id": "foobar",
                  "broker_host": "192.168.0.1",
                  "broker_port": "4000",
                  "environment": "SCT_1",
                  "Handler": "abc",
                  "enable_timeouts": True}
        self.masterApp = MasterApplication(config)
        self.webservice = WebsocketCommunicationHandler({'mqtt_handler': None, 'master_app': self.masterApp})
        return

    def test_command_is_sent_to_app(self, mocker):
        mocker.patch.object(MasterApplication, "dispatch_command")
        data = "{\"type\" : \"cmd\", \"command\" : \"load\" }"
        self.webservice.handle_client_message(data)
        MasterApplication.dispatch_command.assert_called_once()
