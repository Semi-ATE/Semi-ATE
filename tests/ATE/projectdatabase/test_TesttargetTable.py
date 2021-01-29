import os
from pytest import fixture

from ATE.projectdatabase.FileOperator import FileOperator
from ATE.projectdatabase.TestTarget import TestTarget

CURRENT_DIR = os.path.join(os.path.dirname(__file__))


@fixture
def fsoperator():
    fs = FileOperator(CURRENT_DIR)
    fs.query("testtarget").delete().commit()
    return fs


@fixture
def target():
    return TestTarget()


def test_can_create_testtarget(fsoperator, target: TestTarget):
    target.add(fsoperator, "targetname", "aprog", "hw57", "mybase", "test", True, True)
    pkg = target.get(fsoperator, "targetname", "hw57", "mybase", "test")
    assert(pkg.prog_name == "aprog")
