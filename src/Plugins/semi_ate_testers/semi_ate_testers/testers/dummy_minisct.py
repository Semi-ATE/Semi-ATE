"""Dummy Interface for the miniSCT.

:Date: |today|

"""
from enum import Enum
from semi_ate_testers.testers.tester_interface import TesterInterface
from labml_adjutancy.misc.mqtt_client import mqtt_deviceattributes
from labml_adjutancy.misc.attributes import create_attributes
from labml_adjutancy.gui.instruments.minisct.minisct import mqttcmds

__author__ = "Zlin526F"
__copyright__ = "Copyright 2020, Lab"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"
__version__ = 0.1


class DummyMiniSCT(TesterInterface, create_attributes, mqtt_deviceattributes):
    """
    Dummy Tester for the miniSCT.

    :Date: |today|

    #    .. image:: ../_static/??.jpg

    """
    SITE_COUNT = 1
    gui = "labml_adjutancy.gui.instruments.minisct.minisct"

    class Force_state(Enum):
        """Enum for force state."""

        FORCE_Z = 0
        FORCE_D = 1
        FORCE_U = 2

    class Termination(Enum):
        """Enum for Termination state."""

        TERMINATION_OFF = 0
        TERMINATION_ON = 1

    class Mux_out(Enum):
        """Enum for comparator mux_out."""

        CA = 0
        CB = 1
        CACB = 2

    class R_load(Enum):
        """Enum for passive load resistance."""

        R_140 = 140
        R_151 = 151
        R_165 = 165
        R_207 = 207
        R_240 = 240
        R_290 = 290
        R_540 = 540
        R_1000 = 1000

    class I_range(Enum):
        """Enum for current range."""

        I_RANGE20uA = 1
        I_RANGE200uA = 2
        I_RANGE2mA = 3
        I_RANGE20mA = 4
        I_RANGE200mA = 5

    class V_range(Enum):
        """Enum for voltage range."""

        V_RANGE_3V = 1
        I_RANGE_22V = 2

    class V_lpf(Enum):
        """Enum for Voltage LPF filter."""

        V_LPF_ON = 1
        V_LPF_OFF = 0

    class I_lpf(Enum):
        """Enum for Current LPF filter."""

        I_LPF_ON = 1
        I_LPF_OFF = 0

    class Compensation(Enum):
        """Enum for current range."""

        CMPS_ON = 1
        CMPS_OFF = 0

    def __init__(self, logger=None, mqttc=None, instName="tester"):
        """Initialise.

        Args:
           instName (string):
              Instance Name from parent.

        Examples
        --------
           >>> # Initialization
           >>> tester = DummyMiniSCT()

        more detailed examples:
           not yet...

        """
        self.logger = logger
        self.mqttc = mqttc
        self.instName = instName

    def init_hardware(self):
        """Initialise the 'hardware'."""
        self.gui = "labml_adjutancy.gui.instruments.minisct.minisct"
        mqtt_deviceattributes.__init__(self)
        if self.mqttc is not None:
            self.mqtt_add(self.mqttc, self)
        create_attributes.__init__(self)
        self.inst = DummyInst(self, **{"message": "Use Dummy MiniSCT !"})
        self.setup_inst()
        # self.mqtt_all = list(self._properties_ch.keys())  # approved commands for mqtt
        self.setdefault()

    def setup_inst(self):
        """Set some instrument settings."""
        properties_ch = {}
        for mqttcmd in mqttcmds["commands"]["CH"]:  # create the proberties for the channels from mqttcmd
            if mqttcmd.find("None") < 0:
                cmd = mqttcmds["commands"]["CH"][mqttcmd][0]
                properties_ch[cmd] = ((cmd, cmd), mqttcmds["commands"]["CH"][mqttcmd][1], None)
        for index in range(0, 1):  # create channels 0..7
            # childname = f"ch({index})"     # not running yet :-(
            childname = f"CH{index}"
            self.createattributes(properties_ch, child=f"CH{index}", childname=childname)
            for key in list(properties_ch.keys()):
                self.mqtt_all.append(f"{childname}.{key}")
            # connect(lambda widget, obj=widget: self.gui2mqtt(obj))
            # getattr(self, f"CH{index}").connect = (lambda switch: self.connect(switch, lambda index: index))
            getattr(self, f"CH{index}").connect = (lambda switch: self.connect(switch, index))
            getattr(self, f"CH{index}").disconnect = (lambda switch: self.disconnect(switch, index))
            getattr(self, f"CH{index}")._saturn = DummySaturn(self)
            self.mqtt_enable = True

        properties_dps = {}
        for mqttcmd in mqttcmds["commands"]["dps"]:     # create the proberties for the dps from mqttcmd
            cmd = mqttcmds["commands"]["dps"][mqttcmd][0]
            properties_dps[cmd] = ((cmd, cmd), mqttcmds["commands"]["dps"][mqttcmd][1], None)
        self.createattributes(properties_dps, child="dps")
        self.__is_initialized = True

        self.startKeywords = dir(self)
        self.startKeywords.remove("connect")
        self.startKeywords.remove("disconnect")

    def setup_mqtt(self, mqttc):
        self.mqtt_add(mqttc, self)  # subscribe for mqtt and send information about the gui
        self.mqttc = mqttc

    def ch(self, index):
        return getattr(self, f"ch{index}")

    def setdefault(self):
        """Set for default values."""
        self.log_measure("{} set default values".format(self.instName))

    def reset(self):
        """Reset the instrument."""
        pass

    def message(self, message=None):
        """Message display to Python console."""
        if message is not None:
            self.log_info(message)

    def connect(self, switch, index):
        self.publish_get(f"CH{index}.connect()", switch)

    def disconnect(self, switch, index):
        self.publish_get(f"CH{index}.disconnect()", switch)

    @property
    def Die_Rev(self):
        return(f'MiniSCT dummy Die_Rev V{__version__}')

    @property
    def Product_ID(self):
        return(f'MiniSCT dummy Product_ID V{__version__}')

    @property
    def id(self):
        """Query IDN."""
        value = self.inst.query("*IDN?")
        return value.replace("\r", "").replace("\n", "")

    def get_id(self):
        """
        Get identifikation from MinSCT.

        Returns
        -------
            string: identifikation.
        """
        self.inst.write("*IDN?")
        return self.inst.read()

    def close(self):
        if self.mqttc is not None:
            self.mqtt_disconnect()

    # functions for the plugin:
    def do_request(self, site_id: int, timeout: int) -> bool:
        return True

    def test_in_progress(self, site_id: int):
        self.log_info(f"{__class__.__name__}.test_in_progress({site_id})")

    def test_done(self, site_id: int, timeout: int):
        self.log_info(f"{__class__.__name__}.test_done({site_id})")

    def do_init_state(self, site_id: int):
        self.log_info(f"{__class__.__name__}.do_init_state({site_id}) running")
        self.init_hardware()


