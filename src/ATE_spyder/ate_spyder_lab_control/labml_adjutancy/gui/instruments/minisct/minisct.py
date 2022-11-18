# -*- coding: utf-8 -*-
"""
miniSCT.

Created on Mon Jan  3 09:19:17 2022
@author: C. Jung

TODO:
    Bug: no bugs known, but in work.....
"""

import sys
import qdarkstyle
import os
from PyQt5 import QtWidgets  # QtCore, QtGui
from labml_adjutancy.gui.instruments.base_instrument import Gui as Guibase
from labml_adjutancy.gui.instruments.base_instrument import load_ui

# from SCT8.gui.miniSCT import _properties_ch as proberties

__author__ = "Christian Jung"
__copyright__ = "Copyright 2022, TDK Micronas"
__credits__ = ["Christan Jung"]
__email__ = "christian.jung@tdk.com"
__version__ = "0.0.3"

# TODO:  in docu ch(0) but in python CH(0)
#       "PE_F",   drv.off/pmu.off    but how works the enable

mqttcmds = {
    "relais!": {
        # svg-name :  (None, value for connect/disconnect)
        "SPST.230": (None, "termination"),  # no command connect/disconnect   use cmp.cfg_dif(termination)   :-(
        "SPST.255": (None, "FS"),
        "SPST.323": (None, "PE_50BP"),
        # "SPDT": (None, "PE_F"),          # not yet implemented,  drv.off/pmu.off    but how works the enable
        "SPST.252": (None, "PE_S"),
        "SPST.77": (None, "PBUS_F"),
        "SPST.286": (None, "PBUS_S"),
        "SPST.72": (None, "ABUS0_F"),
        "SPST.281": (None, "ABUS0_S"),
        "SPST.67": (None, "ABUS1_F"),
        "SPST.276": (None, "ABUS1_S"),
        "SPST.62": (None, "CBUS_F"),
        "SPST.271": (None, "CBUS_S"),
        "SPST.44": (None, "GBUS_F"),
        "SPST.266": (None, "GBUS_S"),
        "SPST": (None, "DUT_F"),
        "SPST.227": (None, "DUT_S"),
    },
    "commands": {
        'CH': {
            # svg-name: (command for the MiniSCT, range)
            "relais!1": ("connect()", 1),                # relais!1 means: this command have to translate with the dictionary 'relais'
            "relais!2": ("disconnect()", 0),             # todo: do we need in LIne 157: self.mqtt_cmds.append(f"{svgfile}{channel}.{cmd.split('!')[0]}")
            # drv
#            "force_state": ("drv.force_state", "Force_state"),
#            "vdh": ("drv.vdh", [-2.0, 22.0]),
#            "vdl": ("drv.vdl", [-3.0, 18.0]),
#            "slew_pos": ("drv.slew_pos", [0.1, 1.0]),
#            "slew_neg": ("drv.slew_neg", [0.1, 1.0]),
            # cmp
#            "vch": ("cmp.vch", [-4.0, 18.0]),
#            "vcl": ("cmp.vcl", [-4.0, 18.0]),
#            "termination": ("cmp.termination", "Termination"),
#            "read_state": ("cmp.read_state", None),     # in docu get_state ?   -> ask
#            "mux": ("cmp.mux", "Mux_out"),              # cfg_cpu(mux_out , dig_level)   mux_out = CA, CB, CA|CB
            },
        'dps': {
#            "v_range": ("v_range", [-2.0, 2.0])         # not implemented yet
        }
    }
}


