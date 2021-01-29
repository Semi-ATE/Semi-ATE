import os
from pytest import fixture

from ATE.projectdatabase.FileOperator import FileOperator

CURRENT_DIR = os.path.join(os.path.dirname(__file__))


@fixture
def fsoperator():
    return FileOperator(CURRENT_DIR)


def test_can_create_operator(fsoperator):
    assert(True)


def test_can_load_data(fsoperator):
    fsoperator.query("dummydata")


def test_can_get_all_data(fsoperator):
    fsoperator.query_with_subtype("dummydata", "test1").filter(lambda x: True).delete().commit()
    fsoperator.query_with_subtype("dummydata", "test1").insert([{'foo': 'bar'}, {'foo': "fork"}]).commit()
    data = fsoperator.query("dummydata").all()
    assert (len(data) == 2)


def test_can_get_specific_data(fsoperator):
    fsoperator.query_with_subtype("dummydata", "test1").filter(lambda x: True).delete().commit()
    fsoperator.query_with_subtype("dummydata", "test1").insert([{'id': 'bar'}, {'id': "fork"}]).commit()
    data = fsoperator.query("dummydata").filter(lambda x: x.id == "bar").all()
    assert(len(data) == 1)


def test_can_get_unique_item(fsoperator):
    fsoperator.query_with_subtype("dummydata", "test1").filter(lambda x: True).delete().commit()
    fsoperator.query_with_subtype("dummydata", "test1").insert([{'id': 'bar'}, {'id': "fork"}]).commit()
    data = fsoperator.query("dummydata").filter(lambda x: x.id == "bar").one()
    data.id == "bar"


def test_can_add_item(fsoperator):
    fsoperator.query("adddelete").insert([{'foo': 'bar'}, {'foo': "fork"}]).commit()
    fsoperator.query("adddelete").filter(lambda x: x.foo == "bar").one()
    fsoperator.query("adddelete").filter(lambda x: x.foo == "bar").delete().commit()
    # file should be empty now, so queryiing again should yield no result:
    items = fsoperator.query("adddelete").filter(lambda x: x.foo == "bar").all()
    assert(len(items) == 0)


def test_can_update_item(fsoperator):
    fsoperator.query("updateitem").filter(lambda x: True).delete().commit()
    fsoperator.query("updateitem").insert([{'foo': 'bar', "test": 1}, {'foo': "fork", "test": 2}]).commit()
    item = fsoperator.query("updateitem").filter(lambda x: x.test == 2).one()
    item.test = 3
    fsoperator.commit()
    item = fsoperator.query("updateitem").filter(lambda x: x.foo == "fork").one()
    assert(item.test == 3)


def test_can_sort_items(fsoperator):
    fsoperator.query("updateitem").filter(lambda x: True).delete().commit()
    fsoperator.query("updateitem").insert([{'foo': 'bar', "test": 2}, {'foo': "fork", "test": 7}, {'foo': "fork", "test": 1}]).commit()
    items = fsoperator.query("updateitem").sort(lambda x: x.test).all()
    assert(len(items) == 3)
    assert(items[0].test == 1)
    assert(items[1].test == 2)
    assert(items[2].test == 7)


def test_can_count_items(fsoperator):
    fsoperator.query("updateitem").filter(lambda x: True).delete().commit()
    fsoperator.query("updateitem").insert([{'foo': 'bar', "test": 2}, {'foo': "fork", "test": 7}, {'foo': "fork", "test": 1}]).commit()
    numitems = fsoperator.query("updateitem").sort(lambda x: x.test).count()
    assert(numitems == 3)


def test_can_use_subtype(fsoperator):
    fsoperator.query_with_subtype("dummydata2", "test1")\
              .insert([{"a": 1, "b": 2}])\
              .commit()


def test_can_delete_subtype(fsoperator):
    # Make sure the file is empty
    fsoperator.query_with_subtype("dummydata", "test1")\
              .delete()\
              .commit()

    fsoperator.query_with_subtype("dummydata", "test1")\
              .insert([{"a": 1, "b": 2}])\
              .commit()

    all_items = fsoperator.query_with_subtype("dummydata", "test1").all()
    assert(len(all_items) == 1)

    fsoperator.query_with_subtype("dummydata", "test1")\
              .delete()\
              .commit()

    items = fsoperator.query_with_subtype("dummydata", "test1")\
                      .all()
    assert(len(items) == 0)


def test_can_rename_thingy(fsoperator):
    fsoperator.query_with_subtype("dummydata2", "test1")\
              .delete()\
              .commit()

    fsoperator.query_with_subtype("dummydata2", "test2")\
              .delete()\
              .commit()

    fsoperator.query_with_subtype("dummydata2", "test1")\
              .insert([{"a": 1, "b": 2}])\
              .commit()

    fsoperator.rename("dummydata2", "test1", "test2")
    items = fsoperator.query_with_subtype("dummydata2", "test2").all()
    assert(len(items) == 1)
