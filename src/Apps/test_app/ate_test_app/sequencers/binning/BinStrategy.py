from ate_common.program_utils import BinTableFieldName
from ate_test_app.sequencers.binning.BinStrategyBase import BinStrategyBase


class BinStrategy(BinStrategyBase):
    def __init__(self, bin_table_path: str):
        super().__init__(bin_table_path)

        self.bin_mapping = self._generate_bin_mapping(self.standard_binning['bin-table'])

    def _generate_bin_mapping(self, bin_table: dict) -> dict:
        binning_tuple = {}
        for bin_info in bin_table:
            binning_tuple.setdefault(bin_info[BinTableFieldName.HBin()], []).append(bin_info[BinTableFieldName.SBinNum()])

        return binning_tuple
