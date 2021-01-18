class ResolverBase:
    def _is_valid_value(self, value, power):
        min_base = self._min * power
        max_base = self._max * power

        return min_base <= value <= max_base

    def get_input_value(self):
        power = self._get_power(self._exponent, self._op.get_exponent())

        measurement = self._op.get_measurement()
        if self._is_valid_value(measurement, power):
            return measurement

        raise Exception("input value cannot be extracted")

    @staticmethod
    def _get_power(exponent_input, exponent_output):
        exponent = abs(exponent_input - exponent_output)
        return pow(10, exponent)
