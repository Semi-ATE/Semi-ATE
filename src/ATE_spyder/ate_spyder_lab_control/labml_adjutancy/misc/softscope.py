# -*- coding: utf-8 -*-
"""
Created on Thu Jan  7 17:18:03 2021

@author: jung
"""
from ate_common.logger import LogLevel
from labml_adjutancy.misc.mqtt_client import mqtt_deviceattributes
from labml_adjutancy.misc import common
from time import time
from threading import Timer

__author__ = "Zlin526F"
__copyright__ = "Copyright 2021, Lab"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"


class Softscope(mqtt_deviceattributes):
    """
    Class for the communication with the softcope-GUI.

    via mqtt some command controlled the sending of data:
        start:
            create a Timer-thread with the loop-time = sampleTime
        stop:
            stop the Timer-thread
        setchannel(value):
            call the value as attribute for each timing event
        sampleTime:
            loop time

    TODO: very simple.....
            max sample Time ~50Hz

    """

    def __init__(self, mqttc, logger, instName="softscope"):
        """Initialise."""
        self.instName = instName
        self.logger = logger
        super().__init__()
        self.gui = "labml_adjutancy.gui.instruments.softscope.softscope"  # semi-ctrl use this lib for the scope gui
        self.mqtt_all = ["setchannel()", "on()", "off()", "sampleTime", "test"]  # approved commands for mqtt
        if mqttc is not None:
            self.mqtt_add(mqttc, self)  # subscribe for mqtt and send information about the gui
        self.scopeChannel = None
        self._samplethread = None
        self.sampleTime = 1.0
        self._minSampleTime = 0.01
        self._sawtooth = 0
        self.topinstname = None
        self.busy = False

    def init(self, topinstname):
        self.topinstname = topinstname

    def setchannel(self, value):
        """set the scopeChannel via mqtt"""
        result = common.strcall(self.topinstname, value, "set")
        self.scopeChannel = value if result != "ERROR" else "ERROR"
        self.publish_set("scopeChannel", self.scopeChannel)

    def on(self):
        if self.busy:
            self.off()
        if self.scopeChannel is None:
            self.logger.log_message(LogLevel.Error(), f"{self.instName} scopeChannel not defined")
            return
        self.busy = True
        self._newsample()

    def off(self):
        self.busy = False
        if self._samplethread is not None:
            self._samplethread.cancel()

    @property
    def sampleTime(self):
        return self._sampleTime

    @sampleTime.setter
    def sampleTime(self, value):
        if type(value) not in [int, float]:
            return
        self._sampleTime = value

    def close(self):
        self.off()
        self.mqtt_disconnect()

    def _newsample(self):
        if not self.busy:
            return
        starttime = time()
        # print(f'_newsample: {self.topinstname}, {self.scopeChannel}')
        result = common.strcall(self.topinstname, self.scopeChannel, typ="func")
        if result == "ERROR":
            self.logger.log_message(LogLevel.Error(), f"{self.instName} get ERROR from {self.scopeChannel}  -->stop sampling")
            return
        # print(result)
        mytime = self._sampleTime - (time() - starttime)
        if mytime <= 0:
            mytime = self._minSampleTime
        self._samplethread = Timer(mytime, self._newsample)
        self._samplethread.start()

    @property
    def test(self):
        # print(f'call scope.sawtooth value= {self._sawtooth}')
        self._sawtooth += 1
        if self._sawtooth > 256:
            self._sawtooth = 0
        return self._sawtooth

    def __repr__(self):
        return f"{self.__class__}"


if __name__ == "__main__":
    from labml_adjutancy.misc.mqtt_client import mylogger

    scope = Softscope(mqttc=None, logger=mylogger, instName="softscope")
