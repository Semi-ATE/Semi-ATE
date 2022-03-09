from ate_test_app.sequencers.binning.Utils import load_json_from_file


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

    def set_new_hbin(self, sbin: int, hbin: int):
        self._pop_sbin(str(sbin))
        self.bin_mapping.setdefault(str(hbin), []).append(str(sbin))

    def _pop_sbin(self, sbin: str):
        for _, bins in self.bin_mapping.items():
            if sbin not in bins:
                continue

            bins.pop(bins.index(sbin))
            break
