
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
