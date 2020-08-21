from ATE.TES.apps.common.logger import Logger
import os
import re


class FileSystemDataSource:
    def __init__(self, jobname, configuration, parser):
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

        self.log = Logger.get_logger()
        self.fullpath = os.path.join(self.path, self.jobname)

    def does_file_exist(self):
        if not os.path.exists(self.fullpath):
            self.log.error("file not found")
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
                self.log.error(f"{key} section missing")
                return None

        return param_data

    def verify_data(self, param_data):
        return (self.is_lot_number_valid(param_data.get("MAIN"), self.lot_number)
                and self.does_device_id_exist(param_data.get("CLUSTER"))
                and self.is_station_valid(param_data.get("STATION"))
                and self.does_handler_id_exist(param_data.get("CLUSTER")))

    def get_test_information(self, param_data: dict):
        for _, value in param_data.get("STATION").items():
            if self.does_device_id_exist(value):
                return self.remove_digit_from_keys(value)

        self.log.warning("device information in station section are missed")
        return None

    def remove_digit_from_keys(self, data: dict):
        raw_data = {}
        for key, value in data.items():
            raw_data[''.join(i for i in key if not i.isdigit())] = value

        return raw_data

    def is_lot_number_valid(self, param_data: dict, lot_number):
        if not (param_data.get("LOTNUMBER") == lot_number):
            self.log.warning("lot number does not match")
            return False

        return True

    def does_handler_id_exist(self, param_data: dict):
        if not (param_data.get("HANDLER_PROBER") == self.device_handler):
            self.log.warning("HANDLER name does not match")
            return False

        return True

    def does_device_id_exist(self, param_data: dict):
        for key, value in param_data.items():
            if key == 'TESTER' or re.match(r'TESTER\d', key) is not None:
                if self.device_id == value:
                    return True

        self.log.warning("tester could not be found")
        return False

    def is_station_valid(self, param_data: dict):
        for _, value in param_data.items():
            if self.does_device_id_exist(value):
                return True

        self.log.warning("device id mismatch in station section")
        return False
