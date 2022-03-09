from ate_common.program_utils import BinTableFieldName
from ate_common.logger import LogLevel
import os
import re


class FileSystemDataSource:
    def __init__(self, jobname, configuration, parser, logger):
        self.parser = parser
        self.configuration = configuration.get('jobformat')
        self.device_id = configuration.get('device_id')
        self.device_handler = configuration.get("Handler")
        self.device_environment = configuration.get("Environment")

        self.path = configuration['filesystemdatasource.path']
        # the jobpattern defines a pattern for
        # the filename, e.g. le#jobname#.xml
        self.lot_number = jobname
        self.jobname = configuration['filesystemdatasource.jobpattern'].\
            replace("#jobname#", jobname)

        self.log = logger
        self.fullpath = os.path.join(self.path, self.jobname)

    def does_file_exist(self):
        if not os.path.exists(self.fullpath):
            self.log.log_message(LogLevel.Error(), f'job file "{self.fullpath}" could not be not found')
            return False

        return True

    def retrieve_data(self):
        if not self.does_file_exist():
            return None

        if self.configuration is None:
            return None

        if self.parser is None:
            return None

        param_data = self.parser.parse(self.fullpath)
        for key, value in param_data.items():
            if value is None:
                self.log.log_message(LogLevel.Error(), f'{key} section is missing')
                return None

        return param_data

    def verify_data(self, param_data):
        return (self.is_lot_number_valid(param_data.get("MAIN"), self.lot_number)
                and self.does_device_id_exist(param_data.get("CLUSTER"))
                and self.is_station_valid(param_data.get("STATION"))
                and self.does_handler_id_exist(param_data.get("CLUSTER")))

    def get_test_information(self, param_data: dict):
        test_information = {}
        test_information['PACKAGE_ID'] = param_data['MAIN']['PACKAGEID_SHORT']
        test_information['SUBLOT_ID'] = param_data['MAIN']['LOTNUMBER'].split('.')[1]
        for _, value in param_data.get("STATION").items():
            if self.does_device_id_exist(value):
                test_information.update(self.remove_digit_from_keys(value))
                test_information['PART_ID'] = f"{param_data['MAIN']['MATCHCODE']}_{test_information['TESTERPRG']}"
                return test_information

        self.log.log_message(LogLevel.Warning(), f'device information for "{self.device_id}" in the STATION section are missing')
        return None

    def remove_digit_from_keys(self, data: dict):
        raw_data = {}
        for key, value in data.items():
            raw_data[''.join(i for i in key if not i.isdigit())] = value

        return raw_data

    def is_lot_number_valid(self, param_data: dict, lot_number):
        if not (param_data.get("LOTNUMBER") == lot_number):
            self.log.log_message(LogLevel.Warning(),
                                 f'lot number: {lot_number} could not be found, lot number defined in xml file: {param_data.get("LOTNUMBER")}')
            return False

        return True

    def does_handler_id_exist(self, param_data: dict):
        if not (param_data.get("HANDLER_PROBER") == self.device_handler):
            self.log.log_message(LogLevel.Warning(),
                                 f'HANDLER: {self.device_handler} name could not be found, handler name defined in xml file: {param_data.get("HANDLER_PROBER")}')
            return False

        return True

    def does_device_id_exist(self, param_data: dict):
        for key, value in param_data.items():
            if key == 'TESTER' or re.match(r'TESTER\d', key) is not None:
                if self.device_id == value:
                    return True

        return False

    def is_station_valid(self, param_data: dict):
        for _, value in param_data.items():
            if self.does_device_id_exist(value):
                return True

        self.log.log_message(LogLevel.Warning(), f'device id {self.device_id} could not be found in STATION section')
        return False

    @staticmethod
    def get_bin_table(data: list):
        bin_table = []
        for entry in data['BINTABLE']['ENTRY']:
            bin_element = {}
            for key, value in entry.items():
                key = key.replace('@', '')
                bin_element[key] = value

            bin_table.append(bin_element)

        return bin_table

    @staticmethod
    def get_binning_tuple(bin_table: list) -> dict:
        binning_tuple = {}
        for bin_info in bin_table:
            binning_tuple.setdefault(bin_info[BinTableFieldName.HBin()], []).append(bin_info[BinTableFieldName.SBinNum()])

        return binning_tuple
