from ate_test_app.sequencers.MqttClient import MqttClient
import json


class TemperatureProxy():
    def set_mqtt_client(self, mqtt: MqttClient):
        self.mqtt = mqtt

    def set_temperature(self, temp_degrees: list):
        print(f"TemperatureProxy: Set Temperature to {temp_degrees}")
        message = {"type": "io-control-request",
                   "periphery_type": "Temperature",
                   "ioctl_name": "set_temperature",
                   "parameters": {"temperature": temp_degrees, "timeout": 5}
                   }

        has_timed_out, data = self.mqtt.publish_with_reply("Temperature", json.dumps(message), 5.0)

        if has_timed_out:
            pass
