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
import numpy as np
from ATE.utils.DT import DT
import getpass
from jinja2 import FileSystemLoader, Environment


def project_generator(project_path):
    """This function generates the

    This generator should be called upon the creation of a new project.
    It will subsequently call the following generators:
        - spyder_generator
        - doc_generator
        - src__init__generator
    """
    project_root_generator(project_path)
    src__init__generator(project_path)
    src_common_generator(project_path)
    project_doc_generator(project_path)
    project_spyder_generator(project_path)


def hardware_generator(project_path, hardware):
    """Generator for a new hardware structure."""

    HW__init__generator(project_path, hardware)
    HW_common_generator(project_path, hardware)

    PR__init__generator(project_path, hardware)
    PR_common_generator(project_path, hardware)

    FT__init__generator(project_path, hardware)
    FT_common_generator(project_path, hardware)


def test_generator(project_path, definition):
    test_base_generator(project_path, definition)
    test_proper_generator(project_path, definition)
    test__init__generator(project_path, definition)


def program_generator(definition):
    pass


##############################################################################
# The below generators are 'private', they are used by the generators above. #
##############################################################################


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


def prepare_module_docstring():
    retval = []

    line = f"Created on {str(DT())}"
    retval.append(line)

    line = "By "
    user = getpass.getuser()
    line += user
    domain = str(os.environ.get('USERDNSDOMAIN'))
    if domain != 'None':
        line += f" ({user}@{domain})".lower()
    retval.append(line)
    return retval


def prepare_input_parameters_table(ip):
    """Generates a list of strings, holding a talble (with header) of the input parameters"""

    retval = []
    name_ = 0
    Shmoo_ = 3  # True = Yes, False = No
    Min_ = 0
    Default_ = 0
    Max_ = 0
    Unit_ = 0
    fmt_ = 0
    for param in ip:
        if len(f"ip.{param}") > name_:
            name_ = len(f"ip.{param}")
    # Min --> number or -inf (no nan)
        if np.isinf(ip[param]['Min']):
            length = len('-∞')
            if Min_ < length:
                Min_ = length
        elif np.isnan(ip[param]['Min']):
            raise Exception(f"ip.{param}['Min'] == np.nan ... not possible !")
        else:
            length = len(f"{ip[param]['Min']:{ip[param]['fmt']}}")
            if Min_ < length:
                Min_ = length
    # Default --> number (no nan or inf)
        if np.isinf(ip[param]['Default']):
            raise Exception(f"ip.{param}['Default'] == ±np.inf ... not possible !")
        elif np.isnan(ip[param]['Default']):
            raise Exception(f"ip.{param}['Default'] == np.nan ... not possible !")
        else:
            length = len(f"{ip[param]['Default']:{ip[param]['fmt']}}")
            if Default_ < length:
                Default_ = length
    # Max --> number or inf (no nan)
        if np.isinf(ip[param]['Max']):
            length = len('+∞')
            if Max_ < length:
                Max_ = length
        elif np.isnan(ip[param]['Max']):
            raise Exception(f"ip.{param}['Max'] == np.nan ... not possible !")
        else:
            length = len(f"{ip[param]['Max']:{ip[param]['fmt']}}")
            if Max_ < length:
                Max_ = length
    # combined Unit
        length = len(f"{ip[param]['10ᵡ']}{ip[param]['Unit']}")
        if Unit_ < length:
            Unit_ = length
    # format
        length = len(f"{ip[param]['fmt']}")
        if fmt_ < length:
            fmt_ = length

    length = len('Input Parameter')
    if name_ < length:
        name_ = length

    length = len('Shmoo')
    if Shmoo_ < length:
        Shmoo_ = length

    length = len('Min')
    if Min_ < length:
        Min_ = length

    length = len('Default')
    if Default_ < length:
        Default_ = length

    length = len('Max')
    if Max_ < length:
        Max_ = length

    length = len('Unit')
    if Unit_ < length:
        Unit_ = length

    length = len('fmt')
    if fmt_ < length:
        fmt_ = length

    th = f"{'Input Parameter':<{name_}} | "
    th += f"{'Shmoo':^{Shmoo_}} | "
    th += f"{'Min':>{Min_}} | "
    th += f"{'Default':^{Default_}} | "
    th += f"{'Max':<{Max_}} | "
    th += f"{'Unit':>{Unit_}} | "
    th += f"{'fmt':>{fmt_}}"
    retval.append(th)

    bh = '-' * (name_ + 1) + '+'
    bh += '-' * (Shmoo_ + 2) + '+'
    bh += '-' * (Min_ + 2) + '+'
    bh += '-' * (Default_ + 2) + '+'
    bh += '-' * (Max_ + 2) + '+'
    bh += '-' * (Unit_ + 2) + '+'
    bh += '-' * (fmt_ + 1)
    retval.append(bh)

    for index, param in enumerate(ip):
        name = f"ip.{param}"
        Name = f"{name:{name_}} | "
    # Shmoo
        if ip[param]['Shmoo'] is True:
            Shmoo = f"{'Yes':^{Shmoo_}} | "
        else:
            Shmoo = f"{'No':^{Shmoo_}} | "
    # Min
        if np.isinf(ip[param]['Min']):
            Min = f"{'-∞':>{Min_}} | "
        else:
            Min = f"{ip[param]['Min']:>{Min_}{ip[param]['fmt']}} | "
    # Default
        Default = f"{ip[param]['Default']:^{Default_}{ip[param]['fmt']}} | "
    # Max
        if np.isinf(ip[param]['Max']):
            Max = f"{'+∞':<{Max_}} | "
        else:
            Max = f"{ip[param]['Max']:<{Max_}{ip[param]['fmt']}} | "
    # Unit
        cu = ip[param]['10ᵡ'] + ip[param]['Unit']
        Unit = f"{cu:<{Unit_}} | "
    # format
        Fmt = f"{ip[param]['fmt']:<{fmt_}}"

        line = Name + Shmoo + Min + Default + Max + Unit + Fmt
        retval.append(line)
    return retval


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


