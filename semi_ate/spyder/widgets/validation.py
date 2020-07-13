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
valid_test_name_regex = r"^[a-zA-Z][a-zA-Z0-9]*$"
valid_test_parameter_name_regex = r"^[a-zA-Z][a-zA-Z0-9]*$"
valid_testprogram_name_regex = r"^[a-zA-Z][a-zA-Z0-9]*$"
valid_project_name_regex = r"^[a-zA-Z][a-zA-Z0-9]*$"
valid_pcb_name_regex = r"^[a-zA-Z][a-zA-Z0-9]*$"
valid_user_text_name_regex = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
valid_positive_integer_regex = r"^[+]?\d*"
valid_positive_float_1_regex = r"[+]?\d*\.?\d?"

valid_integer_regex = r"^[+-]?\d*"
valid_temp_sequence_regex = r"^([+-]?\d*\,?\d*)*"

valid_test_name_description_regex = r"^[a-zA-Z][a-zA-Z0-9_]*$"

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


def is_valid_die_name(name):
    '''
    Check if the supplied name is a valid name for a 'die'

    Note: in the end this will be the name of a directory ...
    '''
    pattern = re.compile(valid_die_name_regex)
    if pattern.match(name):
        return True
    else:
        return False


def is_valid_product_name(name):
    '''
    Check if the supplied name is a valid name for a 'product'

    Note: should be the same as for the die !
    '''
    pattern = re.compile(valid_product_name_regex)
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


def is_valid_device_name(name):
    '''
    Check if the supplied name is a valid name for a 'device'
    '''
    pattern = re.compile(valid_device_name_regex)
    if pattern.match(name):
        return True
    else:
        return False


def is_valid_package_name(name):
    '''
    Check if the supplied name is a valid name for a 'package'
    '''
    pattern = re.compile(valid_package_name_regex)
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
    pattern = re.compile(valid_test_name_regex)
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
    pattern = re.compile(valid_project_name_regex)
    if pattern.match(name):
        return True
    else:
        return False


def is_valid_pcb_name(name):
    pattern = re.compile(valid_pcb_name_regex)
    if pattern.match(name):
        return True
    else:
        return False


def has_single_site_loadboard(project_path, hardware_version):
    from ATE.org.listings import dict_pcbs_for_hardware_setup
    from ATE.org.listings import list_hardware_setups

    if is_ATE_project(project_path):
        if hardware_version in list_hardware_setups(project_path):
            pcbs = dict_pcbs_for_hardware_setup(project_path, hardware_version)
            if pcbs['SingeSiteLoadboard'] != "":
                return True
    return False


def has_probe_card(project_path, hardware_version):
    from ATE.org.listings import dict_pcbs_for_hardware_setup
    from ATE.org.listings import list_hardware_setups

    if is_ATE_project(project_path):
        if hardware_version in list_hardware_setups(project_path):
            pcbs = dict_pcbs_for_hardware_setup(project_path, hardware_version)
            if pcbs['ProbeCard'] != "":
                return True
    return False


def has_single_site_DIB(project_path, hardware_version):
    pass


if __name__ == '__main__':
    from SpyderMockUp.SpyderMockUp import workspace
    from ATE.org.listings import list_ATE_projects

    for project in list_ATE_projects(workspace):
        print(project)
