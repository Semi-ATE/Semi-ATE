import inspect
import os
import json
import subprocess
from semi_ate_testers.testers.tester_interface import TesterInterface
from ate_test_app.sequencers.CommandLineParser import CommandLineParser
from labml_adjutancy.misc import common
from labml_adjutancy.misc.mqtt_client import mqtt_deviceattributes
from labml_adjutancy.gui.instruments.minisct.minisct import mqttcmds
from semi_ate_testers.testers import minisct
from labml_adjutancy.misc.mqtt_client import mqtt_init
import SCT8

__author__ = "Zlin526F"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"
__version__ = 0.1


class MiniSCT(TesterInterface):
    SITE_COUNT = 1

    knownAttributes = ['__len__', '__init__', 'inst', 'cmd',  '_ismethod',
                       'close',
                       'debug', 'do_init_state', 'do_request', 'get_sites_count',
                       'instName',
                       'mqtt', 'mqttc', 'mqtt_list', 'mqtt_status', '_mqttclient',
                       'logger', 'log_debug', 'log_measure', 'log_info', 'log_warning', 'log_error',
                       'run_pattern', 'on', 'off', 'publish_set',
                       'setup', 'setup_mqtt', 'size', 'shape', 'startKeywords', 'sti',
                       'teardown', 'test_done', 'test_in_progress',
                       ]
    gui = "labml_adjutancy.gui.instruments.minisct.minisct"

    def __init__(self, logger=None, mqttc=None, instName="tester", debug=False):
        TesterInterface.__init__(self, logger)
        self.cmd = ''
        self.debug = debug
        self.mqtt = mqtt_deviceattributes()
        self.instName = instName
        self.mqtt.instName = instName
        self.mqtt.mqtt_all = ['on()', 'off()']
        self.startKeywords = []

    def loadProtocolls(self):
        with open(os.path.join(os.getcwd(), '.lastsettings'), 'r') as json_file:
            settings = json.load(json_file)["settings"]
        path = os.path.join(os.getcwd(), "pattern", settings["hardware"], settings["base"],
                            settings["target"], "protocols")
        # TODO! make should be could only called once
        #from SCT8.sct8 import pf
        result = subprocess.call('make', shell=True, cwd=path)
        if result != 0:
            self.log_error(f'MiniSCT could not load protocols in {path}')

    def setup_mqtt(self, mqttc):
        """Setup for mqtt.

        Before calling setup_mqtt,  self.mqtt.mqtt_all have to be set!

        Parameters
        ----------
        mqttc : object to the mqtt-client

        Returns
        -------
        None.

        """
        # self.mqtt.mqtt_debug = True             # helpful for debugging
        self.mqtt.mqtt_add(mqttc, self)  # subscribe for mqtt and send information about the gui
        self.mqtt_list = self.mqtt.mqtt_list
        self.mqttc = mqttc

    def close(self):
        self.inst.turnOff()
        self.mqtt.close()
        self.mqttc.close()

    def on(self):
        self.inst.turnOn()

    def off(self):
        self.inst.turnOff()

    def do_request(self, site_id: int, timeout: int) -> bool:
        return True

    def test_in_progress(self, site_id: int):
        self.log_info(f"Tester.test_in_progress({site_id})")

    def test_done(self, site_id: int, timeout: int):
        self.log_info(f"Tester.test_done({site_id})")

    def do_init_state(self, site_id: int):
        self.log_info(f'MiniSCT.do_init_state(site_id={site_id})')
        self.inst = SCT8.getTester()
        self.loadProtocolls()
        self.inst.turnOn()
        self.sti = minisct.MiniSCTSTI(board=self.inst, logger=self.logger)
        self.inst.error = False
        self.startKeywords = dir(self.inst)

        # create the list for the allowed mqtt commands
        for index in range(0, 8):  # create mqtt-cmds for channels 0..7
            for cmd in mqttcmds['commands']['CH'].values():
                self.mqtt.mqtt_all.append(f"CH{index}.{cmd[0]}")
        for cmd in mqttcmds['commands']['dps'].values():
            self.mqtt.mqtt_all.append(f"dps.{cmd[0]}")

        mqttc = mqtt_init(typ="instrument")
        params = CommandLineParser([''])
# TODO: use projectname.hardware.lab_control.json to get the right client
#       or connect to the exits client from main context.harness._mqtt_connection.get_mqtt_client()
        mqttc.init(params.broker_host, port=params.broker_port, message_client=None)
        # mqttc.init("192.168.0.11", port=1883, message_client=None)

        self.setup_mqtt(mqttc)
        self.log_info(f"Tester.do_init_state({site_id})")

    def teardown(self):
        self.log_info('MiniSCT.teardown')
        self.close()

    @property
    def protocol_typ(self):
        """Set/get protocol typ."""
        return (self._protocol_typ)

    @protocol_typ.setter
    def protocol_typ(self, value):
        if value != self._protocol_typ:
            self._protocol_typ = value
            self.__getattribute__(self._protocol_typ).init()
            self.delay = self.__getattribute__(self._protocol_typ).delay


    @property
    def mqtt_status(self):
        """Getter for the mqtt_status."""
        return self.mqtt._mqtt_status

    @mqtt_status.setter
    def mqtt_status(self, value):
        self.mqtt.mqtt_status = value

    def __getattribute__(self, attr):
        """Get attribute.

        """
        if (attr != "__class__" and attr != "knownAttributes" and attr not in self.knownAttributes):
            self.cmd += f'{attr}.'
            if attr in self.startKeywords:
                self.cmd = f'{attr}.'
            value = eval(f'self.inst.{self.cmd[:-1]}')
            if not (value is None or isinstance(value, (int, bool, float, complex, str, list, tuple, bytes, bytearray, set, dict))
                    or inspect.ismethod(value)):
                value = self
            elif inspect.ismethod(value):
                return self._ismethod
            elif self.cmd[:-1] != 'mqtt_list':
                if self.debug:
                    self.log_debug(f'self.inst.{self.cmd[:-1]} = {value}')
                self.mqtt.publish_get(f'{self.cmd[:-1]}', value)
                self.cmd = ''
            elif self.cmd[:-1] == 'mqtt_list':
                self.cmd = ''
        else:
            value = super(__class__, self).__getattribute__(attr)
        return value

    def __setattr__(self, attr, value):
        """Set attribute.

        """
        if hasattr(self, "knownAttributes") and attr in self.knownAttributes:
            super(__class__, self).__setattr__(attr, value)
        else:
            evalue = f'"{value}"' if isinstance(value, str) else value
            self.cmd += f'{attr}.'
            if attr in self.startKeywords:
                self.cmd = f'{attr}.'
            if self.debug:
                self.log_debug(f'self.inst.{self.cmd[:-1]} = {value}')
            exec(f'self.inst.{self.cmd[:-1]} = {evalue}')
            self.mqtt.publish_set(f'{self.cmd[:-1]}', value)
            self.cmd = ''

    def _ismethod(self, *kwargs):
        result = common.exec_with_return(f"self.inst.{self.cmd[:-1]}{kwargs}", self)
        self.mqtt.publish_get(f"{self.cmd[:-1]}()", kwargs)
        return result


if __name__ == "__main__":
    tester = MiniSCT()
    tester.do_init_state(1)
    # breakpoint()
    tester.CH0.connections
    # tester.CH0.drv.vdh = 4.5
    tester.CH0.connect("PBUS_F")
    tester.CH0.connect("ABUS0_F")
    tester.CH0.connect("ABUS0_S")
    tester.CH0.disconnect("ABUS0_S")

    tester.CH0.relay_status

    tester.close()
