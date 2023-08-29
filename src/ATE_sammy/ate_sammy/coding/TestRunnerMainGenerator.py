import json
import os
from pathlib import Path
from jinja2 import Environment
from jinja2 import FileSystemLoader
from ate_sammy.coding.generators import BaseGenerator
from ate_sammy.coding.utils import collect_compiled_patterns
from ate_common.parameter import InputColumnKey, OutputColumnKey
from ate_projectdatabase import Test


class test_runner_generator(BaseGenerator):
    def __init__(self, template_dir: Path, project_path: Path, file_path: Path, test_configuration: Test, hardware_definition: dict):
        self.last_index = 0
        file_loader = FileSystemLoader(template_dir)
        env = Environment(loader=file_loader)
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.rstrip_blocks = True
        template_name = 'test_runner_main_template.jinja2'

        self.project_path = project_path

        if not template_dir.joinpath(template_name).exists():
            raise Exception(f"couldn't find the template : {template_name}")

        template = env.get_template(template_name)

        if not file_path.parent.exists():
            os.makedirs(file_path.parent)

        if file_path.exists():
            os.remove(file_path)

        compiled_patterns = collect_compiled_patterns(test_configuration.definition['patterns'], self.project_path)

        output = template.render(
            project_name=project_path.name,
            hardware=test_configuration.hardware,
            base=test_configuration.base,
            test_name=test_configuration.name,
            input_parameters=test_configuration.definition['input_parameters'],
            output_parameters=test_configuration.definition['output_parameters'],
            compiled_patterns=compiled_patterns,
            InputColumnKey=InputColumnKey,
            OutputColumnKey=OutputColumnKey)

        with open(file_path, 'w', encoding='utf-8') as fd:
            fd.write(output)

        # binning and execution strategy configuration files will be generated
        # thus the test flow could be executed
        self._create_binning_config(file_path.parent.joinpath(f'{file_path.stem}_binning.json'))
        self._create_execution_strategy_config(file_path.parent.joinpath(f'{file_path.stem}_execution_strategy.json'))
        self._store_config(file_path.parent.joinpath(f'{file_path.stem}_config.json'), test_configuration)

    def _store_config(self, path: Path, test_configuration: object):
        test_runner_generator._dump(path, {
            'test_name': test_configuration.name,
            'hardware': test_configuration.hardware,
            'base': test_configuration.base,
            'input_parameters': test_configuration.definition['input_parameters'],
            'output_parameters': test_configuration.definition['output_parameters'],
            'patterns': test_configuration.definition['patterns'],
        })

    def _create_execution_strategy_config(self, path: Path):
        execution_strategy = {
            "PR1A": {
                "sites": [
                    [
                        0,
                        0
                    ]
                ],
                "execution_strategy": [
                    [
                        [
                            "0"
                        ]
                    ]
                ]
            }
        }

        test_runner_generator._dump(path, execution_strategy)

    def _create_binning_config(self, path: Path):
        binning_config = {
            "bin-table": [
                {
                    "SBIN": "11",
                    "GROUP": "Contact Fail",
                    "DESCRIPTION": "",
                    "HBIN": "0",
                    "SBINNAME": "Bin_11"
                },
                {
                    "SBIN": "0",
                    "GROUP": "Bad",
                    "DESCRIPTION": "",
                    "HBIN": "0",
                    "SBINNAME": "Bad"
                },
                {
                    "SBIN": "1",
                    "GROUP": "Good1",
                    "DESCRIPTION": "",
                    "HBIN": "1",
                    "SBINNAME": "Good_1"
                },
                {
                    "SBIN": "60000",
                    "GROUP": "Alarm",
                    "DESCRIPTION": "",
                    "HBIN": "0",
                    "SBINNAME": "er_1_ALARM"
                }
            ]
        }

        test_runner_generator._dump(path, binning_config)

    @staticmethod
    def _dump(path, config):
        with open(path, 'w') as f:
            json.dump(config, f, indent=4)
