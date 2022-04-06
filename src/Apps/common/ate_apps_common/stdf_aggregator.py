from typing import List
import time
import itertools
import os

from Semi_ATE.STDF import MIR, STDR
from ate_apps_common.stdf_utils import (generate_FTR, generate_PIR,
                                        generate_PRR, generate_PTR, generate_SDR,
                                        generate_TSR, generate_HBR,
                                        generate_SBR, generate_MRR,
                                        generate_MIR, generate_PCR,
                                        generate_FAR)


class StdfPartTestContext:
    def __init__(self, site_num: int):
        self.site_num = site_num


STDF_PATH = 'temp_final_stdf_file_on_unload.stdf'


class StdfTestResultAggregator:
    completed_part_records: List[List[STDR]]

    def __init__(self, node_name: str, lot_id: str, job_name: str, sites: list, file_path: str = ''):
        self.version = 'V4'
        self.endian = '<'
        self.completed_part_records = []
        self.num_good_parts = 0
        self.setup_timestamp = int(time.time())
        self.start_timestamp = 0
        self.node_name = node_name
        self.lot_id = lot_id
        self.job_name = job_name
        self.end_timestamp = 0
        self.path = STDF_PATH if not file_path else file_path
        self.sites = sites

        self._clean_up()

    def _clean_up(self):
        if not os.path.exists(self.path):
            return

        os.remove(self.path)

    def finalize(self):
        self.end_timestamp = int(time.time())

    def write_to_file(self, filepath):
        full_file_records = self._stdf_header_records() + list(itertools.chain.from_iterable(self.completed_part_records)) + self._stdf_footer_records()
        with open(filepath, "wb") as f:
            f.write(self.serialize_records(full_file_records))

    def write_records_to_file(self, record):
        with open(self.path, "ab") as f:
            f.write(self.serialize_records(record))

    def write_header_records(self):
        self.set_first_part_test_time()
        self.write_records_to_file(self._stdf_header_records())

    def write_footer_records(self):
        self.write_records_to_file(self._stdf_footer_records())

    def _stdf_header_records(self) -> list:
        return [generate_FAR(2, 4),
                self.generate_MIR(),
                generate_SDR(0, 0, len(self.sites), self.sites)]

    def set_test_program_data(self, test_information: dict):
        self.user_text = test_information['USERTEXT']
        self.program_dir = test_information['PROGRAM_DIR']
        self.temperature = test_information['TEMP']
        self.tester_program = test_information['TESTERPRG']
        self.part_id = test_information['PART_ID']
        self.package_id = test_information['PACKAGE_ID']
        self.sublot_id = test_information['SUBLOT_ID']

    def generate_MIR(self) -> MIR:
        node_num = 81  # TODO: this is not specified yet
        operator_name = 'sct'  # TODO: standard value
        return generate_MIR(self.setup_timestamp, self.start_timestamp, 0,
                            self.lot_id, f'{self.part_id}', self.node_name, f'MSCT-{node_num}',
                            self.job_name, operator_name, self.temperature,
                            self.user_text, f'{self.package_id}', self.sublot_id)

    def get_MIR_dict(self) -> dict:
        return self.generate_MIR().to_dict()

    def _stdf_footer_records(self) -> list:
        return [generate_MRR(self.end_timestamp)]

    def set_first_part_test_time(self):
        self.start_timestamp = int(time.time())

    def append_test_results(self, test_results):
        for test_result in test_results:
            rec = {
                'PIR': lambda test_result: self._generate_PIR(test_result),
                'PTR': lambda test_result: self._generate_PTR(test_result),
                'PRR': lambda test_result: self._generate_PRR(test_result),
                'FTR': lambda test_result: self._generate_FTR(test_result),
            }[test_result['type']](test_result)

            self.write_records_to_file([rec])

    @staticmethod
    def _generate_PRR(prr_record: dict):
        part_fix = [0] * 8
        rec = generate_PRR(prr_record['HEAD_NUM'], prr_record['SITE_NUM'], False, prr_record['NUM_TEST'],
                           prr_record['HARD_BIN'], prr_record['SOFT_BIN'], prr_record['X_COORD'],
                           prr_record['Y_COORD'], prr_record['TEST_T'], prr_record['PART_ID'],
                           prr_record['PART_TXT'], part_fix)

        # TODO: there should not be a is_pass in generate_prr function
        rec.set_value('PART_FLG', prr_record['PART_FLG'])
        return rec

    @staticmethod
    def _generate_PTR(ptr_record: dict) -> dict:
        return generate_PTR(ptr_record['TEST_NUM'], ptr_record['HEAD_NUM'], ptr_record['SITE_NUM'],
                            False, ptr_record['PARM_FLG'], ptr_record['RESULT'], ptr_record['TEST_TXT'],
                            ptr_record['ALARM_ID'], ptr_record['LO_LIMIT'], ptr_record['HI_LIMIT'],
                            ptr_record['UNITS'], ptr_record['C_RESFMT'], ptr_record['RES_SCAL'],
                            ptr_record['LO_SPEC'], ptr_record['HI_SPEC'], ptr_record['OPT_FLAG'])

    @staticmethod
    def _generate_FTR(ftr_record: dict) -> dict:
        rec = generate_FTR(ftr_record['TEST_NUM'], ftr_record['HEAD_NUM'], ftr_record['SITE_NUM'], False)
        rec.set_value('TEST_FLG', ftr_record['TEST_FLG'])
        return rec

    @staticmethod
    def _generate_PIR(pir_record: dict) -> dict:
        return generate_PIR(pir_record['HEAD_NUM'], pir_record['SITE_NUM'])

    def append_test_summary(self, tests_summary: list):
        for test_summary in tests_summary:
            rec = self._generate_TSR(test_summary)
            self.write_records_to_file([rec])

    def append_soft_and_hard_bin_record(self, bin_informations: dict):
        self.write_bin_info(bin_informations,
                            lambda head_num, site_num, bin_num, count, bin_name, bin_pf:
                                generate_SBR(head_num, site_num, bin_num, count, bin_name, bin_pf),
                            0)

        self.write_bin_info(bin_informations,
                            lambda head_num, site_num, bin_num, count, bin_name, bin_pf:
                                generate_HBR(head_num, site_num, bin_num, count, bin_name, bin_pf),
                            1)

    def write_bin_info(self, bin_informations: dict, func: callable, bin_pos: int):
        record_summary = [None] * 6
        for bin_name, bin_info in bin_informations.items():
            record_summary[0] = 255         # head num
            record_summary[1] = 0           # site num
            record_summary[3] = 0           # count
            record_summary[4] = bin_name    # bin name
            record_summary[5] = 'F'         # test flag

            for site_id, bin in bin_info.items():
                self.write_records_to_file([func(bin[4], int(site_id), bin[bin_pos], bin[2], bin_name, bin[3])])
                record_summary[3] += bin[2]
                record_summary[2] = bin[bin_pos]
                record_summary[5] = bin[3]
                record_summary[1] = int(site_id)

            self.write_records_to_file([func(record_summary[0], record_summary[1],
                                             record_summary[2], record_summary[3],
                                             record_summary[4], record_summary[5])])

    def append_part_count_infos(self, part_infos: list):
        pcr_recs = []
        for part_info in part_infos:
            pcr_recs.append(generate_PCR(int(part_info['head_num']), int(part_info['site_num']),
                                         part_info['part_count'], part_info['retest_count'],
                                         part_info['abort_count'], part_info['good_count'],
                                         part_info['functional_count']))

        self.write_records_to_file(pcr_recs)

    @staticmethod
    def _generate_TSR(test_summary: dict) -> dict:
        return generate_TSR(test_summary['HEAD_NUM'], test_summary['SITE_NUM'], test_summary['TEST_TYP'],
                            test_summary['TEST_NUM'], test_summary['EXEC_CNT'], test_summary['FAIL_CNT'],
                            test_summary['ALRM_CNT'], test_summary['TEST_NAM'], test_summary['SEQ_NAME'],
                            test_summary['TEST_LBL'], test_summary['OPT_FLAG'], test_summary['TEST_TIM'],
                            test_summary['TEST_MIN'], test_summary['TEST_MAX'], test_summary['TST_SUMS'],
                            test_summary['TST_SQRS'])

    @staticmethod
    def serialize_records(records) -> bytes:
        return bytes(itertools.chain.from_iterable(rec.__repr__() for rec in records))
