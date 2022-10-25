# -*- coding: utf-8 -*-
"""
Created on Mon Jan  3 09:19:17 2022
@author: C. Jung

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

__author__ = "Christian Jung"
__copyright__ = "Copyright 2022, TDK Micronas"
__credits__ = ["Christan Jung"]
__email__ = "christian.jung@micronas.com"
__version__ = '0.0.1'


class Gui(Guibase):
    """Template  Gui.

    inherited from base_instrument
       status

    """

    _states = {
        "connect": ["connect", "color: rgb(0, 255, 0)"],                 # overwrite the definitions in base_instrument
        "disconnect": ["disconnect", "color: rgb(255, 0, 0)"],
        "on":  ["running", "color: rgb(0, 255, 0)"],
        "off":  ["waiting for start...", "color: palette(HighlightedText)"],
        }

    def __init__(self, parent=None, name='scope', channel=None):
        super().__init__(grandparent=parent, name=name)
        self.myframe = load_ui(self.gui.myframe, __file__)
        # bgcolor = self.gui.palette().color(QtGui.QPalette.Background).name()    # getRgb()
        self.myadjustUI()
        self.gui.closeEvent = self.close
        self.parent = parent
        self.mqtt_initlist = ['all attributes do you need. Widgets start with MQTT will add automaticaly']

    def myadjustUI(self):
        # set icons:
        self.gui.runToolBar.setVisible(False)
        # self.add_menuicon('onoff')                              # add existing icon and connection from the base-instrument

        # create and connect Menue entries
        #self.gui.actionexcel = self.add_menue("open registermaster in excel", self.openexcel, False)


        # set connection fom Gui-object to functions:
        #self.myframe.Dsamples.valueChanged.connect(self.rangeSamples)
        #self.myframe.Echname.editingFinished.connect(self.editchname)

        self.mqttConnectWidgets()                 # connect all widget which start with MQTT_

        geometry = self.gui.geometry()
        wh = self.myframe.geometry()
        self.gui.setWindowTitle(f' {os.path.basename(__file__).split(".")[0]}     (Version: {__version__})')
        self.myframe.setGeometry(geometry.x(), geometry.y(), wh.width()+100, wh.height()+250)

# ======================================================
# attributes which connect to an extern call (mqtt-command)
    def mqttreceive(self, instName, msg):
        """common mqtt receive messages, get raw mqtt-Data for more information
        """
        self.logger.debug(f"{instName}.mqttreceive: {msg} ")
        if super().mqttreceive(instName, msg):
            return
        # if you change a widget with the mqtt command, you have to use the widget.blockSignals(True/False)
        if 'cmd' in tuple(msg.keys()) and 'payload' in tuple(msg.keys()):
            if msg['cmd'] == 'my attribute':                                # special handling from mqtt commands
                value = msg['payload']
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
        self.publish('off()')
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
