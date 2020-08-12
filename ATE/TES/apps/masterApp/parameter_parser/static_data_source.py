class StaticDataSource:
    def __init__(self):
        pass

    def retrieve_data(self) -> dict:
        return {}

    def verify_data(self, data) -> bool:
        return data is not None

    def get_test_information(self, data) -> dict:
        return data
