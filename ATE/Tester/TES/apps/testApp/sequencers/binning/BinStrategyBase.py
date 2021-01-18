from ATE.Tester.TES.apps.testApp.sequencers.binning.Utils import load_json_from_file


class BinStrategyBase:
    def __init__(self, bin_table_path):
        self.bin_mapping = None
        self.standard_binning = load_json_from_file(bin_table_path)

    def get_hard_bin(self, sbin: int) -> int:
        for hbin, sbins in self.bin_mapping.items():
            if str(sbin) not in sbins:
                continue

            return int(hbin)

        assert False

    def get_bin_settings(self) -> dict:
        return self.bin_mapping
