import pytest
import json
from ATE.Tester.TES.apps.handlerApp.handler_message_generator import MessageGenerator
from ATE.common.logger import Logger

LOAD_PARAMETERS = {"lotnumber": "010101", "sublotnumber": "000", "devicetype": "cca", "measurementtemperature": "11"}

WRONG_LOAD_PARAMTERS = {"lotNumber": "0x0x0x0",
                        "HandlerType": "T123"}


class TestMessageGenerator:
    def setup_class(self):
        self.message_generator = MessageGenerator(Logger('test'))

    def teardown_class(self):
        self.message_generator = None

    def test_send_command_wrong_parameters(self):
        assert len(self.message_generator.generate_command_msg("load", LOAD_PARAMETERS))

    def test_send_command_wrong_message_type(self):
        assert(self.message_generator.generate_command_msg("load_test", LOAD_PARAMETERS) is None)

    def test_send_command_correct_parameters(self):
        message = json.loads(self.message_generator.generate_command_msg("load", LOAD_PARAMETERS))

        assert(message["type"] == "load")

        for key, value in LOAD_PARAMETERS.items():
            job_data = message["payload"]
            assert(job_data.get(key) == value)
