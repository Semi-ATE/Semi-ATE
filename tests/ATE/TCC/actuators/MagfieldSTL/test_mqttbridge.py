from ATE.TCC.Actuators.common.mqtt.mqttbridge import MqttBridge

from pytest import fixture


class MagFieldMock:
    def __init__(self):
        self.ioctls = []
        self.dry_ioctls = []

    def set_output_state(self, val):
        pass

    def set_field(self, millitesla):
        pass

    def program_curve(self, curve_id, curve_points):
        pass

    def play_curve(self, curve_id):
        pass

    def play_curve_stepwise(self, curve_id):
        pass

    def curve_step(self):
        pass

    def do_dry_call(self, ioctl_name, params):
        self.dry_ioctls.append(ioctl_name)

    def do_io_control(self, ioctl_name, params):
        self.ioctls.append(ioctl_name)
    
    def get_type(self):
        return "MagField"


@fixture
def mqtt():
    return MqttBridge("192.168.0.1", "9001", "1048", MagFieldMock())


def test_disable_command_calls_disable(mqtt):
    request = """
    {
        "type": "io-control-request",
        "ioctl_name": "disable",
        "parameters": {
            "timeout": 5.0
        }
    }"""

    _ = mqtt.on_request(request)
    assert("disable" in mqtt.actuator_impl.ioctls)


def test_drycall_does_drycall(mqtt):
    request = """
    {
        "type": "io-control-drycall",
        "ioctl_name": "disable",
        "parameters": {
            "timeout": 5.0
        }
    }"""

    mqtt.actuator_impl.disable_called = True
    _ = mqtt.on_request(request)
    assert("disable" in mqtt.actuator_impl.dry_ioctls)
