from logging import StreamHandler
from logging.handlers import RotatingFileHandler
import logging
import os
import time
from enum import Enum


MAX_NUM_OF_LOGS = 4000
LOG_FILE_LIFETIME_DAYS = 14


class LogLevel(Enum):
    Info = logging.INFO
    Warning = logging.WARNING
    Debug = logging.DEBUG
    Error = logging.ERROR

    def __call__(self):
        return self.value


# this class could be used to wrap log information into for example a file format other
# than the standard (.log) file
# for now this will propagate the log information to stdout and to mqtt client if defined
class LogHandler(StreamHandler):
    def __init__(self, formatter, mqtt=None):
        super().__init__()
        self.formatter = formatter
        self._last_log = []
        self.mqtt = mqtt

    def emit(self, record):
        log_data = self.formatter.format(record)
        self._last_log.append(log_data)
        print(log_data)   # stream log information

        if self.mqtt:
            self.mqtt.send_log(log_data)

    def get_log_data(self):
        log = self._last_log.copy()
        self._last_log = []
        return log


class Logger:
    datefmt = '%d/%m/%Y %I:%M:%S %p'
    filetime_fmt = '%Y%m%d-%H%M%S'
    base_path = "log"

    def __init__(self, logger_name, mqtt=None):
        self.logger_name = logger_name
        str_time = time.strftime(self.filetime_fmt)
        self.log_file = os.path.join(self.base_path, f'{str_time}_{logger_name}.log')
        self.logs = []

        self.logger = logging.getLogger(self.logger_name)
        os.makedirs(self.base_path, exist_ok=True)
        # set max size of file (100Mb)
        self.file_rotation_handler = RotatingFileHandler(self.log_file,
                                                         maxBytes=100 * 1024 * 1024,
                                                         backupCount=1)

        formatter = logging.Formatter('%(name)-9s|%(asctime)-4s |%(levelname)-7s |%(message)s',
                                      datefmt=self.datefmt)

        self.stream_handler = LogHandler(formatter, mqtt)
        self.logger.addHandler(self.stream_handler)

        self.file_rotation_handler.setFormatter(formatter)
        self.logger.addHandler(self.file_rotation_handler)

        self.set_logger_level(logging.WARNING)
        self.clean_up_log_files_if_needed()

    @staticmethod
    def get_logger():
        return logging.getLogger()

    def warning(self, *args):
        self.logger.warning(*args)

    def info(self, *args):
        self.logger.info(*args)

    def debug(self, *args):
        self.logger.debug(*args)

    def error(self, *args):
        self.logger.error(*args)

    def log_message(self, type, message):
        try:
            {
                LogLevel.Info(): lambda: self.logger.info(message),
                LogLevel.Debug(): lambda: self.logger.debug(message),
                LogLevel.Warning(): lambda: self.logger.warning(message),
                LogLevel.Error(): lambda: self.logger.error(message)
            }[type]()

            self.logs.extend(self.stream_handler.get_log_data())
        except Exception:
            # TODO: should we raise error or ignore unknown types ??
            pass

    def get_logs(self):
        self.clear_logs()
        with open(self.log_file, 'r') as f:
            return self._generate_logs(list(reversed(list(f)[:MAX_NUM_OF_LOGS])))

    def append_log(self, log):
        self.logs.append(log)

    def get_current_logs(self):
        logs = self.logs.copy()
        self.clear_logs()
        return self._generate_logs(list(reversed(logs)))

    def clear_logs(self):
        self.logs = []

    def are_logs_available(self):
        return len(self.logs) > 0

    def clean_up_log_files_if_needed(self):
        from datetime import datetime
        now = datetime.now()
        current_date = datetime.strptime(now.strftime(self.filetime_fmt), self.filetime_fmt)
        for log_file_name in os.listdir(self.base_path):
            log_file_datetime_str = os.path.basename(os.path.splitext(log_file_name)[0]).split('_')[0]
            log_file_datetime = datetime.strptime(log_file_datetime_str, '%Y%m%d-%H%M%S')

            diff = current_date - log_file_datetime
            if diff.days > LOG_FILE_LIFETIME_DAYS:
                self.remove_log_file(os.path.join(self.base_path, log_file_name))

    @staticmethod
    def remove_log_file(log_file):
        if not os.path.exists(log_file):
            return

        os.remove(log_file)

    def get_log_file_information(self):
        with open(self.log_file, 'r') as f:
            return {'filename': os.path.basename(self.log_file), 'content': f.read()}

    def set_logger_level(self, level):
        self.logger.setLevel(level)
        self.stream_handler.setLevel(level)
        self.file_rotation_handler.setLevel(level)

    @staticmethod
    def _generate_logs(logs):
        structured_logs = []
        for log in logs:
            line = log.split('|')
            structured_logs.append({'source': line[0], 'date': line[1], 'type': line[2], 'description': line[3].strip()})

        return structured_logs

    def set_mqtt_client(self, mqtt_client):
        self.mqtt = mqtt_client
