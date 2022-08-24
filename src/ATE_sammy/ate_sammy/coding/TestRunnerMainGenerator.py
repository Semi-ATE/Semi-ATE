import os
from pathlib import Path
from jinja2 import Environment
from jinja2 import FileSystemLoader
from ate_sammy.coding.generators import BaseGenerator
from ate_common.parameter import InputColumnKey, OutputColumnKey
from ate_projectdatabase import Test, Hardware


class test_runner_generator(BaseGenerator):
    def __init__(self, template_dir: Path, project_path: Path, file_path: Path, test_configuration: Test, hardware_definition: dict):
        self.last_index = 0
        file_loader = FileSystemLoader(template_dir)
        env = Environment(loader=file_loader)
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.rstrip_blocks = True

        raise NotImplementedError('shall be fixed in #239')