class DummySaturn():
    def __init__(self, parent):
        self.parent = parent

    @property
    def Die_Rev(self):
        return(f'MiniSCT dummy V{__version__}')

    @property
    def Product_ID(self):
        return(f'MiniSCT dummy V{__version__}')


class DummyInst(object):
    """Dummy object  for the miniSCT instance.

    :Date: |today|

    Usable if you have no real miniSCT as instance

    """

    def __init__(self, parent, **kwargs):
        """Initialise."""
        if "message" in kwargs:
            print(kwargs["message"])
        else:
            print("Use Dummy MiniSCT")
        self._lastcmd = ""

    def query(self, cmd):
        if cmd == "*IDN?":
            return f"{self.__class__}\r"
        cmd = cmd[: cmd.find("?")]
        try:
            value = super(__class__, self).__getattribute__(cmd)
            try:
                value = int(value)
            except Exception:
                pass
            print(f"Dummy miniSCT query {cmd} == {value}")
        except Exception:
            value = 0xDEADBEEF
            print(f"Dummy miniSCT query {cmd} == {hex(value)}")
        return value

    def write(self, cmd):
        self._lastcmd = cmd[: cmd.find("?")] if cmd.find("?") > -1 else ""
        cmd = cmd.split(" ")
        if len(cmd) > 1:
            object.__setattr__(self, cmd[0], cmd[1])
        print(f"Dummy miniSCT write {cmd}")

    def read(self):
        value = 0xDEADBEEF
        print("Dummy miniSCT read 0x{hex(value)}")
        return value

    def flush(self, arg=None):
        pass


if __name__ == "__main__":
    from labml_adjutancy.misc.mqtt_client import mqtt_init
    from labml_adjutancy.misc.mqtt_client import mylogger

    logger = mylogger(enable=True)

    mqttc = mqtt_init(typ="instrument")
    mqttc.init("127.0.0.1", port=1883, message_client=None)

    tester = DummyMiniSCT(logger)
    tester.do_init_state(1)
    tester.setup_mqtt(mqttc)

    tester.CH0.drv.vdh = 4.4
    tester.CH0.connect("PBUS_F")
    tester.CH0.disconnect("PBUS_F")

    tester.close()
    mqttc.close()
