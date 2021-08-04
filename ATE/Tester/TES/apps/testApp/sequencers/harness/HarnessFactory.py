from ATE.Tester.TES.apps.testApp.sequencers.MqttClient import MqttClient
from ATE.Tester.TES.apps.testApp.sequencers.harness.LocalHarness import LocalHarness
from ATE.Tester.TES.apps.testApp.sequencers.harness.MqttHarness import MqttHarness


def create_harness(typ: str, mqtt: MqttClient, test_program_name: str):
    if typ == 'file':
        return LocalHarness(test_program_name)
    if typ == 'external':
        return MqttHarness(mqtt)

    raise Exception(f"'{typ}' strategy typ is not supported")
