from ate_test_app.sequencers.MqttClient import MqttClient
from ate_test_app.sequencers.Harness import Harness


class MqttHarness(Harness):
    def __init__(self, mqtt: MqttClient):
        self._mqtt = mqtt

    def send_summary(self, summary: dict):
        self._mqtt.publish_tests_summary(summary)

    def send_testresult(self, stdf_data: dict):
        self._mqtt.publish_result(stdf_data)

    def next(self):
        pass

    def collect(self, stdf_data: dict):
        pass
