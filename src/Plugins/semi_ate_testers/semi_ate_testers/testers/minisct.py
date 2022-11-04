from SCT8.tester import Tester as sct8
from semi_ate_testers.testers.tester_interface import TesterInterface


# TODO: substitute print by logger, see issue #161


class MiniSCT(TesterInterface, sct8):
    SITE_COUNT = 1

    def do_request(self, site_id: int, timeout: int) -> bool:
        return True

    def test_in_progress(self, site_id: int):
        print(f'Tester.test_in_progress({site_id})')

    def test_done(self, site_id: int, timeout: int):
        print(f'Tester.test_done({site_id})')

    def do_init_state(self, site_id: int):
        print(f'Tester.do_init_state({site_id})')

    def run_pattern(self, pattern_name: str, start_label: str = '', stop_label: str = '', timeout: int = 1000):
        self.pf.run(pattern_name, start_label, stop_label, timeout)
