from ate_test_app.sequencers.MqttClient import MqttClient


class LightProxy():
    def set_mqtt_client(self, mqtt: MqttClient):
        self.mqtt = mqtt

# TBD: API for the Light Actuator
