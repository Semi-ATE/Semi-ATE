"""
Created on Tue Mar  3 14:08:04 2020

@author: hoeren
"""
from argparse import Namespace
from pathlib import Path
from ate_common.program_utils import Sequencer
import json
import os
import platform
from typing import Dict, List

from ate_projectdatabase.Hardware.ParallelismStore import ParallelismStore

from qtpy.QtCore import QObject
from ate_spyder.widgets.constants import TableIds as TableId
from ate_spyder.widgets.constants import UpdateOptions

from ate_projectdatabase.Device import Device
from ate_projectdatabase.Die import Die
from ate_projectdatabase.Hardware import Hardware
from ate_projectdatabase.Maskset import Maskset
from ate_projectdatabase.Package import Package
from ate_projectdatabase.Product import Product
from ate_projectdatabase.Program import Program, ExecutionSequenceType
from ate_projectdatabase.QualificationFlow import QualificationFlowDatum
from ate_projectdatabase.Sequence import Sequence
from ate_projectdatabase.Test import Test
from ate_projectdatabase.TestTarget import TestTarget
from ate_projectdatabase.FileOperator import FileOperator
from ate_projectdatabase.Group import Group
from ate_projectdatabase.Types import Types
from ate_projectdatabase.Settings import Settings
from ate_projectdatabase.Version import Version


definitions = {Types.Maskset(): Maskset}
tables = {'hardwares': Hardware,
          Types.Maskset(): Maskset,
          'dies': Die,
          'packages': Package,
          'devices': Device,
          'products': Product,
          'tests': Test,
          'testtargets': TestTarget}

default_groups = ['checker', 'maintenance', 'production', 'engineering', 'validation', 'quality', 'qualification']


