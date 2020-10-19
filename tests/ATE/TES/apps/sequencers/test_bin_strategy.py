import pytest
import os
from ATE.Tester.TES.apps.testApp.sequencers.binning.BinStrategy import BinStrategy

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'binmapping.json')
BIN_SETTINGS = [{'Bin-Name': 'F_DAW', 'Typ': 'Fail Electric', 'S-Bin': 3},
                {'Bin-Name': 'Good1', 'Typ': 'Type1', 'S-Bin': 2}]

BIN_SETTINGS_WRONG = [{'Bin-Name': 'F_DAW', 'Typ': 'Fail Electric', 'S-Bin': 230},
                      {'Bin-Name': 'Good1', 'Typ': 'Type1', 'S-Bin': 2}]

BIN_TABLE = [{'Bin-Name': 'F_DAW', 'Typ': 'Fail Electric', 'S-Bin': 3, 'H-Bin': 2},
             {'Bin-Name': 'Good1', 'Typ': 'Type1', 'S-Bin': 2, 'H-Bin': 0}]


def test_read_bin_file_not_found():
    with pytest.raises(Exception):
        _ = BinStrategy(BIN_SETTINGS, '')


def test_missing_bins_in_bin_table_trigger_exception():
    with pytest.raises(Exception):
        _ = BinStrategy(BIN_SETTINGS_WRONG, CONFIG_FILE)


def test_soft_bin_not_found_trigger_exception():
    bin_strategy = BinStrategy(BIN_SETTINGS, CONFIG_FILE)
    with pytest.raises(Exception):
        bin_strategy.get_hard_bin(50) == 0


def test_map_soft_bin_to_hard_bin():
    bin_strategy = BinStrategy(BIN_SETTINGS, CONFIG_FILE)
    assert bin_strategy.get_hard_bin(1) == 0


def test_generate_bin_table():
    bin_strategy = BinStrategy(BIN_SETTINGS, CONFIG_FILE)
    assert bin_strategy.generate_bin_table() == BIN_TABLE
