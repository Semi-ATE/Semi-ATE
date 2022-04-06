from ate_common.program_utils import ALARM_BIN_MAX, ALARM_BIN_MIN, GOOD_BIN_MAX, GOOD_BIN_MIN


class PartInformation:
    def __init__(self, head_num, site_num):
        self.part_count = 0
        self.retest_count = 0
        self.abort_count = 0
        self.good_count = 0
        self.functional_count = 0
        self.head_num = head_num
        self.site_num = site_num

    def update_part_information(self, prr_record):
        self.part_count += 1
        self.retest_count += prr_record['PART_RETEST']

        soft_bin = prr_record['SOFT_BIN']
        if self._does_abnormally_end(soft_bin):
            self.abort_count += 1

        if self._is_good_bin(soft_bin):
            self.good_count += 1
            self.functional_count += 1

    @staticmethod
    def _does_abnormally_end(soft_bin: int) -> bool:
        return soft_bin in range(ALARM_BIN_MIN, ALARM_BIN_MAX + 1)

    @staticmethod
    def _is_good_bin(soft_bin: int) -> bool:
        return soft_bin in range(GOOD_BIN_MIN, GOOD_BIN_MAX + 1)

    def get_part_count_info(self) -> dict:
        return {'head_num': int(self.head_num), 'site_num': int(self.site_num), 'part_count': self.part_count,
                'retest_count': self.retest_count, 'abort_count': self.abort_count, 'good_count': self.good_count,
                'functional_count': self.functional_count}


class PartInformationHandler:
    def __init__(self):
        self.part_information = {}

    def set_bin_settings(self, bin_settings: dict):
        self._bin_settings = bin_settings

    def update_part_count_records(self, prr_records: dict):
        for _, prr_record in prr_records.items():
            siteid = str(prr_record['SITE_NUM'])

            if not self.part_information.get(siteid):
                head_num = str(prr_record['HEAD_NUM'])
                self.part_information[siteid] = PartInformation(head_num, siteid)

            self.part_information[siteid].update_part_information(prr_record)

    def get_part_count_infos(self, prr_records: dict) -> list:
        self.update_part_count_records(prr_records)
        part_infos = []
        for _, part_info in self.part_information.items():
            part_infos.append(part_info.get_part_count_info())

        part_infos.append(self._generate_summary_part_count_info(part_infos))
        return part_infos

    @staticmethod
    def _generate_summary_part_count_info(part_infos: list) -> dict:
        summary_part_count_info = {'head_num': 255, 'site_num': 255, 'part_count': 0,
                                   'retest_count': 0, 'abort_count': 0, 'good_count': 0,
                                   'functional_count': 0}

        for part_info in part_infos:
            summary_part_count_info['part_count'] += part_info['part_count']
            summary_part_count_info['retest_count'] += part_info['retest_count']
            summary_part_count_info['abort_count'] += part_info['abort_count']
            summary_part_count_info['good_count'] += part_info['good_count']
            summary_part_count_info['functional_count'] += part_info['functional_count']

        return summary_part_count_info

    def clear_part_information(self):
        self.part_information.clear()
