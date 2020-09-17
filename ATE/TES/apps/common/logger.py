""" logging debug and runtime information """
from logging.handlers import RotatingFileHandler
import logging
import os


logger_name = "logger"
base_path = "log"


class Logger:
    """ configure logger, to save trace information in a log file """
    def __init__(self, log_file):
        self.logger_name = logger_name
        self.log_file = log_file

    def set_logger(self):
        logger = logging.getLogger(self.logger_name)
        os.makedirs(base_path, exist_ok=True)
        log_file = os.path.join(base_path, self.log_file)
        # set max size of file (50Mb)
        file_rotation_handler = RotatingFileHandler(log_file,
                                                    maxBytes=5 * 1024 * 1024,
                                                    backupCount=10)
        formater = logging.Formatter('%(name)s %(levelname)s %(asctime)s %(message)s',
                                     datefmt='%d/%m/%Y %I:%M:%S %p')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formater)
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setFormatter(formater)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        logger.addHandler(file_rotation_handler)

    @staticmethod
    def set_global_logger_name(name):
        global logger_name
        logger_name = name

    @staticmethod
    def get_logger():
        return logging.getLogger(logger_name)

    @staticmethod
    def warning(*args):
        logging.warning(*args)

    @staticmethod
    def info(*args):
        logging.info(*args)

    @staticmethod
    def debug(*args):
        logging.debug(*args)

    @staticmethod
    def error(*args):
        logging.error(*args)
