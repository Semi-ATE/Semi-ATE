from ate_test_app.sequencers.MqttClient import MqttClient
import json


class AcuatorBase:
    def __init__(self, mqtt_client: MqttClient, actuator_type: str, device_id: str):
        self.mqtt = mqtt_client
        self.actuator_type = actuator_type
        self.device_id = device_id
        self.site_id = 0

    def do_io_control(self, ioctl_name: str, parameters: dict, timeout: int):
        message = {"type": "io-control-request",
                   "periphery_type": self.actuator_type,
                   "ioctl_name": ioctl_name,
                   "parameters": parameters
                   }

        request_topic = "ate/" + self.device_id + f"/TestApp/peripherystate/site{self.site_id}/request"
        response_topic = "ate/" + self.device_id + f"/{self.actuator_type}/response"
        has_timed_out, data = self.mqtt.do_request_response(request_topic, response_topic, json.dumps(message), timeout)
        if has_timed_out:
            return []
        return data
