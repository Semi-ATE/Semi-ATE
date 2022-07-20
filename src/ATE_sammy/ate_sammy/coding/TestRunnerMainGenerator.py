import os
from pathlib import Path
from jinja2 import Environment
from jinja2 import FileSystemLoader
from ate_sammy.coding.generators import BaseGenerator
from ate_common.parameter import InputColumnKey, OutputColumnKey


class test_runner_generator(BaseGenerator):
    def __init__(self, template_dir: Path, project_path: Path, file_path: Path, test_configuration: dict):
        self.last_index = 0
        file_loader = FileSystemLoader(template_dir)
        env = Environment(loader=file_loader)
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.rstrip_blocks = True
        template_name = 'test_runner_main_template.jinja2'

        if not template_dir.joinpath(template_name).exists():
            raise Exception(f"couldn't find the template : {template_name}")

        template = env.get_template(template_name)

        if not file_path.parent.exists():
            os.makedirs(file_path.parent)

        if file_path.exists():
            os.remove(file_path)

        output = template.render(
            project_name=project_path.name,
            hardware=test_configuration.hardware,
            base=test_configuration.base,
            test_name=test_configuration.name,
            input_parameters=test_configuration.definition['input_parameters'],
            InputColumnKey=InputColumnKey,
            OutputColumnKey=OutputColumnKey)

        with open(file_path, 'w', encoding='utf-8') as fd:
            fd.write(output)

    def build_test_entry_list(self, tests_in_program, test_targets):
        test_list = []
        test_imports = {}
        for program_entry in tests_in_program:
            test_class = self.resolve_class_for_test(program_entry.test, test_targets)
            test_module = self.resolve_module_for_test(program_entry.test, test_targets)
            params = program_entry.definition
            if not params['is_selected']:
                continue

            test_imports.update({test_module: test_class})
            test_list.append({"test_name": program_entry.test,
                              "test_class": test_class,
                              "test_module": test_module,
                              "test_number": params['test_num'],
                              "sbin": params['sbin'],
                              "instance_name": params['description'],
                              "output_parameters": params['output_parameters'],
                              "input_parameters": params['input_parameters']})

        return test_list, test_imports

    def resolve_class_for_test(self, test_name, test_targets):
        for target in test_targets:
            if target.test == test_name:
                if target.is_default:
                    return f"{test_name}"
                return f"{target.name}"
        raise Exception(f"Cannot resolve class for test {test_name}")

    def resolve_module_for_test(self, test_name, test_targets):
        for target in test_targets:
            if target.test == test_name:
                if target.is_default:
                    return f"{test_name}.{test_name}"
                return f"{test_name}.{target.name}"
        raise Exception(f"Cannot resolve module for test {test_name}")

    def _generate_relative_path(self, hardware, base):
        return os.path.join('src', hardware, base)

    def _generate_render_data(self, abs_path=''):
        pass

    def _render(self, template, render_data):
        pass
