from typing import List
import io
import time
import itertools
import os

from ATE.data.STDF.records import records_from_file
from ATE.data.STDF.records import FAR, MIR, PIR, PTR, PRR, PCR, MRR, STDR
#ToDo: Move these methods to somewhere sane, e.g. ATE.data.STDF.utils or similar
from ATE.Tester.TES.apps.testApp.sequencers.Utils import (generate_PIR, generate_PRR, generate_PTR, generate_TSR)


class StdfPartTestContext:
    def __init__(self, site_num: int):
        self.site_num = site_num


STDF_PATH = 'temp_final_stdf_file_on_unload.stdf'


class StdfTestResultAggregator:
    completed_part_records: List[List[STDR]]

    def __init__(self, node_name: str, lot_id: str, job_name: str, file_path: str = ''):
        self.version = 'V4'
        self.endian = '<'
        self.completed_part_records = []
        self.num_good_parts = 0
        self.setup_timestamp = int(time.time())
        self.node_name = node_name
        self.lot_id = lot_id
        self.job_name = job_name
        self.end_timestamp = 0
        self.path = STDF_PATH if not file_path else file_path

        self._clean_up()

    def _clean_up(self):
        if not os.path.exists(self.path):
            return

        os.remove(self.path)

    def finalize(self):
        self.end_timestamp = int(time.time())

    def add_parttest_records(self, parttest_records: List[STDR], ispass: bool, site_num: int):
        assert self._is_expected_list_of_single_parttest_records(parttest_records)
        for rec in parttest_records:
            rec.set_value('HEAD_NUM', 0)
            rec.set_value('SITE_NUM', site_num)
        if ispass:
            self.num_good_parts += 1
        self.completed_part_records.append(parttest_records)

    def write_to_file(self, filepath):
        full_file_records = self._stdf_header_records() + list(itertools.chain.from_iterable(self.completed_part_records)) + self._stdf_footer_records()
        with open(filepath, "wb") as f:
            f.write(self.serialize_records(full_file_records))

    def write_records_to_file(self, record):
        with open(self.path, "ab") as f:
            f.write(self.serialize_records(record))

    def write_header_records(self):
        self.write_records_to_file(self._stdf_header_records())

    def write_footer_records(self):
        self.write_records_to_file(self._stdf_footer_records())

    def _stdf_header_records(self):
        # FAR, MIR
        # optional/TODO: SDR
        return [self._create_FAR(), self._create_MIR()]

    def _stdf_footer_records(self):
        # optional (statistics): TSR, SBR
        # PCR, MRR
        return [self._create_PCR(self.num_good_parts, len(self.completed_part_records)), self._create_MRR()]

    def _unpack_parttest_records_from_stdf_blob(self, stdf_blob: bytes):
        with io.BytesIO(stdf_blob) as stream:
            return [record for _, _, _, record in records_from_file(
                stream, unpack=True, of_interest=['PIR', 'PTR', 'PRR'])]

    def _is_expected_list_of_single_parttest_records(self, records: List[STDR]):
        return (len(records) >= 3
                and records[0].id == 'PIR'
                and all(rec.id == 'PTR' for rec in records[1: -1])
                and records[-1].id == 'PRR'
                and all(rec.get_value('HEAD_NUM') == 1 for rec in records)
                and all(rec.get_value('SITE_NUM') == 1 for rec in records))

    def _assert_is_expected_list_of_single_parttest_records(self, records: List[STDR]):
        if len(records) < 3:
            raise ValueError(f'minimal records for valid part test is 3, but only got {len(records)}')
        if records[0].id != 'PIR':
            raise ValueError(f'first record was not PIR, but {records[0].id}')
        if records[-1].id != 'PRR':
            raise ValueError(f'last record was not PRR, but {records[-1].id}')
        non_ptr_records = [rec.id for rec in records[1: -1] if rec.id != 'PTR']
        if non_ptr_records:
            raise ValueError(f'non-PTR record in list of records: {non_ptr_records}')
        if any(rec.get_value('HEAD_NUM') != 1 for rec in records):
            raise ValueError(f'HEAD_NUM wass not 1')
        if any(rec.get_value('SITE_NUM') != 1 for rec in records):
            raise ValueError(f'SITE_NUM wass not 1')

    def parse_parttest_stdf_blob(self, stdf_blob: bytes):
        records = self._unpack_parttest_records_from_stdf_blob(stdf_blob)
        self._assert_is_expected_list_of_single_parttest_records(records)
        return records

    def _create_FAR(self):
        rec = FAR(self.version, self.endian)
        rec.set_value('CPU_TYPE', 2)
        rec.set_value('STDF_VER', 4)
        return rec

    def _create_MIR(self):
        rec = MIR(self.version, self.endian)

        rec.set_value('SETUP_T', self.setup_timestamp)
        rec.set_value('START_T', self.setup_timestamp)
        rec.set_value('STAT_NUM', 0)
        rec.set_value('LOT_ID', self.lot_id)
        rec.set_value('PART_TYP', 'MyPart')
        rec.set_value('NODE_NAM', self.node_name)
        rec.set_value('TSTR_TYP', 'MyTester')
        rec.set_value('JOB_NAM', self.job_name)

        return rec

    def _create_PCR(self, num_good_parts: int, num_parts_tested: int):
        rec = PCR(self.version, self.endian)
        rec.set_value('HEAD_NUM', 255)  # this is supposed to be a single record for parts across all sites
        rec.set_value('SITE_NUM', 0)

        rec.set_value('PART_CNT', num_parts_tested)
        rec.set_value('RTST_CNT', 0)
        rec.set_value('ABRT_CNT', 0)
        rec.set_value('GOOD_CNT', num_good_parts)
        rec.set_value('FUNC_CNT', num_parts_tested)

        return rec

    def _create_MRR(self):
        rec = MRR(self.version, self.endian)
        rec.set_value('FINISH_T', self.end_timestamp)
        return rec

    def append_test_results(self, test_results):
        for test_result in test_results:
            rec = {
                'PIR': lambda test_result: self._generate_PIR(test_result),
                'PTR': lambda test_result: self._generate_PTR(test_result),
                'PRR': lambda test_result: self._generate_PRR(test_result),
            }[test_result['type']](test_result)

            self.write_records_to_file([rec])

    @staticmethod
    def _generate_PRR(prr_record):
        part_fix = [0] * 8
        rec = generate_PRR(prr_record['HEAD_NUM'], prr_record['SITE_NUM'], False, prr_record['NUM_TEST'],
                           prr_record['HARD_BIN'], prr_record['SOFT_BIN'], prr_record['X_COORD'],
                           prr_record['Y_COORD'], prr_record['TEST_T'], prr_record['PART_ID'],
                           prr_record['PART_TXT'], part_fix)

        # TODO: there should not be a is_pass in generate_prr function
        rec.set_value('PART_FLG', prr_record['PART_FLG'])
        return rec

    @staticmethod
    def _generate_PTR(ptr_record):
        rec = generate_PTR(ptr_record['TEST_NUM'], ptr_record['HEAD_NUM'], ptr_record['SITE_NUM'],
                           False, ptr_record['PARM_FLG'], ptr_record['RESULT'], ptr_record['TEST_TXT'],
                           ptr_record['ALARM_ID'], ptr_record['OPT_FLAG'])

        return rec

    @staticmethod
    def _generate_PIR(pir_record):
        return generate_PIR(pir_record['HEAD_NUM'], pir_record['SITE_NUM'])

    def append_test_summary(self, tests_summary):
        for test_summary in tests_summary:
            rec = self._generate_TSR(test_summary)
            self.write_records_to_file([rec])

    @staticmethod
    def _generate_TSR(test_summary):
        return generate_TSR(test_summary['HEAD_NUM'], test_summary['SITE_NUM'], test_summary['TEST_TYP'],
                            test_summary['TEST_NUM'], test_summary['EXEC_CNT'], test_summary['FAIL_CNT'],
                            test_summary['ALRM_CNT'], test_summary['TEST_NAM'], test_summary['SEQ_NAME'],
                            test_summary['TEST_LBL'], test_summary['OPT_FLAG'], test_summary['TEST_TIM'],
                            test_summary['TEST_MIN'], test_summary['TEST_MAX'], test_summary['TST_SUMS'],
                            test_summary['TST_SQRS'])

    @staticmethod
    def serialize_records(records) -> bytes:
        return bytes(itertools.chain.from_iterable(rec.__repr__() for rec in records))