def prepare_output_parameters_table(op):
    """Generates a list of strings, holding a talble (with header) of the output parameters"""

    retval = []
    name_ = 0
    LSL_ = 0
    LTL_ = 0
    Nom_ = 0
    UTL_ = 0
    USL_ = 0
    mul_ = 0
    unit_ = 0
    fmt_ = 0
    for param in op:
        if len(f"op.{param}") > name_:
            name_ = len(f"op.{param}")
    # LSL --> inf or number (no nan)
        if np.isinf(op[param]['LSL']):
            if LSL_ < 2:
                LSL_ = 2  # len('-∞') = 2
        else:
            length = len(f"{op[param]['LSL']:{op[param]['fmt']}}")
            if LSL_ < length:
                LSL_ = length
    # LTL --> inf, nan or number
        if np.isinf(op[param]['LTL']):
            if LTL_ < 2:
                LTL_ = 2  # len('-∞') = 2
        elif np.isnan(op[param]['LTL']):
            if not np.isinf(op[param]['LSL']):
                length = len(f"{op[param]['LSL']:{op[param]['fmt']}}") + 2  # the '()' around
                if LTL_ < length:
                    LTL_ = length
        else:
            length = len(f"{op[param]['LTL']:{op[param]['fmt']}}")
            if LTL_ < length:
                LTL_ = length
    # Nom --> number (no inf, no nan)
        length = len(f"{op[param]['Nom']:{op[param]['fmt']}}")
        if length > Nom_:
            Nom_ = length
    # UTL --> inf, nan or number
        if np.isinf(op[param]['UTL']):
            if UTL_ < 2:
                UTL_ = 2
        elif np.isnan(op[param]['UTL']):
            if not np.isinf(op[param]['USL']):
                length = len(f"{op[param]['USL']:{op[param]['fmt']}}") + 2
                if UTL_ < length:
                    UTL_ = length
        else:
            length = len(f"{op[param]['UTL']:{op[param]['fmt']}}")
            if UTL_ < length:
                UTL_ = length
    # USL --> inf or number (not nan)
        if np.isinf(op[param]['USL']):
            if 4 > USL_:
                USL_ = 4
        else:
            length = len(f"{op[param]['USL']:{op[param]['fmt']}}")
            if length > USL_:
                USL_ = length

        if len(f"{op[param]['10ᵡ']}") > mul_:
            mul_ = len(f"{op[param]['10ᵡ']}")

        if len(f"{op[param]['Unit']}") > unit_:
            unit_ = len(f"{op[param]['Unit']}")

        if len(f"{op[param]['fmt']}") > fmt_:
            fmt_ = len(f"{op[param]['fmt']}")

    length = len('Output Parameters')
    if name_ < length:
        name_ = length

    length = len('LSL')
    if LSL_ < length:
        LSL_ = length

    length = len('(LTL)')
    if LTL_ < length:
        LTL_ = length

    length = len('(UTL)')
    if UTL_ < length:
        UTL_ = length

    length = len('USL')
    if USL_ < length:
        USL_ = length

    Unit_ = mul_ + unit_
    length = len('Unit')
    if Unit_ < length:
        Unit_ = length

    length = len('fmt')
    if fmt_ < length:
        fmt_ = length

    th = f"{'Parameter':<{name_}} | "
    th += f"{'LSL':>{LSL_}} | "
    th += f"{'(LTL)':>{LTL_}} | "
    th += f"{'Nom':^{Nom_}} | "
    th += f"{'(UTL)':<{UTL_}} | "
    th += f"{'USL':<{USL_}} | "
    th += f"{'Unit':>{Unit_}} | "
    th += f"{'fmt':>{fmt_}}"
    retval.append(th)

    bh = '-' * (name_ + 1) + '+'
    bh += '-' * (LSL_ + 2) + '+'
    bh += '-' * (LTL_ + 2) + '+'
    bh += '-' * (Nom_ + 2) + '+'
    bh += '-' * (UTL_ + 2) + '+'
    bh += '-' * (USL_ + 2) + '+'
    bh += '-' * (Unit_ + 2) + '+'
    bh += '-' * (fmt_ + 1)
    retval.append(bh)

    for index, param in enumerate(op):
        name = f"op.{param}"
        Name = f"{name:<{name_}} | "
    # LSL
        if np.isinf(op[param]['LSL']):
            LSL = f"{'-∞':>{LSL_}} | "
        else:
            LSL = f"{op[param]['LSL']:>{LSL_}{op[param]['fmt']}} | "
    # LTL
        if np.isinf(op[param]['LTL']):
            LTL = f"{'-∞':>{LTL_}} | "
        elif np.isnan(op[param]['LTL']):
            if np.isinf(op[param]['LSL']):
                LTL = f"{'(-∞)':>{LTL_}} | "
            else:
                ltl = f"({op[param]['LSL']:{op[param]['fmt']}})"
                LTL = f"{ltl:>{LTL_}} | "
        else:
            LTL = f"{op[param]['LTL']:>{LTL_}{op[param]['fmt']}} | "
    # Nom
        Nom = f"{op[param]['Nom']:^{Nom_}{op[param]['fmt']}} | "
    # UTL
        if np.isinf(op[param]['UTL']):
            UTL = f"{'+∞':<{UTL_}} | "
        elif np.isnan(op[param]['UTL']):
            if np.isinf(op[param]['USL']):
                UTL = f"{'(+∞)':<{UTL_}} | "
            else:
                utl = f"({op[param]['USL']:{op[param]['fmt']}})"
                UTL = f"{utl:<{UTL_}} | "
        else:
            UTL = f"{op[param]['UTL']:<{UTL_}{op[param]['fmt']}} | "
    # USL
        if np.isinf(op[param]['USL']):
            USL = f"{'+∞':<{USL_}} | "
        else:
            USL = f"{op[param]['USL']:<{USL_}{op[param]['fmt']}} | "
    # Unit
        cu = op[param]['10ᵡ'] + op[param]['Unit']
        Unit = f"{cu:<{Unit_}} | "
    # format
        Fmt = f"{op[param]['fmt']:<{fmt_}}"

        line = Name + LSL + LTL + Nom + UTL + USL + Unit + Fmt
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

    def __init__(self, project_path, definition, file_name):
        template_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
        file_loader = FileSystemLoader(template_path)
        env = Environment(loader=file_loader)
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.rstrip_blocks = True
        template_name = str(self.__class__.__name__).split('.')[-1].split(' ')[0]
        template_name = template_name.replace('generator', 'template') + '.jinja2'
        template = env.get_template(template_name)
        self.definition = definition

        rel_path_to_dir = self._generate_relative_path()
        abs_path_to_dir = os.path.join(project_path, rel_path_to_dir)
        abs_path_to_file = os.path.join(abs_path_to_dir, file_name)

        render_data = self._generate_render_data(abs_path_to_dir)
        msg = self._render(template, render_data)

        if not os.path.exists(abs_path_to_dir):
            os.makedirs(abs_path_to_dir)

        with open(abs_path_to_file, 'w', encoding='utf-8') as f:
            f.write(msg)

    def _generate_relative_path(self):
        return ''

    def _generate_render_data(self, abs_path=''):
        return {}

    def _render(self, template, render_data):
        return ''


