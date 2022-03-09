# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 13:10:02 2020

@author: hoeren
"""
import os

from ate_spyder.widgets.coding import test_generator

my_definition = {
    'doc_string' : ['Time Domain Reflectometry'],
    'output_parameters' : {},
    'data' : {}
}

my_name = '.'.join(os.path.basename(__file__).split('.')[:-1])

def generator(project_path, hardware, Type, base):
    return test_generator(project_path, my_name, hardware, Type, base, my_definition)
