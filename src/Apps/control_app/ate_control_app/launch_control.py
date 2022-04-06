""" control application """
from ate_control_app.control_application import ControlApplication, ensure_asyncio_event_loop_compatibility_for_windows
from ate_apps_common import configuration_reader
from argparse import ArgumentParser

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


def launch_control(config_file_path=None, user_config_dict=None):
    ensure_asyncio_event_loop_compatibility_for_windows()

    cfg = configuration_reader.ConfigReader(config_file_path)
    configuration = cfg.get_configuration_ex(user_config_dict=user_config_dict)

    f = ControlApplication(configuration)
    f.run()

def main():
    user_config = parse_config_dict_from_command_line()
    launch_control(config_file_path=DEFAULT_CONFIGFILE_PATH,
                   user_config_dict=user_config)

if __name__ == "__main__":
    main()