class ProjectNavigation(QObject):
    '''
    This class takes care of the project creation/navigation/evolution.
    '''
    # The parameter contains the type of the dbchange (i.e. which table was altered)
    verbose = True

    def __init__(self, project_directory, workspace_path, parent):
        super().__init__(parent)
        self.parent = parent
        self.workspace_path = workspace_path
        self.__call__(project_directory)

    def __call__(self, project_directory):
        # determine OS, determine user & desktop
        self.os = platform.system()
        if self.os == 'Windows':
            self.desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        elif self.os == 'Linux':
            self.desktop_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
        elif self.os == 'Darwin':  # TODO: check on mac if this works
            self.desktop_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')
        else:
            raise Exception("unrecognized operating system")
        self.user = self.desktop_path.split(os.sep)[-2]
        self.template_directory = os.path.join(os.path.dirname(__file__), 'templates')

        # TODO: take the keychain in here ?!?

        if project_directory == '':
            self.project_directory = ''
            self.active_target = ''
            self.active_hardware = ''
            self.active_base = ''
            self.project_name = ''
        else:
            self.project_directory = project_directory
            self.active_target = ''
            self.active_hardware = ''
            self.active_base = ''
            self.project_name = os.path.basename(self.project_directory)

            settings_file = os.path.join(project_directory, ".lastsettings")

            # the .lastsettings file is used as a canary to detect if
            # this folder already contains a project or if we have to generate
            # a new project
            if not os.path.exists(settings_file):  # brand new project, initialize it.
                self.create_project_structure()

            self._set_folder_structure()
            self.file_operator = FileOperator(self.project_directory)
            self._store_default_groups()

        if self.verbose:
            print("Navigator:")
            print(f"  - operating system = '{self.os}'")
            print(f"  - user = '{self.user}'")
            print(f"  - desktop path = '{self.desktop_path}'")
            print(f"  - template path = '{self.template_directory}'")
            print(f"  - project path = '{self.project_directory}'")
            print(f"  - active target = '{self.active_target}'")
            print(f"  - active hardware = '{self.active_hardware}'")
            print(f"  - active base = '{self.active_base}'")
            print(f"  - project name = '{self.project_name}'")

    def update_toolbar_elements(self, active_hardware, active_base, active_target):
        self.active_hardware = active_hardware
        self.active_base = active_base
        self.active_target = active_target
        self.parent.toolbar_changed.emit(self.active_hardware, self.active_base, self.active_target)

    def update_active_hardware(self, hardware):
        self.active_hardware = hardware
        self.parent.hardware_activated.emit(hardware)

    def _set_folder_structure(self):
        # make sure that the doc structure is obtained
        doc_path = os.path.join(self.project_directory, "doc")
        os.makedirs(os.path.join(doc_path, "audits"), exist_ok=True)
        os.makedirs(os.path.join(doc_path, "exports"), exist_ok=True)

    def _store_default_groups(self):
        groups = [group.name for group in self.get_groups()]
        for default in default_groups:
            if default in groups:
                continue

            Group.add(self.get_file_operator(), default, is_standard=True)

    def get_groups(self):
        return Group.get_all(self.get_file_operator())

    def update_group_state(self, name: str, is_checked: bool):
        Group.update_state(self.get_file_operator(), name, is_checked)
        self.parent.group_state_changed.emit()

    def add_test_group(self, name: str):
        Group.add(self.get_file_operator(), name, is_standard=False)
        self.parent.group_added.emit(name)

    def is_standard_group(self, name: str):
        return Group.is_standard(self.get_file_operator(), name)

    def remove_group(self, name: str):
        Group.remove(self.get_file_operator(), name)
        self.parent.group_removed.emit(name)

    def get_tests_for_group(self, group: str):
        return Group.get_tests_for_group(self.get_file_operator(), group)

    def get_groups_for_test(self, test):
        return Group.get_all_groups_for_test(self.get_file_operator(), test)

    def create_project_structure(self):
        '''
        this method creates a new project `self.project_directroy` *MUST* exist
        '''
        _ = self.run_build_tool('generate', 'new', os.path.dirname(self.project_directory), self.project_directory)

    def run_build_tool(self, verb, noun, cwd, *params) -> int:
        from ate_sammy.sammy import run
        args = Namespace(verb=verb, noun=noun, params=params)
        return run(args, cwd)

    def add_hardware(self, new_hardware, definition, is_enabled=True):
        Hardware.add(self.get_file_operator(), new_hardware, definition, is_enabled)
        _ = self.run_build_tool("generate", "hardware", self.project_directory, new_hardware)

        self.parent.hardware_added.emit(new_hardware)
        self.parent.database_changed.emit(TableId.Hardware())

    def update_hardware(self, hardware, definition):
        Hardware.update_definition(self.get_file_operator(), hardware, definition)
        _ = self.run_build_tool("generate", "hardware", self.project_directory, hardware)

        _ = self.run_build_tool("generate", "sequence", self.project_directory)

    def get_file_operator(self):
        return self.file_operator

    def get_active_hardware_names(self):
        return [hw.name for hw in Hardware.get_all(self.get_file_operator()) if hw.is_enabled]

    def get_hardware_names(self):
        '''
        This method will return a list of all hardware names available
        '''
        return [hardware.name for hardware in Hardware.get_all(self.get_file_operator())]

    def get_next_hardware(self):
        '''
        This method will determine the next available hardware name
        '''
        latest_hardware = self.get_latest_hardware()
        if latest_hardware == '':
            return "HW0"
        else:
            latest_hardware_number = int(latest_hardware.replace('HW', ''))
            return f"HW{latest_hardware_number + 1}"

    def get_latest_hardware(self):
        '''
        This method will determine the latest hardware name and return it
        '''
        available_hardwares = self.get_hardware_names()
        if len(available_hardwares) == 0:
            return ""
        else:
            return available_hardwares[-1]

    def get_hardware_definition(self, name):
        '''
        this method retreives the hwr_data for hwr_nr.
        if hwr_nr doesn't exist, an empty dictionary is returned
        '''
        return Hardware.get_definition(self.get_file_operator(), name)

    def update_hardware_parallelism_store(self, name, parallelism_store: ParallelismStore):
        Hardware.update_parallelism_store(self.get_file_operator(), name, parallelism_store)

    def get_hardware_parallelism_store(self, name) -> ParallelismStore:
        return Hardware.get_parallelism_store(self.get_file_operator(), name)

    def remove_hardware(self, name):
        Hardware.remove(self.get_file_operator(), name)
        self.parent.database_changed.emit(TableId.Hardware())
        self.parent.hardware_removed.emit(name)
        import shutil
        shutil.rmtree(os.path.join(self.project_directory, 'src', name))

    def add_maskset(self, name, customer, definition, is_enabled=True):
        '''
        this method will insert maskset 'name' and 'definition' in the
        database, but prior it will check if 'name' already exists, if so
        it will trow a KeyError
        '''
        Maskset.add(self.get_file_operator(), name, customer, definition, is_enabled)
        self.parent.database_changed.emit(TableId.Maskset())

    def update_maskset(self, name, definition, customer):
        '''
        this method will update the definition of maskset 'name' to 'definition'
        '''
        Maskset.update(self.get_file_operator(), name, customer, definition)

    def get_masksets(self):
        # ToDo: Docstring is a blatand lie
        '''
        this method returns a DICTIONARY with as key all maskset names,
        and as value the tuple (customer, definition)
        '''
        return Maskset.get_all(self.get_file_operator())

    def get_available_maskset_names(self):
        # ToDo: Docstring is a blatand lie, check how and why this
        # method is used as opposed to get_maskset_names
        '''
        this method returns a DICTIONARY with as key all maskset names,
        and as value the tuple (customer, definition)
        '''
        return [maskset.name for maskset in self.get_masksets()]

    def get_maskset_names(self):
        '''
        this method lists all available masksets
        '''
        return list(self.get_masksets())

    def get_ASIC_masksets(self):
        '''
        this method lists all 'ASIC' masksets
        '''
        return Maskset.get_ASIC_masksets(self.get_file_operator())

    def get_ASSP_masksets(self):
        '''
        this method lists all 'ASSP' masksets
        '''
        return Maskset.get_ASSP_masksets(self.get_file_operator())

    def get_maskset_definition(self, name):
        '''
        this method will return the definition of maskset 'name'
        '''
        return Maskset.get_definition(self.get_file_operator(), name)

    def get_maskset_customer(self, name):
        '''
        this method will return the customer of maskset 'name'
        (empty string means no customer, thus 'ASSP')
        '''
        return Maskset.get(self.get_file_operator(), name).customer

    def remove_maskset(self, name):
        Maskset.remove(self.get_file_operator(), name)
        self.parent.database_changed.emit(TableId.Maskset())

    def add_settings(self, quality_grade: str):
        Settings.set_quality_grade(self.get_file_operator(), quality_grade=quality_grade)

    def get_default_quality_grade(self):
        return Settings.get_quality_grade(self.get_file_operator())

    def add_die(self, name, hardware, maskset, quality, grade, grade_reference, type, customer, is_enabled=True):
        '''
        this method will add die 'name' with the given attributes to the database.
        if 'maskset' or 'hardware' doesn't exist, a KeyError will be raised.
        Also if 'name' already exists, a KeyError will be raised.
        if grade is not 'A'..'I' (9 possibilities) then a ValueError is raised
        if grade is 'A' then grade_reference must be an empty string
        if grade is not 'A', then grade_reference can not be an empty string,
        and it must reference another (existing) die with grade 'A'!
        '''
        Die.add(self.get_file_operator(), name, hardware, maskset, quality, grade, grade_reference, type, customer, is_enabled)

        self.parent.database_changed.emit(TableId.Die())

    def update_die(self, name, hardware, maskset, grade, grade_reference, quality, type, customer, is_enabled=True):
        '''
        this method updates both maskset and hardware for die with 'name'
        '''
        Die.update(self.get_file_operator(), name, hardware, maskset, quality, grade, grade_reference, type, customer)

    def get_dies(self):
        '''
        this method will return a DICTIONARY with as keys all existing die names,
        and as value the tuple (hardware, maskset, grade, grade_reference, customer)
        '''
        return Die.get_all(self.get_file_operator())

    def get_active_die_names(self):
        return [die.name for die in self.get_dies() if die.is_enabled]

    # ToDo: Seems to be unused
    # def get_die_names(self):
    #     '''
    #     this method will return a LIST of all dies
    #     '''
    #     return [die.name for die in self.get_dies()]

    def get_active_die_names_for_hardware(self, hardware):
        '''
        this method will return a LIST of all dies that conform to 'hardware'
        '''
        return [die.name for die in self.get_dies() if die.hardware == hardware and die.is_enabled]

    def get_die(self, name):
        '''
        this method returns a tuple (hardware, maskset, grade, grade_reference, customer) for die 'name'
        if name doesn't exist, a KeyError will be raised.
        '''
        return Die.get_die(self.get_file_operator(), name)

    def get_die_maskset(self, name):
        '''
        this method returns the maskset of die 'name'
        '''
        return self.get_die(name).maskset

    def get_die_hardware(self, name):
        '''
        this method returns the hardware of die 'name'
        '''
        return self.get_die(name).hardware

    def remove_die(self, name):
        Die.remove(self.get_file_operator(), name)
        self.parent.database_changed.emit(TableId.Die())
        self.parent.update_target.emit()

    def add_package(self, name, leads, is_naked_die, is_enabled=True):
        '''
        this method will insert package 'name' and 'pleads' in the
        database, but prior it will check if 'name' already exists, if so
        it will trow a KeyError
        '''
        Package.add(self.get_file_operator(), name, leads, is_naked_die, is_enabled)

        self.parent.database_changed.emit(TableId.Package())

    def update_package(self, name, leads, is_naked_die, is_enabled=True):
        Package.update(self.get_file_operator(), name, leads, is_naked_die, is_enabled)

    def does_package_name_exist(self, name):
        return self.get_package(name) is not None

    def get_package(self, name):
        return Package.get(self.get_file_operator(), name)

    def is_package_a_naked_die(self, package):
        return self.get_package(package).is_naked_die

    def get_packages_info(self):
        # ToDO: Docstring is a lie!
        '''
        this method will return a DICTIONARY with ALL packages as key and
        the number of leads as value
        '''
        return Package.get_all(self.get_file_operator())

    def get_available_packages(self):
        # ToDO: Docstring is a lie, name suggest different behavior, from
        # whats actually happening -> this function should be called "get_package_names"
        '''
        this method will return a DICTIONARY with ALL packages as key and
        the number of leads as value
        '''
        return [package.name for package in self.get_packages_info()]

    def get_packages(self):
        '''
        this method will return a LIST with all packages
        '''
        return list(self.get_packages_info())

    def add_device(self, name, hardware, package, definition, is_enabled=True):
        '''
        this method will add device 'name' with 'package' and 'definition'
        to the database.
        if 'name' already exists, a KeyError is raised
        if 'package' doesn't exist, a KeyError is raised
        '''
        Device.add(self.get_file_operator(), name, hardware, package, definition, is_enabled)
        self.parent.database_changed.emit(TableId.Device())

    def update_device(self, name, hardware, package, definition):
        Device.update(self.get_file_operator(), name, hardware, package, definition)

    def get_device_names(self):
        '''
        this method lists all available devices names
        '''
        return [device.name for device in Device.get_all(self.get_file_operator())]

    def get_active_device_names_for_hardware(self, hardware_name):
        '''
        this method will return a list of devices for 'hardware_name'
        '''
        # ToDo: Add function in device that implements the filter
        return [device.name for device in Device.get_all(self.get_file_operator()) if device.hardware == hardware_name and device.is_enabled]

    def get_devices_for_hardwares(self):
        return [device.name for device in Device.get_all(self.get_file_operator())]

    def get_device_hardware(self, name):
        return Device.get(self.get_file_operator(), name).hardware

    def get_device_package(self, name):
        '''
        this method will return the package of device 'name'
        '''
        return Device.get(self.get_file_operator(), name).package

    def get_device_definition(self, name):
        '''
        this method will return the definition of device 'name'
        '''
        return Device.get_definition(self.get_file_operator(), name)

    def get_device(self, name):
        return {'hardware': self.get_device_hardware(name),
                'package': self.get_device_package(name),
                'definition': self.get_device_definition(name)}

    def get_device_dies(self, device):
        definition = self.get_device_definition(device)
        return definition['dies_in_package']

    def remove_device(self, name):
        Device.remove(self.get_file_operator(), name)
        self.parent.database_changed.emit(TableId.Device())
        self.parent.update_target.emit()

    def add_product(self, name, device, hardware, quality, grade, grade_reference, type, customer, is_enabled=True):
        '''
        this method will insert product 'name' from 'device' and for 'hardware'
        in the the database, but before it will check if 'name' already exists, if so
        it will trow a KeyError
        '''
        session = self.get_file_operator()
        Product.add(session, name, device, hardware, quality, grade, grade_reference, type, customer, is_enabled)
        self.parent.database_changed.emit(TableId.Product())

    def update_product(self, name, device, hardware, quality, grade, grade_reference, type, customer):
        Product.update(self.get_file_operator(), name, device, hardware, quality, grade, grade_reference, type, customer)

    def get_products_info(self):
        return Product.get_all(self.get_file_operator())

    def get_products(self):
        # ToDo this method should be called get_product_names
        '''
        this method will return a list of all products
        '''
        return [product.name for product in self.get_products_info()]

    def get_product(self, name):
        return Product.get(self.get_file_operator(), name)

    def get_product_device(self, name):
        return Product.get(self.get_file_operator(), name).device

    def get_products_for_device(self, device_name):
        return [product.name for product in Product.get_for_device(self.get_file_operator(), device_name)]

    def get_product_hardware(self, name):
        return Product.get(self.get_file_operator(), name).hardware

