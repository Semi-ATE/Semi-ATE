from tests.ATE.TES.apps.test_site_information import PRR_RECORD
from pytest import fixture
from ATE.Tester.TES.apps.masterApp.utils.result_Information_handler import ResultInformationHandler


BIN_TABLE = [{'SBIN': '1', 'HBIN': '1', 'SBINNAME': 'SB_GOOD1', 'GROUP': 'BT_PASS', 'DESCRIPTION': 'Our best choice'},
             {'SBIN': '22', 'HBIN': '42', 'SBINNAME': 'SB_THD', 'GROUP': 'BT_FAIL_ELECTRIC', 'DESCRIPTION': ' Total Harmonic Distortion'},
             {'SBIN': '60000', 'HBIN': '0', 'SBINNAME': 'SB_SMU_ALARM1', 'GROUP': 'BT_ALARM', 'DESCRIPTION': ' SMU Compliance Warning'}]

PRR_RECORD_SITE0 = {'type': 'PRR', 'REC_LEN': None, 'REC_TYP': 5, 'REC_SUB': 20,
                     'HEAD_NUM': 0, 'SITE_NUM': 0, 'PART_FLG': 0, 'NUM_TEST': 1,
                     'HARD_BIN': 1, 'SOFT_BIN': 1, 'X_COORD': 1, 'Y_COORD': 1,
                     'TEST_T': 0, 'PART_ID': '1', 'PART_TXT': '1', 'PART_FIX': 0}

PRR_RECORD_SITE1 = {'type': 'PRR', 'REC_LEN': None, 'REC_TYP': 5, 'REC_SUB': 20,
                     'HEAD_NUM': 0, 'SITE_NUM': 1, 'PART_FLG': 0, 'NUM_TEST': 1,
                     'HARD_BIN': 1, 'SOFT_BIN': 1, 'X_COORD': 1, 'Y_COORD': 1,
                     'TEST_T': 0, 'PART_ID': '2', 'PART_TXT': '1', 'PART_FIX': 0}

SITES = ['0', '1']


@fixture(scope='function')
def result_info_handler():
    result_info = ResultInformationHandler(SITES)
    result_info.set_bin_settings(BIN_TABLE)
    return result_info


def test_handle_part_result_information(result_info_handler: ResultInformationHandler):
    result_info_handler.handle_result(PRR_RECORD_SITE0)
    result_info_handler.handle_result(PRR_RECORD_SITE1)

    assert len(result_info_handler.get_part_count_infos()) == 3


def test_handle_part_result_information_with_retest(result_info_handler: ResultInformationHandler):
    result_info_handler.handle_result(PRR_RECORD_SITE0)
    result_info_handler.handle_result(PRR_RECORD_SITE1)
    result_info_handler.handle_result(PRR_RECORD_SITE1)

    part_result = result_info_handler.get_part_count_infos()
    # part 2, site 1 is tested twice
    assert part_result[1]['retest_count'] == 1
    assert len(part_result) == 3
