# ATE.spyder.widgets.plugins

This directory holds the goods when it comes to plugins for Semi-ATE itself. (not to be confused with the plugin for spyder)

The template is comming is comming from : [ate-org/Semi-ATE-Plugin-cookiecutter](https://github.com/ate-org/Semi-ATE-Plugin-cookiecutter)
which itself is a fork from `audreyr/cookiecutter-pypackage`. We de-couple it so that
fine-tuning doesn't require new releases of `Semi-ATE` itself!

The `Semi_ATE_Plugin_Wizard.ui` & `Semi_ATE_Plugin_Wizard.py` define the 'parameters'.



gist:
```python
import os
import json
from cookiecutter.main import cookiecutter


distutils.dir_util.copy_tree(src, dst)

target = r"C:\cc"
os.chdir(target)
source = os.path.join(os.path.dirname(__file__), "template")
json_path = os.path.join(source, "cookiecutter.json")

data = {
  "full_name": "Audrey Roy Greenfeld",
  "email": "audreyr@example.com",
  "github_username": "audreyr",
  "project_name": "Python Boilerplate",
  "project_slug": "{{ cookiecutter.project_name.lower().replace(' ', '_').replace('-', '_') }}",
  "project_short_description": "Python Boilerplate contains all the boilerplate you need to create a Python package.",
  "pypi_username": "{{ cookiecutter.github_username }}",
  "version": "0.1.0",
  "use_pytest": "n",
  "use_pypi_deployment_with_travis": "y",
  "add_pyup_badge": "n",
  "command_line_interface": ["Click", "Argparse", "No command-line interface"],
  "create_author_file": "y",
  "open_source_license": ["MIT license", "BSD license", "ISC license", "Apache Software License 2.0", "GNU General Public License v3", "Not open source"]
}

with open(json_path, 'w') as fd:
	json.dump(data, fd)

project_dir = cookiecutter(source)









```

The .json with the  is the structure of the 'Semi-ATE Plugin' project.
It works on the basis of jinja2 (also in the naming)
