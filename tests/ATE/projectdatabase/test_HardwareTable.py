import os
from pytest import fixture

from ATE.projectdatabase.FileOperator import FileOperator
from ATE.projectdatabase.Hardware import Hardware

CURRENT_DIR = os.path.join(os.path.dirname(__file__))


@fixture
def fsoperator():
    fs = FileOperator(CURRENT_DIR)
    fs.query("hardware").delete().commit()
    return fs


@fixture
def hw():
    return Hardware()


def test_can_create_hardware(fsoperator, hw: Hardware):
    hw.add(fsoperator, "hw0", {}, True)
    pkg = hw.get(fsoperator, "hw0")
    assert(pkg.is_enabled)
