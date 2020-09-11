import json
from ATE.TES.apps.handlerApp.handler_message_generator import MessageGenerator

load_paramters = {"lotNumber": "0x0x0x0",
                  "HandlerName": "ABC",
                  "HandlerType": "T123"}

wrong_load_paramters = {"lotNumber": "0x0x0x0",
                        "HandlerType": "T123"}


class TestMessageGenerator:
    def setup_class(self):
        self.message_generator = MessageGenerator()

    def teardown_class(self):
        self.message_generator = None

    def test_generate_status_msg(self):
        assert (self.message_generator.generate_status_msg("Idle") == '{"type": "status", "state": "Idle"}')

    def test_send_command_wrong_command(self):
        assert(self.message_generator.generate_command_msg("load", load_paramters) is None)

    def test_send_command_wrong_payload(self):
        assert(self.message_generator.generate_command_msg("load_test", wrong_load_paramters) is None)

    def test_send_command_correct_parameters(self):
        message = json.loads(self.message_generator.generate_command_msg("load_test", load_paramters))

        assert(message["type"] == "cmd")
        assert(message["command"] == "load_test")

        for key, value in load_paramters.items():
            job_data = json.loads(message["job_data"])
            assert(job_data.get(key) == value)
