from ATE.TES.apps.handlerApp.handler_connection_handler import ConnectionHandler
from ATE.TES.apps.handlerApp.handler_message_generator import MessageGenerator

config = {"broker_host": "10.10.10.10",
          "broker_port": 1111,
          "device_id": "SCT_1"}

load_paramters = {"lotNumber": "0x0x0x0",
                  "HandlerName": "ABC",
                  "HandlerType": "T123"}

wrong_load_paramters = {"lotNumber": "0x0x0x0",
                        "HandlerType": "T123"}

# use this to change the behaviour of a function
# with mock.patch.object(class_name, "func", new=new_func):
# def new_func(cls, *args, **kwargs):
#     return


class TestConnectionHandler:
    def setup_class(self):
        self.connection_handler = ConnectionHandler(config)

    def teardown_class(self):
        self.connection_handler = None

    def test_send_command_message_could_not_be_generated(self, mocker):
        mocker.patch.object(MessageGenerator, "generate_command_msg", return_value=None)
        assert(not self.connection_handler.send_command("", wrong_load_paramters))

    def test_send_command_correct_test_paramters(self, mocker):
        mocker.patch.object(ConnectionHandler, "publish")
        mocker.patch.object(MessageGenerator, "generate_command_msg", return_value=load_paramters)
        assert(self.connection_handler.send_command("load_test", load_paramters))
        ConnectionHandler.publish.assert_called_once_with("ate/SCT_1/Master/load_test", load_paramters, qos=2)
