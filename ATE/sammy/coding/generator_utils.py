import getpass
import os
# from ATE.utils.DT import DT


def prepare_module_docstring():
    retval = []

    #line = f"Created on {str(DT())}"
    #retval.append(line)

    line = "By "
    user = getpass.getuser()
    line += user
    domain = str(os.environ.get('USERDNSDOMAIN'))
    if domain != 'None':
        line += f" ({user}@{domain})".lower()
    retval.append(line)
    return retval
