# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23th @ 15:20:40 2020

@author: hoeren

The Abstract Base Class for all ATE plugins is defined here.
The machinery to make the plugin to be recognized by ATE.org as
a 'per-company' plugin is done with the 'pluggy' library, and is
hidden for the developer of the individual plugins.

References :
    pluggy :
        https://buildmedia.readthedocs.org/media/pdf/pluggy/latest/pluggy.pdf
        https://pypi.org/project/pluggy/
    abc :
        https://docs.python.org/3/library/abc.html
"""
import abc

import pluggy

from ate_spyder.widgets.validation import valid_maskset_name_regex

masksetStructure = {
    'Name' : '', # string identifying the maskset
    'Customer' : '', # a string, '' for 'ASSP', for 'ASIC' the customer name
    'WaferDiameter' : '200', # a string, must be one of ['25', '51', '76', '100', '125', '150', '200', '300', '450']
    'Bondpads' : 3, # a positive integer, equal or bigger than 2, and equal or smaller than 99
    'DieSizeX' : None, # positive integer measured in µm
    'DieSizeY' : None, # positive integer measured in µm
    'DieRefX' : None, # positive float measured in µm
    'DieRefY' : None, # positive float measured in µm

#TODO: complete the 'masksetStructure' once the UI is stabilized.

    }



class ATE_plugin(object):

    def __init__(self):
        self.company = self.__class__.__name__

    @abc.abstractmethod
    def importMaskset(self):
        '''
        This method will return as much as possible of the below data:
        '''
        retval = masksetStructure
        return retval





if __name__ == '__main__':
    pass
