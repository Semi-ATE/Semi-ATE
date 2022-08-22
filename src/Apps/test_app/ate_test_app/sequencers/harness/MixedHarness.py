from ate_test_app.sequencers.MqttClient import MqttClient
from ate_test_app.sequencers.Harness import Harness
from ate_test_app.sequencers.harness.LocalHarness import LocalHarness
from ate_test_app.sequencers.harness.MqttHarness import MqttHarness


class MixedHarness(Harness):
    def __init__(self, local_harness: LocalHarness, mqtt_harness: MqttHarness):
        self.local_harness = local_harness
        self.mqtt_harness = mqtt_harness

    def send_summary(self, summary: dict):
        self.local_harness.send_summary(summary)
        self.mqtt_harness.send_summary(summary)

    def send_testresult(self, stdf_data: dict):
        self.local_harness.send_testresult(stdf_data)
        self.mqtt_harness.send_testresult(stdf_data)

    def next(self):
        self.local_harness.next()
        self.mqtt_harness.next()

    def collect(self, stdf_data: dict):
        self.local_harness.collect(stdf_data)
        self.mqtt_harness.collect(stdf_data)
