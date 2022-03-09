import os
from ate_sammy.verbs.migrate import Migrate
from ate_sammy.verbs.generate import Generate
from argparse import Namespace

def generate_new(project_dir: str):
    cwd = os.path.dirname(project_dir)
    allargs = Namespace(verb='generate', noun='new', params=[project_dir])
    template_base_path = os.path.join(os.path.dirname(__file__), 'templates')
    Generate(template_base_path).run(cwd, allargs)
