import json
import time
import subprocess
import argparse
from enum import Enum


MASTER_CONFIG_FILENAME = "master_config_file.json"
CONTROL_CONFIG_FILENAME = "control_config_file.json"
HANDLER_CONFIG_FILENAME = "handler_config_file.json"

MASTER_CONFIG_FILENAME_TEMPLATE = "master_config_file_template.json"
CONTROL_CONFIG_FILENAME_TEMPLATE = "control_config_file_template.json"
HANDLER_CONFIG_FILENAME_TEMPLATE = "handler_config_file_template.json"


class Configs(Enum):
    site_id = "site"
    device_id = "SCT-81-1F"
    host = "127.0.0.1"
    port = 1883
    webui_host = "127.0.0.1"
    webui_port = 8081

    def __call__(self):
        return f'{self.value}'


def read_template_config(filename):
    with open(filename) as conf:
        _conf = json.load(conf)

    return _conf


def create_master_config_file(sites, device_id,
                              host=None,
                              port=None,
                              webui_host=None,
                              webui_port=None):
    config = read_template_config(MASTER_CONFIG_FILENAME_TEMPLATE)
    config["broker_host"] = Configs.host.value if host is None else host
    config["broker_port"] = Configs.port.value if port is None else port
    config["device_id"] = device_id
    config["sites"] = sites
    config["webui_host"] = Configs.webui_host.value if webui_host is None else webui_host
    config["webui_port"] = Configs.webui_port.value if webui_port is None else webui_port

    dump_to_file("master", config)


def create_control_config_file(site_id, device_id, host=None, port=None):
    config = read_template_config(CONTROL_CONFIG_FILENAME_TEMPLATE)
    config["broker_host"] = Configs.host.value if host is None else host
    config["broker_port"] = Configs.port.value if port is None else port
    config["device_id"] = device_id
    config["site_id"] = site_id

    dump_to_file("control", config)


def create_handler_config_file(device_id, host=None, port=None):
    config = read_template_config(HANDLER_CONFIG_FILENAME_TEMPLATE)
    config["broker_host"] = Configs.host.value if host is None else host
    config["broker_port"] = Configs.port.value if port is None else port
    config["device_id"] = device_id

    dump_to_file("handler", config)


def dump_to_file(target, config):
    if target == "master":
        file_name = MASTER_CONFIG_FILENAME
    elif target == "control":
        file_name = CONTROL_CONFIG_FILENAME
    elif target == "handler":
        file_name = HANDLER_CONFIG_FILENAME
    else:
        return

    json_c = json.dumps(config, indent=4)

    with open(file_name, 'w') as f:
        f.write(json_c)


def file_parser():
    parser = argparse.ArgumentParser(prog="auto-script.py", usage="%(prog)s [app typ: 'master', 'control'] [master id]")
    parser.add_argument('typ', help='application typ')
    parser.add_argument('dev_id', help='device id')
    parser.add_argument('-conf', help='define if only the config file must to be generated', action='count', default=0)
    parser.add_argument('-host', help='host ip')
    parser.add_argument('-port', help='host port', type=int)
    parser.add_argument('-web_host', help='webui host name')
    parser.add_argument('-web_port', help='webui host port', type=int)
    parser.add_argument('-num_apps', help='num of to generate apps', default=1, type=int)
    parser.add_argument('-handler', help='handler', default=0)
    parser.add_argument('-env', help='env', default=0)
    parser.add_argument('-browser', help='activate browser', action='count', default=0)

    args = parser.parse_args()
    return args


def kill_process(process_list):
    import sys
    for proc in process_list:
        proc.kill()

    sys.exit(0)


def start_apps():
    args = file_parser()
    num_apps = args.num_apps
    app_typ = args.typ
    device_id = args.dev_id
    pid_list = []
    run = True

    if app_typ == 'master':
        # generate list of site ids
        sites = [str(x) for x in range(num_apps)]
        create_master_config_file(sites, device_id, host=args.host, port=args.port,
                                  webui_host=args.web_host, webui_port=args.web_port)
        # TODO: only one master is supported for now
        if not args.conf:
            master = subprocess.Popen("python launch_master.py -f master_config_file.json")
            pid_list.append(master)
            time.sleep(2)
            # start webserver
            if args.browser:
                configuration = read_template_config(MASTER_CONFIG_FILENAME)
                webui_host = configuration["webui_host"]
                webui_port = configuration["webui_port"]
                subprocess.run(f"start http://{webui_host}:{webui_port}", shell=True)
        else:
            run = False

    elif app_typ == 'control':
        for id in range(num_apps):
            create_control_config_file(str(id), device_id, host=Configs.host(), port=int(Configs.port()))
            if not args.conf:
                control = subprocess.Popen("python launch_control.py")
                pid_list.append(control)
                time.sleep(0.5)
            else:
                run = False

    elif app_typ == 'handler':
        create_handler_config_file(device_id, host=args.host, port=args.port)
        if not args.conf:
            handler = subprocess.Popen("python launch_handler.py --f handler_config_file.json")
            pid_list.append(handler)
            time.sleep(2)
        else:
            run = False

    while run:
        input("press enter to terminate")
        break

    if not args.conf:
        kill_process(pid_list)


start_apps()
