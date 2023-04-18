# -*- coding: utf-8 -*-
"""
smu.

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
    """SMU  Gui.

    inherited from base_instrument
       status

    """

    _states = {
        "connect": ["connect", "color: rgb(0, 255, 0)"],  # overwrite the definitions in base_instrument
        "disconnect": ["disconnect", "color: rgb(255, 0, 0)"],
        "on": ["running", "color: rgb(0, 255, 0)"],
        "off": ["waiting for start...", "color: palette(HighlightedText)"],
    }

    _color_display_enable = "color: rgb(0, 255, 255);background-color: rgb(0, 0, 0);"
    _color_display_disable = "color: #d9d9d9;background-color: rgb(0, 0, 0);"

    def __init__(self, parent=None, name="scope", parentwindow=None, channel=None):
        super().__init__(grandparent=parent, name=name, parentwindow=parentwindow)
        self.myframe = load_ui(self.gui.myframe, __file__)
        # bgcolor = self.gui.palette().color(QtGui.QPalette.Background).name()    # getRgb()
        self.myadjustUI()
        self.gui.closeEvent = self.close
        self.parent = parent
        self.mqtt_initlist = [
            "output_function",
            "Voltage",
            "Current",
        ]  # all attributes do you need for the initialisation from mqtt. Widgets start with MQTT will add automaticaly'
        self.smustatus = ""
        # self.gui.myframe.setEnabled(True)

    def myadjustUI(self):
        # set icons:
        self.gui.runToolBar.setVisible(False)
        # self.add_menuicon('onoff')                              # add existing icon and connection from the base-instrument
        self.myframe.MQTT_SET_voltage.setKeyboardTracking(False)  # QDoubleSpinBox end input with return
        self.myframe.MQTT_i_clamp.setKeyboardTracking(False)
        self.myframe.MQTT_stime.setKeyboardTracking(False)
        self.myframe.MQTT_sweepto.setKeyboardTracking(False)

        # set connection fom Gui-object (widgets) to functions:
        self.myframe.sweep.stateChanged.connect(lambda: self.sweep(self.myframe.sweep))  # QCheckBox
        self.mqttConnectWidgets()  # connect all widget which the objectname start with MQTT

        # connect Gui-objects (widgets) to own ('complex') functions
        widget = self.myframe.output_function
        widget.activated.connect(lambda widget, obj=widget: self.gui2mqtt(obj))
        self._output_function = -1
        self.output_function = "DC_VOLTAGE"
        self.myframe.PBsweep.clicked.connect(self.gui2sweep)
        self.myframe.MQTT_sweepto.valueChanged.disconnect()

        # connect Gui-objects (widgets) with a mouse click to get a mqtt message
        self.myframe.mousePressEvent = self.mqttMeasureEvent

        self.sweep(self.myframe.sweep)
        geometry = self.gui.geometry()
        wh = self.myframe.geometry()
        self.gui.setWindowTitle(f' {os.path.basename(__file__).split(".")[0]}     (Version: {__version__})')
        self.myframe.setGeometry(geometry.x(), geometry.y(), wh.width() + 100, wh.height() + 250)

    def mqttMeasureEvent(self, event):
        self.grandparent.mqtt.publish_get(self.instName, "measure")
        self.grandparent.mqtt.publish_get(self.instName, "cmpl")

    # ======================================================
    # attributes which connect to an extern call (mqtt-command)
    def mqttreceive(self, instName, msg):
        """Common mqtt receive messages, get raw mqtt-Data for more information."""
        self.logger.debug(f"   {instName}.mqttreceive: {msg} ")
        if super().mqttreceive(instName, msg):
            return
        self.logger.debug(f"    {instName}.mqttreceive: continue search ... with {msg} ")
        # if you change with the mqtt command a widget, you have to use the widget.blockSignals(True/False)
        if "cmd" in tuple(msg.keys()) and "payload" in tuple(msg.keys()):
            value = msg["payload"]
            if msg["cmd"] == "measure":  # special handling from mqtt commands
                # self.myframe.MQTT_GET_current.blockSignals(True)
                self.myframe.MQTT_GET_voltage.setProperty("value", value[0])
                self.myframe.MQTT_GET_current.setProperty("value", value[1])
            elif msg["cmd"] == "Voltage":
                self.myframe.MQTT_SET_voltage.blockSignals(True)
                self.myframe.MQTT_SET_voltage.setProperty("value", value)
                self.myframe.MQTT_SET_voltage.blockSignals(False)
                # self.logger.info(f"   {instName}: {msg['cmd']} should do something with value = {value} -> implement it !!!!!!!!!!!!!!!!!")
            elif msg["cmd"] == "Current":
                self.myframe.MQTT_SET_current.blockSignals(True)
                self.myframe.MQTT_SET_current.setProperty("value", value)
                self.myframe.MQTT_SET_current.blockSignals(False)
            else:
                self.logger.warning(f"   {instName} {msg['cmd']} not found  -> do nothing")

    # ======================================================================================
    # definitions from 'complex' mqtt commands, if you need only a connection between the mqtt-command and a widget, start the name of your widget with MQTT_

    @property
    def channel(self):
        return self.id

    @channel.setter
    def channel(self, msg):
        self.id = msg

    @property
    def output_function(self):  # connect to QCombobox
        return self._output_function

    #        if self.gui.output_function.currentIndex() != self._output_function:
    #            self.publish_set(self.gui.output_function.currentText())

    @output_function.setter
    def output_function(self, val):
        if val.find("DC_VOLTAGE") == 0 and self._output_function != 0:
            self.myframe.MQTT_SET_voltage.show()
            self.myframe.MQTT_SET_current.hide()
            self.myframe.MQTT_v_range.show()
            self.myframe.MQTT_i_range.hide()
            self.myframe.MQTT_i_clamp.show()
            self.myframe.MQTT_v_clamp.hide()
            self.myframe.MQTT_I_range.show()
            self.myframe.MQTT_V_range.hide()
            self.myframe.Lfunction.setText("Voltage")
            self.myframe.Llimit.setText("Current")
            self.myframe.MQTT_SET_voltage.setSuffix(" V")
            self.myframe.MQTT_sweepto.setSuffix(" V")
            self.myframe.MQTT_i_clamp.setSuffix(" A")
            self.myframe.si1.setText("V")
            self.myframe.si2.setText("A")
            self._output_function = 0
            self.myframe.output_function.setCurrentIndex(0)
        elif val.find("DC_CURRENT") == 0 and self._output_function != 1:
            self.myframe.MQTT_SET_voltage.hide()
            self.myframe.MQTT_SET_current.show()
            self.myframe.MQTT_v_range.hide()
            self.myframe.MQTT_i_range.show()
            self.myframe.MQTT_i_clamp.hide()
            self.myframe.MQTT_v_clamp.show()
            self.myframe.MQTT_I_range.hide()
            self.myframe.MQTT_V_range.show()
            self.myframe.Lfunction.setText("Current")
            self.myframe.Llimit.setText("Voltage")
            self.myframe.MQTT_SET_current.setSuffix(" A")
            self.myframe.MQTT_sweepto.setSuffix(" A")
            self.myframe.MQTT_v_clamp.setSuffix(" V")
            self.myframe.si1.setText("V")
            self.myframe.si2.setText("A")
            self._output_function = 1
            self.myframe.output_function.setCurrentIndex(1)
        self.sweep(self.myframe.sweep)

    @property
    def cmpl(self):
        pass

    @cmpl.setter
    def cmpl(self, val):
        if self._output_function == 0 and val:
            self.myframe.Lcmpl.setStyleSheet(self._color_display_enable)
            self.myframe.Lcc.setStyleSheet(self._color_display_enable)
            self.myframe.Lcv.setStyleSheet(self._color_display_disable)
        elif self._output_function == 1 and val:
            self.myframe.Lcmpl.setStyleSheet(self._color_display_enable)
            self.myframe.Lcc.setStyleSheet(self._color_display_disable)
            self.myframe.Lcv.setStyleSheet(self._color_display_enable)
        else:
            self.myframe.Lcmpl.setStyleSheet(self._color_display_disable)
            self.myframe.Lcc.setStyleSheet(self._color_display_disable)
            self.myframe.Lcv.setStyleSheet(self._color_display_disable)

    # end extern calling attributes (mqtt)
    # ======================================================================================
    #
    # connected GUI-function to buttons or menues
    #
    def gui2sweep(self):
        if self._output_function == 0:
            self.publish("voltage", [self.myframe.MQTT_SET_voltage.value(), self.myframe.MQTT_sweepto.value()])
        elif self._output_function == 1:
            self.publish("current", [self.myframe.MQTT_SET_current.value(), self.myframe.MQTT_sweepto.value()])

    def close(self, event=None):
        self.publish("off()")
        super().close()

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

    def sweep(self, b):
        if b.isChecked():
            self.myframe.Lfrom.show()
            self.myframe.Lto.show()
            self.myframe.MQTT_SET_voltage.blockSignals(True)
            self.myframe.MQTT_SET_current.blockSignals(True)
            self.myframe.MQTT_sweepto.show()
            self.myframe.Ltime.show()
            self.myframe.MQTT_stime.show()
            self.myframe.PBsweep.show()
        else:
            self.myframe.Lfrom.hide()
            self.myframe.Lto.hide()
            self.myframe.MQTT_SET_voltage.blockSignals(False)
            self.myframe.MQTT_SET_current.blockSignals(False)
            self.myframe.MQTT_sweepto.hide()
            self.myframe.Ltime.hide()
            self.myframe.MQTT_stime.hide()
            self.myframe.PBsweep.hide()


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
