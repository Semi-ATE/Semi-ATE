
class Dummysct():


    def get_sites_count(self):
        return 1

    def do_request(self, site_id: int, timeout: int) -> bool:
        return True

    def test_in_progress(self, site_id: int):
        print(f'Dummysct.test_in_progress({site_id})')

    def test_done(self, site_id: int, timeout: int):
        print(f'Dummysct.test_done({site_id})')

    def do_init_state(self, site_id: int):
        print(f'Dummysct.do_init_state({site_id})')