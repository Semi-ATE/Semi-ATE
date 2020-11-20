# These tests are probably redundant by now!

from ATE.Tester.TES.apps.masterApp.peripheral_controller import PeripheralController
import pytest
import json

class DummyMqtt:
    def __init__(self):
        self.sent_data = []

    def publish(self, topic, payload=None, qos=0, retain=False):
        tup = (topic, payload)
        self.sent_data.append(tup)

    async def publish_with_response(self, request_topic, message):
        self.sent_data.append((request_topic + "/request", message))
        pass


class TestPeripheralController:
    def test_can_create_peripheral_controller(self):
        _ = PeripheralController(None, 9911)

    @pytest.mark.asyncio
    async def test_will_publish_into_correct_topic(self):
        ctrl = PeripheralController(DummyMqtt(), 4711)
        await ctrl.device_io_control("FnordPeriphery", "foo_ioctl", {"foo": "bar"})
        sent_data = ctrl.mqtt_client.sent_data.pop()
        assert (sent_data[0] == "ate/4711/FnordPeriphery/io-control/request")

        @pytest.mark.asyncio
        async def test_will_publish_correct_data(self):
            ctrl = PeripheralController(DummyMqtt(), 8150)
            await ctrl.device_io_control("FnordPeriphery", "foo_ioctl", {"foo": "bar"})
            sent_data = ctrl.mqtt_client.sent_data.pop()
            params = json.loads(sent_data[1])
            assert (params["type"] == "io-control-request")
            assert (params["ioctl_name"] == "foo_ioctl")
            assert (params["parameters"]["foo"] == "bar")
