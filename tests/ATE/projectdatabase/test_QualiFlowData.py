import os
from pytest import fixture

from ATE.projectdatabase.FileOperator import FileOperator
from ATE.projectdatabase.QualificationFlow import QualificationFlowDatum
from tests.ATE.spyder.widgets.CI.qt.qualification_wizard.mock_db_object import MockDBObject
CURRENT_DIR = os.path.join(os.path.dirname(__file__))


@fixture
def fsoperator():
    fs = FileOperator(CURRENT_DIR)
    fs.query("test").delete().commit()
    return fs


@fixture
def quali():
    return QualificationFlowDatum()


def test_can_create_item(fsoperator, quali: QualificationFlowDatum):
    quali.add_or_update_qualification_flow_data(fsoperator, MockDBObject.from_dict({"name": "test"}))
    quali.add_or_update_qualification_flow_data(fsoperator, MockDBObject.from_dict({"name": "test", "highway": "myway"}))
    item = quali._get_by_name(fsoperator, "test")
    assert(item.highway == "myway")
