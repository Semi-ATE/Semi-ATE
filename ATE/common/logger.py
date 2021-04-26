from logging import StreamHandler
from logging.handlers import RotatingFileHandler
import logging
import os
import time
from enum import IntEnum


MAX_NUM_OF_LOGS = 4000
MAX_LINE_LENGTH_IN_BYTE = 100
MAX_DATA_TO_READ = MAX_LINE_LENGTH_IN_BYTE * MAX_NUM_OF_LOGS
LOG_FILE_LIFETIME_DAYS = 14


class LogLevel(IntEnum):
    Info = logging.INFO
    Measure = 15
    Debug = logging.DEBUG
    Warning = logging.WARNING
    Error = logging.ERROR

    def __call__(self):
        return self.value


def add_log_level(level_num: int, level_name: str):
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    logging.addLevelName(level_num, level_name)
    setattr(logging, level_name, level_num)
    setattr(logging.getLoggerClass(), level_name.lower(), logForLevel)
    setattr(logging, level_name.lower(), logToRoot)


add_log_level(LogLevel.Measure(), 'MEASURE')


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
        print(log_data)

        if self.mqtt:
            self.mqtt.send_log(log_data)

    def get_log_data(self):
        log = self._last_log.copy()
        self._last_log = []
        return log

    def has_log_entries(self):
        return len(self._last_log) > 0

    def set_mqtt_client(self, mqtt_client):
        self.mqtt = mqtt_client


class Logger:
    datefmt = '%d/%m/%Y %I:%M:%S %p'
    filetime_fmt = '%Y%m%d-%H%M%S'
    base_path = "log"

    def __init__(self, logger_name, mqtt=None):
        self.active_loggers = {}
        self.logger_name = logger_name
        self.global_log_level = logging.WARNING
        str_time = time.strftime(self.filetime_fmt)
        self.log_file = os.path.join(self.base_path, f'{str_time}_{logger_name}.log')

        os.makedirs(self.base_path, exist_ok=True)
        # set max size of file (100Mb)
        self.file_rotation_handler = RotatingFileHandler(self.log_file,
                                                         maxBytes=100 * 1024 * 1024,
                                                         backupCount=1)

        formatter = logging.Formatter('%(name)-9s|%(asctime)-4s |%(levelname)-7s |%(message)s',
                                      datefmt=self.datefmt)

        self.stream_handler = LogHandler(formatter, mqtt)
        self.file_rotation_handler.setFormatter(formatter)
        self.logger = self.get_logger_for_component(self.logger_name)

        self.set_logger_level(logging.WARNING)
        self.clean_up_log_files_if_needed()

    def cleanup(self):
        # remove all used handler
        self.logger.handlers = []

    def get_logger_for_component(self, component_name):
        if component_name in self.active_loggers:
            return self.active_loggers[component_name]

        new_logger = logging.getLogger(component_name)
        new_logger.addHandler(self.stream_handler)
        new_logger.addHandler(self.file_rotation_handler)
        new_logger.setLevel(self.global_log_level)
        self.active_loggers[component_name] = new_logger
        return new_logger

    @staticmethod
    def get_logger():
        return logging.getLogger()

    def log_message(self, type, message):
        try:
            {
                LogLevel.Info(): lambda: self.logger.info(message),
                LogLevel.Debug(): lambda: self.logger.debug(message),
                LogLevel.Warning(): lambda: self.logger.warning(message),
                LogLevel.Error(): lambda: self.logger.error(message),
                LogLevel.Measure(): lambda: self.logger.measure(message),
            }[type]()
        except Exception as e:
            raise Exception(f"message type could not be handled: {e}")

    def get_logs(self):
        self.clear_logs()
        with open(self.log_file, 'r') as f:
            # go to the end of the file
            f.seek(0, os.SEEK_END)
            if f.tell() > MAX_DATA_TO_READ:
                # if we have more than we need then
                # go to the end of the file and go back the size of data to be read
                f.seek(-MAX_DATA_TO_READ, os.SEEK_END)
            else:
                # if the data we have not large enough then
                # go to the beginning of the file and read from there
                f.seek(0, os.SEEK_SET)

            data = f.readlines(MAX_DATA_TO_READ)
            return self._generate_logs(list(reversed(data)))

    def append_log(self, log):
        # Attention: This approach will replace the date of the original
        # entry with the datetime when this method was called for the entry,
        # thus introducing a potential difference between the time an event
        # is logged here and the time it was originally generated on the
        # remote application
        line = log.split('|')
        component_logger = self.get_logger_for_component(line[0])
        loglevel = line[2]
        if "INFO" in loglevel:
            component_logger.info(line[3])
        if "WARNING" in loglevel:
            component_logger.warning(line[3])
        if "DEBUG" in loglevel:
            component_logger.debug(line[3])
        if "ERROR" in loglevel:
            component_logger.error(line[3])
        if "MEASURE" in loglevel:
            component_logger.measure(line[3])

    def get_current_logs(self):
        logs = self.stream_handler.get_log_data()
        return self._generate_logs(list(reversed(logs)))

    def clear_logs(self):
        _ = self.get_current_logs()

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
        for _, logger in self.active_loggers.items():
            logger.setLevel(level)
        self.stream_handler.setLevel(level)
        self.file_rotation_handler.setLevel(level)
        self.global_log_level = level

    @staticmethod
    def _generate_logs(logs):
        structured_logs = []
        for log in logs:
            line = log.split('|')
            if len(line) < 3:
                continue
            structured_logs.append({'source': line[0], 'date': line[1], 'type': line[2], 'description': line[3].strip()})

        return structured_logs

    def set_mqtt_client(self, mqtt_client):
        self.mqtt = mqtt_client
        self.stream_handler.set_mqtt_client(mqtt_client)
