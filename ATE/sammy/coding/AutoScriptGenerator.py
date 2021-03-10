from jinja2 import Environment
from jinja2 import FileSystemLoader
import os


class AutoScriptGenerator:
    def __init__(self, template_dir, file_name):
        template_path = os.path.normpath(template_dir)
        file_loader = FileSystemLoader(template_path)
        env = Environment(loader=file_loader)
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.rstrip_blocks = True
        template_name = 'auto_script_template.jinja2'
        if not os.path.exists(os.path.join(template_path, template_name)):
            raise Exception(f"couldn't find the template : {template_name}")

        template = env.get_template(template_name)
        output = template.render()
        with open(file_name, 'w', encoding='utf-8') as fd:
            fd.write(output)
