# -*- coding: utf-8 -*-
"""
Created on Tue Aug 30 09:17:27 2022

@author: jung



"""
import pandas as pd

#from ate_spyder.widgets.navigation import ProjectNavigation

from ate_projectdatabase.Test import Test
from ate_projectdatabase.Group import Group
from ate_projectdatabase.Types import Types
from ate_projectdatabase.FileOperator import FileOperator
from argparse import Namespace
import numpy as np

#import  ate_projectdatabase
# ate_projectdatabase.latest_semi_ate_project_db_version


class ReadExcelTests(object):

    test_definition = {
        'name': 'trial',
        'type': 'custom',                       # <-- needs to be 'custom' otherwhise explode
        'quality': 'automotive',
        'hardware': 'HW0',
        'base': 'FT',
        'docstring': ['a nice message ....'],
        'input_parameters': {
            'Temperature':    {'shmoo': True, 'min': -40.0, 'default': 25.0, 'max': 170.0, 'exp10': 0, 'unit': '\u00b0C', 'fmt': '.0f'},
            },
        'output_parameters': {
            'new_parameter1': {'lsl': -np.inf, 'ltl':  np.nan, 'nom':  0.0, 'utl': np.nan, 'usl': np.inf, 'exp10': 0, 'unit': '\u00b0C', 'fmt': '.3f', 'mpr': False},
            },
        'dependencies': {}
        }

    def __init__(self, filename="", sheetname="", header=0):
        self.project_directory = r'C:\Users\jung\ATE\packages\envs\semi-ate-4\tb_ate'    # todo: should come frome project
        wb = pd.ExcelFile(filename)
        if sheetname == "" and len(wb.sheetnames) > 1:
            print(f'There a more than one sheets available: {wb.sheetnames}')
            raise IOError()
        wb = pd.read_excel(filename, engine='openpyxl', header=header, sheet_name=sheetname)
        #for col in wb.values:
        #    print(col)


        self.file_operator = FileOperator(self.project_directory)
        allExistTests = Test.get_all(self.file_operator)    # name, definition

        #template_base_path = os.path.dirname(generate.__file__)
        #template_base_path = os.path.join(template_base_path, "templates")
        #generator = generate.Generate(template_base_path)


        groups = 'production'
        groups = 'engineer'
        hardware = 'HW0'              # todo: get from project_info
        base = 'FT'                   # todo: "
        typ = 'custom'

        definition = self.test_definition
        is_enabled = True
        definition['name'] = 'cj_version1'

        # ProjectNavigation.add_custom_test(definition)   # the lines below are from this call, perhaps we can use it directly to use the TestProgramWizard
        Test.add(self.file_operator, definition['name'], hardware, base, typ, definition, is_enabled)        # das funktioniert nur, wenn testname noch nicht existiert!!
        # Group.update_groups_for_test(self.file_operator, definition['name'], groups)    # *** AssertionError: 0 :-()
        
        mygroups= Group.get_all(self.file_operator)
        Group.add_test_to_group(self.file_operator, definition['name'], groups)

        # args = Namespace(verb="generate", noun= "test", params=params)
        _ = self.run_build_tool("generate", "test", self.project_directory, definition['name'], hardware, base)

        #self.parent.groups_update.emit(definition['name'], groups)

        #self.file_operator.generate_path
        #self.file_operator.get_current_target_list_name()


    def run_build_tool(self, verb, noun, cwd, *params) -> int:
        from ate_sammy.sammy import run
        args = Namespace(verb=verb, noun=noun, params=params)
        return run(args, cwd)

if __name__ == "__main__":
    ReadExcelTests(r"C:\Users\jung\ATE\Docu\HATB\Output_HATB_65.xlsx", "TTR_318_Cold", header = 1)
