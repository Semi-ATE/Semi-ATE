from ate_test_app.sequencers.DutTesting.TestParameters import OutputParameter
from ate_test_app.parameters.ResolverBase import ResolverBase


class LocalResolver(ResolverBase):
    def __init__(self, name: str, shmoo: bool, op: OutputParameter, min_value: float, max_value: float, exponent: bool):
        super().__init__()
        self._name = name
        self._shmoo = shmoo
        self._op = op
        self._min = min_value
        self._max = max_value
        self._exponent = int(exponent)

    def __call__(self):
        return self.get_input_value()
