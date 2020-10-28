from ATE.TCC.Actuators.MagfieldSTL.driver.util import do_command


class CommandBuilder():
    def __init__(self, com_channel):
        self.com_channel = com_channel

    def init_command(self, commandname):
        self.parameters = []
        self.fail = False
        self.bad_params = []
        self.timeout = 0
        self.commandname = commandname
        return self

    def constrain_numeric_parameter(self, name, min, max, value):
        if not (min <= value <= max):
            self.fail = True
            self.bad_params.append(name)
        self.parameters.append(value)
        return self

    def constrain_value_parameter(self, name, valid_values, value):
        if value not in valid_values:
            self.fail = True
            self.bad_params.append(name)
        self.parameters.append(value)
        return self

    def with_timeout(self, timeout):
        self.timeout = timeout
        return self

    def _make_bad_param_result(self):
        error_string = "Invalid parameters: "
        for bad_param in self.bad_params:
            error_string = error_string + (bad_param + " ")
        return {"status": "badparamvalue", "error_message": error_string}

    def execute(self, is_dry_call):
        if self.fail:
            return self._make_bad_param_result()

        if is_dry_call:
            return {"status": "ok"}

        param_string = ""
        for param in self.parameters:
            param_string = param_string + str(param) + ','

        # It's easiest to just append all params with a comma
        # and strip the last comma away in the end:
        param_string = param_string[0:len(param_string) - 1]
        return self.__do_command(self.commandname, param_string, self.timeout)

    def __do_command(self, commandname, parameters, timeout):
        results = do_command(self.com_channel, commandname, parameters, timeout)
        result_dict = {}
        for index, result_value in enumerate(result for result in results if result != ""):
            result_dict[f"value{index}"] = result_value
        result_dict["status"] = "ok"
        return result_dict
