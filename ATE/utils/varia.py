'''
Created on Aug 9, 2019

@author: hoeren
'''
import os
import sys


def sys_platform():
    if sys.platform == "linux" or sys.platform == "linux2":
        return "Linux"
    elif sys.platform == "Darwin":
        return "OSX"
    elif sys.platform == "win32": # and what with windows64?!?
        return "Windows"
    else:
        return "Unknown OS : %s" % sys.platform

def get_real_size(obj, seen=None):
    '''
    Recursively finds size of objects
    '''
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_real_size(v, seen) for v in obj.values()])
        size += sum([get_real_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_real_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_real_size(i, seen) for i in obj])
    return size

def os_is_case_sensitive():
    if os.path.normcase('A') == os.path.normcase('a'):
        return False
    return True

def path_is_writeable_by_me(path):
    '''
    This function will see if path is writeable.
    if path doesn't exist, try to make the path first.
    '''
    import tempfile
    path = os.path.normpath(path)
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except:
            return False
    if not os.path.isdir(path):
        return False
    try:
        tfd, tfn = tempfile.mkstemp(dir=path)
        tfo = os.fdopen(tfd, 'w+')
        tfo.write("hallelujah")
        tfo.close()
    except:
        return False
    try:
        os.unlink(tfn)
    except:
        return False
    return True

if __name__ == '__main__':
    pass