class test_proper_generator(BaseTestGenerator):
    """Generator for the Test Class."""

    def __init__(self, project_path, definition):
        file_name = f"{definition['name']}.py"
        super().__init__(project_path, definition, file_name)

    def _generate_relative_path(self):
        hardware = self.definition['hardware']
        base = self.definition['base']
        name = self.definition['name']

        return os.path.join('src', hardware, base, name)

    def _generate_render_data(self, abs_path=''):
        return {'module_doc_string': prepare_module_docstring(),
                'input_parameter_table': prepare_input_parameters_table(self.definition['input_parameters']),
                'output_parameter_table': prepare_output_parameters_table(self.definition['output_parameters']),
                'definition': self.definition}

    def _render(self, template, render_data):
        return template.render(module_doc_string=render_data['module_doc_string'],
                               input_parameter_table=render_data['input_parameter_table'],
                               output_parameter_table=render_data['output_parameter_table'],
                               definition=self.definition)


class test_base_generator(BaseTestGenerator):
    """Generator for the Test Base Class."""

    def __init__(self, project_path, definition):
        file_name = f"{definition['name']}_BC.py"
        super().__init__(project_path, definition, file_name)

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


class test__init__generator(BaseTestGenerator):
    """Generator for the __init__.py file of a given test."""

    def __init__(self, project_path, definition):
        file_name = '__init__.py'
        super().__init__(project_path, definition, file_name)
        self.defintion = definition

    def _generate_relative_path(self):
        hardware = self.definition['hardware']
        base = self.definition['base']
        name = self.definition['name']

        return os.path.join('src', hardware, base, name)

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


