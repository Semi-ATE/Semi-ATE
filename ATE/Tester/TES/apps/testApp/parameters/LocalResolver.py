from ATE.Tester.TES.apps.testApp.parameters.ResolverBase import ResolverBase


class LocalResolver(ResolverBase):
    def __init__(self, name, shmoo, op, min_value, max_value, exponent):
        super().__init__()
        self._name = name
        self._shmoo = shmoo
        self._op = op
        self._min = min_value
        self._max = max_value
        self._exponent = int(exponent)

    def __call__(self):
        return self.get_input_value()
