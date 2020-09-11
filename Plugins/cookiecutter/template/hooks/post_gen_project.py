# -*- coding: utf-8 -*-

# Standard library imports
import os

# Constants
PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def remove_file(filepath):
    os.remove(os.path.join(PROJECT_DIRECTORY, filepath))


if __name__ == '__main__':
    if 'Not open source' == '{{ cookiecutter.open_source_license }}':
        remove_file('LICENSE.txt')

    if '{{ cookiecutter.plugin_type }}' == 'Spyder Dockable Plugin':
        remove_file(
            '{{ cookiecutter.project_package_name }}/spyder/container.py')