# ToDo: Not used?!?!?
    # def remove_product(self, name):
    #     Product.remove(self.get_file_operator(), name)
    #     self.parent.database_changed.emit(TableId.Product())

    def tests_get_standard_tests(self, hardware, base):
        '''
        given 'hardware' and 'base', this method will return a LIST
        of all existing STANDARD TESTS.
        '''
        return Test.get_for_hw_base_test_typ(self.get_file_operator(), hardware, base, 'standard')

    def add_standard_test(self, name, hardware, base):
        import runpy
        raise Exception('impl me')
        from ate_spyder.widgets.coding.standard_tests import names as standard_test_names

        if name in standard_test_names:
            temp = runpy.run_path(standard_test_names[name])
            # TODO: fix this
            if not temp['dialog'](name, hardware, base):
                print(f"... no joy creating standard test '{name}'")
        else:
            raise Exception(f"{name} not a standard test ... WTF!")

    def add_custom_test(self, definition, is_enabled=True):
        '''This method adds a 'custom' test to the project.

        'definition' is a structure as follows:

            test_definition = {
                'name': 'trial',
                'type': 'custom', <-- needs to be 'custom' otherwhise explode
                'quality': 'automotive',
                'hardware': 'HW0',
                'base': 'FT',
                'doc_string': ['line1', 'line2'],
                'input_parameters': {
                    'Temperature':    {'Shmoo': True, 'Min': -40.0, 'Default': 25.0, 'Max': 170.0, '10ᵡ': '', 'Unit': '°C', 'fmt': '.0f'},
                    'new_parameter1': {'Shmoo': False, 'Min': -np.inf, 'Default': 0.0, 'Max': np.inf, '10ᵡ': 'μ', 'Unit':  'V', 'fmt': '.3f'},
                    'new_parameter2': {'Shmoo': False, 'Min': -np.inf, 'Default':  0.123456789, 'Max': np.inf, '10ᵡ':  '', 'Unit':  'dB', 'fmt': '.6f'}},
                'output_parameters' : {
                    'new_parameter1': {'LSL': -np.inf, 'LTL':  np.nan, 'Nom':  0.0, 'UTL': np.nan, 'USL': np.inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.3f'},
                    'new_parameter2': {'LSL': -np.inf, 'LTL': -5000.0, 'Nom': 10.0, 'UTL':   15.0, 'USL': np.inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.1f'},
                    'new_parameter3': {'LSL': -np.inf, 'LTL':  np.nan, 'Nom':  0.0, 'UTL': np.nan, 'USL': np.inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.6f'},
                    'new_parameter4': {'LSL': -np.inf, 'LTL':  np.nan, 'Nom':  0.0, 'UTL': np.nan, 'USL': np.inf, '10ᵡ': '', 'Unit': '?', 'fmt': '.3f'}},
                'dependencies' : {}}
        '''

        if definition['type'] != 'custom':
            raise Exception("not a 'custom' test!!!")

        groups = definition.pop('groups')
        Test.add(self.get_file_operator(), definition['name'], definition['hardware'], definition['base'], definition['type'], definition, is_enabled)
        self._update_test_groups(definition['name'], groups)
        _ = self.run_build_tool("generate", "test", self.project_directory, definition['name'], definition['hardware'], definition['base'])
        self.parent.groups_update.emit(definition['name'], groups)

    def update_custom_test(self, definition: dict, update_option: UpdateOptions):
        groups = definition['groups']
        if update_option >= UpdateOptions.DB_Update():
            self.update_custom_test_db(definition)
        if update_option == UpdateOptions.Group_Update:
            self._update_test_groups(definition['name'], groups)
            self.parent.groups_update.emit(definition['name'], groups)
        if update_option == UpdateOptions.Code_Update:
            self._update_test_code(definition)
            self._update_test_target_code(definition)
            self._update_programs_state_for_test(definition['name'])

    def _update_test_groups(self, test_name: str, groups: list):
        Group.update_groups_for_test(self.get_file_operator(), test_name, groups)

    def update_custom_test_db(self, definition):
        Test.update(self.get_file_operator(), definition['name'], definition['hardware'], definition['base'], definition['type'], definition, True)

    def _update_programs_state_for_test(self, test_name, do_validate=False):
        programs = Sequence.get_programs_for_test(self.get_file_operator(), test_name)
        programs = set([program.prog_name for program in programs if self.active_hardware in program.owner_name and self.active_base in program.owner_name])

        for program in programs:
            Program.set_program_validity(self.get_file_operator(), program, do_validate)
            _ = self.run_build_tool('generate', 'sequence', self.project_directory, program)

        self.parent.database_changed.emit(TableId.Test())
        self.parent.database_changed.emit(TableId.Flow())

    def is_test_program_valid(self, program_name):
        program = Program.get(self.get_file_operator(), program_name)
        return program.is_valid

    def _update_test_target_code(self, definition):
        targets = [target for target in self.get_test_targets_for_test(definition['name'])]
        for target in targets:
            self._update_test_changed_flag(target.name, definition['name'], definition['hardware'], definition['base'], test_changed=True)

    def _update_test_code(self, definition):
        _ = self.run_build_tool("generate", "test", self.project_directory, definition['name'], definition['hardware'], definition['base'])

    def get_tests_from_files(self, hardware, base, test_type='all'):
        '''
        given hardware , base and type this method will return a dictionary
        of tests, and as value the absolute path to the tests.
        by searching the directory structure.
        type can be:
            'standard' --> standard tests
            'custom' --> custom tests
            'all' --> standard + custom tests
        '''
        retval = {}
        tests_directory = os.path.join(self.project_directory, 'src', 'tests', hardware, base)
        potential_tests = os.listdir(tests_directory)
        from ate_spyder.widgets.actions_on.tests import standard_test_names

        for potential_test in potential_tests:
            if potential_test.upper().endswith('.PY'):  # ends with .PY, .py, .Py or .pY
                if '_' not in potential_test.upper().replace('.PY', ''):  # name doesn't contain an underscore
                    if '.' not in potential_test.upper().replace('.PY', ''):  # name doesn't contain extra dot(s)
                        if test_type == 'all':
                            retval[potential_test.split('.')[0]] = os.path.join(tests_directory, potential_test)
                        elif test_type == 'standard':
                            if '.'.join(potential_test.split('.')[0:-1]) in standard_test_names:
                                retval[potential_test.split('.')[0]] = os.path.join(tests_directory, potential_test)
                        elif test_type == 'custom':
                            if '.'.join(potential_test.split('.')[0:-1]) not in standard_test_names:
                                retval[potential_test.split('.')[0]] = os.path.join(tests_directory, potential_test)
                        else:
                            raise Exception('unknown test type !!!')
        return retval

    def get_test_table_content(self, name, hardware, base):
        table = Test.get(self.get_file_operator(), name, hardware, base)
        infos = {'name': table.name, 'hardware': table.hardware, 'type': table.type, 'base': table.base}
        infos.update(table.definition)

        return infos

    def get_test_temp_limits(self, test, hardware, base):
        test = self.get_test_table_content(test, hardware, base)
        temp = test['input_parameters']['Temperature']
        return int(temp['Min']), int(temp['Max'])

    def get_tests_from_db(self, hardware, base, test_type='all'):
        '''
        given hardware and base, this method will return a dictionary
        of tests, and as value the absolute path to the tests.
        by querying the database.
        type can be:
            'standard' --> standard tests
            'custom' --> custom tests
            'all' --> standard + custom tests
        '''

        if test_type not in ('standard', 'custom', 'all'):
            raise Exception('unknown test type !!!')

        return Test.get_for_hw_base_test_typ(self.get_file_operator(), hardware, base, test_type)

    def remove_test(self, name: str, hardware: str, base: str, group: str):
        Test.remove(self.get_file_operator(), name, hardware, base)
        Group.remove_test_from_group(self.get_file_operator(), group, name, do_commit=False)

    def replace_test(self, database):
        Test.replace(self.get_file_operator(), database)

    def get_data_for_qualification_flow(self, quali_flow_type, product):
        return QualificationFlowDatum.get_data_for_flow(self.get_file_operator(), quali_flow_type, product)

    def get_unique_data_for_qualifcation_flow(self, quali_flow_type, product):
        '''
            Returns one and only one instance of the data for a given quali_flow.
            Will throw if multiple instances are found in db.
            Will return a default item, if nothing exists.
        '''
        items = self.get_data_for_qualification_flow(quali_flow_type, product)
        if(len(items) == 0):
            data = FileOperator._make_db_object({"product": product})
            return data
        elif(len(items) == 1):
            return items[0]
        else:
            raise Exception("Multiple items for qualification flow, where only one is allowed")

    def add_or_update_qualification_flow_data(self, quali_flow_data):
        '''
            Inserts a given set of qualification flow data into the database,
            updating any already existing data with the same "name" field. Note
            that we expect a "type" field to be present.
        '''
        QualificationFlowDatum.add_or_update_qualification_flow_data(self.get_file_operator(), quali_flow_data)
        self.parent.database_changed.emit(TableId.Flow())

    def delete_qualification_flow_instance(self, quali_flow_data):
        QualificationFlowDatum.remove(self.get_file_operator(), quali_flow_data)
        self.parent.database_changed.emit(TableId.Flow())

    def insert_program(
        self, name, hardware, base, target, usertext, sequencer_typ, temperature,
        definition, owner_name, order, test_target, cache_type, caching_policy,
        test_ranges, group, instance_count: int, execution_sequence: ExecutionSequenceType
    ):
        for _, test in enumerate(definition):
            base_test_name = test['name']
            self.add_test_target(name, test_target, hardware, base, base_test_name, True, False)

        Program.add(
            self.get_file_operator(), name, hardware, base, target, usertext, sequencer_typ,
            temperature, owner_name, order, cache_type, caching_policy, test_ranges, instance_count, execution_sequence
        )
        self._insert_sequence_informations(owner_name, name, definition)
        self._generate_program_code(name, owner_name)

        Group.add_testprogram_to_group(self.get_file_operator(), group, name)

        self.parent.database_changed.emit(TableId.Flow())
        self.parent.database_changed.emit(TableId.Test())

    def _generate_program_code(self, name, owner):
        self.run_build_tool('generate', 'sequence', self.project_directory, name)

    def _insert_sequence_informations(self, owner_name, prog_name, definition):
        for index, test in enumerate(definition):
            Sequence.add_sequence_information(self.get_file_operator(), owner_name, prog_name, test['name'], index, test)

    def update_program(
        self, name, hardware, base, target, usertext, sequencer_typ, temperature,
        definition, owner_name, test_target, cache_type, caching_policy, test_ranges,
        instance_count: int, execution_sequence: ExecutionSequenceType
    ):
        self._update_test_targets_list(name, test_target, hardware, base, definition)
        Program.set_program_validity(self.get_file_operator(), name, True)
        Program.update(
            self.get_file_operator(), name, hardware, base, target, usertext, sequencer_typ,
            temperature, owner_name, cache_type, caching_policy, test_ranges,
            instance_count, execution_sequence
        )

        self._delete_program_sequence(name, owner_name)
        self._insert_sequence_informations(owner_name, name, definition)
        self._generate_program_code(name, owner_name)

        self.parent.database_changed.emit(TableId.Flow())
        self.parent.database_changed.emit(TableId.Test())

    def get_program_names_for_group(self, group):
        return Group.get_programs_for_group(self.get_file_operator(), group)

    def _get_tests_for_target(self, hardware, base, test_target):
        return [test.test for test in TestTarget.get_tests(self.get_file_operator(), hardware, base, test_target)]

    def _update_test_targets_list(self, program_name, test_target, hardware, base, definition):
        tests = []
        for test in definition:
            test.pop('is_valid', None)
            test_name = test['name']
            tests.append(test_name)

        tests.sort()
        available_tests = self._get_tests_for_target(hardware, base, test_target)
        available_tests.sort()

        diff = set(tests) - set(available_tests)
        for test_name in diff:
            self.add_test_target(program_name, test_target, hardware, base, test_name, True, False)

        diff = set(available_tests) - set(tests)
        for test_name in diff:
            self.remove_test_target(test_target, test_name, hardware, base)

    def _delete_program_sequence(self, prog_name, owner_name):
        Sequence.remove_program_sequence(self.get_file_operator(), prog_name, owner_name)

    def _generate_program_name(self, program_name, index):
        prog_name = program_name[:-1]
        return prog_name + str(index)

    def delete_program(self, program_name, owner_name, program_order, emit_event):
        self._remove_test_targets_for_test_program(program_name)

        Program.remove(self.get_file_operator(), program_name, owner_name)
        Sequence.remove_for_program(self.get_file_operator(), program_name)

        self._remove_file(self._generate_program_path(program_name))
        self._remove_file(self._generate_bin_table_path(program_name))
        self._remove_file(self._generate_auto_script_path(program_name))
        self._remove_file(self._generate_strategy_file_path(program_name))

        self._remove_testprogram_form_group_list(program_name, owner_name)

        if emit_event:
            self._update_test_program_sequence(program_order, owner_name)
            self.parent.database_changed.emit(TableId.Flow())

        self.parent.database_changed.emit(TableId.Test())

    def _remove_testprogram_form_group_list(self, prog_name: str, owner_name: str):
        # group name is contained in owner_name
        group = owner_name.split('_')[-1]
        Group.remove_testprogram_from_group(self.get_file_operator(), group, prog_name)

    @staticmethod
    def _remove_file(file_name):
        os.remove(file_name)

    def _generate_program_path(self, program_name):
        return self._generate_path_for_program_with_suffix(program_name, '.py')

    def _generate_bin_table_path(self, program_name):
        return self._generate_path_for_program_with_suffix(program_name, '_binning.json')

    def _generate_auto_script_path(self, program_name):
        return self._generate_path_for_program_with_suffix(program_name, '_auto_script.py')

    def _generate_strategy_file_path(self, program_name):
        return self._generate_path_for_program_with_suffix(program_name, '_execution_strategy.json')

    def _generate_path_for_program_with_suffix(self, program_name, suffix: str) -> Path:
        return Path(self.project_directory).joinpath('src', self.active_hardware, self.active_base, program_name + suffix)

    def _update_test_program_sequence(self, program_order, owner_name):
        # program order starts counting by one but program_order is basically the order
        # defined in the tree view so we add one (which starts with zero)
        for index in range(program_order + 1, self.get_program_owner_element_count(owner_name) + 1):
            session = self.get_file_operator()
            Program.update_program_order(session, index, owner_name, index + 1)

    @staticmethod
    def _rename_file(file_name: Path, new_name: Path):
        os.rename(str(file_name), str(new_name))

    def _remove_test_targets_for_test_program(self, prog_name):
        tests = set([seq.test for seq in Sequence.get_for_program(self.get_file_operator(), prog_name)])
        targets = [target.name for target in TestTarget.get_for_program(self.get_file_operator(), prog_name)]
        TestTarget.remove_for_test_program(self.get_file_operator(), prog_name)

        for target, test in zip(targets, tests):
            self.parent.test_target_deleted.emit(target, test)

    def move_program(self, program_name, owner_name, _program_order, is_up):
        session = self.get_file_operator()
        prog = Program.get_by_name_and_owner(session, program_name, owner_name)
        order = prog.prog_order
        prog_id = prog.id

        count = self.get_program_owner_element_count(owner_name)
        if is_up:
            if order == 0:
                return
            prev = order - 1
        else:
            if order == count - 1:
                return
            prev = order + 1

        self._update_elements(program_name, owner_name, order, prev, prog_id)

        self.parent.database_changed.emit(TableId.Flow())

    def _update_sequence(self, prog_name, new_prog_name, owner_name):
        Sequence.switch_sequences(self.get_file_operator(), prog_name, new_prog_name)

    def _get_test_program_name(self, prog_order, owner_name):
        return Program.get_by_order_and_owner(self.get_file_operator(), prog_order, owner_name).prog_name

    def _update_elements(self, prog_name, owner_name, prev_order, order, id):
        neighbour = self._get_test_program_name(order, owner_name)
        self._update_sequence(prog_name, neighbour, owner_name)

        self._update_program_order(owner_name, prev_order, order, neighbour)
        self._update_program_order_neighbour(owner_name, order, prev_order, prog_name, id)

    def _update_program_order_neighbour(self, owner_name, prev_order, order, new_name, id):
        Program._update_program_order_neighbour(self.get_file_operator(), owner_name, prev_order, order, new_name, id)

    def _update_program_order(self, owner_name, prev_order, order, new_name):
        Program._update_program_order(self.get_file_operator(), owner_name, prev_order, order, new_name)

    def get_program_owner_element_count(self, owner_name):
        return Program.get_program_owner_element_count(self.get_file_operator(), owner_name)

    def get_programs_for_owner(self, owner_name):
        return Program.get_programs_for_owner(self.get_file_operator(), owner_name)

    def get_program_configuration_for_owner(self, owner_name, prog_name):
        prog = Program.get_by_name_and_owner(self.get_file_operator(), prog_name, owner_name)
        retval = prog.__dict__.copy()
        if prog.sequencer_type != Sequencer.Static():
            retval.update({"temperature": ','.join(str(x) for x in prog.temperature)})

        return retval

    def get_program_test_configuration(self, program, owner):
        sequence = Sequence.get_for_program(self.get_file_operator(), program)
        retval = []
        for sequence_entry in sequence:
            retval.append(sequence_entry.definition)

        return retval

    def get_tests_for_program(self, prog_name, owner_name):
        return Sequence.get_for_program(self.get_file_operator(), prog_name)

    def get_programs_for_node(self, type, name):
        all = Program.get_programs_for_target(self.get_file_operator(), name)
        retval = {}

        for row in all:
            if retval.get(row.owner_name) and row.prog_name in retval[row.owner_name]:
                continue

            retval.setdefault(row.owner_name, []).append(row.prog_name)

        return retval

    def get_programs_for_test(self, test_name):
        all = Sequence.get_programs_for_test(self.get_file_operator(), test_name)
        retval = {}

        for row in all:
            if retval.get(row.owner_name) and row.prog_name in retval[row.owner_name]:
                continue

            retval.setdefault(row.owner_name, []).append(row.prog_name)

        return retval

    def get_programs_for_hardware(self, hardware):
        data = [(program.prog_name, program.owner_name) for program in Program.get_programs_for_hardware(self.get_file_operator(), hardware)]
        retval = {}

        for row in data:
            retval.setdefault(row[1], []).append(row[0])

        return retval

    def get_programs_executions_matching_hardware(self, hardware) -> Dict[str, ExecutionSequenceType]:
        return {
            x.prog_name: x.execution_sequence
            for x in Program.get_programs_for_hardware(self.get_file_operator(), hardware)
        }

    def add_parallelism_to_execution_sequence(self, parallelism_name: str, ping_pong_id: int):
        Program.add_parallelism_to_execution_sequence(self.get_file_operator(), self.active_hardware, parallelism_name, ping_pong_id)
        _ = self.run_build_tool('generate', 'sequence', self.project_directory)

    def remove_parallelism_from_execution_sequence(self, parallelism_name: str):
        Program.remove_parallelism_from_execution_sequence(self.get_file_operator(), self.active_hardware, parallelism_name)
        _ = self.run_build_tool('generate', 'sequence', self.project_directory)

    def get_ping_pong_in_executions(self, parallelism_name, ping_pong_id) -> List[str]:
        return Program.get_ping_pong_in_executions(self.get_file_operator(), parallelism_name, ping_pong_id)

    def add_test_target(self, prog_name, name, hardware, base, test, is_default, is_enabled=False):
        if TestTarget.exists(self.get_file_operator(), name, hardware, base, test, prog_name):
            return

        TestTarget.add(self.get_file_operator(), name, prog_name, hardware, base, test, is_default, is_enabled)
        self.parent.database_changed.emit(TableId.Test())

    def remove_test_target(self, name, test, hardware, base):
        TestTarget.remove(self.get_file_operator(), name, test, hardware, base)
        self.parent.test_target_deleted.emit(name, test)

    def set_test_target_default_state(self, name, hardware, base, test, is_default):
        TestTarget.set_default_state(self.get_file_operator(), name, hardware, base, test, is_default)

        self._update_test_changed_flag(name, test, hardware, base)
        self.update_test_target(name, hardware, base, test)

        self.parent.database_changed.emit(TableId.TestItem())

    def update_test_target(self, name, hardware, base, test):
        self.run_build_tool('generate', 'test_target', self.project_directory, name, hardware, base, test)
        self._update_programs_state_for_test(test, do_validate=True)

    def set_test_target_state(self, name, hardware, base, test, is_enabled):
        TestTarget.toggle(self.get_file_operator(), name, hardware, base, test, is_enabled)

    def is_test_target_set_to_default(self, name, hardware, base, test):
        return TestTarget.get(self.get_file_operator(), name, hardware, base, test).is_default

    def get_available_test_targets(self, hardware, base, test):
        return [test.name for test in TestTarget.get_for_hardware_base_test(self.get_file_operator(), hardware, base, test)]

    def get_test_targets_for_program(self, prog_name):
        return TestTarget.get_for_program(self.get_file_operator(), prog_name)

    def get_test_targets_for_test(self, test_name):
        return TestTarget.get_for_test(self.get_file_operator(), test_name, self.active_hardware, self.active_base)

    def get_depandant_test_target_for_program(self, prog_name):
        dependants = {}
        targets = [(target.test, target.name) for target in self.get_test_targets_for_program(prog_name)]
        for target in targets:
            if not dependants.get(target[0]):
                dependants.update({target[0]: [target[1]]})
            else:
                dependants[target[0]].append(target[1])

        return dependants

    def get_tests_for_test_target(self, hardware, base, test):
        return self.get_available_test_targets(hardware, base, test)

    def _update_test_changed_flag(self, target_name, test, hardware, base, test_changed=False):
        if test_changed:
            TestTarget.update_test_changed_flag(self.get_file_operator(), target_name, hardware, base, test, is_changed=True)

    def get_changed_test_targets(self, hardware, base, prog_name):
        return TestTarget.get_changed_test_targets(self.get_file_operator(), hardware, base, prog_name)

    def update_changed_state_test_targets(self, hardware, base, prog_name):
        TestTarget.update_changed_state_test_targets(self.get_file_operator(), hardware, base, prog_name)

    def get_available_testers(self):
        # TODO: implement once the pluggy stuff is in place.
        return ['SCT', 'CT']

    def _get_dependant_objects_for_node(self, node, dependant_objects, node_type):
        tree = {}
        for definition in dependant_objects:
            query = f"SELECT * FROM {definition} WHERE {node_type} = ?"
            self.cur.execute(query, (node,))
            for row in self.cur.fetchall():
                if tree.get(definition) is None:
                    tree[definition] = [row[0]]
                else:
                    tree[definition].append(row[0])

        return tree

    def get_dependant_objects_for_hardware(self, hardware):
        dependant_objects = ['devices', 'dies', 'products', 'tests']

        tree = {}
        for dep in dependant_objects:
            all = tables[dep].get_all_for_hardware(self.get_file_operator(), hardware)
            for row in all:
                if tree.get(dep) is None:
                    tree[dep] = [row.name]
                else:
                    tree[dep].append(row.name)

        programs = {'programs': self.get_programs_for_hardware(hardware)}
        if not programs['programs']:
            return tree

        tree.update(programs)
        return tree

    def get_dependant_objects_for_maskset(self, maskset):
        dependant_objects = ['dies']
        tree = {}
        for dep in dependant_objects:
            all = tables[dep].get_all_for_maskset(self.get_file_operator(), maskset)
            for row in all:
                if tree.get(dep) is None:
                    tree[dep] = [row.name]
                else:
                    tree[dep].append(row.name)

        return tree

    def get_dependant_objects_for_die(self, die):
        objs = {}
        deps = {'devices': []}
        devices = self.get_device_names()
        for name in devices:
            definition = self.get_device_definition(name)['dies_in_package']
            elements = [die_text for die_text in definition if die in die_text]
            if len(elements):
                deps['devices'].append(name)

        if deps['devices']:
            objs.update(deps)

        programs = {'programs': self.get_programs_for_node('target', die)}
        if programs['programs']:
            objs.update(programs)

        return objs

    def get_dependant_objects_for_package(self, package):
        deps = {'devices': []}
        devices = self.get_device_names()
        for name in devices:
            definition = self.get_device_package(name)
            if package in definition:
                deps['devices'].append(name)

        if len(deps['devices']) == 0:
            return {}

        return deps

    def get_dependant_objects_for_device(self, device):
        deps = {'products': []}
        product = self.get_products_for_device(device)
        deps['products'] = product

        if len(deps['products']) == 0:
            return {}

        return deps

    def get_dependant_objects_for_test(self, test):
        return self.get_programs_for_test(test)

    def get_hardware_state(self, name):
        return Hardware.get_state(self.get_file_operator(), name)

    def update_hardware_state(self, name, state):
        Hardware.update_state(self.get_file_operator(), name, state)
        if not state:
            self.parent.hardware_removed.emit(name)
        else:
            self.parent.hardware_added.emit(name)

    def get_maskset_state(self, name):
        return Maskset.get(self.get_file_operator(), name).is_enabled

    def update_maskset_state(self, name, state):
        Maskset.update_state(self.get_file_operator(), name, state)

    def get_die_state(self, name):
        return Die.get(self.get_file_operator(), name).is_enabled

    def update_die_state(self, name, state):
        Die.update_state(self.get_file_operator(), name, state)
        self.parent.update_target.emit()

    def get_package_state(self, name):
        return Package.get(self.get_file_operator(), name).is_enabled

    def update_package_state(self, name, state):
        Package.update_state(self.get_file_operator(), name, state)

    def get_device_state(self, name):
        return Device.get(self.get_file_operator(), name).is_enabled

    def update_device_state(self, name, state):
        Device.update_state(self.get_file_operator(), name, state)
        self.parent.update_target.emit()

    def get_product_state(self, name):
        return Product.get(self.get_file_operator(), name).is_enabled

    def update_product_state(self, name, state):
        Product.update_state(self.get_file_operator(), name, state)

    def get_test(self, name, hardware, base):
        return Test.get(self.get_file_operator(), name, hardware, base)

    def store_plugin_cfg(self, hw, object_name, cfg):
        file_dir = os.path.join(self.project_directory, "src", hw)
        file_path = os.path.join(file_dir, f"{object_name}.json")
        with open(file_path, 'w+') as writer:
            writer.write(json.dumps(cfg))

    def load_plugin_cfg(self, hw, object_name):
        file_path = os.path.join(self.project_directory, "src", hw, f"{object_name}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as reader:
                raw = reader.read()
                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return {}
        else:
            return {}

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        pass

    def delete_item(self, type, name):
        tables[type].remove(self.get_file_operator(), name)
        self.parent.database_changed.emit(TableId.Definition())

        # TODO: exception should be removed later
        try:
            definitions[type].remove(self.get_file_operator(), name)
        except KeyError:
            pass

    def last_project_setting(self):
        return os.path.join(self.project_directory, '.lastsettings')

    def store_settings(self, hardware, base, target):
        import json
        settings = {'settings': {'hardware': hardware,
                                 'base': base,
                                 'target': target}
                    }

        with open(self.last_project_setting(), 'w') as f:
            json.dump(settings, f, indent=4)

    def load_project_settings(self):
        import json
        settings_path = self.last_project_setting()
        if not os.path.exists(settings_path):
            return '', '', ''

        with open(settings_path, 'r') as f:
            settings = json.load(f)
            try:
                settings = settings['settings']
                if not len(settings['hardware']):
                    return '', '', ''

                return settings['hardware'], settings['base'], settings['target']
            except Exception:
                return '', '', ''

    def get_version(self) -> str:
        return Version.get(self.get_file_operator()).version

    def get_test_groups(self, test_name: str) -> list:
        return [group.name for group in self.get_groups_for_test(test_name)]

    def does_test_exist(self, name, hardware, base) -> bool:
        return Test.get_one_or_none(self.get_file_operator(), name, hardware, base) is not None

    def get_test_path(self, name, hardware, base):
        return Path(self.project_directory).joinpath('src', hardware, base, name, name)
