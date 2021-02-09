import os
from pytest import fixture

from ATE.projectdatabase.FileOperator import FileOperator
from ATE.projectdatabase.Program import Program

CURRENT_DIR = os.path.join(os.path.dirname(__file__))


@fixture
def fsoperator():
    fs = FileOperator(CURRENT_DIR)
    fs.query("program").delete().commit()
    return fs


@fixture
def program():
    return Program()


def test_can_create_program(fsoperator, program: Program):
    program.add(fsoperator, "foo", "hw0", "PR", "some target", "A", "B", "ASIC", "Evil Monkey", 1, "cache", "cachepolicy", "101")
    pkg = program.get(fsoperator, "foo")
    assert(pkg.base == "PR")
