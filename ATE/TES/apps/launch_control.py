""" control application """
from ATE.TES.apps.common.logger import Logger
from ATE.TES.apps.controlApp.control_application import ControlApplication, ensure_asyncio_event_loop_compatibility_for_windows
from ATE.TES.apps.common import configuration_reader
from argparse import ArgumentParser
import json

DEFAULT_LOGFILE_NAME = "control_app.log"
DEFAULT_CONFIGFILE_PATH = "./control_config_file.json"


def parse_config_dict_from_command_line():
    parser = ArgumentParser()
    parser.add_argument('-d', '--device-id', help='device id', type=str)
    parser.add_argument('-s', '--site-id', help='site-ids', type=str)
    args = parser.parse_args()

    config = {}
    if args.device_id is not None:
        config['device_id'] = args.device_id
    if args.site_id is not None:
        config['site_id'] = args.site_id

    return config


def launch_control(*, log_file_name=None, config_file_path=None, user_config_dict=None):
    ensure_asyncio_event_loop_compatibility_for_windows()

    Logger.set_global_logger_name('control')
    Logger(log_file_name).set_logger()
    logger = Logger.get_logger()

    cfg = configuration_reader.ConfigReader(config_file_path)
    configuration = cfg.get_configuration_ex(user_config_dict=user_config_dict)

    logger.debug('active config (based on file "%s"): %s\n',
                 config_file_path,
                 json.dumps(configuration, sort_keys=True, indent=4))

    f = ControlApplication(configuration)
    f.run()


if __name__ == "__main__":
    user_config = parse_config_dict_from_command_line()
    launch_control(log_file_name=DEFAULT_LOGFILE_NAME,
                   config_file_path=DEFAULT_CONFIGFILE_PATH,
                   user_config_dict=user_config)
