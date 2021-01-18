
CURVE_ITEM_SIZE = 1
MAX_CURVE_SIZE = 1024       # Limit to 1024 Entries per curve
MIN_TIMEOUT = 1.5


class MagFieldImpl:
    def __init__(self, stldcs6k_driver_instance):
        self.driver = stldcs6k_driver_instance
        self.curves = {}
        self.curve_index = -1
        self.curve_point_index = -1

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
        if not type(curve_id) == int or curve_id < 0:
            return {"status": "invalidid"}
        if len(curve_points) > MAX_CURVE_SIZE:
            return {"status": "curvetoolarge"}
        self.curves[curve_id] = curve_points

        # Program each point of the curve into the stl
        start_address = curve_id * MAX_CURVE_SIZE * CURVE_ITEM_SIZE
        for index, point in enumerate(curve_points):
            result = self.driver.set_sequence_line(start_address + index, point[0], 0, 0, "standard", 0, dry)
            if result["status"] != "ok":
                return result

        return result

    def _play_curve(self, curve_id, dry):
        if not type(curve_id) == int or curve_id < 0:
            return {"status": "invalidid"}
        if curve_id not in self.curves:
            return {"status": "unknown"}
        # the STL uses a very simplistic model of a curve
        # so we have to do some augmentation here

        curve_to_play = self.curves[curve_id]

        # calcualte size of the curve
        curve_size = len(curve_to_play) * CURVE_ITEM_SIZE
        start_address = MAX_CURVE_SIZE * curve_id
        end_address = start_address + curve_size
        seq_time = (len(curve_to_play) * curve_to_play[0][1])
        seq_timeout = seq_time + MIN_TIMEOUT

        return self.driver.start_sequence(start_address, end_address, 1, "time", seq_time, "intern", seq_timeout, dry)

    def _output_curve_point(self, point_id, dry):
        curve_point = self.curves[self.curve_index][point_id]
        return self.driver.set_value(curve_point[0], dry)

    def _play_curve_stepwise(self, curve_id, dry):
        if not type(curve_id) == int or curve_id < 0:
            return {"status": "invalidid"}
        if curve_id not in self.curves:
            return {"status": "unknown"}
        self.curve_index = curve_id
        self.curve_point_index = 0
        return self._output_curve_point(self.curve_point_index, dry)

    def _curve_step(self, dry):
        if self.curve_index < 0:
            return {"status": "notplaying"}
        self.curve_point_index = self.curve_point_index + 1
        ret_val = self._output_curve_point(self.curve_point_index, dry)
        if ret_val["status"] != "ok":
            return ret_val
        # Check if we've reached the last point of the curve:
        if self.curve_point_index + 1 == len(self.curves[self.curve_index]):
            return {"status": "done"}
        # returning ret_val here again is necessary, if status == ok at this point
        return ret_val

    def _curve_stop(self, dry):
        return {}

    def get_status(self):
        if self.driver.is_connected():
            return "available"
        return "connecting"
