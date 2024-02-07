# -*- coding: utf-8 -*-
"""

Created on Thu Jan  7 17:18:03 2021

@author: ZLin526F


"""
import inspect
from ate_test_app.sequencers.MqttClient import MqttClient
from ate_common.logger import LogLevel
from labml_adjutancy.misc.mqtt_client import mqtt_deviceattributes, mqtt_init
from labml_adjutancy.misc.common import color
from labml_adjutancy.misc.softscope import Softscope

__author__ = "Zlin526F"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"
__version__ = "0.0.6"


mqttc = None


class ShortName(object):
    def __init__(self, topinstname):
        self.topinstname = topinstname
        # self._initdic = tuple(self.__class__.__dict__)
        self._initdic = dir(self)

    def setattr(self, name, value):
        if name in self._initdic:
            self.logger("WARNING: can't use name '{name}' for a Shortname\n Change the name")
        object.__setattr__(self, name, value)

    @property
    def names(self):
        mynames = []
        mydic = dir(self)
        for name in mydic:
            if name not in self._initdic and name != "_initdic":
                mynames.append(name)
        return mynames


class LabCtrl(mqtt_deviceattributes):
    """
    Class for the Communication with the Spyder PluginLab Control.

    Provide workaround 'breakpoint' for using Spyder with semi-ATE
    provide START TESTBENCH$ for semi-cntrl

    """

    parameter = {"SemiCtrl.Control": ["Log level"]}

    command = {
        "menu": {"type": "cmd", "command": "menu", "payload": None},
        "gui": {"type": "cmd", "command": "create", "instname": None, "lib": None},
        "reset": {"type": "cmd", "command": "reset", "sites": ["0"]},
        "terminate": {"type": "cmd", "command": "terminate", "sites": ["0"]},
    }
    default_topinstname = "env"  # better will be labml or tester?

    def __init__(self, logger=None):
        """Initialise."""
        global mqttc

        super().__init__()
        self.logger = logger
        self.instName = "semictrl"
        self.parent = None
        mqttc = mqtt_init(typ="instrument")
        mqttc.init(broker="127.0.0.1", port=1883, message_client=None, username="", userpasswd="",
                   qos=0, retain=False)     # TODO: or use access with self.logger.stream_handler.mqtt ?
        self.mqtt_add(mqttc, self)
        self.mqttc = mqttc
        self._sbreakpoint = False
        self.mqtt_list = ["_breakpoint"]
        self.softscope = Softscope(mqttc, logger, "softscope")
        logger.debug = self.log_debug
        logger.measure = self.log_measure
        logger.info = self.log_info
        logger.warning = self.log_warning
        logger.error = self.log_error
        self.logger.debug(f"{self.instName}.__init__ done")
        self.publish("breakpoint", None)
        self.logger.info(f"{self.instName} initialized")

    def init(self, parent):
        """Init the semictrl plugin."""
        if self.parent is None:
            if self.loglevel != "":
                self.logger.set_logger_level(LogLevel[self.loglevel])
            self.parent = parent
            self.publish("topinstname", self.topinstname)
            self._setShortInstances()
            self.setShortNames(parent)
            if hasattr(parent.context, 'tester') and hasattr(parent.context.tester, "setup_mqtt"):
                parent.context.tester.setup_mqtt(self.mqttc)  # create mqtt-messages for the tester
            # workaround for breakpoints:
            if self._breakpoint:
                self.publish("breakpoint", "hold")
                print(color("b_red", "Hold on the default breakpoint"))
                print(color("b_red", "This is a workaround, otherwise your breapoints doesn't working"))
                print(color("b_red", "To continue: Click in Spyder 'continue execution' "))
                breakpoint()
                self.publish("breakpoint", "testing")
            # end workaround breakpoint
        else:
            self.setShortNames(parent)

    def setShortNames(self, parent=None):
        """Init semi-ctrl."""
        if self.parent == "close":
            self.logger.error(f"{self.instName} already closed, do nothing")
        else:
            for name in self.topinstance.names:
                if name not in dir(parent):
                    parent.__setattr__(name, object.__getattribute__(self.topinstance, name))
        if hasattr(self.parent, 'setup'):
            self.parent.setup.testbench_name = parent.__class__.__name__

    def _setShortInstances(self):
        parent = self.parent.context
        for instancename in dir(parent):
            pos = instancename.find("_instance")
            if pos < 0:
                continue
            shortname = instancename[:pos].lower() if instancename != "LABML_Instruments_instance" else self.default_topinstname
            pos = shortname.find("_")
            shortname = shortname[pos + 1:] if pos > -1 else shortname
            instrument = getattr(parent, instancename)
            if hasattr(instrument, "instName"):
                shortname = instrument.instName
            self.topinstance.setattr(shortname, instrument)
        self.topinstance.setattr("logger", self.logger)
        self.topinstance.setattr("softscope", self.softscope)
        if hasattr(self.topinstance, self.default_topinstname):
            self.labmlNames()
        self.log_debug(f"set shortnames: {self.topinstance}")

    def labmlNames(self):
        parent = getattr(self.topinstance, self.default_topinstname).instruments
        for instrument in dir(parent):  # add information from each instrument to result.instruments
            if instrument.find("_") != -1:
                continue
            instrument = getattr(parent, instrument)
            if not inspect.isclass(instrument):  # filter out the class-definitions
                if hasattr(instrument, "instName"):
                    self.topinstance.setattr(instrument.instName, instrument)

    def _setData(self, data):
        # data = ['Log level']
        parameter = self.parameter["SemiCtrl.Control"]
        self.log_debug(f"{self.__class__.__name__}: Set Parameter to {data}")
        print(f"{self.__class__.__name__}: Set Parameter to {data}")
        object.__setattr__(self, self.default_topinstname, ShortName(self.default_topinstname))
        self.topinstance = object.__getattribute__(self, self.default_topinstname)
        self.topinstname = self.default_topinstname
        self.softscope.init(self.topinstance)
        self.loglevel = data[parameter[0]] if parameter[0] in data and data[parameter[0]] in dir(LogLevel) else ""
        if self.loglevel != "":
            self.logger.set_logger_level(LogLevel[self.loglevel])
        elif self.loglevel == "" and parameter[0] in data:
            self.log_error(f"couln't set loglevel = {data[parameter[0]]}")

    def close(self):
        if self.parent == "close":
            return
        self.logger.log_message(LogLevel.Debug(), f"try to close: {self.topinstance.names}")
        for instName in self.topinstance.names:  # close all instruments
            if instName == "semictrl":
                continue
            instrument = getattr(self.topinstance, instName)
            try:
                instrument.close()
                delattr(self.topinstance, instName)
            except Exception:
                pass
        self.mqtt_disconnect()
        if hasattr(self, 'mqttc'):
            self.mqttc.close()
        self.parent = "close"
        self.log_info("semictrl closed")

    def __repr__(self):
        return f"{self.__class__}"

    def get(self):
        """Get the handler."""
        return self

    @property
    def _breakpoint(self):
        return self._sbreakpoint

    @_breakpoint.setter
    def _breakpoint(self, value):
        print(f"set breakpoint :={value}")
        self._sbreakpoint = value

    def log_debug(self, message: str):
        """Send the message with loglevel=debug to the logger."""
        self.logger.log_message(LogLevel.Debug(), message)

    def log_measure(self, message: str):
        """Send the message with loglevel=measure to the logger."""
        self.logger.log_message(LogLevel.Measure(), message)

    def log_info(self, message: str):
        """Send the message with loglevel=info to the logger."""
        self.logger.log_message(LogLevel.Info(), message)

    def log_warning(self, message: str):
        """Send the message with loglevel=warning to the logger."""
        self.logger.log_message(LogLevel.Warning(), message)

    def log_error(self, message: str):
        """Send the message with loglevel=error to the logger."""
        self.logger.log_message(LogLevel.Error(), message)

    # --------------
    def do_import(self):
        """Only empty dummy function."""
        print(f"{self.__class__.__name__}: do_import only dummy function")
        return False

    def do_export(self):
        """Only empty dummy function."""
        print(f"{self.__class__.__name__}:: do_export only dummy function")
        return False

    def get_abort_reason(self):
        """Only empty dummy function."""
        print("Semi.Ctrl: get_abort_reason only dummy function")
        return "f'{self.__class__.__name__}: Error, I don't know why"

    def set_mqtt_client(self, mqtt: MqttClient):
        self.mqtt = mqtt

    def set_configuration_values(self, data):
        """Only empty dummy function."""
        print(f"{self.__class__.__name__}: set_configuration_values only dummy function")
        pass

    def apply_configuration(self, data):
        """Everthing should be ok."""
        self._setData(data)
        # self.sbreakpoint(self)  # this doesn't work, you have to call this function once in a test :-(
