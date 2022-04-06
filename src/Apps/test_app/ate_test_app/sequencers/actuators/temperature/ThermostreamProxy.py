from ate_test_app.sequencers.MqttClient import MqttClient
from ate_test_app.sequencers.actuators.generic import AcuatorBase


class ThermostreamProxy():
    def __init__(self, mqtt_client: MqttClient, device_id: str):
        self.actuator = AcuatorBase(mqtt_client, "Temperature", device_id)

    def set_mqtt_client(self, mqtt: MqttClient):
        self.mqtt = mqtt

    def set_temperature(self, temp_degrees: list):
        print(f"ThermostreamProxy: Set Temperature to {temp_degrees}")
        parameters = {"temperature": temp_degrees, "timeout": 5}
        return self.actuator.do_io_control("set_temperature", parameters, 5.0)
