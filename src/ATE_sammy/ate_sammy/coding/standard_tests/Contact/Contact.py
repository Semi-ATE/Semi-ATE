# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 11:28:28 2020

@author: hoeren
"""
import os

from ate_spyder.widgets.coding import test_generator

my_definition = {
    'doc_string' : [], #list of lines
    'input_parameters' : {},
    'output_parameters' : {},
    'data' : {}
}

my_name = '.'.join(os.path.basename(__file__).split('.')[:-1])

def generator(project_path, hardware, base):
    print(project_path, hardware, base)

class Wizard(object):
    pass

def dialog(project_path, hardware, base):
    # no wizrd used
    generator(project_path, hardware, base)
