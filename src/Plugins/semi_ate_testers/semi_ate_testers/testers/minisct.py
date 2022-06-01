from SCT8.tester import Tester as sct8


# TODO: substitute print by logger, see issue #161


class MiniSCT(sct8):

    def get_sites_count(self):
        return 1

    def do_request(self, site_id: int, timeout: int) -> bool:
        return True

    def test_in_progress(self, site_id: int):
        print(f'Tester.test_in_progress({site_id})')

    def test_done(self, site_id: int, timeout: int):
        print(f'Tester.test_done({site_id})')

    def do_init_state(self, site_id: int):
        print(f'Tester.do_init_state({site_id})')
