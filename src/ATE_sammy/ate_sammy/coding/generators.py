#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 07:22:29 2020

@author: tom

References:
    PEP8 : https://www.python.org/dev/peps/pep-0008/
    numpy doc style : https://numpydoc.readthedocs.io/en/latest/format.html


There are four (4) entries to the generators from outside:
    1. project_generator
    2. hardware_generator
    3. test_generator
    4. program_generator

all other generators are called by these 4 'top level' generators.



"""
import os
import shutil
from pathlib import Path

from jinja2 import Environment
from jinja2 import FileSystemLoader

from ate_sammy.coding.BaseGenerator import BaseGenerator
from ate_sammy.coding.ProperGenerator import test_proper_generator
from ate_sammy.coding.BaseTestGenerator import test_base_generator, BaseTestGenerator
from ate_projectdatabase import latest_semi_ate_project_db_version, Test, Hardware
from ate_sammy.coding.AutoScriptGenerator import AutoScriptGenerator
from ate_sammy.coding.TestRunnerMainGenerator import test_runner_generator


def project_generator(template_path, project_path):
    """This function generates the

    This generator should be called upon the creation of a new project.
    It will subsequently call the following generators:
        - spyder_generator
        - doc_generator
        - src__init__generator
    """
    project_root_generator(template_path, project_path)
    src__init__generator(template_path, project_path)
    src_common_generator(template_path, project_path)
    project_doc_generator(template_path, project_path)

    Path(project_path).joinpath('pattern').mkdir(exist_ok=True)


def hardware_generator(template_path, project_path, hardware):
    """Generator for a new hardware structure."""

    HW__init__generator(template_path, project_path, hardware)

    PR__init__generator(template_path, project_path, hardware)
    PR_common_generator(template_path, project_path, hardware)

    FT__init__generator(template_path, project_path, hardware)
    FT_common_generator(template_path, project_path, hardware)

    AutoScriptGenerator(template_path, project_path, hardware)

    create_pattern_hardware_folder(Path(project_path), hardware)


def create_pattern_hardware_folder(project_path: Path, hardware_db: dict):
    project_path.joinpath('pattern').mkdir(exist_ok=True)
    project_path.joinpath('pattern', hardware_db['hardware']).mkdir(exist_ok=True)

    # for each testing phase (e.g. `probing` and `final`) a folder is generated automatically
    project_path.joinpath('pattern', hardware_db['hardware'], 'PR').mkdir(exist_ok=True)
    project_path.joinpath('pattern', hardware_db['hardware'], 'FT').mkdir(exist_ok=True)


def test_generator(template_path, project_path, definition):
    test_base_generator(template_path, project_path, definition)
    test_proper_generator(template_path, project_path, definition)
    test__init__generator(template_path, project_path, definition)


def test_update(template_path, project_path, definition):
    test_base_generator(template_path, project_path, definition)
    test_proper_generator(template_path, project_path, definition, do_update=True)


def test_runner_main_generator(template_path: Path, project_path: Path, file_path: Path, test_configuration: Test, hardware_definition: Hardware):
    test_runner_generator(Path(template_path), project_path, file_path, test_configuration, hardware_definition)


def copydir(source, destination, ignore_dunder=True):
    """This function copies everything under 'source' to 'destination' recursively.

    If 'destination' doesn't exits, it will be created.
    If ignore_dunder is True (default), any file or directory starting with
    double underscore (__*) is ignored.
    """

    if not os.path.exists(destination):
        os.makedirs(destination, exist_ok=True)

    for root, dirs, files in os.walk(source):
        rel_path = root.replace(source, '')
        if rel_path.startswith(os.path.sep):
            rel_path = rel_path[1:]

        for Dir in dirs:
            if ignore_dunder and Dir.startswith('__'):
                continue
            dir_to_create = os.path.join(destination, rel_path, Dir)
            os.makedirs(dir_to_create, exist_ok=True)

        for File in files:
            if ignore_dunder and File.startswith('__'):
                continue
            from_path = os.path.join(root, File)
            to_path = os.path.join(destination, rel_path, File)
            destination_directory = os.path.dirname(to_path)
            if not os.path.exists(destination_directory):
                os.makedirs(destination_directory, exist_ok=True)
            shutil.copy(from_path, to_path)


class test__init__generator(BaseTestGenerator):
    """Generator for the __init__.py file of a given test."""

    def __init__(self, template_path, project_path, definition):
        file_name = '__init__.py'
        super().__init__(template_path, project_path, definition, file_name)
        self.defintion = definition

    def _generate_relative_path(self):
        hardware = self.definition['hardware']
        base = self.definition['base']
        name = self.definition['name']

        return self.project_path.joinpath(Path(self.project_path).name, hardware, base, name)

    def _generate_render_data(self, abs_path):
        imports = []
        for item in os.listdir(abs_path):
            if item.upper().endswith('_BC.PY'):
                what = '.'.join(item.split('.')[:-1])
                imports.append(f"from {what} import {what}")

        return {'hardware': self.definition['hardware'],
                'base': self.definition['base'],
                'name': self.definition['name'],
                'imports': imports}

    def _render(self, template, render_data):
        return template.render(hardware=render_data['hardware'],
                               base=render_data['base'],
                               name=render_data['name'],
                               imports=render_data['imports'])


def project_root_generator(template_dir, project_path):
    """This function will create the base project structure.

    Here we put everything that live in ther project root.
    """
    project__main__generator(template_dir, project_path)
    project__init__generator(template_dir, project_path)
    project_gitignore_generator(template_dir, project_path)
    project_setup_file_generator(template_dir, project_path)
    project_defintinion_generator(project_path)


def project_doc_generator(template_dir, project_path):
    """This function will create and populate the 'doc' directory under the project root.

    This generator should be called **ONCE** upon the creation of a new project.
    It copies the contents of templates/doc/* to the project doc.
    """

    template_path = os.path.normpath(template_dir)
    doc_src_path = os.path.join(template_path, 'doc')
    doc_dst_path = os.path.join(project_path, 'doc')

    copydir(doc_src_path, doc_dst_path)


def project_defintinion_generator(project_path):
    definition_path = os.path.join(project_path, "definitions")
    os.makedirs(definition_path, exist_ok=True)
    _make_definition_dir(definition_path, "device")
    _make_definition_dir(definition_path, "die")
    _make_definition_dir(definition_path, "hardware")
    _make_definition_dir(definition_path, "masksets")
    _make_definition_dir(definition_path, "package")
    _make_definition_dir(definition_path, "product")
    _make_definition_dir(definition_path, "program")
    _make_definition_dir(definition_path, "sequence")
    _make_definition_dir(definition_path, "test")
    _make_definition_dir(definition_path, "testtarget")
    _make_definition_dir(definition_path, "qualification")
    _make_definition_dir(definition_path, "group")
    _make_definition_dir(definition_path, "settings")
    _generate_version_file(definition_path)


def _generate_version_file(definition_path):
    _make_definition_dir(definition_path, "version")
    import os
    import json
    from pathlib import Path
    path = os.path.join(definition_path, "version", "version.json")
    with open(os.fspath(Path(path)), 'w') as f:
        json.dump([{"version": latest_semi_ate_project_db_version}], f, indent=4)


def _make_definition_dir(root, dir_name):
    os.makedirs(os.path.join(root, dir_name), exist_ok=True)
    # add git markerfile so that this directory survives if the project is
    # checked in while there are no relevant files there:
    f = open(os.path.join(root, dir_name, ".gitkeep"), "a")
    f.close()


class BaseProjectGenerator:
    """Generator for the project's __main__.py file."""

    def __init__(self, template_dir: str, project_path: str, file_name: str, template_name: str = ''):
        template_path = os.path.normpath(template_dir)
        file_loader = FileSystemLoader(template_path)
        env = Environment(loader=file_loader)
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.rstrip_blocks = True
        if not template_name:
            template_name = str(self.__class__.__name__).split('.')[-1].split(' ')[0]
            template_name = template_name.replace('generator', 'template') + '.jinja2'
        if not os.path.exists(os.path.join(template_path, template_name)):
            raise Exception(f"couldn't find the template : {template_name}")
        template = env.get_template(template_name)

        project_name = os.path.basename(project_path)

        rel_path_to_dir = self._generate_relative_path()
        abs_path_to_dir = os.path.join(project_path, rel_path_to_dir)
        abs_path_to_file = os.path.join(abs_path_to_dir, file_name)

        msg = template.render(project_name=project_name)

        if not os.path.exists(abs_path_to_dir):
            os.makedirs(abs_path_to_dir)

        with open(abs_path_to_file, 'w', encoding='utf-8') as f:
            f.write(msg)

    def _generate_relative_path(self):
        return ''


class project__main__generator(BaseProjectGenerator):
    """Generator for the project's __main__.py file."""

    def __init__(self, template_dir, project_path, file_name='__main__.py'):
        super().__init__(template_dir, project_path, file_name)


class project_setup_file_generator(BaseProjectGenerator):
    """Generator for the project's setup.py file."""
    def __init__(self, template_dir, project_path, file_name='setup.py'):
        super().__init__(template_dir, project_path, file_name, template_name='project_setup_file_template.jinja2')


class project__init__generator(BaseProjectGenerator):
    """Generator for the project's __init__.py file."""

    def __init__(self, template_dir, project_path, file_name='__init__.py'):
        super().__init__(template_dir, project_path, file_name)


class project_gitignore_generator(BaseProjectGenerator):
    """Generator for the project's .gitignore file."""

    def __init__(self, template_dir, project_path, file_name='.gitignore'):
        super().__init__(template_dir, project_path, file_name)


class src__init__generator(BaseProjectGenerator):
    """Generator for the __init__.py file of the src (root)

    This file contains nothing more than "system wide" 'constants'

    This generator should be called upon the creation of a new project.
    """

    def __init__(self, template_dir, project_path, file_name='__init__.py'):
        self.project_name = Path(project_path).name
        super().__init__(template_dir, project_path, file_name)

    def _generate_relative_path(self):
        return self.project_name


class src_common_generator(src__init__generator):
    """Generator for the common.py file of the src (root)

    This file contains nothing more than "system wide" functionality.

    This generator should be called upon the creation of a new project.
    """

    def __init__(self, project_path, file_name='common.py'):
        super().__init__(project_path, file_name)


class HW__init__generator(BaseGenerator):
    """Generator for the __init__.py file of the hardware proper."""

    def __init__(self, template_path, project_path, definition, file_name="__init__.py"):
        super().__init__(template_path, project_path, definition, file_name)

    def _generate_relative_path(self):
        return Path(self.project_path).joinpath(self.project_path.name, self.definition['hardware'])


class HW_common_generator(HW__init__generator):
    """Generator for the common.py file of of the hardware proper."""

    def __init__(self, template_path, project_path, definition, file_name='common.py'):
        super().__init__(template_path, project_path, definition, file_name)


class Base_Source_generator(BaseGenerator):
    def __init__(self, base_name, template_path, project_path, definition, file_name='__init__.py', template_file_name=None):
        self.base_name = base_name
        definition["active_base"] = base_name
        super().__init__(template_path, project_path, definition, file_name, template_file_name)

    def _generate_relative_path(self):
        return self.project_path.joinpath(self.project_path.name, self.definition['hardware'], self.base_name)


class PR__init__generator(Base_Source_generator):
    """Generator for the __init__.py file of 'PR' for the given hardware."""

    def __init__(self, template_path, project_path, definition, file_name='__init__.py'):
        super().__init__('PR', template_path, project_path, definition, file_name, template_file_name="base_init_template.jinja2")


class FT__init__generator(Base_Source_generator):
    """Generator for the __init__.py file of 'FT' for the given hardware."""

    def __init__(self, template_path, project_path, definition, file_name='__init__.py'):
        super().__init__('FT', template_path, project_path, definition, file_name, template_file_name="base_init_template.jinja2")


class BaseCommonGenerator:
    """Generator for the project's __main__.py file."""

    def __init__(self, template_dir: str, project_path: str, definition: dict):
        from pathlib import Path
        template_path = Path(template_dir)
        file_loader = FileSystemLoader(template_path)
        env = Environment(loader=file_loader)
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.rstrip_blocks = True
        template_name = 'base_common_template.jinja2'
        if not template_path.joinpath(template_name).exists():
            raise Exception(f"couldn't find the template : {template_name}")
        template = env.get_template(template_name)

        abs_path_to_dir = Path(project_path).joinpath(Path(project_path).name, definition['hardware'], definition['active_base'])
        abs_path_to_file = abs_path_to_dir.joinpath('common.py')

        # in this section, the concrete type of the tester will be extracted and used to generate the code.
        # this is necessary to type hint the tester instance which provides the IDE with the information needed to support the autocompletion
        from ate_semiateplugins.pluginmanager import get_plugin_manager
        tester_types = get_plugin_manager().hook.get_tester_type(tester_name=definition['tester'])
        if not tester_types:
            print('''selected type not found within the supported tester types
                this is not an error but the user will not have any IDE support (e.g autocompletion)
            ''')
            module_name = 'object'
            module_path = ''
            module_import = ''
        else:
            module_name = get_plugin_manager().hook.get_tester_type(tester_name=definition['tester'])[0].__name__
            module_path = get_plugin_manager().hook.get_tester_type(tester_name=definition['tester'])[0].__module__
            module_import = f'from {module_path} import {module_name}'

        msg = template.render(definition=definition, module_import=module_import, module_name=module_name)

        if not abs_path_to_dir.exists():
            os.makedirs(abs_path_to_dir)

        with open(abs_path_to_file, 'w', encoding='utf-8') as f:
            f.write(msg)


class FT_common_generator(BaseCommonGenerator):
    """Generator for the common.py file of 'FT' for the given hardware."""

    def __init__(self, template_path, project_path, definition):
        definition["active_base"] = 'FT'
        super().__init__(template_path, project_path, definition)


class PR_common_generator(BaseCommonGenerator):
    """Generator for the common.py file of 'PR' for the given hardware."""

    def __init__(self, template_path, project_path, definition):
        definition["active_base"] = 'PR'
        super().__init__(template_path, project_path, definition)
