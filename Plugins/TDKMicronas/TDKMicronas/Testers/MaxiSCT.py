
from TDKMicronas.Testers.InterfaceSCT import InterfaceSCT


class MaxiSCT(InterfaceSCT):
    def get_sites_count(self):
        # TODO: temporary value for 16
        return 16

    def do_request(self, site_id: int, timeout: int) -> bool:
        return True

    def test_in_progress(site_id: int, timeout: int):
        pass

    def test_done(site_id: int, timeout: int):
        pass
