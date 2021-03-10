import os
from pytest import fixture

from ATE.projectdatabase.FileOperator import FileOperator
from ATE.projectdatabase.Settings import Settings

CURRENT_DIR = os.path.join(os.path.dirname(__file__))


@fixture
def fsoperator():
    fs = FileOperator(CURRENT_DIR)
    fs.query("settings").delete().commit()
    return fs


@fixture
def settings():
    return Settings()


def test_can_create_program(fsoperator, settings: Settings):
    settings.set_quality_grade(fsoperator, "foo")
    settings.set_quality_grade(fsoperator, "funky")
    assert settings.get_quality_grade(fsoperator) == "funky"
