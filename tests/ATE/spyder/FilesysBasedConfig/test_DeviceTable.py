import pytest
import os
from pytest import fixture

from ATE.spyder.widgets.FileBasedConfig.FileOperator import FileOperator
from ATE.spyder.widgets.FileBasedConfig.Device import Device

CURRENT_DIR = os.path.join(os.path.dirname(__file__))


@fixture
def fsoperator():
    fs = FileOperator(CURRENT_DIR)
    fs.query("device").delete().commit()
    return fs


@fixture
def device():
    return Device()


def test_can_create_device(fsoperator, device: Device):
    device.add(fsoperator, "foo", "hw0", "somepack", {}, False)
    pkg = device.get(fsoperator, "foo")
    assert(pkg.hardware == "hw0")
