from ate_test_app.sequencers.Harness import Harness
from ate_apps_common.stdf_aggregator import StdfTestResultAggregator


class LocalHarness(Harness):
    def __init__(self, test_program_name: str):
        self._stdf_aggregator = StdfTestResultAggregator('testnode', 'no_lot', 'test', ['0'], f'{test_program_name}.stdf')
        self._is_first = True

    def next(self):
        if not self._is_first:
            return

        self._stdf_aggregator.set_test_program_data(self.generate_dummy_test_information())
        self._stdf_aggregator.write_header_records()

        self._is_first = False

    def collect(self, stdf_data: dict):
        self._stdf_aggregator.append_test_results(stdf_data)

    @staticmethod
    def generate_dummy_test_information():
        test_information = {}
        test_information['USERTEXT'] = ' '
        test_information['PROGRAM_DIR'] = ' '
        test_information['TEMP'] = ' '
        test_information['TESTERPRG'] = ' '
        test_information['PART_ID'] = ' '
        test_information['PACKAGE_ID'] = ' '
        test_information['SUBLOT_ID'] = ' '

        return test_information

    def send_summary(self, summary: dict):
        self._stdf_aggregator.append_test_summary(summary)
        self._stdf_aggregator.finalize()
        self._stdf_aggregator.write_footer_records()

    def send_testresult(self, stdf_data: dict):
        pass
        # self._stdf_aggregator.append_test_results(stdf_data)
