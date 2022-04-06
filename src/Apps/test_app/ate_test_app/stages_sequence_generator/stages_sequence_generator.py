from typing import Dict, List, Optional, Tuple
import json


class StagesSequenceGenerator:
    def __init__(self, config_file_path: str):
        self.configuration = self.read_configuration(config_file_path)

    @staticmethod
    def read_configuration(config_file_path: str) -> Dict[str, dict]:
        with open(config_file_path, 'r') as f:
            return json.load(f)

    def get_execution_strategy(self, layout: List[Tuple[int, int]]) -> List[List[str]]:
        layout_name = self._get_layout_name(layout)
        return self.configuration[layout_name]['execution_strategy']

    def _get_layout_name(self, layout: List[Tuple[int, int]]) -> Optional[str]:
        for parallelism, config in self.configuration.items():
            if config['sites'] != layout:
                continue

            return parallelism

        raise Exception(f'no configuration for layout "{layout}" was found')
