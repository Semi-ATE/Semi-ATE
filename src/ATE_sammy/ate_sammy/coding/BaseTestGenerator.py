
import os

from jinja2 import Environment
from jinja2 import FileSystemLoader

from ate_sammy.coding.generator_utils import prepare_module_docstring


def prepare_input_parameters_ppd(ip):
    '''Test Input Parameters Pretty Print Dict.

    This function creates a list of strings that 'pretty print' the dictionary.
    '''

    retval = []
    for index, param in enumerate(ip):
        if index == len(ip) - 1:
            line = f"'{param}': {ip[param]}}}"
        else:
            line = f"'{param}': {ip[param]},"
        line = line.replace('nan', 'np.nan')
        line = line.replace('inf', 'np.inf')
        retval.append(line)
    return retval


def prepare_output_parameters_ppd(op):
    """Test Output Parameters Pretty Print Dict.

    This function creates a list of strings that 'pretty print' the dictionary.
    """

    retval = []
    for index, param in enumerate(op):
        if index == len(op) - 1:
            line = f"'{param}': {op[param]}}}"
        else:
            line = f"'{param}': {op[param]},"
        line = line.replace('nan', 'np.nan')
        line = line.replace('inf', 'np.inf')
        retval.append(line)
    return retval


class BaseTestGenerator:
    """Generator for the Test Base Class."""

    def __init__(self, template_dir, project_path, definition, file_name):
        template_path = os.path.normpath(template_dir)
        file_loader = FileSystemLoader(template_path)
        env = Environment(loader=file_loader)
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.rstrip_blocks = True
        template_name = str(self.__class__.__name__).split('.')[-1].split(' ')[0]
        template_name = template_name.replace('generator', 'template') + '.jinja2'
        template = env.get_template(template_name)
        self.definition = definition
        self.project_path = project_path

        rel_path_to_dir = self._generate_relative_path()
        abs_path_to_dir = os.path.join(self.project_path, rel_path_to_dir)
        self.abs_path_to_file = os.path.join(abs_path_to_dir, file_name)
        if not os.path.exists(abs_path_to_dir):
            os.makedirs(abs_path_to_dir)

        render_data = self._generate_render_data(abs_path_to_dir)
        msg = self._render(template, render_data)

        self._generate(self.abs_path_to_file, msg)

    @staticmethod
    def _generate(path, msg):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(msg)

    def _generate_relative_path(self):
        return ''

    def _generate_render_data(self, abs_path=''):
        return {}

    def _render(self, template, render_data):
        return ''


class test_base_generator(BaseTestGenerator):
    """Generator for the Test Base Class."""

    def __init__(self, template_path, project_path, definition):
        file_name = f"{definition['name']}_BC.py"
        super().__init__(template_path, project_path, definition, file_name)

    def _generate_relative_path(self):
        hardware = self.definition['hardware']
        base = self.definition['base']
        name = self.definition['name']

        return os.path.join('src', hardware, base, name)

    def _render_parameters(self, parameter_type):
        paramlist = []
        for op in self.definition[parameter_type]:
            the_param = {}
            the_param['name'] = op
            the_param.update(self.definition[parameter_type][op])
            paramlist.append(the_param)
        return paramlist

    def _generate_render_data(self, abs_path=''):
        output_params = self._render_parameters('output_parameters')
        input_params = self._render_parameters('input_parameters')

        return {'module_doc_string': prepare_module_docstring(),
                'ipppd': prepare_input_parameters_ppd(self.definition['input_parameters']),
                'opppd': prepare_output_parameters_ppd(self.definition['output_parameters']),
                'definition': self.definition,
                'output_params': output_params,
                'input_params': input_params}

    def _render(self, template, render_data):
        return template.render(module_doc_String=render_data['module_doc_string'],
                               definition=self.definition,
                               ipppd=render_data['ipppd'],
                               opppd=render_data['opppd'],
                               output_params=render_data['output_params'],
                               input_params=render_data['input_params'])
