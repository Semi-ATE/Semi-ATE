from ATE.Tester.TES.apps.masterApp.utils.yield_information import YieldInformation


class TestYieldInformation:
    types = {"type1": {"sbins": [1, 2], "hbins": [3, 6]}, "type2": {"sbins": [4], "hbins": [5]}}

    def setup_method(self):
        self.yield_info = YieldInformation(list(self.types.keys()), 1)

    def test_yield_information_init(self):
        assert self.yield_info.get_yield_info() == {"type1": {"count": 0, "value": 0}, "type2": {"count": 0, "value": 0}}

    def test_yield_information_update(self):
        self.yield_info.update_yield_info("type1")
        assert self.yield_info.get_yield_info() == {"type1": {"count": 1, "value": 100.0}, "type2": {"count": 0, "value": 0}}

        self.yield_info.update_yield_info("type2")
        assert self.yield_info.get_yield_info() == {"type1": {"count": 1, "value": 50.0}, "type2": {"count": 1, "value": 50.0}}
