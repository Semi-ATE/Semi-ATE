from ATE.spyder.widgets.actions_on.program.Utils import ALARM_BIN_MIN
from ATE.spyder.widgets.actions_on.program.Binning.Utils import BinTableFieldName


class AlarmBinGenerator:
    def __init__(self):
        self._alarm_bin_number = ALARM_BIN_MIN

    def generate_bin(self, sb_group: str, sb_desc: str) -> dict:
        bin = {BinTableFieldName.SBinNum(): str(self._alarm_bin_number), BinTableFieldName.SBinGroup(): sb_group,
               BinTableFieldName.SBinDescription(): sb_desc, BinTableFieldName.HBin(): '0'}
        self._alarm_bin_number += 1
        return bin
