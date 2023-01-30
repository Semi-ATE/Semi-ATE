"""
Some functions for environment handling for the TCC Labor .


"""
import os
import sys

__author__ = "Zlin526F"
__copyright__ = "Copyright 2023, Lab"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"
__version__ = '0.0.1'


def path_insert(self, path, check=True, append=False):
    """Insert path to sys.path in the top or bottom.

    if check -> insert only if path not exist in sys.path
    if append -> insert path in the bottom
    """
    if path is None:
        self.log_error('labml_adjutancy: setup path==None')
        return False
    path = os.path.normcase(path)
    found = False
    method = 'insert'
    if append:
        method = 'append'
    for entry in sys.path:
        if entry == path:
            found = True
    if not found and check and not os.path.exists(path):
        self.log_error('labml_adjutancy: setup path {} not exist'.format(path))
        return False                           # not OK
    elif not found and os.path.exists(path):
        if not append:
            sys.path.insert(0, path)
        else:
            sys.path.append(path)
        self.log_info("labml_adjutancy: add {} {} to Path".format(method, path))
        return True                            # OK
    elif found and os.path.exists(path):
        # print("   {} already exist in Path".format(path))
        return True                           # OK


def environ_getpath(self, key):
    '''Get environment from the key.

    Check if key a path and running on nt,  add prefix from the network
    replace the the environment.
    '''
    result = os.environ.get(key)
    if result is None:
        msg = f'labml_adjutancy: key {key} not found in environment'
        if hasattr(self, "log_error"):
            self.log_error(msg)
        else:
            print(msg)
        return None
    network = os.environ['NETWORK'] if os.environ['NETWORK'] is not None else ''
    if network != '' and os.name == "nt" and (result.find('/') == 0 or result.find('\\') == 0) and result.find(network) != 0:
        result = network + result
        os.environ[key] = result
    return result

def checkNetworkPath(name, network=''):
    if os.environ['NETWORK'] and network=='':
        network = os.environ['NETWORK']
    elif os.environ['NETWORK'] is None and network != '':
        os.environ['NETWORK'] == network
    if name is not None and network != '' and os.name == "nt" and (name.find('/') == 0 or name.find('\\') == 0) and name.find(network) != 0:
        name = network + name
    return name
    

def replaceEnvs(dictionary, network=''):
    """
    check if dictionary has environment-variables starts with $,
    or dictionary has path-value.

    if yes than replace environment-variables with its value,
    if it a path-value than add the network-name

    """
    for key in dictionary:
        if type(dictionary) == dict:
            value = dictionary[key]
        else:
            value = key
        if type(value) == dict or type(value) == list:
            replaceEnvs(value)
        elif type(value) == str and value.find('$') > -1:   # find environment variables inside the value?
            split = value.split(';')                        # better to use reg to replace $name
            nvalue = ''
            for paths in split:
                tmp = paths.split('/')
                pvalue = ''
                for s in tmp:
                    found = s.find('$')
                    if found >= 0:
                        s = os.environ.get(s[found+1:])
                        if s is None:
                            break
                    pvalue += s + '/'
                if pvalue != '':
                    nvalue += pvalue + ';'
            if nvalue != '':
                if type(dictionary) == dict:
                    dictionary[key] = nvalue[:-1]
                else:
                    dictionary[1] = nvalue[:-1]
        elif type(value) == str and len(value) > 0 and value[0] == '/' and os.name == "nt" and value.find(f'{network}') != 0:
            if type(dictionary) == dict:
                dictionary[key] = network + value
            else:
                dictionary[1] = network + value
    return(dictionary)
