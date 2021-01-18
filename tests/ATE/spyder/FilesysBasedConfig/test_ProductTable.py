import os
from pytest import fixture

from ATE.spyder.widgets.FileBasedConfig.FileOperator import FileOperator
from ATE.spyder.widgets.FileBasedConfig.Product import Product

CURRENT_DIR = os.path.join(os.path.dirname(__file__))


@fixture
def fsoperator():
    fs = FileOperator(CURRENT_DIR)
    fs.query("product").delete().commit()
    return fs


@fixture
def prod():
    return Product()


def test_can_create_product(fsoperator, prod: Product):
    prod.add(fsoperator, "foo", "dev", "hw57", "qual", "A", "B", "ASIC", "Evil Monkey", False)
    pkg = prod.get(fsoperator, "foo")
    assert(pkg.hardware == "hw57")
