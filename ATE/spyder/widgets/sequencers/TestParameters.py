class InputParameter:
    def __init__(self, name, shmoo, value):
        self._value = value
        self._shmoo = value
        self._name = name

    def __call__(self):
        return self._value


class OutputParameter:
    def __init__(self, name, lsl, ltl, nom, utl, usl):
        self._name = name
        self._lsl = lsl
        self._ltl = ltl
        self._nom = nom
        self._utl = utl
        self._usl = usl
        # initialize the measurement with a value,
        # that is guaranteed to fail the test, if
        # if the test fails to write the param.
        self._measurement = self._lsl

    def write(self, measurement):
        self._measurement = measurement

    def is_pass(self):
        return self._measurement >= self._ltl and self._measurement <= self._utl

    def randn(self):
        # ToDo: This should create a normal distribution,
        # for now we just use halfway between LTL and UTL
        return (self._ltl + self._utl) / 2.0

    def set_limits(self, ltl, utl):
        if(ltl > utl):
            raise ValueError("LTL must be smaller than UTL")

        if(ltl < self._lsl or utl > self._usl):
            raise ValueError("Testlimits must not violate speclimits")

        self._ltl = ltl
        self._utl = utl
