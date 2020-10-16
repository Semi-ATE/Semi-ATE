from ATE.Tester.TES.apps.handlerApp.handler_runner import HandlerRunner
from ATE.Tester.TES.apps.common.configuration_reader import ConfigReader
from argparse import ArgumentParser


def parse_config_dict_from_command_line():
    parser = ArgumentParser(description='Handler arguments')
    parser.add_argument('port', type=str,
                        help='serial interface for tester communication')
    parser.add_argument('--baudrate', default=115200, type=int,
                        help='set bautrate')
    parser.add_argument('--timeout', default=1, type=int,
                        help='set timeout')
    parser.add_argument('--parity', default='N', type=str,
                        help='set parity')
    parser.add_argument('--bytesize', default=8, type=int,
                        help='set bytesize')
    parser.add_argument('--stopbits', default=1, type=int,
                        help='set stopbits')

    return parser.parse_args()


if __name__ == "__main__":
    config = ConfigReader("./handler_config_file.json")
    configuration = config.get_configuration()

    args = parse_config_dict_from_command_line()
    app = HandlerRunner(configuration, args)
    app.run()
