# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 12:35:07 2020

@author: hoeren
"""
import os

from ATE.spyder.widgets.coding import test_generator

my_definition = {
    'doc_string' : [
        'The worst case (min) voltage at the output that drives a logical 1 (page 81)'],
    'input_parameters' : {},
    'output_parameters' : {},
    'data' : {}
}

my_name = '.'.join(os.path.basename(__file__).split('.')[:-1])

def generator(project_path, hardware, Type, base):
    return test_generator(project_path, my_name, hardware, Type, base, my_definition)
