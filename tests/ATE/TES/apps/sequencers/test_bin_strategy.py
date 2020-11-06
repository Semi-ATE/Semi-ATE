import pytest
import os
from ATE.Tester.TES.apps.testApp.sequencers.binning.BinStrategy import BinStrategy

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'binmapping.json')
CONFIG_FILE_NO_BIN_0 = os.path.join(os.path.dirname(__file__), 'binmapping_no_bin0.json')
CONFIG_FILE_NO_BIN_1 = os.path.join(os.path.dirname(__file__), 'binmapping_no_bin1.json')

BIN_SETTINGS = [{'Bin-Name': 'F_DAW', 'Typ': 'Fail Electric', 'SBin': 3},
                {'Bin-Name': 'Good1', 'Typ': 'Type1', 'SBin': 2}]

BIN_SETTINGS_WRONG = [{'Bin-Name': 'F_DAW', 'Typ': 'Fail Electric', 'SBin': 230},
                      {'Bin-Name': 'Good1', 'Typ': 'Type1', 'SBin': 2}]

BIN_TABLE = [{'Bin-Name': 'F_DAW', 'Typ': 'Fail Electric', 'SBin': 3, 'HBin': 2},
             {'Bin-Name': 'Good1', 'Typ': 'Type1', 'SBin': 2, 'HBin': 0}]


def test_read_bin_file_not_found():
    with pytest.raises(Exception):
        _ = BinStrategy(BIN_SETTINGS, '')


def test_missing_bins_in_bin_table_trigger_exception():
    with pytest.raises(Exception):
        _ = BinStrategy(BIN_SETTINGS_WRONG, CONFIG_FILE)


def test_missing_bin0_raises_execption():
    # A contact fail is always treated as bin 0, but this thin
    # will not necessarily show up in the bintable
    with pytest.raises(Exception):
        _ = BinStrategy(BIN_SETTINGS, CONFIG_FILE_NO_BIN_0)


def test_missing_bin1_raises_execption():
    # All DUTs start off as bin 1, if no test does any
    # binning at all they remain bin 1, therefore,
    # this bin needs to be available in the configfile
    with pytest.raises(Exception):
        _ = BinStrategy(BIN_SETTINGS, CONFIG_FILE_NO_BIN_1)


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
