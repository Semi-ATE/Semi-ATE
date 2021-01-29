import os
from pytest import fixture

from ATE.projectdatabase.FileOperator import FileOperator
from ATE.projectdatabase.Maskset import Maskset

CURRENT_DIR = os.path.join(os.path.dirname(__file__))


@fixture
def fsoperator():
    fs = FileOperator(CURRENT_DIR)
    fs.query("masksets").delete().commit()
    return fs


@fixture
def maskset():
    return Maskset()


def test_can_create_maskset(fsoperator, maskset: Maskset):
    maskset.add(fsoperator, "foo", "acme inc", {}, False)
    pkg = maskset.get(fsoperator, "foo")
    assert(pkg.customer == "acme inc")
