class MagFieldImpl:
    def __init__(self, stldcs6k_driver_instance):
        self.driver = stldcs6k_driver_instance

    def get_type(self):
        return "MagField"

    def do_io_control(self, ioctl, param_data):
        return self._dispatch_ioctl(ioctl, param_data, False)

    def do_dry_call(self, ioctl, param_data):
        return self._dispatch_ioctl(ioctl, param_data, True)

    def _dispatch_ioctl(self, ioctl, param_data, do_dry):
        try:
            if ioctl == "disable":
                return self._disable(do_dry)
            if ioctl == "set_field":
                return self._set_field(param_data["millitesla"], do_dry)
            if ioctl == "play_curve":
                return self._play_curve(param_data["id"], do_dry)
            if ioctl == "curve_step":
                return self._curve_step(do_dry)
            if ioctl == "curve_stop":
                return self._curve_stop(do_dry)
            if ioctl == "play_curve_stepwise":
                return self._play_curve_stepwise(param_data["id"], do_dry)
            if ioctl == "program_curve":
                return self._program_curve(param_data["id"], param_data["hull"], do_dry)
        except KeyError:
            return {"status": "missing_parameter"}
        except ValueError:
            # Experimental: We send an error to the client
            # but keep running. The next time a command
            # arrives the CommChannel will attempt to
            # reconnect.
            # Rationale:
            # Depending on where this service is running
            # "let it crash" is probably not the correct
            # philosophy here.
            return {"status": "connection_lost"}
        return {"status": "bad_ioctl", "error_message": f"The ioctl {ioctl} is undefined."}

    def _selftest(self):
        return {}

    def _disable(self, dry):
        return self.driver.set_output_state("off", dry)

    def _set_field(self, millitesla, dry):
        # ToDo: Calculate correct value from parameter...
        result_set_value = self.driver.set_value(millitesla, dry)
        if result_set_value["status"] != "ok":
            return result_set_value
        return self.driver.set_output_state("active", dry)

    def _program_curve(self, curve_id, curve_points, dry):
        return {}

    def _play_curve(self, curve_id, dry):
        return {}

    def _play_curve_stepwise(self, curve_id, dry):
        return {}

    def _curve_step(self, dry):
        return {}

    def _curve_stop(self, dry):
        return {}
