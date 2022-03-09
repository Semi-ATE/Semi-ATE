import os
from jinja2 import Environment
from jinja2 import FileSystemLoader
from ate_sammy.coding.generators import BaseGenerator
from ate_sammy.coding.AutoScriptGenerator import AutoScriptGenerator


class test_program_generator(BaseGenerator):
    def indexgen(self):
        self.last_index = self.last_index + 1
        return self.last_index

    def __init__(self, template_dir, project_path, prog_name, tests_in_program, test_targets, program_configuration):
        self.last_index = 0
        template_path = os.path.normpath(template_dir)
        file_loader = FileSystemLoader(template_path)
        env = Environment(loader=file_loader)
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.rstrip_blocks = True
        env.globals.update(idgen=self.indexgen)
        template_name = str(self.__class__.__name__).split('.')[-1].split(' ')[0]
        template_name = 'testprogram_template.jinja2'
        if not os.path.exists(os.path.join(template_path, template_name)):
            raise Exception(f"couldn't find the template : {template_name}")
        template = env.get_template(template_name)
        file_name = f"{prog_name}.py"

        rel_path_to_dir = self._generate_relative_path(program_configuration.hardware, program_configuration.base)
        abs_path_to_dir = os.path.join(project_path, rel_path_to_dir)
        self.abs_path_to_file = os.path.join(abs_path_to_dir, file_name)

        if not os.path.exists(abs_path_to_dir):
            os.makedirs(abs_path_to_dir)

        if os.path.exists(self.abs_path_to_file):
            os.remove(self.abs_path_to_file)

        test_list, test_imports = self.build_test_entry_list(tests_in_program, test_targets)

        output = template.render(test_list=test_list, test_imports=test_imports, program_configuration=program_configuration)

        with open(self.abs_path_to_file, 'w', encoding='utf-8') as fd:
            fd.write(output)

        script_name = os.path.join(abs_path_to_dir, f'{prog_name}_auto_script.py')
        if not os.path.exists(script_name):
            AutoScriptGenerator(template_path, script_name)

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

    @staticmethod
    def append_exception_code(prog_path: str):
        msg = "raise Exception('test program is invalid')\n"
        with open(prog_path, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(msg + content)
