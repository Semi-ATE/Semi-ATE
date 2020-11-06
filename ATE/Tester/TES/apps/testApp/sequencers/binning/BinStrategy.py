from ATE.Tester.TES.apps.testApp.sequencers.binning.IBinStrategy import IBinStrategy

import json
import os


class BinStrategy(IBinStrategy):
    def __init__(self, bin_settings, config_file):
        self.config_file = config_file
        self.bin_settings = bin_settings

        self.bin_mapping = self.get_binning_table()
        self._validate_bin_settings()

    def _validate_bin_settings(self):
        for bin_setting in self.bin_settings:
            soft_bin = bin_setting['SBin']
            _ = self.get_hard_bin(soft_bin)

        _ = self.get_hard_bin(0)    # sbin 0 is implicit, and must be available!
        _ = self.get_hard_bin(1)    # sbin 1 is implicit, and must be available!

    def get_hard_bin(self, soft_bin):
        for hbin, sbins in self.bin_mapping.items():
            if soft_bin in sbins:
                return int(hbin)

        raise Exception(f'soft bin: "{soft_bin}" could not be mapped')

    def get_binning_table(self):
        return self.load_json_from_file(self.config_file)

    @staticmethod
    def load_json_from_file(config_file):
        if not os.path.exists(config_file):
            raise FileNotFoundError(f'configuration file not found: {config_file}')

        with open(config_file) as f:
            return json.load(f)

    def generate_bin_table(self):
        bin_table = self.bin_settings
        for bin_setting in bin_table:
            soft_bin = bin_setting['SBin']
            bin_setting.update({'HBin': self.get_hard_bin(soft_bin)})

        return bin_table
