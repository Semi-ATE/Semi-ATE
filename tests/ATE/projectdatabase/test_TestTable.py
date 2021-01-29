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
def tst():
    return Test()


def test_can_create_test(fsoperator, tst: Test):
    tst.add(fsoperator, "testname", "hw0", "PR", "sometype", {}, True)
    pkg = tst.get(fsoperator, "testname", "hw0", "PR")
    assert(pkg.type == "sometype")
