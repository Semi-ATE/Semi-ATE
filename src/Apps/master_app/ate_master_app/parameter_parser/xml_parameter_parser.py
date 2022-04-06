import xmltodict


class XmlParameterParser:

    def __init__(self):
        self.xml_data = None
        self.root = None
        self.param_dict = {"MAIN": None,
                           "CLUSTER": None,
                           "TESTPROGRAM": None,
                           "HANDLERSECTION": None,
                           "PAT": None,
                           "STATION": None,
                           "DIEELEMENT_COUNT": None,
                           "DIEELEMENT": None}

    def parse(self, path: str) -> dict:
        with open(path) as x:
            param = xmltodict.parse(x.read())
            self.root = next(iter(param))

        self.param_dict.update(param.get(self.root))
        return self.param_dict
