from pytest import fixture
from ATE.Tester.TES.apps.masterApp.utils.bin_information import BinInformationHandler


BIN_TABLE = [{'SBIN': '1', 'HBIN': '1', 'SBINNAME': 'SB_GOOD1', 'GROUP': 'BT_PASS', 'DESCRIPTION': 'Our best choice'},
             {'SBIN': '22', 'HBIN': '42', 'SBINNAME': 'SB_THD', 'GROUP': 'BT_FAIL_ELECTRIC', 'DESCRIPTION': ' Total Harmonic Distortion'},
             {'SBIN': '60000', 'HBIN': '0', 'SBINNAME': 'SB_SMU_ALARM1', 'GROUP': 'BT_ALARM', 'DESCRIPTION': ' SMU Compliance Warning'}]

PRR_RECORD = {'part_id': {'type': 'PRR', 'REC_LEN': None, 'REC_TYP': 5, 'REC_SUB': 20,
                          'HEAD_NUM': 0, 'SITE_NUM': 0, 'PART_FLG': 0, 'NUM_TEST': 1,
                          'HARD_BIN': 1, 'SOFT_BIN': 1, 'X_COORD': 1, 'Y_COORD': 1,
                          'TEST_T': 0, 'PART_ID': '1', 'PART_TXT': '1', 'PART_FIX': 0}}

SITE_NUM = '0'


@fixture(scope='function')
def site_info_handler():
    site_info = BinInformationHandler([SITE_NUM])

    return site_info


def test_set_sites_information(site_info_handler: BinInformationHandler):
    site_info_handler.set_sites_information(BIN_TABLE)
    assert site_info_handler.get_num_sites() == 1


def test_no_test_result_stored(site_info_handler: BinInformationHandler):
    assert len(site_info_handler.get_summary_information({})) == 0


def test_store_test_result(site_info_handler: BinInformationHandler):
    site_info_handler.set_sites_information(BIN_TABLE)

    assert len(site_info_handler.get_summary_information(PRR_RECORD)) > 0
