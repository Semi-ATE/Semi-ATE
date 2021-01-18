class StaticDataSource:
    def __init__(self):
        pass

    def retrieve_data(self) -> dict:
        return {}

    def verify_data(self, data) -> bool:
        return data is not None

    def get_test_information(self, data) -> dict:
        return data

    @staticmethod
    def get_bin_table(data: list) -> list:
        return data

    @staticmethod
    def get_binning_tuple(bin_table: list) -> dict:
        return bin_table

    @staticmethod
    def get_bin_settings(bin_table: list) -> dict:
        return bin_table
