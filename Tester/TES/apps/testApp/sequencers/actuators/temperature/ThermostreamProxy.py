from ATE.Tester.sequencers.actuators.generic import AcuatorBase


class ThermostreamProxy():
    def __init__(self, mqtt_client, device_id):
        self.actuator = AcuatorBase(mqtt_client, "Temperature", device_id)

    def set_mqtt_client(self, mqtt):
        self.mqtt = mqtt

    def set_temperature(self, temp_degrees):
        print(f"ThermostreamProxy: Set Temperature to {temp_degrees}")
        parameters = {"temperature": temp_degrees, "timeout": 5}
        return self.actuator.do_io_control("set_temperature", parameters, 5.0)