class Gui(Guibase):
    """MinSCT  Gui.

    inherited from base_instrument
       status
    """

    _states = {
        "connect": [
            "connect",
            "color: rgb(0, 255, 0)",
        ],  # overwrite the definitions in base_instrument
        "disconnect": ["disconnect", "color: rgb(255, 0, 0)"],
        "on": ["running", "color: rgb(0, 255, 0)"],
        "off": ["waiting for start...", "color: palette(HighlightedText)"],
    }

    _color_display_enable = (
        "color: rgb(0, 255, 255);background-color: rgb(0, 0, 0);"
    )
    _color_display_disable = "color: #d9d9d9;background-color: rgb(0, 0, 0);"

    _maxTabs = 9
    mqtt_cmds = []

    def __init__(
        self, parent, name="miniSCT", parentwindow=None, channel=None
    ):
        super().__init__(
            grandparent=parent, name=name, parentwindow=parentwindow
        )
        self.mydir = os.path.dirname(__file__) + os.sep
        self.myframe = load_ui(self.gui.myframe, self.mydir + "svg.ui")
        self.mqtt2svgelement = []
        # bgcolor = self.gui.palette().color(QtGui.QPalette.Background).name()    # getRgb()
        self.myadjustUI()
        self.gui.closeEvent = self.close
        self.parent = parent
        self.mqtt_initlist = (
            []
        )  # all attributes do you need for the initialisation from mqtt. Widgets start with MQTT will add automaticaly'
        # self.gui.myframe.setEnabled(True)

    def myadjustUI(self):
        # self.myframe.QTab.setMovable(True)
        # self.myframe.QTab.setTabsClosable(True)
        svgfiles = {"CH": ("sct8_v7_pdc", 2), "dps": ("sct8_v7_dps", 1)}
        self.chtabs = []
        dirname = os.path.dirname(__file__)
        for svgfile in svgfiles:
            for index in range(0, svgfiles[svgfile][1]):
                self.chtabs.append(QtWidgets.QWidget())
                tabname = (
                    f"{svgfile}({index})"
                    if svgfiles[svgfile][1] > 1
                    else svgfile
                )
                channel = index if svgfiles[svgfile][1] > 1 else None
                self.myframe.QTab.addTab(self.chtabs[-1], tabname)
                svgWidget = self.mqttConnectSVGWidget(
                    f"{dirname}/{svgfiles[svgfile][0]}.svg",
                    svgfile,
                    channel=channel,
                )

                svgWidget.setTextColor(
                    "#c00000"
                )  # find all Text elements with this color, listen to getattribute
                svgWidget.setclickableText()  # make the element clickable, now the element also listen to setattr

                svgWidget.setAllsvgElementsWTxt(
                    "SPST"
                )  # search for all elements which has an text item 'SPST'  -> this are the switches
                svgWidget.setElementSvg(
                    "SWITCH", f"{dirname}/sw0.svg", f"{dirname}/sw1.svg"
                )
                svgWidget.setclickableElement()  # make the elements cklickable
                svgWidget.setAllsvgElementsWTxt("SPDT")  # double-throw switch
                svgWidget.setTextColor("#00B050")

                for cmd in mqttcmds['commands'][svgfile].keys():    # Create a list with all mqtt-commands in self.mqtt_cmds
                    if channel is not None:                         # channels 0-7
                        if cmd.split("!")[0] in mqttcmds:
                            self.mqtt_cmds.append(f"{svgfile}{channel}.{cmd.split('!')[0]}!")
                            pass
                        else:
                            self.mqtt_cmds.append(f"{svgfile}{channel}.{cmd}")
                        self.mqtt2svgelement.append(f"{svgfile}{channel}.{mqttcmds['commands'][svgfile][cmd][0]}")
                    else:
                        self.mqtt2svgelement.append(f"{svgfile}.{mqttcmds['commands'][svgfile][cmd][0]}")
                        self.mqtt_cmds.append(f"{svgfile}.{mqttcmds['commands'][svgfile][cmd][0]}")

                if self.gui.geometry().height() < svgWidget.height():
                    self.gui.setGeometry(
                        self.gui.geometry().x() + 15,
                        self.gui.geometry().y() + 15,
                        self.gui.geometry().width(),
                        svgWidget.height() + 100,
                    )
                if self.gui.geometry().width() < svgWidget.width():
                    self.gui.setGeometry(
                        self.gui.geometry().x() + 15,
                        self.gui.geometry().y() + 15,
                        svgWidget.width() + 50,
                        self.gui.geometry().height(),
                    )
                layout = QtWidgets.QFormLayout()
                layout.addRow(svgWidget)
                self.chtabs[-1].setLayout(layout)
                # print(self.mqtt_cmds)
        # set icons:
        self.gui.runToolBar.setVisible(False)

        geometry = self.gui.geometry()
        wh = self.myframe.geometry()
        self.gui.setWindowTitle(
            f' {os.path.basename(__file__).split(".")[0]}     (Version: {__version__})'
        )
        self.myframe.setGeometry(
            geometry.x(), geometry.y(), wh.width() + 100, wh.height() + 250
        )
        self.gui.myframe.setEnabled(
            True
        )  # for test, normaly it should be disabled after start,

    # ======================================================
    # attributes which connect to an extern call (mqtt-command)
    def mqttreceive(self, instName, msg):
        """common mqtt receive messages, get raw mqtt-Data for more information"""
        check = True
        if "cmd" in tuple(msg.keys()) and msg["cmd"] in self.mqtt2svgelement:   # translate mqtt command to real svg-name
            oldcmd = msg["cmd"].split('.')
            msg["cmd"] = self.mqtt_cmds[self.mqtt2svgelement.index(msg["cmd"])]
            key = msg["cmd"].split('.')[-1]
            if key.find("!") > 0:
                key = key[:key.find("!")+1]
            if key in mqttcmds:         # is this a function? than another translate dictionary is available
                payload = msg["payload"] if type(msg["payload"]) == str else msg["payload"][0]
                index = [list(mqttcmds[key].values())[x][1] for x in range(0, len(mqttcmds[key].values()))].index(payload)
                msg["cmd"] = f"{msg['cmd'].split('.')[0]}.{list(mqttcmds[key])[index]}"
                for prefix in mqttcmds['commands'].keys():       # search for the translated values
                    if oldcmd[0].find(prefix) == 0:
                        for trcmd in mqttcmds['commands'][prefix]:
                            if trcmd.find(key) == 0 and mqttcmds['commands'][prefix][trcmd][0].find(oldcmd[-1]) == 0:
                                msg["payload"] = mqttcmds['commands'][prefix][trcmd][1]
                check = False
            if check:
                print(f"      for {key} not translation found  in = {msg['cmd']} ")   
            print(f'   {instName}.mqttreceive: translate to {msg}')
        if super().mqttreceive(instName, msg, check):
            ch = msg["cmd"].split(".")[0]
            print(f"   {instName}.mqttreceive: search for tab={ch}")
            for index in range(0, self._maxTabs):
                if self.myframe.QTab.tabText(index) == ch:
                    self.myframe.QTab.setCurrentIndex(index)
                    break
            return
        print(f"    {instName}.mqttreceive: continue search ... with {msg} ")

    # ======================================================================================
    # definitions from 'complex' mqtt commands, if you need only a connection between the mqtt-command and a widget,
    # begin the name of your widget with MQTT_

    @property
    def channel(self):
        return self.id

    @channel.setter
    def channel(self, msg):
        self.id = msg

    def svg2mqtt(self, name, value):
        """Overwrite from the base_instrument.svg2mqtt.

        translate svg-names to his mqtt command.
        """
        rawname = name[name.find(".") + 1:]
        if name in self.mqtt_cmds:
            cmd = self.mqtt2svgelement[self.mqtt_cmds.index(name)]
        elif rawname in mqttcmds["relais!"]:
            cmd = name.split(".")[0]
            cmd += ".connect()" if value == "1" else ".disconnect()"
            value = mqttcmds["relais!"][rawname][1]
        else:
            print(f"svg2mqtt: {name} = {value} not implemented yet")
            return
        print(f"svg2mqtt: {cmd}, {value}")
        self.publish(cmd, value)

    # end extern calling attributes (mqtt)
    # ======================================================================================
    #
    # connected GUI-function to buttons or menues
    #

    def close(self, event=None):
        self.publish("off()")
        super().close(event)


if __name__ == "__main__":
    from labml_adjutancy.misc.mqtt_client import mqtt_init

    # broker = 127.0.0.1'
    mqttclient = mqtt_init()  # prepare mqtt
    mqttclient.init()

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = Gui(app)
    app.exec_()
    # window.scope.anim.event_source.stop()
