import os
from pytest import fixture

from ate_projectdatabase.FileOperator import FileOperator
from ate_projectdatabase.QualificationFlow import QualificationFlowDatum

class MockDBObject:

    def __init__(self,):
        self.dict = {}

    def from_dict(d: dict):
        result = MockDBObject()
        result.dict = d
        return result

    def get_definition(self):
        return {}

    def to_dict(self):
        return self.dict

    def write_attribute(self, member_name: str, value):
        self.dict[member_name] = value

    def read_attribute(self, attribute_name):       # Returntype can be just about anything!
        return self.dict[attribute_name]

    def has_attribute(self, attribute_name: str) -> bool:
        return attribute_name in self.dict


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
