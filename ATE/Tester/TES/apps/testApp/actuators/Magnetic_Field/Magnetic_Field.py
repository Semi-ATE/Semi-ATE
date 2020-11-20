import json


class Magnetic_FieldProxy():
    def set_mqtt_client(self, mqtt):
        self.mqtt = mqtt

    def _do_request(self, ioctl, payload):
        message = {"type": "io-control-request",
                   "periphery_type": "MagField",
                   "ioctl_name": ioctl,
                   "parameters": payload
                   }

        has_timed_out, data = self.mqtt.publish_with_reply("MagField", json.dumps(message), 5.0)
        return data

    def set_field(self, field_strength):
        return self._do_request("set_field", {"millitesla": field_strength})

    def disable_field(self):
        return self._do_request("disable", {})

    def program_curve(self):
        # Not implemented!
        pass

    def play_curve(self, curve_id):
        return self._do_request("play_curve", {"id": curve_id})

    def play_curve_stepwise(self, curve_id):
        return self._do_request("play_curve_stepwise", {"id": curve_id})

    def do_curve_step(self):
        return self._do_request("curve_step", {})

    def stop_curve(self):
        return self._do_request("curve_stop", {})
