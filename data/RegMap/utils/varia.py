'''
Created on Aug 21, 2019

@author: hoeren
'''
import os
import pickle


def register_maps_in_directory(path):
    '''
    This function will return a list of register maps found in path.
    a register map is a file with '.regmap' at the end.
    '''
    retval = []
    if os.path.exists(path) and os.path.isdir(path):
        for item in os.listdir(path):
            if item.endswith('.regmap'):
                retval.append(item)
    return retval



def register_map_config_manager():
    '''
    graphical tool to configure register maps.
    '''
    pass

def register_map_save(FileName, regmap):
    '''
    Given a register_map dictionary (regmap) and a file, save (pickle) the dictionary.
    If FileName doesn't end with '.regmap', nothing is done.
    '''
    if FileName.endswith('.regmap'):
        if os.path.exists(FileName) and os.path.isfile(FileName):
            os.remove(FileName)
        with open(FileName, 'wb') as writer:
            pickle.dump(regmap, writer)

def register_map_load(FileName):
    '''
    this function will load the register_map from FileName, and return the dictionary to be used in subclasses of register_map_abc
    '''
    retval = {}
    if os.path.exists(FileName) and os.path.isfile(FileName) and FileName.endswith('.regmap'):
        with open(FileName, 'rb') as reader:
            retval = pickle.load(reader)
    return retval


def register_map_ok(regmap):
    '''
    This function returns True if it finds regmap to be in order, False otherwhise
    '''
    if 'address_size' not in regmap: return False
    if 'word_size' not in regmap: return False
    #TODO: add more checkings
    return True


if __name__ == '__main__':
    pass
