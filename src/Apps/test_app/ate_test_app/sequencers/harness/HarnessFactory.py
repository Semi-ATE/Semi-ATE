from ate_test_app.sequencers.MqttClient import MqttClient
from ate_test_app.sequencers.harness.LocalHarness import LocalHarness
from ate_test_app.sequencers.harness.MqttHarness import MqttHarness
from ate_test_app.sequencers.harness.MixedHarness import MixedHarness


def create_harness(typ: str, mqtt: MqttClient, test_program_name: str):
    if typ == 'file':
        return LocalHarness(test_program_name)
    if typ == 'external':
        return MqttHarness(mqtt)
    if typ == 'mixed':
        return MixedHarness(LocalHarness(test_program_name), MqttHarness(mqtt))

    raise Exception(f"'{typ}' strategy typ is not supported")
