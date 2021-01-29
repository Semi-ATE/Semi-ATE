import os
from pytest import fixture

from ATE.projectdatabase.FileOperator import FileOperator
from ATE.projectdatabase.Die import Die

CURRENT_DIR = os.path.join(os.path.dirname(__file__))


@fixture
def fsoperator():
    fs = FileOperator(CURRENT_DIR)
    fs.query("die").delete().commit()
    return fs


@fixture
def die():
    return Die()


def test_can_create_die(fsoperator, die: Die):
    die.add(fsoperator, "foo", "hw0", "somepack", "qual", "A", "B", "ASIC", "Evil Monkey", False)
    pkg = die.get(fsoperator, "foo")
    assert(pkg.customer == "Evil Monkey")