def project_root_generator(project_path):
    """This function will create the base project structure.

    Here we put all the **FILES** that live in ther project root.
    """

    os.makedirs(project_path)
    project__main__generator(project_path)
    project__init__generator(project_path)
    project_gitignore_generator(project_path)


def project_doc_generator(project_path):
    """This function will create and populate the 'doc' directory under the project root.

    This generator should be called **ONCE** upon the creation of a new project.
    It copies the contents of templates/doc/* to the project doc.
    """

    template_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    doc_src_path = os.path.join(template_path, 'doc')
    doc_dst_path = os.path.join(project_path, 'doc')

    copydir(doc_src_path, doc_dst_path)


def project_spyder_generator(project_path):
    """This function will create and populate the project with spyder config files.

    This generator should be called **ONCE** upon the creation of a new project.
    """

    template_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    spyder_src_path = os.path.join(template_path, 'spyder')
    spyder_dst_path = os.path.join(project_path, '.spyproject')

    copydir(spyder_src_path, spyder_dst_path)


class BaseGenerator:
    """ Base Geneartor """

    def __init__(self, project_path, definition, file_name):
        template_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
        file_loader = FileSystemLoader(template_path)
        env = Environment(loader=file_loader)
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.rstrip_blocks = True
        template_name = str(self.__class__.__name__).split('.')[-1].split(' ')[0]
        template_name = template_name.replace('generator', 'template') + '.jinja2'
        if not os.path.exists(os.path.join(template_path, template_name)):
            raise Exception(f"couldn't find the template : {template_name}")
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


class BaseProjectGenerator:
    """Generator for the project's __main__.py file."""

    def __init__(self, project_path, file_name):
        template_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
        file_loader = FileSystemLoader(template_path)
        env = Environment(loader=file_loader)
        env.trim_blocks = True
        env.lstrip_blocks = True
        env.rstrip_blocks = True
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

    def __init__(self, project_path, file_name='__main__.py'):
        super().__init__(project_path, file_name)


class project__init__generator(BaseProjectGenerator):
    """Generator for the project's __init__.py file."""

    def __init__(self, project_path, file_name='__init__.py'):
        super().__init__(project_path, file_name)


class project_gitignore_generator(BaseProjectGenerator):
    """Generator for the project's .gitignore file."""

    def __init__(self, project_path, file_name='.gitignore'):
        super().__init__(project_path, file_name)


class src__init__generator(BaseProjectGenerator):
    """Generator for the __init__.py file of the src (root)

    This file contains nothing more than "system wide" 'constants'

    This generator should be called upon the creation of a new project.
    """

    def __init__(self, project_path, file_name='__init__.py'):
        super().__init__(project_path, file_name)

    def _generate_relative_path(self):
        return 'src'


