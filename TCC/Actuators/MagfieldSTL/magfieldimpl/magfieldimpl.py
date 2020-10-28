class MagFieldImpl:
    def __init__(self, stldcs6k_driver_instance):
        self.driver = stldcs6k_driver_instance

    def _init_load(self, rref, lref, deltaRref, deltaLRef):
        # According to RefMan 3.3.5 of the DCS6k
        result = self.driver.read_reference_impedance()
        if MagFieldImpl._is_error(result):
            return result

        result = self.driver.measure_current_impedance()
        if MagFieldImpl._is_error(result):
            return result

        result = self.driver.set_reference_impedance(rref, lref, deltaRref, deltaLRef, False)
        if MagFieldImpl._is_error(result):
            return result

        result = self.driver.perform_impedance_test()
        return result

    def _do_load_adaption(self, proportial_factor, integral_factor, slew_rate):
        result = self.driver.initialize_pid()
        if MagFieldImpl._is_error(result):
            return result

        result = self.driver.set_pid("standard", proportial_factor, integral_factor, slew_rate, False)
        return result

    def _setup_dcs6k(self):
        result = self.driver.set_operation_mode("analog", False)
        if MagFieldImpl._is_error(result):
            return result

        result = self.driver.set_startup_mode("analog", False)
        if MagFieldImpl._is_error(result):
            return result

        result = self.driver.set_analog_parameters(1, "standard", 1, 0.05, False)
        return result

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

            # Ioctls not part of the official actuator interface, but used to configure
            # the source:
            if ioctl == "init_load":
                return self._init_load(param_data["rref"], param_data["lref"], param_data["deltaRref"], param_data["deltaLref"])
            if ioctl == "do_load_adaption":
                return self._do_load_adaption(param_data["proportial_factor"], param_data["integral_factor"], param_data["slew_rate"])
            if ioctl == "setup_dcs6k":
                return self._setup_dcs6k()
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

    def _is_error(result):
        return result["status"] != "ok"

    def _set_field(self, millitesla, dry):
        return self.driver.set_value(millitesla, dry)

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

    def get_status(self):
        if self.driver.is_connected():
            return "available"
        return "connecting"
