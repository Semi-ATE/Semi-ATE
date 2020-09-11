# -*- coding: utf-8 -*-

# Local imports
import re
import sys

# Third party imports
import requests

# Constants
MODULE_REGEX = r'^[_a-zA-Z][_a-zA-Z0-9]+$'
module_name = '{{ cookiecutter.project_package_name}}'
pypi_name = '{{ cookiecutter.project_pypi_name}}'
pypi_url = "https://pypi.org/pypi/{}/json".format(pypi_name)


# Check if package name is a valid Python name
if not re.match(MODULE_REGEX, module_name):
    print(f"ERROR: The project slug \"{module_name}\" is not a valid Python module name.")
    # Exit to cancel project
    sys.exit(1)


# Check if PyPI name is available
r = requests.head(pypi_url)
if r.status_code == 200:
    print(f"ERROR: The project PyPI name \"{pypi_name}\" is already taken")
    # Exit to cancel project
    sys.exit(1)
