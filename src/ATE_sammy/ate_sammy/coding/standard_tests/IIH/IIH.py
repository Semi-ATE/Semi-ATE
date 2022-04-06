# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 13:04:20 2020

@author: hoeren
"""
import os

from ate_spyder.widgets.coding import test_generator

my_definition = {
    'doc_string' : [
        'The worst case (max) current the input pin can sink to maintain logic 1',
        'voltage at output of the device it is connected to',
        'file://~/doc/help/ATE_Fundamentals.pdf#82' ],
    'output_parameters' : {},
    'data' : {}
}

my_name = '.'.join(os.path.basename(__file__).split('.')[:-1])

def generator(project_path, hardware, base):
    return test_generator(project_path, my_name, hardware, base, my_definition, Type='standard')
