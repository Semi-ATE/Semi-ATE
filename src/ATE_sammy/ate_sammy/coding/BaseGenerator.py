import os

from jinja2 import Environment
from jinja2 import FileSystemLoader


class BaseGenerator:
    """ Base Geneartor """

    def __init__(self, template_dir, project_path, definition, file_name, template_file_name=None):
        template_path = os.path.normpath(template_dir)
        file_loader = FileSystemLoader(template_path)
        env = Environment(loader=file_loader)
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.rstrip_blocks = True
        template_name = template_file_name
        if template_name is None:
            template_name = str(self.__class__.__name__).split('.')[-1].split(' ')[0]
            template_name = template_name.replace('generator', 'template') + '.jinja2'
        if not os.path.exists(os.path.join(template_path, template_name)):
            raise Exception(f"couldn't find the template : {template_name} in {template_path}")
        template = env.get_template(template_name)

        self.definition = definition

        rel_path_to_dir = self._generate_relative_path()
        abs_path_to_dir = os.path.join(project_path, rel_path_to_dir)
        abs_path_to_file = os.path.join(abs_path_to_dir, file_name)

        if not os.path.exists(abs_path_to_dir):
            os.makedirs(abs_path_to_dir)

        if os.path.exists(abs_path_to_file):
            os.remove(abs_path_to_file)

        msg = template.render(definition=self.definition)

        with open(abs_path_to_file, 'w', encoding='utf-8') as fd:
            fd.write(msg)

    def _generate_relative_path(self):
        return ''
