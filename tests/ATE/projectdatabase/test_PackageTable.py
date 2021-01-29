import os
from pytest import fixture

from ATE.projectdatabase.FileOperator import FileOperator
from ATE.projectdatabase.Package import Package

CURRENT_DIR = os.path.join(os.path.dirname(__file__))


@fixture
def fsoperator():
    fs = FileOperator(CURRENT_DIR)
    fs.query("package").delete().commit()
    return fs


@fixture
def package():
    return Package()


def test_can_create_package(fsoperator, package):
    package.add(fsoperator, "foo", 4, False, False)
    pkg = package.get(fsoperator, "foo")
    assert(pkg.leads == 4)


def test_can_update_package(fsoperator, package):
    package.add(fsoperator, "foo", 4, False, False)
    package.update(fsoperator, "foo", 6, False, False)
    pkg = package.get(fsoperator, "foo")
    assert(pkg.leads == 6)
