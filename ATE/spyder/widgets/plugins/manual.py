# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 14:39:41 2020

@author: hoeren
"""
import json
import os
import shutil
import tempfile

from cookiecutter.main import cookiecutter


dir_name = os.path.dirname(__file__)

project_root = os.path.join(dir_name, 'trial')  # this we get from spyder
shutil.rmtree(project_root)  # remove if exists
os.mkdir(project_root) # create new
os.mkdir(os.path.join(project_root, '.spyproject'))  # simulate spyder having created the base.

temp_path = tempfile.mkdtemp()
os.chdir(temp_path)


template = "gh:ate-org/Semi-ATE-Plugin-cookiecutter"

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

print(f"created project in '{project_dir}'")







#shutil.rmtree(temp_path)







os.chdir(target)
source = os.path.join(dir_name, "template")
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

print(f"created project in '{project_dir}'")
