import pytest
import os
from ATE.Tester.TES.apps.testApp.sequencers.binning.BinStrategy import BinStrategy

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'binmapping.json')

BIN_TABLE = {'0': ['11', '12', '60002'], '1': ['1']}


def test_read_bin_file_not_found():
    with pytest.raises(Exception):
        _ = BinStrategy('')


def test_map_soft_bin_to_hard_bin():
    bin_strategy = BinStrategy(CONFIG_FILE)
    assert bin_strategy.get_hard_bin(1) == 1


def test_generate_bin_table():
    bin_strategy = BinStrategy(CONFIG_FILE)
    assert bin_strategy.bin_mapping == BIN_TABLE
