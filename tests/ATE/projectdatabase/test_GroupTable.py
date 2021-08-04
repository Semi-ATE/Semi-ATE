import os
from _pytest.fixtures import get_scope_node
from pytest import fixture

from ATE.projectdatabase.FileOperator import FileOperator
from ATE.projectdatabase.Group import Group

CURRENT_DIR = os.path.join(os.path.dirname(__file__))


@fixture
def fsoperator():
    fs = FileOperator(CURRENT_DIR)
    fs.query("group").delete().commit()
    return fs


@fixture
def group():
    return Group()


def test_create_group(fsoperator, group: Group):
    group.add(fsoperator, 'test')
    assert len(group.get_all(fsoperator)) == 1


def test_update_state(fsoperator, group: Group):
    group.add(fsoperator, 'test')
    group.update_state(fsoperator, 'test', False)

    assert group.get(fsoperator, 'test').is_selected is False


def test_remove_group(fsoperator, group: Group):
    group.add(fsoperator, 'test')
    group.remove(fsoperator, 'test')
    assert len(group.get_all(fsoperator)) == 0


def test_add_remove_program_from_group(fsoperator, group: Group):
    group.add(fsoperator, 'test')
    assert len(group.get(fsoperator, 'test').programs) == 0
    group.add_testprogram_to_group(fsoperator, 'test', 'test_program_1')
    assert len(group.get(fsoperator, 'test').programs) == 1
    group.remove_testprogram_from_group(fsoperator, 'test', 'test_program_1')
    assert len(group.get(fsoperator, 'test').programs) == 0


def test_add_remove_test_from_group(fsoperator, group: Group):
    group.add(fsoperator, 'test')
    assert len(group.get(fsoperator, 'test').tests) == 0
    group.add_test_to_group(fsoperator, 'test', 'test_1')
    assert len(group.get(fsoperator, 'test').tests) == 1
    group.remove_test_from_group(fsoperator, 'test', 'test_1')
    assert len(group.get(fsoperator, 'test').tests) == 0


def test_get_groups_for_test(fsoperator, group: Group):
    group.add(fsoperator, 'test')
    group.add_test_to_group(fsoperator, 'test', 'test_1')

    assert len(group.get_all_groups_for_test(fsoperator, 'test_1')) == 1


def test_update_groups_for_test(fsoperator, group: Group):
    group.add(fsoperator, 'test')
    group.add(fsoperator, 'group')
    group.add_test_to_group(fsoperator, 'test', 'test_1')
    group.update_groups_for_test(fsoperator, 'test_1', ['test', 'group'])

    assert len(group.get_all_groups_for_test(fsoperator, 'test_1')) == 2
