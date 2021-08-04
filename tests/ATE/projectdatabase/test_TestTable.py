import os
from pytest import fixture

from ATE.projectdatabase.FileOperator import FileOperator
from ATE.projectdatabase.Test import Test

CURRENT_DIR = os.path.join(os.path.dirname(__file__))


@fixture
def fsoperator():
    fs = FileOperator(CURRENT_DIR)
    fs.query("test").delete().commit()
    return fs


@fixture
def test():
    return Test()


def test_can_create_test(fsoperator, test: Test):
    test.add(fsoperator, "testname", "hw0", "PR", "sometype", {}, True)
    pkg = test.get(fsoperator, "testname", "hw0", "PR")
    assert(pkg.type == "sometype")


NEW = {"name": "testname", "hardware": "hw0", "base": 'PR', "type": 'somethingelse', "definition": {'test': 'hello'}, "is_enabled": True}


def test_replace_test(fsoperator, test: Test):
    test.add(fsoperator, "testname", "hw0", "PR", "sometype", {}, True)
    assert len(test.get(fsoperator, 'testname', 'hw0', 'PR').definition) == 0
    test.replace(fsoperator, NEW)
    assert len(test.get(fsoperator, 'testname', 'hw0', 'PR').definition) != 0
    assert test.get(fsoperator, 'testname', 'hw0', 'PR').definition['type'] == 'somethingelse'
