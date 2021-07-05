'''
Created on Nov 19, 2019

@author: hoeren
'''
import os
import re

valid_python_class_name_regex = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
valid_die_name_regex = r"^[a-zA-Z][a-zA-Z0-9]*$"
valid_product_name_regex = r"^[a-zA-Z][a-zA-Z0-9]*$"
valid_maskset_name_regex = r"^[a-zA-Z][a-zA-Z0-9]*$"
valid_device_name_regex = r"^[a-zA-Z][a-zA-Z0-9]*$"
valid_package_name_regex = r"^[a-zA-Z][a-zA-Z0-9]*$"

valid_name_regex = r"^[a-zA-Z][a-zA-Z0-9_]*$"

valid_pcb_name_regex = r"^[a-zA-Z][a-zA-Z0-9]*$"
valid_positive_integer_regex = r"^[+]?\d*"
valid_positive_float_1_regex = r"[+]?\d*\.?\d?"

valid_integer_regex = r"^[+-]?\d*"
valid_temp_sequence_regex = r"^([+-]?\d*\,?\d*)*"

valid_float_regex = "[+-]?(∞|[0-9]+(\\.[0-9]+)?)"
valid_min_float_regex = "[+-]?(∞|[0-9]+(\\.[0-9]+)?)"
valid_default_float_regex = "[+-]?([0-9]+(\\.[0-9]+)?)"
valid_max_float_regex = "[+-]?(∞|[0-9]+(\\.[0-9]+)?)"
valid_fmt_regex = "([0-9]*\\.[0-9]+)?f"


def is_Spyder_project(project_directory):
    '''
    this function will return True if the project under 'project_directory' is
    a standard Spyder project.
    '''
    if os.path.exists(os.path.join(project_directory, '.spyproject')):
        return True
    else:
        return False


def is_ATE_project(project_directory):
    '''
    this method will return true if the project under 'project_directory' is
    1) a spyder project
    2) an ATE project
    '''
    if not is_Spyder_project(project_directory):
        return False

    if os.path.exists(os.path.join(project_directory, '.spyproject', 'ATE.config')):
        return True
    else:
        return False


def is_valid_python_class_name(name):
    '''
    this method will return True if 'name' is a valid python class name
    '''
    pattern = re.compile(valid_python_class_name_regex)
    if pattern.match(name):
        return True
    else:
        return False


def is_valid_maskset_name(name):
    '''
    Check if the supplied name is a valid name for a 'maskset'
    '''
    pattern = re.compile(valid_maskset_name_regex)
    if pattern.match(name):
        return True
    else:
        return False


def is_valid_test_name(name):
    '''
    Check if the supplied name is a valid name for a 'test'

    As a test is a .py file, and in the .py file the class will be the same name,
    this reverts to 'is_valid_python_class_name', however, we don't want the word
    'test' in any capitalisations in this name (it is always a test, so let's skip it) !!!
    '''
    if 'TEST' in name.upper():
        return False
    pattern = re.compile(valid_name_regex)
    if pattern.match(name):
        return True
    else:
        return False


def is_valid_project_name(name):
    '''
    Check if the supplied name is a valid name for a 'project'
    '''
    if 'TEST' in name.upper():
        return False
    pattern = re.compile(valid_name_regex)
    if pattern.match(name):
        return True
    else:
        return False
