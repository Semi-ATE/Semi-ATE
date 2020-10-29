from ATE.Tester.TES.apps.handlerApp.handler_runner import HandlerRunner
from ATE.Tester.TES.apps.common.configuration_reader import ConfigReader
from argparse import ArgumentParser
import serial


def parse_config_dict_from_command_line():
    parser = ArgumentParser(description='Handler arguments')
    parser.add_argument('port', type=str,
                        help='serial interface for tester communication')
    parser.add_argument('--baudrate', default=115200, type=int,
                        help='set bautrate')
    parser.add_argument('--timeout', default=0.2, type=float,
                        help='set timeout')
    parser.add_argument('--parity', default='N', type=str,
                        help='set parity')
    parser.add_argument('--bytesize', default=8, type=int,
                        help='set bytesize')
    parser.add_argument('--stopbits', default=1, type=int,
                        help='set stopbits')

    return parser.parse_args()


def generate_serial_object():
    args = parse_config_dict_from_command_line()
    return serial.Serial(args.port, baudrate=args.baudrate, bytesize=args.bytesize,
                         parity=args.parity, stopbits=args.stopbits, timeout=args.timeout)


def launch_handler(configuration, comm):
    app = HandlerRunner(configuration, comm)
    app.run()


def main():
    config = ConfigReader("./handler_config_file.json")
    configuration = config.get_configuration()

    comm = generate_serial_object()
    launch_handler(configuration, comm)


if __name__ == "__main__":
    main()
