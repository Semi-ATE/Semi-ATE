from ATE.TES.apps.masterApp.peripheral_controller import PeripheralController
import pytest


TIMEOUT = 5


class DummyActuator():
    def __init__(self):
        self.init_calls = 0
        self.device_io_control_calls = 0
        self.close_calls = 0
        self.last_ioctl = 0

    def init(self, mqtt):
        self.init_calls += 1

    async def device_io_control(self, ioctl_name, data):
        self.device_io_control_calls += 1
        self.last_ioctl = ioctl_name

    def close(self):
        self.close_calls += 1


class DummyHook:
    def __init__(self):
        self.last_actuator = None
        self.last_actuator_name = None

    def get_actuator(self, required_capability):
        tmp = DummyActuator()
        self.last_actuator_name = required_capability
        self.last_actuator = tmp
        return [tmp]


class DummyPluginManager:
    def __init__(self):
        self.hook = DummyHook()


@pytest.fixture
def pluginmanager():
    return DummyPluginManager()


class TestPeripheralController:
    def test_can_create_peripheral_controller(self):
        p = PeripheralController(DummyPluginManager(), None)

    @pytest.mark.asyncio
    async def test_peripheral_controller_lazily_initializes_actuator(self, pluginmanager):
        p = PeripheralController(pluginmanager, None)
        await p.device_io_control("DummyActuator", 17, None)
        assert(pluginmanager.hook.last_actuator_name == "DummyActuator")
        assert(pluginmanager.hook.last_actuator.init_calls == 1)

    @pytest.mark.asyncio
    async def test_peripheral_controller_will_call_init_only_once(self, pluginmanager):
        p = PeripheralController(pluginmanager, None)
        await p.device_io_control("DummyActuator", 1, None)
        await p.device_io_control("DummyActuator", 1, None)
        assert(pluginmanager.hook.last_actuator.init_calls == 1)

    @pytest.mark.asyncio
    async def test_peripheral_controller_will_call_device_io_control(self, pluginmanager):
        p = PeripheralController(pluginmanager, None)
        await p.device_io_control("DummyActuator", 4711, None)
        assert(pluginmanager.hook.last_actuator.device_io_control_calls == 1)

    @pytest.mark.asyncio
    async def test_peripheral_controller_can_use_multiple_peripherals(self, pluginmanager):
        p = PeripheralController(pluginmanager, None)
        await p.device_io_control("Actuator1", 301, None)
        actuator1 = pluginmanager.hook.last_actuator
        await p.device_io_control("Actuator2", 103, None)
        actuator2 = pluginmanager.hook.last_actuator
        assert(actuator1.last_ioctl == 301)
        assert(actuator1.device_io_control_calls == 1)
        assert(actuator2.last_ioctl == 103)
        assert(actuator2.device_io_control_calls == 1)

    @pytest.mark.asyncio
    async def test_peripheral_controller_will_call_unload(self, pluginmanager):
        p = PeripheralController(pluginmanager, None)
        await p.device_io_control("Actuator1", 301, None)
        p.unload()
        assert(pluginmanager.hook.last_actuator.close_calls == 1)
