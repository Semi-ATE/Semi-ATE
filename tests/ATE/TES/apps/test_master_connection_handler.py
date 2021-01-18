from ATE.Tester.TES.apps.masterApp.master_connection_handler import MasterConnectionHandler
from ATE.Tester.TES.apps.common.mqtt_connection import MqttConnection
from ATE.common.logger import Logger

PORT = 1883
HOST = '10.9.1.6'
SITE = 0
DEVICEID = "sct01"
HANDLERID = "abc"

SITES = [0, 1, 2]


class Msg:
    def __init__(self):
        self.topic = ""
        self.payload = ""

    def decode(self, dummy):
        return self.payload


class TestApplication:
    log = Logger('test')

    def on_control_status_changed(self, siteid, msg):
        self.controlsite = siteid
        self.controlmsg = msg

    def on_testapp_status_changed(self, siteid, msg):
        self.testappsite = siteid
        self.testappmsg = msg

    def on_testapp_testresult_changed(self, siteid, msg):
        pass

    def on_handler_command_message(self, message):
        self.handler_command = message

    def setup_method(self):
        self.connection_handler = MasterConnectionHandler(HOST,
                                                          PORT,
                                                          SITES,
                                                          DEVICEID,
                                                          HANDLERID,
                                                          self)
        self.controlsite = None
        self.controlmsg = None
        self.testappsite = None
        self.testappmsg = None
        self.handler_command = None

    def teardown_method(self):
        self.connection_handler = None
        self.controlsite = None
        self.controlmsg = None
        self.testappsite = None
        self.testappmsg = None
        self.handler_command = None

    def test_masterconnhandler_control_status_event_is_dispatched(self):
        msg = Msg()

        msg.topic = "ate/sct01/Control/status/site1"
        msg.payload = "{\"state\" : \"busy\"}"
        self.connection_handler.mqtt._on_message_handler(None, None, msg)
        assert(self.controlsite == "1")

    def test_masterconnhandler_testapp_Status_event_is_dispatched(self):
        msg = Msg()

        msg.topic = "ate/sct01/TestApp/status/site1"
        msg.payload = "{\"state\" : \"busy\"}"
        self.connection_handler.mqtt._on_message_handler(None, None, msg)
        assert(self.testappsite == "1")

# ToDo: Implement me!

    # def test_masterconnhandler_sendnext_sends_correct_data(self, mocker):
    #     # spy = mocker.spy(Cls, "method")
    #     # ToDo: Check if the correctly formed message is sent
    #     assert False

    def test_masterconnhandler_sendload_sends_correct_data(self, mocker):
        mocker.patch.object(MqttConnection, "publish")
        self.connection_handler.send_load_test_to_all_sites("placeholder_string___this_should_be_a_dict_with_certain_keys_for_a_valid_cmd_payload")
        MqttConnection.publish.assert_called_once_with("ate/sct01/Control/cmd", "{\"type\": \"cmd\", \"command\": \"loadTest\", \"testapp_params\": \"placeholder_string___this_should_be_a_dict_with_certain_keys_for_a_valid_cmd_payload\", \"sites\": [0, 1, 2]}", 0, False)

    def test_masterconnhandler_sendterminate_sends_correct_data(self, mocker):
        mocker.patch.object(MqttConnection, "publish")
        self.connection_handler.send_terminate_to_all_sites()
        MqttConnection.publish.assert_called_once_with("ate/sct01/TestApp/cmd", "{\"type\": \"cmd\", \"command\": \"terminate\", \"sites\": [0, 1, 2]}", 0, False)

    def test_masterconnhandler_identify_is_routed_correctly(self, mocker):
        mocker.patch.object(MqttConnection, "publish")
        msg = Msg()

        msg.topic = "ate/sct01/Master/cmd"
        msg.payload = "{\"type\" : \"identfy\", \"payload\": \"[]\"}"
        self.connection_handler.mqtt._on_message_handler(None, None, msg)
        assert(self.handler_command is not None)
