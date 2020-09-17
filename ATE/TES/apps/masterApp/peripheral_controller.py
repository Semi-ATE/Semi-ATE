import asyncio

DEFAULT_TIMEOUT = 5


class PeripheralController:
    def __init__(self, plugin_manager, mqtt_client):
        self.plugin_manager = plugin_manager
        self.mqtt_client = mqtt_client
        self.peripherals = {}

    async def device_io_control(self, peripheral_name, ioctl_name, data):
        if peripheral_name not in self.peripherals:
            peripheral_instance = self.plugin_manager.hook.get_actuator(required_capability=peripheral_name)[0]
            self.peripherals[peripheral_name] = peripheral_instance
            peripheral_instance.init(self.mqtt_client)

        timeout = data.get('timeout') if data else DEFAULT_TIMEOUT
        result = await asyncio.wait_for(self.peripherals[peripheral_name].device_io_control(ioctl_name, data), timeout)
        return result

    def unload(self):
        for peripheral in self.peripherals.items():
            peripheral[1].close()
