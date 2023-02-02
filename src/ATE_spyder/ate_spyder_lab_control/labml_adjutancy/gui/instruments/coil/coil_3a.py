# -*- coding: utf-8 -*-
"""
coil_3a.

Created on Mon Jan  3 09:19:17 2022

TODO:
    Bug: no bugs known, but in work.....
"""

import sys
import qdarkstyle

# import numpy as np
import os
from PyQt5 import QtWidgets
from labml_adjutancy.gui.instruments.base_instrument import Gui as Guibase
from labml_adjutancy.gui.instruments.base_instrument import load_ui

__author__ = "Zlin526F"
__copyright__ = "Copyright 2020, Lab"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"
__version__ = "0.0.1"


class Gui(Guibase):
    """Template  Gui.

    inherited from base_instrument
       status

    """

    _states = {
        "connect": ["connect", "color: rgb(0, 255, 0)"],  # overwrite the definitions in base_instrument
        "disconnect": ["disconnect", "color: rgb(255, 0, 0)"],
        "on": ["running", "color: rgb(0, 255, 0)"],
        "off": ["waiting for start...", "color: palette(HighlightedText)"],
    }

    def __init__(self, parent=None, name="scope", parentwindow=None, channel=None):
        super().__init__(grandparent=parent, name=name, parentwindow=parentwindow)
        self.myframe = load_ui(self.gui.myframe, __file__)
        # bgcolor = self.gui.palette().color(QtGui.QPalette.Background).name()    # getRgb()
        self.myadjustUI()
        self.gui.closeEvent = self.close
        self.parent = parent
        self.mqtt_initlist = [""]
        self.smustatus = ""

    def myadjustUI(self):
        # set icons:
        self.gui.runToolBar.setVisible(False)
        # self.add_menuicon('onoff')                              # add existing icon and connection from the base-instrument

        # set connection fom Gui-object to functions:
        # self.myframe.Dsamples.valueChanged.connect(self.rangeSamples)
        # self.myframe.Echname.editingFinished.connect(self.editchname)
        self.myframe.sweep.stateChanged.connect(lambda: self.sweep(self.myframe.sweep))  # QCheckBox
        self.myframe.mousePressEvent = self.mqttMeasureEvent

        self.mqttConnectWidgets()  # connect all widget which start with MQTT_

        self.sweep(self.myframe.sweep)
        geometry = self.gui.geometry()
        wh = self.myframe.geometry()
        self.gui.setWindowTitle(f' {os.path.basename(__file__).split(".")[0]}     (Version: {__version__})')
        self.myframe.setGeometry(geometry.x(), geometry.y(), wh.width() + 100, wh.height() + 250)

    def mqttMeasureEvent(self, event):
        self.grandparent.mqtt.publish_get(self.instName, "mField")
        self.grandparent.mqtt.publish_get(self.instName, "current")
        self.grandparent.mqtt.publish_get(self.instName, "voltage")

    # ======================================================
    # attributes which connect to an extern call (mqtt-command)
    def mqttreceive(self, instName, msg):
        """Common mqtt receive messages, get raw mqtt-Data for more information."""
        self.logger.debug(f"{instName}.mqttreceive: {msg} ")
        if super().mqttreceive(instName, msg):
            return
        # if you change a widget with the mqtt command, you have to use the widget.blockSignals(True/False)
        if "cmd" in tuple(msg.keys()) and "payload" in tuple(msg.keys()):
            if msg["cmd"] == "my attribute":  # special handling from mqtt commands
                value = msg["payload"]
                self.logger.info(f"{instName}: {msg['cmd']} should do something with value = {value} -> implement it")

            else:
                self.logger.warning(f"{instName} {msg['cmd']} not found -> do nothing")

    # ======================================================================================
    # definitions from complex mqtt commands, if you need only a connection between the mqtt-command and a widget, start the name of your widget with MQTT_

    # end extern calling attributes
    # ======================================================================================
    #
    # connected GUI-function to buttons or menues
    #
    def close(self, event=None):
        self.publish("off()")
        super().close()

    def sweep(self, b):
        if b.isChecked():
            self.myframe.Lfrom.show()
            self.myframe.Lto.show()
            self.myframe.Lpoints.show()
            self.myframe.Lstime.show()
            self.myframe.MQTT_points.show()
            self.myframe.MQTT_stime.show()
            self.myframe.MQTT_sweepto.show()
            self.myframe.PBsweep.show()
        else:
            self.myframe.Lfrom.hide()
            self.myframe.Lto.hide()
            self.myframe.Lpoints.hide()
            self.myframe.Lstime.hide()
            self.myframe.MQTT_points.hide()
            self.myframe.MQTT_stime.hide()
            self.myframe.MQTT_sweepto.hide()
            self.myframe.PBsweep.hide()

    @property
    def smustatus(self):
        return self._smustatus

    @smustatus.setter
    def smustatus(self, msg):
        if msg != "":
            print("Error: {}".format(msg))
        # self.gui.status.setText(self._translate("Form", "Current"))
        self.myframe.status.setText(msg)
        self._smustatus = msg


if __name__ == "__main__":
    # from pytestsharing.instruments.mqtt_client import mqtt_init

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
