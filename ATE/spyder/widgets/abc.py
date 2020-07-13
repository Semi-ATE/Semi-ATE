# -*- coding: utf-8 -*-
'''
Created on 24 Oct 2016

@author: tho

'''

import inspect, imp
import logging
import os, sys, re
import copy
import random
import hashlib
import abc.ABC

Pass = 1
Fail = 0
Undetermined = -1
Unknown = -1

class testABC(abc.ABC):
    '''
    This is the Abstract Base Class for all ATE.org tests.
    '''
    input_parameters = {}
    output_parameters = {}
    patterns = []
    tester_states = []
    test_dependencies = []
    tester = None
    ran_before = False

    def __init__(self, call_values=None, limits=None, SBINs=None):
        self.name = self.__class__.__name__
        tmp = str(inspect.getmodule(self)).split("from '")[1].replace("'", '').replace('>', '').split('/')
        self.test_dir = os.sep.join(tmp[0:-1])
        self.file_name = tmp[-1]
        self.file_name_and_path = os.sep.join(tmp)
        self.project_path = os.sep.join(tmp[0:-3])
        self.project_name = tmp[-3]

        logging.debug("Initializing test '%s' in module '%s'" % (self.name, self.file_name_and_path))

        #self._add_setup_states_to_start_state()
        #self._add_teardown_states_to_end_state()
        self._extract_patterns()
        self._extract_tester_states()




        self._extract_tester()
        self.sanity_check()

    def __call__(self, input_parameters, output_parameters, extra_output_parameters, data_manager):
        '''
        This method is how the test will be called from a higher level
        '''
        # retval = self.do(input_parameters, output_parameters, extra_output_parameters, data_manager)


    def __del__(self):
        pass


    @abc.abstractmethod
    def do(self, ip, op, ep, dm):
        pass

    def _extract_definition(self):
        '''
        this method will create the defintion dictionary from the overloaded class.
        '''
        retval = {}
        retval['name'] = '.'.join(os.path.split(os.path.basename(__file__), '.')[:-1]) # file name without the last extension
        if retval['name'] != self.name:
            raise Exception(f"the file name and the test-class name don't match ('{retval['name']}' vs '{self.name}'")
        retval['type'] = self.Type
        retval['hardware'] = self.hardware
        retval['base'] = self.base
        retval['docstring'] = inspect.getdoc(self)
        retval['input_parameters'] = self.input_parameters
        retval['output_parameters'] = self.output_parameters
        retval['dependencies'] = {} #TODO: add the dependencies when available

        return retval

    def _extract_tester(self):
        '''
        This method will extract the used tester from the loaded objects.
        '''
        retval = 'SCT'
        #TODO: need to see how pluggy 'identifies' testers.
        return 'SCT'

    def _get_imports(self):
        '''
        This method will return a list of all imports of this (test) module.
        Each import is a tuple formatted as follows (from, what, as)
            'from bla.bla.bla import foo as bar" --> ('bla.bla.bla', 'foo', 'bar')
            'import os' --> ('', os, '')
        '''
        retval = []
        fp, pathname, description = imp.find_module(self.name, [self.test_dir])
        module = imp.load_module(self.name, fp, pathname, description)
        for member in inspect.getmembers(module):
            print(member)

        return retval

    def _get_method_source(self, method):
        '''
        This method will return the source code of the named method of the test class
        '''
        fp, pathname, description = imp.find_module(self.name, [self.test_dir])
        module = imp.load_module(self.name, fp, pathname, description)
        class_of_interest = None
        retval = ''
        for member in inspect.getmembers(module, inspect.isclass):
            if member[0] == self.name:
                class_of_interest = member[1]
        print(method)
        print(class_of_interest)
        if class_of_interest is not None:
            method_of_interest = None
            for member in inspect.getmembers(class_of_interest, inspect.ismethod):
                print(member)
                if member[0] == method:
                    method_of_interest = member[1]
            print(method_of_interest)
            retval = inspect.getsource(method_of_interest)
        return retval

    def _set_method_source(self, method, source):
        '''

        '''
        pass

    def _add_target(self, target_name):
        '''
        this method adds a new do_target to the source.
        (alphabetically inserted)
        '''
        temp_file = os.path.join(__file__, '.tmp')
        existing_targets = self._get_targets()
        new_target = f"do_{target_name}"
        if new_target not in existing_targets:
            target_lines = {key:existing_targets[key][1] for key in existing_targets}
            target_lines[new_target] = -1
            last_target_line = 0
            break_on_next = False
            for target in sorted(target_lines):
                if target == new_target:
                    break_on_next = True
                else:
                    last_target_line = target_lines[target]
                    if break_on_next:
                        break
            insertion_line = last_target_line
            line_nr = 0
            with open(__file__, 'r') as ifd, open(temp_file, 'w') as ofd:
                if line_nr == insertion_line:
                    ofd.write(f"\tdef {new_target}(ip, op):\n")
                    ofd.write("\t\treturn self.do(ip, op)\n\n")
                line = ifd.readline()
                line_nr+=1
                ofd.write(f"{line}\n")

    def _get_method_info(self, method_object):
        '''
        this method returns a tuple (source_file, source_lines, line_number, doc_string) of obj.
        obj **must** be a method object!
        '''
        if not inspect.ismethod(method_object):
            raise Exception("What is going on ?!? 'obj' should be a menthod !!!")
        source_file = inspect.getfile(method_object)
        source_lines, line_number = inspect.getsourcelines(method_object)
        doc_string = inspect.getdoc(method_object)
        return(source_file, source_lines, line_number, doc_string)

    def _get_targets(self):
        '''
        this method returns a dictionary with as key the 'do' and 'do_' methods defined,
        and as value a tuple (method_code_hash, default, source_file_name, line_number)
        where default indicates if the 'do' function is called (directly) or not.
        line_number is the line number on which the method is defined.
        Notes
            - Of course the 'do' method itself is always 'default' 🙂
        TODO:
            - exclude the docstring from the code prior to hashing
            - get how 'do' is called, and use that for all members (instead of static compare)
        '''
        retval ={}
        all_members = inspect.getmembers(self)
        members_of_interest = {}
        for member in all_members:
            if member[0]=='do' or member[0].startswith('do_'):
                if inspect.ismethod(member[1]):
                    members_of_interest[member[0]] = member[1]
        if not 'do' in members_of_interest:
            raise Exception("What the fuck!, where is the default 'do' implementation ?!?")

        for member in members_of_interest:
            source_file, source_lines, line_number, doc_string = self._get_method_info(members_of_interest[member])
            method_code_hash = self._calculate_hash(source_lines, doc_string)
            if member == 'do':
                members_of_interest[member] = (method_code_hash, True, source_file, line_number)
            else:
                if source_lines[-1].strip() == 'return self.do()':
                    members_of_interest[member] = (method_code_hash, True, source_file, line_number)
                else:
                    members_of_interest[member] = (method_code_hash, False, source_file, line_number)

        return members_of_interest

    def _calculate_hash(self, source_lines, doc_string):
        '''
        this method calculates tha hash of the source_lines (excluding the
        doc_string and any commented out lines).
        '''
        def cleanup(source_lines, doc_string, block_size):
            '''
            this method removes the doc_string and any comments from source_lines
            and returns the concateneted ASCII version of the source_lines in a
            list of block_size chunks.
            '''
            pure_ascii_code = b''
            my_doc_string = ''
            in_doc_string = False
            for index in range(1, len(source_lines)):
                line = source_lines[index].lstrip()
                if in_doc_string:
                    if line.rstrip().endswith("'''") or line.rstrip().endswith('"""'):
                        in_doc_string = False
                        if line.rstrip()[:-3] != '':
                            my_doc_string += line.rstrip()[:-3]
                        else:
                            my_doc_string = my_doc_string.rstrip()
                        continue
                    else:
                        if line == '':
                            my_doc_string += '\n'
                        else:
                            my_doc_string += line
                else:
                    if line.startswith("'''") or line.startswith('"""'):
                        if line.rstrip().endswith("'''") or line.rstrip().endswith('"""'):
                            pass
                        else:
                            in_doc_string = True
                            if line[3:].strip() != '':
                                my_doc_string += line[3:]
                            continue
                    else:
                        pure_ascii_code += source_lines[index].encode('ascii', 'ignore')
            if my_doc_string == '':
                my_doc_string = None



            print(source_lines[0].strip())
            print('-'*len(source_lines[0].strip()))
            print(my_doc_string)
            print('='*100)
            print(doc_string)
            print('-'*99, '>', my_doc_string == doc_string)







            if len(pure_ascii_code)>block_size:
                pure_ascii_code_chunks = [pure_ascii_code[i*block_size:(i+1)*block_size] for i in range(int(len(pure_ascii_code)/block_size))]
                if len(pure_ascii_code)%block_size!=0:
                    pure_ascii_code_chunks+=[pure_ascii_code[int(len(pure_ascii_code)/block_size):]]
            else:
                pure_ascii_code_chunks = [pure_ascii_code]
            return pure_ascii_code_chunks

        method_hash = hashlib.sha512()
        pure_ascii_code_chunks = cleanup(source_lines, doc_string, method_hash.block_size)
        for pure_ascii_code_chunk in pure_ascii_code_chunks:
            method_hash.update(pure_ascii_code_chunk)
        return method_hash.hexdigest()




    def run(self, from_state, to_state, ip, op, eop=None, dm=None):
        logging.debug("Running test '%s' from start_state '%s' to end_state '%s' with parameters '%s'" % (self.name, from_state, to_state, ip))
        if from_state != self.start_state[0]:
            if from_state in self.start_state[1]:
                logging.debug("   Executing setup(%s)" % from_state)
                self.pre_do(from_state)
            else:
                msg = "Test '%s' doesn't support running from '%s' state" % (self.name, from_state)
                logging.critical(msg)
                raise Exception(msg)
        else:
            logging.debug("   Skipping pre_do")
        logging.debug("   Executing do(%s, %s, %s, %s)" % (ip, op, eop, dm))
        retval = self.do(ip, op, eop, dm)
        logging.debug("   do returned '%s'" % retval)
        if to_state != self.end_state[0]:
            if to_state in self.end_state[1]:
                logging.debug("   Executing teardown(%s)" % to_state)
                self.post_do(to_state)
            else:
                msg = "Test '%s' doesn't support running to '%s' state" % (self.name, to_state)
                logging.critical(msg)
                raise Exception(msg)
        else:
            logging.debug("   Skipping post_do")
        bin_code = int(random.uniform(0, 100)) #TODO: pass op & eop to the data manager and get a bincode back.
        logging.debug("   data manager returned (soft) bincode '%s'" % bin_code)
        if not self.ran_before:
            self.ran_fefore = True

def isEmptyFunction(func):
    '''
    This function will determine if the passed func (or method) is empty or not.
    A doc-string may be present but doesn't influence this function, nor does multiple pass statements.
    '''
    def empty_func():
        pass

    def empty_func_with_doc():
        """Empty function with docstring."""
        pass

    return func.__code__.co_code == empty_func.__code__.co_code or func.__code__.co_code == empty_func_with_doc.__code__.co_code

if __name__ == '__main__':
    pass
    #TODO: Implement the unit tests here ...
