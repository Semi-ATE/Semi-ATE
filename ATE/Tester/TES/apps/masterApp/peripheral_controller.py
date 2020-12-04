import json
import asyncio


class PeripheralController:
    def __init__(self, mqtt_client, device_id):
        self.mqtt_client = mqtt_client
        self.device_id = device_id
        self.ioctl_response_event = asyncio.Event()

    async def device_io_control(self, peripheral_name, ioctl_code, parameters):
        message = {"type": "io-control-request",
                   "ioctl_name": ioctl_code,
                   "parameters": parameters
                   }

        request_topic = f"ate/{self.device_id}/{peripheral_name}/io-control"
        self.ioctl_response_event.clear()
        return await self.mqtt_client.publish_with_response(request_topic, json.dumps(message))

    def on_response_received(self, response):
        self.received_response = response
        self.ioctl_response_event.set()
