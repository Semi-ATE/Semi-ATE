# -*- coding: utf-8 -*-
"""
Simple basci gui for the registermaster.

Created on Mon Jan  3 09:19:17 2022
@author: C. Jung

TODO:
    Bug: no bugs known, but in work.....
"""

import sys
import qdarkstyle

# import numpy as np
import os
import pathlib
import qtawesome as qta
from PyQt5 import QtWidgets
from labml_adjutancy.gui.instruments.base_instrument import Gui as Guibase
from labml_adjutancy.gui.instruments.base_instrument import load_ui
from labml_adjutancy.register.registermaster import RegisterMaster

# from labml_adjutancy.misc.common import color

__author__ = "Zlin526F"
__copyright__ = "Copyright 2020, Lab"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"
__version__ = "0.0.2"


class Gui(Guibase):
    """Simple basci gui for the registermaster.

    inherited from base_instrument
       status

    """

    _states = {
        "connect": ["connect", "color: rgb(0, 255, 0)"],  # overwrite the definitions in base_instrument
        "disconnect": ["disconnect", "color: rgb(255, 0, 0)"],
        "on": ["running", "color: rgb(0, 255, 0)"],
        "off": ["waiting for start...", "color: palette(HighlightedText)"],
    }

    def __init__(self, parent=None, name="reg", parentwindow=None, channel=None):
        super().__init__(grandparent=parent, name=name, parentwindow=parentwindow)
        self.myframe = load_ui(self.gui.myframe, __file__)
        # bgcolor = self.gui.palette().color(QtGui.QPalette.Background).name()    # getRgb()
        self.myadjustUI()
        self.gui.closeEvent = self.close
        self.parent = parent
        self.mqtt_initlist = ["filename"]
        self._filename = ""
        self.regs = None
        self.show_regs = []
        if __name__ == "__main__":
            self.filename = "//samba/proot/hana/0504/workareas/appslab/units/top/register_master/xlsdb/hana_regs_20210218.xls"
            self.mqttreceive("regs", {"type": "set", "cmd": "TEST7.read", "payload": 1608})
            self.show_regs[-1].Bhold.setChecked(True)
            self.mqttreceive("regs", {"type": "set", "cmd": "CFX.read", "payload": 208})
            self.show_regs[-2].Bhold.setChecked(False)
            self.mqttreceive("regs", {"type": "set", "cmd": "DAC.read", "payload": 50})

    def myadjustUI(self):
        # set icons:
        self.gui.runToolBar.setVisible(False)
        # self.add_menuicon('onoff')                              # add existing icon and connection from the base-instrument

        # create and connect Menue entries
        self.gui.actionexcel = self.add_menue("open registermaster in excel", self.openexcel, False)
        self.gui.actionshownames = self.add_menue("show names", self.showregdoc, True, True, True)
        self.gui.actionshowbits = self.add_menue("show bits", self.showregdoc, True, True, True)
        self.gui.actionshowval = self.add_menue("show value", self.showregdoc, True, True, True)
        self.gui.actionshowdir = self.add_menue("show dir", self.showregdoc, True, True)
        self.gui.actionshowres = self.add_menue("show reset values", self.showregdoc, True, True)

        # set connection fom Gui-object to functions:
        # self.myframe.Dsamples.valueChanged.connect(self.rangeSamples)
        # self.myframe.Echname.editingFinished.connect(self.editchname)

        self.mqttConnectWidgets()  # connect all widget which start with MQTT_

        geometry = self.gui.geometry()
        wh = self.myframe.geometry()
        self.gui.setWindowTitle(f' {os.path.basename(__file__).split(".")[0]}     (Version: {__version__})')
        self.myframe.setGeometry(geometry.x(), geometry.y(), wh.width() + 100, wh.height() + 250)

    def regstatus(self, msg):
        self.myframe.Lstatus.setText(msg)
        self.myframe.Lstatus.setStyleSheet("color: rgb(255, 0, 0)")

    # ======================================================
    # attributes which connect to an extern call (mqtt-command)
    def mqttreceive(self, instName, msg):
        """common mqtt receive messages, get raw mqtt-Data for more information"""
        if super().mqttreceive(instName, msg):
            return
        self.logger.debug(f"{instName}.mqttreceive: {msg} ")  # e.q. msg={'type': 'set', 'cmd': 'TEST7.read', 'payload': 1608}
        # if you change a widget with the mqtt command, you have to use the widget.blockSignals(True/False)
        if "cmd" in tuple(msg.keys()) and "payload" in tuple(msg.keys()):
            mycmd = msg["cmd"].split(".")
            if len(mycmd) == 2 and mycmd[1] in ["read", "write"]:  # special handling from mqtt commands
                self.regstatus(" ")
                if mycmd[0] in dir(self.regs):
                    self.registerframe(self.regs.__dict__[mycmd[0]], msg["payload"])
                else:
                    self.regstatus(f"{mycmd[0]} not found in the registermaster")
            else:
                self.logger.warning(f"{instName} {msg['cmd']} not found -> do nothing")

    def registerframe(self, register, value):
        self.logger.debug(f"      call registerframe with {register} {value}")
        register._cache = value
        table = register.value_table
        width = register._len_slices()
        myregister = None
        myregisters = self.show_regs.copy()
        hl = ""
        hle = ""
        for regs in myregisters:
            if not regs.Bhold.isChecked() and regs.name != register._name:
                regs.hide()
                self.myframe.QVBregisters.removeWidget(regs)
                regs.destroy()
                regs.deleteLater()
                self.show_regs.remove(regs)
            elif regs.name == register._name:
                myregister = regs
        if myregister is None:
            self.show_regs.append(QtWidgets.QGroupBox(self.myframe))
            myregister = self.show_regs[-1]
            load_ui(myregister, os.path.dirname(__file__) + "\\register.ui")  # QBregister
            myregister.Bhold.setIcon(qta.icon("fa5s.thumbtack", color="white", scale_factor=1.0, color_active="orange"))
            myregister.Bhold.clicked.connect(lambda: self.toggleBhold(myregister.Bhold))
            # self.myframe.Name.mousePressEvent = self.readreg(register._name)
            self.myframe.QVBregisters.addWidget(myregister)
        elif value != myregister.value:
            hl = '<font color="orange">'
            hle = "</font>"
        self.showdoc(self.gui.actionshownames, myregister.Lbitname)
        self.showdoc(self.gui.actionshowbits, myregister.Lbit)
        self.showdoc(self.gui.actionshowval, myregister.Lvalue)
        self.showdoc(self.gui.actionshowdir, myregister.Lrw)
        self.showdoc(self.gui.actionshowres, myregister.Lres)

        # <font color="orange"></font>
        myregister.name = register._name
        myregister.value = value
        myregister.Name.setTitle(f"{register._name} = {value}(d)    = 0x{value:0{width//4}x}    = b{value:0{width}b}")
        bits = bitname = "    "
        rw = "dir"
        val = "val"
        res = "res"
        for index in table.index:
            length = len(table["name"][index]) if len(table["name"][index]) > len(index) else len(index)
            bits = f"{bits}{index:>{length}} "
            bitname = f"{bitname}{table['name'][index]:>{length}} "
            rw = f"{rw}{table['dir'][index]:>{length}} " if table["dir"][index] is not None else f"{rw} {'x':>{length-1}} "
            val = f"{val}{table['dec'][index]:>{length}} "
            # val = f"{val}{' ':>{length}}{hl}{table['dec'][index]}{hle} "
            res = f"{res}{table['res'][index]:>{length}} "
        myregister.Lbit.setText(bits)
        myregister.Lbitname.setText(bitname)
        myregister.Lrw.setText(rw)
        myregister.Lvalue.setText(val)
        myregister.Lres.setText(res)
        myregister.Lbitname.setToolTip(register.__doc__)
        # _len_slices()

    # ======================================================================================
    # definitions from complex mqtt commands, if you need only a connection between the mqtt-command and a widget, start the name of your widget with MQTT_

    @property
    def filename(self):
        return self._filename

    @filename.setter
    def filename(self, val):
        self._filename = val
        val = val.split("/")
        index = 0
        shortpath = ""
        for name in val:
            if name == "proot":
                project = val[index + 1]
                version = val[index + 2]
                workarea = val[index + 4]
                shortpath = f": {project}/{version}/{workarea}/.../"
            index += 1
        self.id = f": {shortpath}{val[-1]}"
        self.gui.actionexcel.setEnabled(True)
        try:
            self.regs = RegisterMaster(filename=self._filename)
            self.regs.init()
        except Exception as ex:
            self.regstatus(f"could not load {self._filename}")
            msg = f"registermaster.filename something is wrong :-( : {ex}"
            self.logger.error(msg)
            print(msg)
            return
        self.logger.info(f"registermaster.filename set to {val}")

    def showdoc(self, action, label):
        if not action.isChecked():
            label.hide()
        else:
            label.show()

    # end extern calling attributes
    # ======================================================================================
    #
    # connected GUI-function to buttons or menues
    #

    def close(self, event=None):
        super().close()

    def openexcel(self):
        filename = pathlib.Path(self.filename)
        msg = f"start excel {filename}"
        self.logger.info(msg)
        os.system(msg)

    def toggleBhold(self, hold):
        if hold.isChecked():
            hold.setIcon(qta.icon("fa5s.thumbtack", color="orange", scale_factor=1.0, color_active="white"))
        else:
            hold.setIcon(qta.icon("fa5s.thumbtack", color="white", scale_factor=1.0, color_active="orange"))

    def showregdoc(self):
        if not hasattr(self, "show_regs"):
            return
        for myregister in self.show_regs:
            self.showdoc(self.gui.actionshownames, myregister.Lbitname)
            self.showdoc(self.gui.actionshowbits, myregister.Lbit)
            self.showdoc(self.gui.actionshowval, myregister.Lvalue)
            self.showdoc(self.gui.actionshowdir, myregister.Lrw)
            self.showdoc(self.gui.actionshowres, myregister.Lres)
            myregister.show()

    def readreg(self, regname):
        self.logger.error(f" readreg {regname} ")
        self.publish(f"{regname}.read")


if __name__ == "__main__":
    # from labml_adjutancy.instruments.mqtt_client import mqtt_init

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
