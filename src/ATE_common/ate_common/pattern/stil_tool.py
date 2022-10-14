from STIL_Tools.sc_loader import SLoader


class StilTool:
    def __init__(self):
        self.loader = SLoader()

    def load_pattern(self, compiled_patterns: dict):
        for pattern_name, path in compiled_patterns.items():
            self.loader.load(path, f'/tmp/mem/{pattern_name}')

    def run_pattern(self, pattern_name: str):
        self.loader.run(pattern_name)
