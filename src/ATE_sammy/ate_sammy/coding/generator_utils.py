import getpass
import os


def prepare_module_docstring():
    retval = []

    line = "By "
    user = getpass.getuser()
    line += user
    domain = str(os.environ.get('USERDNSDOMAIN'))
    if domain != 'None':
        line += f" ({user}@{domain})".lower()
    retval.append(line)
    return retval
