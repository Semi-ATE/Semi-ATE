import json
from ate_common.program_utils import (ALARM_BIN_MAX, ALARM_BIN_MIN)
from ate_spyder.widgets.actions_on.program.Binning.AlarmBinGenerator import AlarmBinGenerator
from ate_common.program_utils import BinTableFieldName

GOOD_GRADE_BIN = 1


class BinTableGenerator:
    def __init__(self):
        self._binning_table = {}
        self._alarm_binning_table = {}
        self._alarm_bin_generator = AlarmBinGenerator()

    def add_bin(self, sb_name: str, sb_num: str, sb_group: str, sb_desc: str, h_bin: str = '0'):
        self._binning_table[sb_name] = {BinTableFieldName.SBinNum(): sb_num, BinTableFieldName.SBinGroup(): sb_group,
                                        BinTableFieldName.SBinDescription(): sb_desc, BinTableFieldName.HBin(): h_bin}

    def add_alarm_bin(self, sb_name: str, sb_group: str, sb_desc: str):
        self._alarm_binning_table[sb_name] = self._alarm_bin_generator.generate_bin(sb_group, sb_desc)

    def remove_bin(self, sb_name: str):
        self._binning_table.pop(sb_name)

    def update_bin_name(self, sb_name: str, sb_new_name: str):
        self._binning_table[sb_new_name] = self._binning_table.pop(sb_name)

    def update_bin_info(self, sb_name: str, sb_num: str, sb_group: str, sb_desc: str):
        self._binning_table[sb_name][BinTableFieldName.SBinNum()] = sb_num
        self._binning_table[sb_name][BinTableFieldName.SBinGroup()] = sb_group
        self._binning_table[sb_name][BinTableFieldName.SBinDescription()] = sb_desc

    def _generate_bin_table(self) -> dict:
        self._binning_table.update(self._alarm_binning_table)
        # TODO: is there a better way to integrade good bin 1 ?
        self.add_bin("Good_1", '1', 'Good1', '', h_bin='1')
        for sb_name in self._binning_table.keys():
            self._binning_table[sb_name][BinTableFieldName.SBinName()] = sb_name

        return self._binning_table.items()

    def does_bin_exist(self, bin_name: str) -> bool:
        return self._binning_table.get(bin_name) is None

    def get_bin_info(self, sb_name: str) -> dict:
        return self._binning_table.get(sb_name)

    def get_available_bin_names(self) -> list:
        return [bin for bin in self._binning_table.keys() if 'ALARM' not in bin]

    def get_alarm_bin_num(self, sb_name: str) -> str:
        return self._alarm_binning_table[sb_name][BinTableFieldName.SBinNum()]

    def create_binning_file(self, file_name: str):
        data = {'bin-table': [value for _, value in self._generate_bin_table()]}
        with open(file_name, 'w') as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def read_binning_file(file_name: str) -> dict:
        with open(file_name, 'r') as f:
            data = json.load(f)
            return data['bin-table']

    def load_bin_table(self, file_name: str):
        data = self.read_binning_file(file_name)
        self._binning_table.clear()

        for bin_info in data:
            if int(bin_info[BinTableFieldName.SBinNum()]) in range(ALARM_BIN_MIN, ALARM_BIN_MAX + 1) or \
               int(bin_info[BinTableFieldName.SBinNum()]) == GOOD_GRADE_BIN:
                continue

            self.add_bin(bin_info[BinTableFieldName.SBinName()], bin_info[BinTableFieldName.SBinNum()],
                         bin_info[BinTableFieldName.SBinGroup()], bin_info[BinTableFieldName.SBinDescription()])

    def get_bin_table(self) -> dict:
        return self._binning_table

    def get_bin_table_size(self) -> int:
        return len(self._binning_table)

    def does_bin_num_exist(self, bin_num: str) -> bool:
        for _, value in self._binning_table.items():
            if value[BinTableFieldName.SBinNum()] == bin_num:
                return True

        return False

    def generate_bin_identrifiers(self, identifier_offset: int = 1):
        sb_num = 11
        sb_name = f'Bin_{sb_num}'

        if not self._binning_table:
            return sb_name, str(sb_num)

        sb_num = max([int(bin[BinTableFieldName.SBinNum()]) for _, bin in self._binning_table.items()]) + identifier_offset
        sb_name = f'Bin_{sb_num}'

        if self._binning_table.get(sb_name):
            return self.generate_bin_identrifiers(identifier_offset + 1)

        return sb_name, str(sb_num)

    def clear_alarm_table(self):
        self._alarm_binning_table.clear()
