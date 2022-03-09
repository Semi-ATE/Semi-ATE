# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 13:08:35 2020

@author: hoeren
"""
import os

my_definition = {
    'doc_string' : [
        'Output Short Circuit Current',
        'file://~/doc/help/ATE_Fundamentals.pdf' ],
    'output_parameters' : {},
    'data' : {}
}

my_name = '.'.join(os.path.basename(__file__).split('.')[:-1])

def generator(project_path, hardware, base):
    from ate_spyder.widgets.coding import test_generator

    print(f"{project_path} {my_name} {hardware} {base} {my_definition}")
    return test_generator(project_path, my_name, hardware, base, my_definition, Type='standard')
