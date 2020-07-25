# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 16:40:44 2020

@author: hoeren
"""
import abc
import hashlib
import inspect

class testABC(abc.ABC):

    def __init__(self):
        self.do_you_know = 'FUBAR'
        self.me_myself_and_I = __file__

    @abc.abstractmethod
    def do(self):
        pass

    def _get_method_info(self, obj):
        '''
        this method returns a tuple (source_file, source_lines, line_number, doc_string) of obj.
        obj **must** be a method object!
        '''
        if not inspect.ismethod(obj):
            raise Exception("What is going on ?!? 'obj' should be a menthod !!!")
        source_file = inspect.getfile(obj)
        source_lines, line_number = inspect.getsourcelines(obj)
        doc_string = inspect.getdoc(obj)
        return(source_file, source_lines, line_number, doc_string)

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



class A(testABC):

    def do(self):
        # foo
        pass


    def do_target1(self):
        '''
        docstring
        '''
        retval = {}
        return retval

    def do_target2(self):
        # some comment
        return self.do()

    def do_target3(self):
        return self.do()

if __name__ == '__main__':

    a = A()
    targets = a._get_targets()
    print(targets)
