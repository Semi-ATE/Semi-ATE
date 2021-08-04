import argparse
import json


class CommandLineParser:
    __slots__ = ["broker_host", "broker_port", "device_id", "site_id", "strategytype"]

    def __init__(self, argv=None):
        self.broker_host = "127.0.0.1"
        self.broker_port = 1883
        self.device_id = "SCT-81-1F"
        self.site_id = "0"
        self.strategytype = "file"
        self.init_from_command_line(argv)

    def to_json(self):
        return {key: getattr(self, key, None) for key in self.__slots__}

    def update_from_json(self, json_str: str):
        for key, v in json.loads(json_str).items():
            if key in self.__slots__:
                setattr(self, key, v)

    def update_from_kwargs(self, **kwargs):
        for key, v in kwargs.items():
            if key in self.__slots__ and v is not None:
                setattr(self, key, v)

    def update_from_file(self, filename: str):
        with open(filename, 'r') as infile:
            self.update_from_json(infile.read())

    def update_from_parsed_argparse_args(self, args: list):  # args = argparse.ArgumentParser().parse_args()
        self.update_from_kwargs(**vars(args))

    def add_argparse_arguments(self, parser: argparse.ArgumentParser):
        for key in self.__slots__:
            parser.add_argument('--' + key)

    def init_from_command_line(self, argv: list):
        parser = argparse.ArgumentParser(prog=argv[0], formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        self.add_argparse_arguments(parser)
        parser.add_argument('config_file', metavar='config-file', nargs='?')
        parser.add_argument("-v", "--verbose",
                            help="increase output verbosity",
                            action="store_true")
        parser.add_argument('--parent-pid')
        parser.add_argument('--ptvsd-host', nargs='?', default='0.0.0.0', type=str,
                            help="remote debugger list ip address")
        parser.add_argument('--ptvsd-port', nargs='?', default=5678, type=int,
                            help="remote debugger list port")
        parser.add_argument('--ptvsd-enable-attach', action="store_true",
                            help="enable remote debugger attach")
        parser.add_argument('--ptvsd-wait-for-attach', action="store_true",
                            help="wait for remote debugger attach before start (implies --ptvsd-enable-attach)")
        args = parser.parse_args(argv[1:])

        if args.ptvsd_enable_attach or args.ptvsd_wait_for_attach:
            import ptvsd
            ptvsd.enable_attach(address=(args.ptvsd_host, args.ptvsd_port))
            if args.ptvsd_wait_for_attach:
                ptvsd.wait_for_attach()

        self.update_from_parsed_argparse_args(args)
