from ate_master_app.utils.bin_information import BinInformationHandler
from ate_common.program_utils import BinTableFieldName
from ate_master_app.utils.part_information import PartInformationHandler
from ate_master_app.utils.yield_information import YieldInformationHandler
from ate_master_app.utils.table_information import BinTableInformationHandler

REQUIRED_FIELDS = ['HEAD_NUM', 'SITE_NUM', 'HARD_BIN', 'SOFT_BIN', 'PART_ID', 'PART_RETEST', 'PART_FLG']


class ResultInformationHandler:
    def __init__(self, sites_id: list):
        self._yield_info_handler = YieldInformationHandler()
        self._part_info_handler = PartInformationHandler()
        self._site_info_handler = BinInformationHandler(sites_id)
        self._bin_table_info_handler = BinTableInformationHandler(sites_id)
        self.prr_rec_information = {}

    def handle_result(self, prr_record: dict):
        part_id = self._get_part_id(prr_record)
        site_num = str(prr_record['SITE_NUM'])
        soft_bin = str(prr_record['SOFT_BIN'])
        message_handle_result = (True, '')

        # add 'PART_RETEST' field to count part retest commands
        if not self.prr_rec_information.get(part_id):
            prr_record['PART_RETEST'] = 0
            self.prr_rec_information[part_id] = self._extract_needed_fields(prr_record)
            message_handle_result = self._yield_info_handler.accumulate_site_bin_info(site_num, soft_bin)
            self._bin_table_info_handler.accumulate_bin_table_info(site_num, soft_bin)
        else:
            old_prr_rec = self.prr_rec_information[part_id]
            part_count = old_prr_rec['PART_RETEST']
            prr_record['PART_RETEST'] = part_count + 1
            self.prr_rec_information.update({part_id: prr_record})
            message_handle_result = self._yield_info_handler.reaccumulate_bin_info(self.prr_rec_information)
            self._bin_table_info_handler.reaccumulate_bin_table_info(self.prr_rec_information)

        return message_handle_result

    @staticmethod
    def _extract_needed_fields(prr: dict):
        return {field_name: prr[field_name] for field_name in REQUIRED_FIELDS}

    @staticmethod
    def _get_part_id(prr_record: dict):
        part_id = ''
        if prr_record['PART_ID']:
            part_id = prr_record['PART_ID']
        else:
            default_value = -32768
            if (prr_record['X_COORD'], prr_record['Y_COORD']) == (default_value, default_value):
                assert False
            else:
                part_id = f"{prr_record['X_COORD']}x{prr_record['Y_COORD']}"

        return part_id

    def set_bin_settings(self, bin_table: dict):
        bin_settings = self.get_bin_settings(bin_table)

        self._site_info_handler.set_sites_information(bin_table)
        self._yield_info_handler.set_bin_settings(bin_settings)
        self._part_info_handler.set_bin_settings(bin_settings)
        self._bin_table_info_handler.set_bin_table(bin_table)

    def update_hbin_number(self, sbin: str, hbin: str):
        self._bin_table_info_handler._update_hbin_num(sbin, hbin)

    @staticmethod
    def get_bin_settings(bin_table: list) -> dict:
        settings = {}

        for bin_info in bin_table:
            settings.setdefault(bin_info[BinTableFieldName.SBinGroup()], {'hbins': [], 'sbins': []})['hbins'].append(bin_info[BinTableFieldName.HBin()])
            settings.setdefault(bin_info[BinTableFieldName.SBinGroup()], {'hbins': [], 'sbins': []})['sbins'].append(bin_info[BinTableFieldName.SBinNum()])

        return settings

    def clear_all(self):
        self._yield_info_handler.clear_yield_information()
        self._part_info_handler.clear_part_information()
        self._site_info_handler.clear_site_information()
        self._bin_table_info_handler.clear_bin_table()
        self.prr_rec_information.clear()

    def get_site_result_response(self, prr_record: dict) -> dict:
        return self._yield_info_handler.get_site_result(prr_record)

    def get_yield_messages(self) -> dict:
        return self._yield_info_handler.get_yield_messages()

    def get_site_yield_info_message(self, site: str) -> dict:
        return self._yield_info_handler.get_site_yield_info_message(site)

    def get_hbin_soft_bin_report(self) -> dict:
        return self._site_info_handler.get_summary_information(self.prr_rec_information)

    def get_part_count_infos(self) -> dict:
        return self._part_info_handler.get_part_count_infos(self.prr_rec_information)

    def get_bin_table(self) -> list:
        return self._bin_table_info_handler.get_bin_table_infos()
