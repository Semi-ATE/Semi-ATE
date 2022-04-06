""" master application """
# from common.application import Application
from ate_master_app.master_application import MasterApplication, assert_valid_system_mimetypes_config
from ate_apps_common import configuration_reader
from argparse import ArgumentParser


DEFAULT_LOGFILE_NAME = "master_app.log"
DEFAULT_CONFIGFILE_PATH = "./master_config_file.json"


def parse_config_dict_from_command_line():
    parser = ArgumentParser()
    parser.add_argument('-d', '--device-id', help='device id', type=str)
    parser.add_argument('-s', '--sites', help='comma delimited list of site-ids', type=lambda s: [item.strip() for item in s.split(',')])
    parser.add_argument('-f', '--file', help='configuration file name', type=lambda s: [item.strip() for item in s.split(',')])
    args = parser.parse_args()

    config = {}
    if args.device_id is not None:
        config['device_id'] = args.device_id
    if args.sites is not None:
        config['sites'] = args.sites

    if args.file is not None:
        config['file'] = args.file

    return config


def launch_master(*, config_file_path=None, user_config_dict=None):
    assert_valid_system_mimetypes_config()

    cfg = configuration_reader.ConfigReader(config_file_path)
    configuration = cfg.get_configuration_ex(user_config_dict=user_config_dict)

    f = MasterApplication(configuration)
    f.run()


def main():
    user_config = parse_config_dict_from_command_line()
    launch_master(config_file_path=DEFAULT_CONFIGFILE_PATH,
                  user_config_dict=user_config)

if __name__ == '__main__':
    main()
