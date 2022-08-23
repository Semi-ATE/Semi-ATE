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
        template_name = 'test_runner_main_template.jinja2'

        if not template_dir.joinpath(template_name).exists():
            raise Exception(f"couldn't find the template : {template_name}")

        template = env.get_template(template_name)

        if not file_path.parent.exists():
            os.makedirs(file_path.parent)

        if file_path.exists():
            os.remove(file_path)

        hardware_definition['base'] = test_configuration.base
        output = template.render(
            project_name=project_path.name,
            hardware=test_configuration.hardware,
            base=test_configuration.base,
            test_name=test_configuration.name,
            input_parameters=test_configuration.definition['input_parameters'],
            output_parameters=test_configuration.definition['output_parameters'],
            hardware_definition=hardware_definition,
            InputColumnKey=InputColumnKey,
            OutputColumnKey=OutputColumnKey)

        with open(file_path, 'w', encoding='utf-8') as fd:
            fd.write(output)
