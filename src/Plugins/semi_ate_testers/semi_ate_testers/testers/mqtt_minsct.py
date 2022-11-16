import inspect
from semi_ate_testers.testers.tester_interface import TesterInterface
from labml_adjutancy.misc import common
from labml_adjutancy.misc.mqtt_client import mqtt_deviceattributes
from labml_adjutancy.misc.gui.minisct import mqttcmds
from SCT8.tester import Tester as sct8


class Tester(TesterInterface):

    knownAttributes = ['size', 'shape', '__len__', '__init__', 'inst', 'cmd', 'startKeywords', '_ismethod',
                       'do_init_state', 'get_sites_count', 'do_request', 'test_in_progress', 'test_done',
                       'instName', 'setup_mqtt', 'close',
                       'mqtt', 'debug', 'logger', 'mqtt_list'
                       ]

    def __init__(self, mqttc=None, instName="tester", debug=False):
        breakpoint()
        self.cmd = ''
        self.debug = debug
        self.mqtt = mqtt_deviceattributes()
        self.instName = instName
        self.mqtt.instName = instName
        self.mqtt.gui = "labml_adjutancy.misc.gui.minisct"
        self.inst = sct8()
        self.startKeywords = dir(self.inst)

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

    def close(self):
        # self.del_hardware()                                #TODO: not working
        mqtt_deviceattributes.close(self)

    def get_sites_count(self):
        return 1

    def do_request(self, site_id: int, timeout: int) -> bool:
        return True

    def test_in_progress(self, site_id: int):
        self.log_info(f"Tester.test_in_progress({site_id})")

    def test_done(self, site_id: int, timeout: int):
        self.log_info(f"Tester.test_done({site_id})")

    def do_init_state(self, site_id: int):
        breakpoint()
        self.inst.init_hardware()
        self.startKeywords = self.inst.startKeywords if hasattr(self.inst, 'startKeywords') else dir(self.inst)
        for index in range(0, 8):  # create mqtt-cmds for channels 0..7
            for cmd in mqttcmds['commands']['CH'].values():
                self.mqtt.mqtt_all.append(f"CH{index}.{cmd[0]}")
        for cmd in mqttcmds['commands']['dps'].values():
            self.mqtt.mqtt_all.append(f"dps.{cmd[0]}")
        self.log_info(f"Tester.do_init_state({site_id})")

    def __getattribute__(self, attr):
        """Get attribute.

        """
        if (attr != "__class__" and attr != "knownAttributes" and attr not in self.knownAttributes):
            self.cmd += f'{attr}.'
            if attr in self.startKeywords:
                self.cmd = f'{attr}.'
            value = eval(f'self.inst.{self.cmd[:-1]}')
            if not(value is None or isinstance(value, (int, bool, float, complex, str, list, tuple, bytes, bytearray, set, dict))
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
    from labml_adjutancy.misc.mqtt_client import mqtt_init

    mqttc = mqtt_init(typ="instrument")
    mqttc.init("127.0.0.1", port=1883, message_client=None)

    tester = Tester(mqttc=mqttc)
    tester.do_init_state(1)
    breakpoint()
    # tester.CH0.drv.vdh = 4.5
    tester.CH0.connect("PBUS_F")
    tester.CH0.connect("ABUS0_F")
    tester.CH0.connect("ABUS0_S")
    tester.CH0.disconnect("ABUS0_S")

    tester.CH0.relay_status()

    tester.close()
    mqttc.close()
