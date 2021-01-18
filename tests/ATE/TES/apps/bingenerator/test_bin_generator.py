import os
from ATE.spyder.widgets.actions_on.program.Binning.BinTableGenerator import BinTableGenerator
import pytest


BIN_TABLE_PATH = os.path.join(os.path.dirname(__file__), 'test.json')


@pytest.fixture
def bin_generator():
    return BinTableGenerator()


def test_generate_bin_table(bin_generator: BinTableGenerator):
    bin_generator.add_bin('alarm_out', '12', 'ALARM', 'make it rain')
    bin_generator.add_bin('contact', '22', 'contact_fail', 'make it rain again')
    bin_generator.create_binning_file(BIN_TABLE_PATH)
    assert os.path.exists(BIN_TABLE_PATH)


def test_remove_element_from_bin_table(bin_generator: BinTableGenerator):
    bin_generator.add_bin('alarm_out', '12', 'ALARM', 'make it rain')
    bin_generator.add_bin('contact', '22', 'contact_fail', 'make it rain again')
    bin_generator.create_binning_file(BIN_TABLE_PATH)
    bin_generator.remove_bin('contact')
    assert bin_generator.get_bin_info('contact') is None


def test_get_alarm_bin_from_bin_table(bin_generator: BinTableGenerator):
    bin_generator.add_alarm_bin('test1_alarm', 'ALARM', 'make it rain')
    bin_generator.add_alarm_bin('test2_alarm', 'ALARM', 'make it rain')
    assert bin_generator.get_alarm_bin_num('test1_alarm') == '60000'
    assert bin_generator.get_alarm_bin_num('test2_alarm') == '60001'


def test_get_bin_information(bin_generator: BinTableGenerator):
    assert bin_generator.read_binning_file(BIN_TABLE_PATH)
