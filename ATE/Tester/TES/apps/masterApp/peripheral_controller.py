import json


class PeripheralController:
    def __init__(self, mqtt_client, device_id):
        self.mqtt_client = mqtt_client
        self.device_id = device_id

    async def device_io_control(self, peripheral_name, ioctl_code, parameters):
        message = {"type": "io-control-request",
                   "ioctl_name": ioctl_code,
                   "parameters": parameters
                   }

        request_topic = f"ate/{self.device_id}/io-control/{peripheral_name}/request"
        # Note: Response shall only be subscribed to by the testprogs!
        self.mqtt_client.publish(request_topic, json.dumps(message), 0, False)