class src_common_generator(src__init__generator):
    """Generator for the common.py file of the src (root)

    This file contains nothing more than "system wide" functionality.

    This generator should be called upon the creation of a new project.
    """

    def __init__(self, project_path, file_name='common.py'):
        super().__init__(project_path, file_name)


class HW__init__generator(BaseGenerator):
    """Generator for the __init__.py file of the hardware proper."""

    def __init__(self, project_path, definition, file_name="__init__.py"):
        super().__init__(project_path, definition, file_name)

    def _generate_relative_path(self):
        return os.path.join('src', self.definition['hardware'])


class HW_common_generator(HW__init__generator):
    """Generator for the common.py file of of the hardware proper."""

    def __init__(self, project_path, definition, file_name='common.py'):
        super().__init__(project_path, definition, file_name)


class PR__init__generator(BaseGenerator):
    """Generator for the __init__.py file of 'PR' for the given hardware."""

    def __init__(self, project_path, definition, file_name='__init__.py'):
        super().__init__(project_path, definition, file_name)

    def _generate_relative_path(self):
        return os.path.join('src', self.definition['hardware'], 'PR')


class PR_common_generator(PR__init__generator):
    """Generator for the common.py file of 'PR' for the given hardware."""

    def __init__(self, project_path, definition):
        super().__init__(project_path, definition, file_name='common.py')


class FT__init__generator(BaseGenerator):
    """Generator for the __init__.py file of 'FT' for the given hardware."""

    def __init__(self, project_path, definition, file_name='__init__.py'):
        super().__init__(project_path, definition, file_name)

    def _generate_relative_path(self):
        return os.path.join('src', self.definition['hardware'], 'FT')


class FT_common_generator(FT__init__generator):
    """Generator for the common.py file of 'FT' for the given hardware."""

    def __init__(self, project_path, definition):
        super().__init__(project_path, definition, file_name='common.py')


