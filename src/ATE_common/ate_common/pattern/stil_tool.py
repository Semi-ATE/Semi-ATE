from STIL_Tools.sc_loader import SLoader


OUTPUT_DIR = '/tmp/mem'


class StilTool:
    def __init__(self):
        self._loader = SLoader()
        self._compiled_pattern_tuples = None

    def _load_patterns(self, compiled_pattern_tuples: dict):
        self._compiled_pattern_tuples = compiled_pattern_tuples
        for _, path in self._compiled_pattern_tuples.items():
            self._loader.load(path, OUTPUT_DIR)

    def run_pattern(self, pattern_name: str):
        if not self._compiled_pattern_tuples:
            raise Exception('no pattern is loaded')

        self._loader.run(self._compiled_pattern_tuples[pattern_name])
