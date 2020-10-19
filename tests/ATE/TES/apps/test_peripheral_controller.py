# These tests are probably redundant by now!

from ATE.Tester.TES.apps.masterApp.peripheral_controller import PeripheralController
import pytest
import json


# TIMEOUT = 5


# class DummyActuator():
#     def __init__(self):
#         self.init_calls = 0
#         self.device_io_control_calls = 0
#         self.close_calls = 0
#         self.last_ioctl = 0

#     def init(self, mqtt):
#         self.init_calls += 1

#     async def device_io_control(self, ioctl_name, data):
#         self.device_io_control_calls += 1
#         self.last_ioctl = ioctl_name

#     def close(self):
#         self.close_calls += 1


# class DummyHook:
#     def __init__(self):
#         self.last_actuator = None
#         self.last_actuator_name = None

#     def get_actuator(self, required_capability):
#         tmp = DummyActuator()
#         self.last_actuator_name = required_capability
#         self.last_actuator = tmp
#         return [tmp]


# class DummyPluginManager:
#     def __init__(self):
#         self.hook = DummyHook()


# @pytest.fixture
# def pluginmanager():
#     return DummyPluginManager()

class DummyMqtt:
    def __init__(self):
        self.sent_data = []

    def publish(self, topic, payload=None, qos=0, retain=False):
        tup = (topic, payload)
        self.sent_data.append(tup)


class TestPeripheralController:
    def test_can_create_peripheral_controller(self):
        _ = PeripheralController(None, 9911)

    @pytest.mark.asyncio
    async def test_will_publish_into_correct_topic(self):
        ctrl = PeripheralController(DummyMqtt(), 4711)
        await ctrl.device_io_control("FnordPeriphery", "foo_ioctl", {"foo": "bar"})
        sent_data = ctrl.mqtt_client.sent_data.pop()
        assert (sent_data[0] == "ate/4711/io-control/FnordPeriphery/request")

        @pytest.mark.asyncio
        async def test_will_publish_correct_data(self):
            ctrl = PeripheralController(DummyMqtt(), 8150)
            await ctrl.device_io_control("FnordPeriphery", "foo_ioctl", {"foo": "bar"})
            sent_data = ctrl.mqtt_client.sent_data.pop()
            params = json.loads(sent_data[1])
            assert (params["type"] == "io-control-request")
            assert (params["ioctl_name"] == "foo_ioctl")
            assert (params["parameters"]["foo"] == "bar")
