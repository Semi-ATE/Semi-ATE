from ate_common.program_utils import BinTableFieldName
from dataclasses import dataclass


@dataclass()
class BinInfo:
    bin_name: str = ''
    sbin: int = -1
    hbin: int = -1
    count: int = 0
    result_flag: str = ''
    head_num: int = 0

    def update_infos(self, result_flag: str, head_num: int):
        self.count += 1
        self.result_flag = 'P' if result_flag == 0 else 'F'
        self.head_num = head_num

    def is_bin_name(self, bin_name):
        return bin_name == self.bin_name

    def to_dict(self):
        return {self.bin_name: [self.sbin, self.hbin, self.count, self.result_flag, self.head_num]}


class SiteInformation:
    def __init__(self, site_id: int, site_infos: dict):
        self.site_id = site_id
        self.site_infos = self.generate_site_infos(site_infos)

    def store_test_result(self, prr_record: dict):
        # make sure the record is a prr record
        assert prr_record['type'] == 'PRR'

        self.site_infos[str(prr_record['SOFT_BIN'])].update_infos(prr_record['PART_FLG'], int(prr_record['HEAD_NUM']))

    @staticmethod
    def generate_site_infos(site_infos: dict):
        ret_dict = {}
        for site_info in site_infos:
            ret_dict[site_info[BinTableFieldName.SBinNum()]] =\
                BinInfo(site_info[BinTableFieldName.SBinName()],
                        int(site_info[BinTableFieldName.SBinNum()]),
                        int(site_info[BinTableFieldName.HBin()]),
                        0,
                        'F')

        return ret_dict

    def get_bin_information(self) -> dict:
        ret_dict = {}
        for _, site_info in self.site_infos.items():
            ret_dict.update(site_info.to_dict())

        return ret_dict


class SiteInformationHandler:
    def __init__(self, sites_id: list):
        self.sites_info = {}
        self.sites_id = sites_id
        self.bin_names = []

    def set_sites_information(self, site_infos: dict):
        self.bin_names = [site_info[BinTableFieldName.SBinName()] for site_info in site_infos]

        for site_id in self.sites_id:
            self.sites_info[site_id] = SiteInformation(site_id, site_infos)

    def store_test_result(self, site_id: str, prr_record: dict):
        self.sites_info[site_id].store_test_result(prr_record)

    def get_summary_information(self):
        summary = {}
        for site_id, site_info in self.sites_info.items():
            bin_info = site_info.get_bin_information()

            for bin_name in self.bin_names:
                summary.setdefault(bin_name, {}).update({site_id: bin_info[bin_name]})

        return summary

    def get_num_sites(self):
        return len(self.sites_info)
