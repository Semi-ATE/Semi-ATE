from ATE.Tester.TES.apps.masterApp.utils.table_information import BinTableInformationHandler

SITES = ['0', '1']
BIN_TABLE = [{'SBIN': '1', 'HBIN': '1', 'SBINNAME': 'SB_GOOD1', 'GROUP': 'BT_PASS', 'DESCRIPTION': 'Our best choice'},
             {'SBIN': '12', 'HBIN': '12', 'SBINNAME': 'SB_CONT_OPEN', 'GROUP': 'BT_FAIL_CONT', 'DESCRIPTION': 'Open Contacts'},
             {'SBIN': '20', 'HBIN': '13', 'SBINNAME': 'SB_IDD', 'GROUP': 'BT_FAIL_ELECTRIC', 'DESCRIPTION': ' Current Consumption'},
             {'SBIN': '22', 'HBIN': '42', 'SBINNAME': 'SB_THD', 'GROUP': 'BT_FAIL_ELECTRIC', 'DESCRIPTION': ' Total Harmonic Distortion'}]

PRR_RECORD = {'part_id': {'type': 'PRR', 'SITE_NUM': 0, 'HARD_BIN': 10, 'SOFT_BIN': 12, 'PART_ID': 1, 'PART_RETEST': 0, 'PART_FLG': 1}}


class TestBinTableInformationHandler:
    def setup_method(self):
        self.bin_table_handler = BinTableInformationHandler(SITES)
        self.bin_table_handler.set_bin_table(BIN_TABLE)

    def test_set_bin_table(self):
        assert len(self.bin_table_handler.get_bin_table_infos()) == 4

    def test_accumuldate_bin_table_info(self):
        site = '0'
        sbin = 1

        self.bin_table_handler.accumulate_bin_table_info('0', 1)
        bin_table = self.bin_table_handler.get_bin_table_infos()

        self._check_valid_table(bin_table, 'SB_GOOD1', site, sbin, 1)

    # since we can retest parts
    def test_reaccumuldate_bin_table_info(self):
        site = '0'
        sbin = 1

        self.bin_table_handler.accumulate_bin_table_info('0', 1)
        bin_table = self.bin_table_handler.get_bin_table_infos()
        self._check_valid_table(bin_table, 'SB_GOOD1', site, sbin, 1)
        self.bin_table_handler.reaccumulate_bin_table_info(PRR_RECORD)

        # after retest part failed
        new_sbin = PRR_RECORD['part_id']['SOFT_BIN']
        bin_table = self.bin_table_handler.get_bin_table_infos()
        self._check_valid_table(bin_table, 'SB_GOOD1', site, sbin, 0)
        self._check_valid_table(bin_table, 'SB_CONT_OPEN', site, new_sbin, 1)

    def _check_valid_table(self, bin_table: list, bin_name: str, site_id: str, sbin: int, count: int):
        for bin_info in bin_table:
            if bin_info['sBin'] != sbin:
                continue

            assert bin_info['name'] == bin_name

            for site_count in bin_info['siteCounts']:
                if site_count['siteId'] != site_id:
                    continue

                assert site_count['count'] == count
