# -*- coding: utf-8 -*-
"""
softscope.

Created on Wed April 21 13:43:20 2021
@author: C. Jung

TODO:
    Bug: no bugs known, but in work.....
"""

import sys
import qdarkstyle

# import numpy as np
import os
from PyQt5 import QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot
from labml_adjutancy.gui.instruments.base_instrument import Gui as Guibase
from labml_adjutancy.gui.instruments.base_instrument import load_ui
import time

__author__ = "Christian Jung"
__copyright__ = "Copyright 2022, TDK Micronas"
__credits__ = ["Christan Jung"]
__email__ = "christian.jung@micronas.com"
__version__ = "0.0.8"


class Scope(FigureCanvas):
    sampleSteps = 100

    def __init__(self, gui, frame=None, width=5, height=5, dpi=100, min_y=None, max_y=None, bgcolor=None):
        self.gui = gui
        self.frame = frame
        self._min_y = min_y if min_y is not None else 0
        self._max_y = max_y if max_y is not None else 5
        self.x_value = [0]
        self.y = [0]
        self.samples = 0
        self._max_x = 100
        self.data = []
        self.first = 0
        self.samplesperframe = 1
        fig = pyplot.figure(figsize=(width, height), dpi=dpi, facecolor=bgcolor)
        FigureCanvas.__init__(self, fig)
        self.setParent(frame.scope)
        self.ax = pyplot.axes(xlim=(0, self.max_x), ylim=(self.min_y, self.max_y))
        self.ax.tick_params(colors="white", which="both")
        self.ax.xaxis.label.set_color("white")
        self.ax.yaxis.label.set_color("white")
        self.ax.grid()
        self.ax.set_xlabel("samples")  # time (s)
        (self.line,) = self.ax.plot([], [], lw=2)
        self.onoff = 0
        self.oldtime = time.time()

    def newdata(self, y):
        timedelta = time.time() - self.oldtime
        self.samplerate = timedelta
        self.oldtime = time.time()
        y_average = 0
        y_average = y + y_average
        # x=time()
        self.samples += 1
        while self.x_value[-1] - self.x_value[0] > self.max_x:
            del self.x_value[0]
            del self.y[0]
        self.x_value.append(self.samples)
        self.y.append(y)
        self.data.append((self.samples, y))
        # calculate y-Axis label:
        self.min_y = y
        self.max_y = y
        self.line.set_data(self.x_value, self.y)
        # calculate x-Axis label:
        if self.first == 0 and self.x_value[-1] - self.x_value[0] == self.max_x:  # fill scope until max samples
            self.first = 1
        elif self.first == 1:  # max samples reached -> now scroll
            self.ax.set_xlim(self.x_value[0], self.x_value[-1])
            self.ax.figure.canvas.draw()
        if len(self.x_value) < self.max_x:
            self.setrange()
        y_average = y_average / self.samplesperframe
        self.value = y_average

    def setrange(self):
        tmin = self.min_y
        tmax = self.max_y
        diff = tmax - tmin
        if type(diff) == int and diff < 10:
            diff = 10
        self.ax.set_ylim(tmin - 0.1 * diff, tmax + 0.1 * diff)
        # ax.set_ylim(auto=True)
        self.ax.figure.canvas.draw()
        return

    def init(self):
        """initialization function."""
        self.line.set_data([], [])
        return (self.line,)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.gui.setLabel(self.frame.Lvalue, self._value)

    @property
    def samplerate(self):
        return self._samplerate

    @samplerate.setter
    def samplerate(self, value):
        if value != 0:
            self._samplerate = 1 / value
            self.gui.setLabel(self.frame.Lsamplerate, f"{self._samplerate:0.1f}", "/s")

    @property
    def max_x(self):
        """Maximum samples."""
        return self._max_x

    @max_x.setter
    def max_x(self, value):
        value = (value // self.sampleSteps) * self.sampleSteps
        if value < self._max_x:
            self._max_x = value
            self.clear()
        self.first = 0
        self._max_x = value
        self.ax.set_xlim(self.x_value[0], self.x_value[0] + value)
        self.ax.figure.canvas.draw()
        self.ax.relim()

    @property
    def min_y(self):
        if self._min_y is None:
            return 0
        return self._min_y

    @min_y.setter
    def min_y(self, value):
        if self._min_y is None or self.min_y > value:
            self._min_y = value
            self.gui.setLabel(self.frame.Lmin, self._min_y)

    @property
    def max_y(self):
        if self._max_y is None:
            return 0
        return self._max_y

    @max_y.setter
    def max_y(self, value):
        if self._max_y is None or self._max_y < value:
            self._max_y = value
            self.gui.setLabel(self.frame.Lmax, self._max_y)

    @property
    def samples(self):
        return self._samples

    @samples.setter
    def samples(self, value):
        self._samples = value
        self.gui.setLabel(self.frame.Lsamples, self._samples)

    def clear(self):
        self.samples = 0
        self.line.set_data([], [])
        self.x_value = [0]
        self.y = [self.y[-1]]
        self.data = []
        self._min_y = None
        self._max_y = None
        self.ax.set_xlim([0, self.max_x])

    def __del__(self):
        pass


class Gui(Guibase):
    """Softscope Gui.

    inherited from base_instrument
       status

    """

    _states = {
        "connect": ["connect", "color: rgb(0, 255, 0)"],  # overwrite the definitions in base_instrument
        "disconnect": ["disconnect", "color: rgb(255, 0, 0)"],
        "chFound": ["channel ok", "color: rgb(0, 255, 0)"],
        "chNotDef": ["no channel defined", "color: rgb(255, 0, 0)"],
        "chNotFound": ["channel name not found", "color: rgb(255, 0, 0)"],
        "on": ["running", "color: rgb(0, 255, 0)"],
        "off": ["waiting for start...", "color: palette(HighlightedText)"],
        "waitChannel": ["waiting for channel name", "color: rgb(255, 165, 0)"],
    }

    def __init__(self, parent=None, name="softscope", parentwindow=None, channel=None):
        super().__init__(grandparent=parent, name=name, parentwindow=parentwindow)
        self.myframe = load_ui(self.gui.myframe, __file__)
        bgcolor = self.gui.palette().color(QtGui.QPalette.Background).name()  # getRgb()
        self.scope = Scope(self, self.myframe, width=5, height=4, bgcolor=bgcolor)  # 8,4
        self.scope.move(5, 5)
        self.myadjustUI()
        self.gui.closeEvent = self.close
        self._scopeChannel = None
        self.parent = parent
        # self.mqtt_initlist = ['all attributes do you need, widgets start with MQTT will add automaticaly']

    def myadjustUI(self):
        # set icons:
        self.add_menuicon("onoff")  # add existing icon and connection from the base-instrument
        self.add_menuicon("clear", connect=self.scope.clear)

        # set connection fom Gui-object to functions:
        self.myframe.Dsamples.valueChanged.connect(self.rangeSamples)
        self.myframe.Echname.editingFinished.connect(self.editchname)

        self.mqttConnectWidgets()  # connect all widget which start with MQTT_

        geometry = self.gui.geometry()
        wh = self.myframe.geometry()
        self.gui.setWindowTitle(f' {os.path.basename(__file__).split(".")[0]}     (Version: {__version__})')
        self.myframe.setGeometry(geometry.x(), geometry.y(), wh.width() + 100, wh.height() + 250)

    # ======================================================
    # attributes which connect to an extern call (mqtt-command)
    def mqttreceive(self, instName, msg):
        """common mqtt receive messages, get raw mqtt-Data for more information"""
        self.logger.debug(f"    {self.instName}.mqttreceive:   {instName}: {msg} ")
        if super().mqttreceive(instName, msg):
            return
        if "cmd" in tuple(msg.keys()) and "payload" in tuple(msg.keys()):
            if msg["cmd"] == self._scopeChannel:
                value = msg["payload"]
                if self.myframe.CBfilter.currentText().find("Integer") == 0:
                    n = int(self.myframe.CBfilter.currentText().split(" ")[1])
                    if value > 2 ** (n - 1):
                        value = -(~value + 2**n + 1)
                self.scope.newdata(value)
            else:
                self.logger.debug(f"   softscope {msg['cmd']} != {self._scopeChannel} -> not for me, do nothing")

    @property
    def scopeChannel(self):
        return self._scopeChannel

    @scopeChannel.setter
    def scopeChannel(self, value):
        value = self.filtersubtopic(value)
        self.logger.debug(f"get scopeChannel = {value},  subtopic = {self.topinstname}.{self.subtopic}, ")
        if value == 0:
            return
        msg = "chNotFound" if value == "ERROR" else "chFound"
        channel = value[value.find(".") + 1 :]
        channel = channel[:-2] if channel[-1] == ")" else channel
        self.logger.debug(f"set channel = {channel} -->")
        self._scopeChannel = channel
        self.status = msg
        self._onoff_ = 0

    # end extern calling attributes
    # ======================================================================================
    #
    # connected GUI-function to buttons or menues
    #

    def rangeSamples(self):
        self.scope.max_x = self.myframe.Dsamples.value()
        self.myframe.QLsamples.setText(f"{self.scope.max_x} Samples")

    def editchname(self):
        channel = self.myframe.Echname.text()
        self._scopeChannel = None
        self._onoff_ = None
        channel = self.filtersubtopic(channel)
        if channel != "":
            self.status = "disconnect"
            self.subtopic = channel
            self.publish("setchannel()", channel)
        else:
            self.status = "chNotDef"

    def close(self, event=None):
        self.publish("off()")
        self.subtopic = []
        super().close()


if __name__ == "__main__":
    # from labml_adjutancy.misc.mqtt_client import mqtt_init

    # broker = 127.0.0.1'
    # message_client = 'ate/DT1604092/matrix'
    # mqttclient = mqtt_init()                                                 # prepare mqtt
    # mqttclient.init(None, message_client=message_client.split('/')[0])    # mqtt client connect to broker
    # mqttclient.init()

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = Gui(app)
    app.exec_()
    # window.scope.anim.event_source.stop()
