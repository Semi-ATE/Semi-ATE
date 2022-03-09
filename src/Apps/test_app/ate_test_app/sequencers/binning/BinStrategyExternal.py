from ate_test_app.sequencers.binning.BinStrategyBase import BinStrategyBase
from ate_common.program_utils import BinTableFieldName
import os
import ast


class BinStrategyExternal(BinStrategyBase):
    def __init__(self, bin_table_path: str, test_program_name):
        super().__init__(bin_table_path)
        self.bin_mapping = ast.literal_eval(os.environ[os.path.basename(test_program_name)])

        self.do_bin_mapping(self.standard_binning, self.bin_mapping)

    @staticmethod
    def do_bin_mapping(standard_binning: list, external_bin_mapping: dict):
        for bin_info in standard_binning['bin-table']:
            mapped = False
            for hbin, sbins in external_bin_mapping.items():
                if bin_info[BinTableFieldName.SBinNum()] in sbins:
                    bin_info[BinTableFieldName.HBin()] = hbin
                    mapped = True

            assert mapped, f'sbin "{bin_info[BinTableFieldName.SBinNum()]}" could not be mapped'
