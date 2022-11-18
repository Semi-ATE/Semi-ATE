import platform
from semi_ate_testers.testers.tester_interface import TesterInterface
from SCT8.tester import Tester as sct8



class MiniSCT(TesterInterface, sct8):
    SITE_COUNT = 1

    def __init__(self, logger=None):
        TesterInterface.__init__(self, logger)
        sct8.__init__(self)

    def do_request(self, site_id: int, timeout: int) -> bool:
        self.log_info(f'MiniSCT.do_request(site_id={site_id})')
        return True

    def test_in_progress(self, site_id: int):
        self.log_info(f'MiniSCT.test_in_progress(site_id={site_id})')

    def test_done(self, site_id: int, timeout: int):
        self.log_info(f'MiniSCT.test_done({site_id})')

    def do_init_state(self, site_id: int):
        self.log_info(f'MiniSCT.do_init_state(site_id={site_id})')
        if hasattr(sct8, 'do_init_state'):
            sct8.do_init_state(self)

    def teardown(self):
        self.log_info('MiniSCT.teardown')
        sct8.close(self)

    def run_pattern(self, pattern_name: str, start_label: str = '', stop_label: str = '', timeout: int = 1000):
        self.pf.run(pattern_name, start_label, stop_label, timeout)
