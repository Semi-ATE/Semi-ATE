class BinTableInformationHandler:
    def __init__(self, sites: list):
        self._bin_table = {}
        self._sites = sites

    def set_bin_table(self, bin_table: dict):
        for bin_info in bin_table:
            self._bin_table[bin_info['SBIN']] = self._generate_table_row(bin_info['SBINNAME'], int(bin_info['SBIN']), int(bin_info['HBIN']), bin_info['GROUP'])

    def _generate_table_row(self, bin_name: str, sbin: int, hbin: int, typ: str):
        site_counts = []
        for site in self._sites:
            site_counts.append({'siteId': site, 'count': 0})

        return {'name': bin_name, 'sBin': sbin, 'hBin': hbin, 'type': typ, 'siteCounts': site_counts}

    def _update_hbin_num(self, sbin: str, hbin: str):
        self._bin_table[sbin]['hBin'] = int(hbin)

    def clear_bin_table(self):
        self._bin_table.clear()

    def get_bin_table_infos(self) -> list:
        return [table_row for _, table_row in self._bin_table.items()]

    def accumulate_bin_table_info(self, site_id: str, sbin: int):
        return self._update_site_count(site_id, sbin)

    def _update_site_count(self, site_id: str, sbin: int):
        for site_count in self._bin_table[str(sbin)]['siteCounts']:
            if site_count['siteId'] != site_id:
                continue

            site_count['count'] += 1

    def reaccumulate_bin_table_info(self, prrs: list):
        self._reset_site_count()
        for _, prr in prrs.items():
            site = str(prr['SITE_NUM'])
            sbin = str(prr['SOFT_BIN'])
            self._update_site_count(site, int(sbin))

    def _reset_site_count(self):
        for _, bin_info in self._bin_table.items():
            for site_count in bin_info['siteCounts']:
                site_count['count'] = 0
