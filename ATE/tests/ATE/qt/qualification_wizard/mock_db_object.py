
class MockDBObject:

    def __init__(self, definition):
        self.__definition = definition

    def get_definition(self):
        return self.__definition