if __name__ == '__main__':
    hardware_definition = {
        'hardware': 'HW0',
        'PCB': {},
        'tester': ('SCT', 'import stuff'),
        'instruments': {},
        'actuators': {}}

    test_definition = {
        'name': 'trial',
        'type': 'custom',
        'hardware': 'HW0',
        'base': 'FT',
        'doc_string': ['line1', 'line2'],
        'input_parameters': {
            'Temperature':    {'Shmoo': True, 'Min': -40.0, 'Default': 25.0, 'Max': 170.0, '10ᵡ': '', 'Unit': '°C', 'fmt': '.0f'},
            'new_parameter1': {'Shmoo': False, 'Min': -np.inf, 'Default': 0.0, 'Max': np.inf, '10ᵡ': 'μ', 'Unit':  'V', 'fmt': '.3f'},
            'new_parameter2': {'Shmoo': False, 'Min': -np.inf, 'Default':  0.123456789, 'Max': np.inf, '10ᵡ':  '', 'Unit':  'dB', 'fmt': '.6f'}},
        'output_parameters' : {
            'new_parameter1': {'LSL': -np.inf, 'LTL':  np.nan, 'Nom':  0.0, 'UTL': np.nan, 'USL': np.inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.3f'},
            'new_parameter2': {'LSL': -np.inf, 'LTL': -5000.0, 'Nom': 10.0, 'UTL':   15.0, 'USL': np.inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.1f'},
            'new_parameter3': {'LSL': -np.inf, 'LTL':  np.nan, 'Nom':  0.0, 'UTL': np.nan, 'USL': np.inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.6f'},
            'new_parameter4': {'LSL': -np.inf, 'LTL':  np.nan, 'Nom':  0.0, 'UTL': np.nan, 'USL': np.inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.3f'}},
        'dependencies' : {}}

    program_definition = {
        'hardware': 'HW0',
        'base': 'FT',
        'target': 'target',
        'USER_TXT': 'H2LHH',
        'MOD_COD': 'P',  # see STDF V4 definition page 19 --> needs further elaboration on the codes ! P = Production
        'FLOW_ID': '1',  # see STDF V4 definition page 19 --> needs further elaboration
        'sequencer': ('Fixed Temperature', -40.0, 1),
        'sequence': {
            'test1': {
                'call values': {
                    'ipname1': 123.456,
                    'ipname2': 789.012
                },
                'limits': {  # (LTL, UTL)
                    'opname1': (1.1, 2.2),
                    'opname2': (3.3, 4.4)
                }
            },
            'test2': {
                'call values': {
                    'ipname1': 1.234,
                    'ipname2': 5.678
                },
                'limits': {
                    'opname1': (5.5, 6.6),
                    'opname2': (7.7, 8.8)
                }
            }
        },
        'binning': {  # TODO: needs some more thinking !!!
            'test1': {   # (TSTNUM, SBIN, SBIN_GROUP)
                'opname1': (10, 10, 'test1/opname1 fail'),
                'opname2': (11, 11, 'test1/opname2 fail')
            },
            'test2': {
                'opname1': (12, 12, 'test2/opname1 fail'),
                'opname2': (13, 13, 'test2/opname2 fail')
            }
        },
        'pingpong': {
            'PR1.1': ((1,),),
            'PR15.1': ((1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15),),
            'PR15.3': ((1, 2, 3, 4, 5), (6, 7, 8, 9, 10), (11, 12, 13, 14, 15)),
            'PR15.15': ((1,), (2,), (3,), (4,), (5,), (6,), (7,), (8,), (9,), (10,), (11,), (12,), (13,), (14,), (15,))
        },
        'execution': {
            'PR1': {
                'test1': 'PR1.1',
                'test2': 'PR1.1'
            },
            'PR15': {
                'test1': 'PR15.1',
                'test2': 'PR15.3'
            }
        }
    }

    project_name = 'TRIAL'
    project_path = os.path.join(os.path.dirname(__file__), project_name)
    if os.path.exists(project_path):
        shutil.rmtree(project_path)

    project_generator(project_path)

    hardware_generator(project_path, hardware_definition)

    test_generator(project_path, test_definition)
    test_definition['base'] = 'PR'
    test_generator(project_path, test_definition)


class test_target_generator(test_proper_generator):
    """Generator for the Test Class."""

    def __init__(self, project_path, definition):
        super().__init__(project_path, definition)

    def _generate_relative_path(self):
        hardware = self.definition['hardware']
        base = self.definition['base']
        base_class = self.definition['base_class']

        return os.path.join('src', hardware, base, base_class)

    def _generate_render_data(self, abs_path=''):
        return {'module_doc_string': prepare_module_docstring(),
                'input_parameter_table': prepare_input_parameters_table(self.definition['input_parameters']),
                'output_parameter_table': prepare_output_parameters_table(self.definition['output_parameters']),
                'definition': self.definition}

    def _render(self, template, render_data):
        return template.render(module_doc_string=render_data['module_doc_string'],
                               input_parameter_table=render_data['input_parameter_table'],
                               output_parameter_table=render_data['output_parameter_table'],
                               definition=self.definition)


class test_program_generator(BaseGenerator):
    def indexgen(self):
        self.last_index = self.last_index + 1
        return self.last_index

    def __init__(self, prog_name, owner, datasource):
        self.datasource = datasource
        self.last_index = 0
        template_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
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

        rel_path_to_dir = self._generate_relative_path()
        abs_path_to_dir = os.path.join(datasource.project_directory, rel_path_to_dir)
        abs_path_to_file = os.path.join(abs_path_to_dir, file_name)

        if not os.path.exists(abs_path_to_dir):
            os.makedirs(abs_path_to_dir)

        if os.path.exists(abs_path_to_file):
            os.remove(abs_path_to_file)

        test_list = self.build_test_entry_list(datasource, owner, prog_name)

        output = template.render(test_list=test_list)

        with open(abs_path_to_file, 'w', encoding='utf-8') as fd:
            fd.write(output)

    def build_test_entry_list(self, datasource, owner, prog_name):
        # step 1: Get tests and test params in sequence
        tests_in_program = datasource.get_tests_for_program(prog_name, owner)
        # step 2: Get all testtargets for progname
        test_targets = datasource.get_test_targets_for_program(prog_name)

        # step 3: Augment sequences with actual classnames
        test_list = []
        for program_entry in tests_in_program:
            test_class = self.resolve_class_for_test(program_entry.test, test_targets)
            test_module = self.resolve_module_for_test(program_entry.test, test_targets)

            import pickle
            params = pickle.loads(program_entry.definition)
            test_list.append({"test_name": program_entry.test,
                              "test_class": test_class,
                              "test_module": test_module,
                              "instance_name": params['description'],
                              "output_parameters": params['output_parameters'],
                              "input_parameters": params['input_parameters']})

        return test_list

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

    def _generate_relative_path(self):
        hardware = self.datasource.active_hardware
        base = self.datasource.active_base
        return os.path.join('src', hardware, base)

    def _generate_render_data(self, abs_path=''):
        pass

    def _render(self, template, render_data):
        pass
    