import os
from pytest import fixture

from ATE.projectdatabase.FileOperator import FileOperator
from ATE.projectdatabase.Sequence import Sequence

CURRENT_DIR = os.path.join(os.path.dirname(__file__))


@fixture
def fsoperator():
    fs = FileOperator(CURRENT_DIR)
    fs.query("sequence").delete().commit()
    return fs


@fixture
def seq():
    return Sequence()


def test_can_create_sequence(fsoperator, seq: Sequence):
    seq.add_sequence_information(fsoperator, "owner", "progname", "test", 1047, {})
    pkg = seq.get_for_program(fsoperator, "progname")
    assert(pkg[0].owner_name == "owner")


def test_can_use_multiple_sequences_different_owners(fsoperator, seq: Sequence):
    seq.add_sequence_information(fsoperator, "owner1", "progname1", "test", 1047, {})
    seq.add_sequence_information(fsoperator, "owner2", "progname2", "test", 1047, {})
    pkg = seq.get_for_program(fsoperator, "progname1")
    assert(pkg[0].owner_name == "owner1")
