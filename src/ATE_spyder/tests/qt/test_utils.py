from ate_spyder.widgets.actions_on.tests.TestItems.utils import generate_file_content, FileStruct
from pytest import fixture
import io


def generate_content(test_name):
    content = f'''#!/usr/bin/env conda run -n ATE python
    # -*- coding: utf-8 -*-
    """
    By abdou (abdou@awinia.lan)
    """
    if __name__ == '__main__':
        from {test_name}_BC import {test_name}_BC
    else:
        from {test_name}.{test_name}_BC import {test_name}_BC


    class {test_name}({test_name}_BC):
        def do(self):
            """Default implementation for test."""

            # sleep used only for test puposes (CI build), without provoking sleep the test-app's state change from ready to testing could not be detected 
            # must be removed when start implementing the test !!
            import time
            time.sleep(2)

            self.op.new_parameter1.default()
    '''

    buf = io.StringIO(content)
    return buf.readlines()


@fixture
def file_struct():
    data = {}
    data.update({'version': '1'})
    data.update({'database': {'name': 'new_name'}})
    data.update({'groups': ['test']})
    data.update({'file': generate_content('aa')})

    return FileStruct(**data)


def test_generate_file_content(file_struct: FileStruct):
    new_content = generate_file_content(file_struct, 'aa')

    assert new_content.find('aa') == -1
    assert new_content.find('aa_BC') == -1
    assert new_content.count('new_name_BC') > 0
    assert new_content.count('new_name') > 0
