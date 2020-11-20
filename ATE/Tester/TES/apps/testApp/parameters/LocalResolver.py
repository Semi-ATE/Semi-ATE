class LocalResolver:
    def __init__(self, name, shmoo, op):
        self._name = name
        self._shmoo = shmoo
        self.op = op

    def __call__(self):
        return self.op._measurement
