# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © {% now "local", "%Y" %}, {{ cookiecutter.full_name }}
#
# Licensed under the terms of the {{ cookiecutter.open_source_license }}
# ----------------------------------------------------------------------------
"""
{{cookiecutter.project_name}} setup.
"""
from setuptools import find_packages
from setuptools import setup

from {{cookiecutter.project_package_name}} import __version__


setup(
    # See: https://setuptools.readthedocs.io/en/latest/setuptools.html
    name="{{cookiecutter.project_pypi_name}}",
    version=__version__,
    author="{{cookiecutter.full_name}}",
    author_email="{{cookiecutter.email}}",
    description="{{cookiecutter.project_short_description}}",
    license="{{cookiecutter.open_source_license}}",
    url="https://github.com/{{cookiecutter.github_username}}/{{cookiecutter.project_pypi_name}}",
    install_requires=[
        "qtpy",
        "qtawesome",
        # "spyder",
    ],
    packages=find_packages(),
    entry_points={
        "spyder.plugins": [
            "{{cookiecutter.project_package_name}} = {{cookiecutter.project_package_name}}.spyder.plugin:{{cookiecutter.project_name.replace(" ", "")}}"
        ],
    },
    classifiers=[
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
    ],
)
