# -*- coding: utf-8 -*-
"""
base_instrument.

Copyright <2022> <Christian  Jung, www.heli2.de>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial
portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


Created on Fri Jan 14 11:56:24 2022
@author: Christian Jung


INFO:
    icons von https://github.com/spyder-ide/qtawesome
        conda install qtawesome

Done:
    read svg-files and connect id's to a mqtt-command

"""

import os
import qdarkstyle
from PyQt5 import QtCore, QtWidgets, uic
import qtawesome as qta
from labml_adjutancy.misc.iasvg import InteractiveSvgWidget
from labml_adjutancy.misc.mqtt_client import mylogger
from labml_adjutancy.misc.common import str2num

__author__ = "Christian Jung"
__copyright__ = "Copyright 2022, Christian Jung"
__credits__ = ["Christan Jung"]
__email__ = "christian.jung@heli2.de"
__version__ = "0.0.5"


def load_ui(window, my_uifile):
    name = os.path.splitext(my_uifile)
    if len(name) > 1 and name[1] == ".py":
        my_uifile = my_uifile.replace(".py", ".ui")
    if not os.path.exists(my_uifile):
        raise Exception("'%s' doesn't exist" % my_uifile)
    return uic.loadUi(my_uifile, window)


class Gui(object):
    """Base Class for Gui Applikations with an Sensor/Instrument
    Needs:
       - mqtt-message from the parent

    Provides:
       - basic-Window for Instruments
       - receive and show mqtt_status in the statusbar
       - subtopic
       - function mqttConnectWidgets: if Objects-name or an svg-id start with MQTT than automatically connect this object to gui2mqtt() and send the new value about mqtt
         recognise QT-objects: QCombobox, QPushButton, QDoubleSpinBox, QSpinBox, QLCDNumber, QLabel
       - if the Gui starts, it send the mqtt connect message
         if the Gui receive a mqtt connect, it send the the mqtt get from the list self.mqtt_initlist + self.mqtt_cmds

    """

    _states = {
        "disconnect": ["disconnect", "color: rgb(255, 0, 0)"],
        "connect": ["connect", "color: rgb(0, 255, 0)"],
        "on": ["on", "color: rgb(0, 255, 0)"],
        "off": [
            "off",
            "color: palette(HighlightedText)",
        ],  # { color: palette(dark); }#QPalette::HighlightedText
    }
    _mqttPrefix = "MQTT_"
    _mqttSet = "SET_"
    _mqttGet = "GET_"
    _tabPrefix = "TAB_"

    def __init__(self, grandparent=None, name=None, parentwindow=None):
        self.logger = mylogger() if not hasattr(grandparent, "logger") else grandparent.logger
        self.parentwindow = parentwindow if parentwindow is not None else grandparent
        window = QtWidgets.QMainWindow(parentwindow)
        self.instName = name
        self.instNameExtension = ""
        self.grandparent = grandparent
        load_ui(window, __file__)
        self.gui = window
        self.adjustUI()
        self.geometry = self.gui.geometry
        self.width = self.gui.width
        self.height = self.gui.height
        self.gui.closeEvent = self.close
        self.gui.show()
        self._onoff_ = None
        self._id = ""
        self._mqtt_status = "disconnect"
        self.status = "disconnect"
        self.mqtt_status
        self.topinstname = ""
        self._subtopic = ""
        self._lastsvgcolour = None
        self.mqtt_initlist = []
        self.mqtt_cmds = []
        self.publish("mqtt_status", "connect")  # I'm alive
        window.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        # self.gui.myframe.setEnabled(True)

    def adjustUI(self):
        self.gui.setWindowTitle(f" {os.path.basename(__file__)}-Gui (Version {__version__})")
        self._translate = QtCore.QCoreApplication.translate
        # set icons:
        self.gui.actionQuit.setIcon(
            qta.icon(
                "ei.remove-sign",
                color="white",
                scale_factor=1.0,
                color_active="orange",
            )
        )

        # set connect:
        self.gui.actionQuit.triggered.connect(self.gui.close)
        self.gui.runToolBar = self.gui.addToolBar("Run")
        self.gui.runMenu = []

    def add_menue(self, menue, connect, enabled, checkable=False, checked=False):
        """add a menue item to Setup"""
        action = QtWidgets.QAction(self.gui)
        action.setText(menue)
        action.triggered.connect(connect)
        action.setEnabled(enabled)
        if checkable:
            action.setCheckable(True)
            action.setChecked(checked)
        self.gui.menuSetup.addAction(action)
        return action

    def add_menuicon(self, typ, connect=None):
        """add icon and action to the menu:

        "onoff" : on/off
        """
        if typ == "":
            return ()
        self.gui.runMenu.append(QtWidgets.QAction(self.gui.runToolBar))
        self.gui.runMenu[-1].setText(typ)
        self.gui.runToolBar.addAction(self.gui.runMenu[-1])
        if connect is not None:
            self.gui.runMenu[-1].triggered.connect(connect)
        if typ == "onoff":
            self.gui.runMenu[-1].setIcon(qta.icon("ei.play", color="green", scale_factor=0.6))
            self.gui.runMenu[-1].triggered.connect(lambda: self._onoff())
        elif typ == "clear":
            self.gui.runMenu[-1].setIcon(qta.icon("ei.remove", color="white", scale_factor=0.6))

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.checkBox.setText(_translate("Form", "CheckBox"))
        self.label.setText(_translate("Form", "Label"))

    def setLabel(self, Label, value, ext=None):
        """
        Parameters
        ----------
        Label : object
            the label object.
        value : string
            this text will be displayed.
        ext : string, optional
            extention,  The default is None.

        Returns
        -------
        None.

        """
        text = Label.text()
        text = f"{text[:text.find(':')]}: {value}"
        if ext is not None:
            text = f"{text} {ext}"
        Label.setText(text)

    def set_Geometry(self, geometry):
        found = False
        for i in range(0, QtWidgets.QDesktopWidget().screenCount()):
            screen = QtWidgets.QDesktopWidget().screenGeometry(i)
            if screen.x() < geometry[0] and screen.y() < geometry[1]:
                found = True
        if found:
            self.gui.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
        else:
            print(f"Warning: coudn't set last geometry for {self.instName}, it is out of the actual screen")

    @property
    def subtopic(self):
        return self._subtopic

    @subtopic.setter
    def subtopic(self, value):
        if value == []:
            self._subtopic = value
            return
        split = value.split(".")
        self._subtopic = [split[0]] if split[0] != self.topinstname else [split[1]]

    def filtersubtopic(self, value):
        return (
            value[value.find(self.topinstname) + len(self.topinstname) + 1 :]
            if value.split(".")[0] == self.topinstname
            else value
        )

    def unitOfMeasurement(self, value, unit=None):
        split = value.split(" ")
        result = str2num(split[0])
        unit = split[1][0] if len(split) > 1 and unit is None else unit
        mul = 1
        if unit == "M":
            mul = 1000000
        elif unit == "k":
            mul = 1000
        elif unit == "m":
            mul = 0.001
        elif unit == "u":
            mul = 0.000001
        elif unit == "n":
            mul = 0.000000001
        return result * mul

    def objectName2mqttName(self, name):
        """filter from the object name the right mqtt name.

        e.q. objectname = MQTT_voltage   -> voltage  listen on get and set
                        = MQTT_set_I_limit -> I_limit listen only on set
                        = MQTT_get_I_limit -> I_limit listen only on get
                        = TAB_ch           -> Name for a tab-name
        """
        pos = name.find(self._mqttPrefix)
        listen = ""
        result = None
        if pos == 0:
            pos = len(self._mqttPrefix)
            listen = ""
            setget = name[pos:].find(self._mqttSet)
            if setget == 0:
                pos += len(self._mqttSet)
                listen = "set"
            setget = name[pos:].find(self._mqttGet)
            if setget == 0:
                pos += len(self._mqttSet)
                listen = "get"
            result = name[pos:]
        else:
            pos = name.find(self._tabPrefix)
            if pos == 0:
                result = self._tabPrefix
        return listen, result

    # =======================================================
    # attributes which connect to an extern call (mqtt-command)
    def mqttreceive(self, instName, msg, check=False):
        """common mqtt receive messages, get raw mqtt-Data for receiving more information"""
        print(f'        {instName}.mqttreceive from base class:   search {msg["cmd"]}')
        result = False
        if "cmd" in tuple(msg.keys()) and "payload" in tuple(msg.keys()) and (msg["cmd"] in self.mqtt_cmds or not check):
            typ = msg["type"].upper()
            widget = None
            for name in [
                f'MQTT_{typ}_{msg["cmd"]}',
                f'MQTT_{msg["cmd"]}',
            ]:  # search for corresponding widget
                if hasattr(self.myframe, name):
                    widget = getattr(self.myframe, name)
                    break
            if widget is None and hasattr(self, "svgWidgets"):  # search for corresponding svg-id
                print(f'        now search for {msg["cmd"]} in {self.svgWidgets.keys()}')
                name = msg["cmd"].split(".")
                if name[0] in self.svgWidgets:
                    print(f"        {self.instName}.mqttreceive base:  found svgWidgets: {name}")
                    if len(name) == 1:
                        svgwidget = self.svgWidgets[name]
                    else:
                        element = msg["cmd"][msg["cmd"].find(".") + 1:]
                        svgwidget = self.svgWidgets[name[0]]
                    svgwidget.setIdText(element, msg["payload"])
                    print(f"        {self.instName}.mqttreceive base:  set {name[0]}.{element}={msg['payload']}")
                    return True
            if widget is None:
                # print(f'    Warning {self.instName}.mqttreceive base: {instName}, cmd={msg["cmd"]} type= msg["type"] not implemented yet !')
                return False
            print(f'    {self.instName}.mqttreceive base: {instName}, found {widget.objectName()}, type={type(widget)} value={msg["payload"]}')
            value = str2num(msg["payload"], default=-1)
            twidget = type(widget)
            result = True
            if twidget == dict:
                widget["svgelement"].getchildren()[0].text = value
                return result
            if twidget == QtWidgets.QComboBox:
                widget.blockSignals(True)
                for index in range(0, widget.count()):
                    itemvalue = self.unitOfMeasurement(widget.itemText(index))
                    if type(value) in [int, float] and value >= itemvalue:
                        break
                    elif type(value) == str and value.find(widget.itemText(index).split(" ")[0]) == 0:
                        break
                # if index >widget.count():  self.logger.error(f'    {self.instName}.mqttreceive base: {instName}, {msg}, cmd={msg["cmd"]} type = {type(value)} not found')
                widget.setCurrentIndex(index)
                print(f'    {self.instName}.mqttreceive base: {instName}, {msg}, cmd={msg["cmd"]}  done')
            elif twidget == QtWidgets.QPushButton:
                widget.blockSignals(True)
                if type(value) == bool:
                    value = 0 if not value else 1
                if value <= len(widget.textchoice):
                    widget.setText(widget.textchoice[value])
                # if value == 1:
                #     widget.setStyleSheet("color: palette(HighlightedText);background-color: #19c9ff;")
                # elif value == 0:
                #     widget.setStyleSheet("color: palette(HighlightedText);background-color: transparent;")
                widget.setChecked(bool(value))
            elif twidget in [
                QtWidgets.QDoubleSpinBox,
                QtWidgets.QSpinBox,
                QtWidgets.QLCDNumber,
            ]:
                widget.blockSignals(True)
                widget.setProperty("value", value)
            elif twidget == QtWidgets.QLabel:
                widget.blockSignals(True)
                widget.setText(value)
                result = True
            else:
                print(f'    {self.instName}.mqttreceive base: {instName}, {msg}, cmd={msg["cmd"]} widget={type(widget)}  not yet implemented -> improve it !')
                result = False
            widget.blockSignals(False)
        else:
            print(f'        {instName}.mqttreceive from base:  {msg["cmd"]} not found in {self.mqtt_cmds}')
        return result

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value
        self.instNameExtension = self.id
        self.mqtt_status

    @property
    def mqtt_status(self):
        print(f"   {self.instName}.mqtt_status == {self._mqtt_status}")
        msg = f"{self.instName}: {self._mqtt_status}"
        self.gui.myInstrument.setTitle(msg)
        return self._mqtt_status

    @mqtt_status.setter
    def mqtt_status(self, value):
        print(f"   {self.instName}.mqtt_status := {value}")
        self.status = value
        if value == "disconnect":
            self._mqtt_status = value
            self.publish("mqtt_status", "connect")
            self.gui.myframe.setEnabled(False)
        elif value == "connect":
            self._mqtt_status = value
            self.gui.myframe.setEnabled(True)
            print(f"   now ask for init values  {self.mqtt_initlist}, {self.mqtt_cmds}")
            for attribute in self.mqtt_initlist + self.mqtt_cmds:
                if attribute.find("!") < 0:
                    print(f"       {attribute}")
                    self.grandparent.mqtt.publish_get(self.instName, attribute)
        msg = f"{self.instName}: {value}"
        self.gui.myInstrument.setTitle(msg)

    # end extern calling attributes
    # ======================================================================================
    #
    # connected GUI-function to buttons or menues
    #

    def mqttConnectWidgets(self):
        """
        Connect all object which start with MQTT_ to the function gui2mqtt().

        Create a list with all commands in self.mqtt_cmds
        """
        for objectname in dir(self.myframe):
            listen, mqtt_objectname = self.objectName2mqttName(objectname)
            if mqtt_objectname is not None:
                self.mqtt_cmds.append(mqtt_objectname)
                widget = getattr(self.myframe, objectname)
                widget.listen = listen
                connect = None
                if type(widget) == QtWidgets.QComboBox:
                    connect = widget.activated
                elif type(widget) == QtWidgets.QPushButton:
                    connect = widget.clicked
                    widget.textchoice = widget.text().split(";")
                    widget.setText(widget.textchoice[0])
                elif type(widget) in [
                    QtWidgets.QDoubleSpinBox,
                    QtWidgets.QSpinBox,
                ]:
                    connect = widget.valueChanged
                if connect is not None:
                    connect.connect(lambda widget, obj=widget: self.gui2mqtt(obj))
                elif type(widget) not in [
                    QtWidgets.QLCDNumber,
                    QtWidgets.QLabel,
                ]:  # the widgets in the table needs normaly only receiver
                    print(
                        f"Error:   base_instrument.mqttConnectWidgets: {objectname} with widget {type(widget)} connect not yet implemented -> improve it !!"
                    )

    def mqttConnectSVGWidget(self, filename, name, channel=None):
        """
        Create an InteractiveSvgWidget and load the filname.

        Connect all clicks to the text id's to the function svg2mqtt().
        """
        if not hasattr(self, "svgWidgets"):
            self.svgWidgets = {}
        # firstname = f'{name}({channel})' if channel is not None else name              #todo mqtt send = ch(0) not possible yet
        firstname = f"{name}{channel}" if channel is not None else name
        svgWidget = InteractiveSvgWidget(filename, firstname=firstname)
        svgWidget.setStyleSheet("background-color: white;")
        self.svgWidgets[firstname] = svgWidget
        svgWidget.changedId.connect(self.svg2mqtt)
        return svgWidget

    def _onoff(self):
        if self._mqtt_status == "disconnect":
            return
        if self._onoff_ is None:
            self.publish("off()")
            self.status = "no channel defined"
        elif self._onoff_ == 0:
            self.publish("on()")
            self.gui.runMenu[0].setIcon(qta.icon("ei.pause", color="red", scale_factor=1.0))
            self._onoff_ = 1
            self.status = "on"
        else:
            self.publish("off()")
            self.gui.runMenu[0].setIcon(qta.icon("ei.play", color="green", scale_factor=1.0))
            self._onoff_ = 0
            self.status = "off"

    @property
    def status(self):
        return self.gui.statusbar.currentMessage()

    @status.setter
    def status(self, value):
        style = None
        msg = value
        if type(value) == tuple:
            msg = value[0]
            style = value[1]
        if value in self._states:
            msg = self._states[value][0]
            style = self._states[value][1]
        style == "color: palette(HighlightedText);background-color: transparent;" if None else style
        self.gui.statusbar.setStyleSheet(style)
        self.gui.statusbar.showMessage(f"{msg}")

    def publish(self, cmd, value="", instName=None):
        instName = self.instName if instName is None else instName
        # print(f"{self.instName}.publish {cmd} = {value}")
        if hasattr(self.grandparent, "mqtt") and hasattr(self.grandparent.mqtt, "publish_set"):
            self.grandparent.mqtt.publish_set(instName, cmd, value)
        else:
            print(f"Error: {instName}.{cmd} := {value}   but no publish_set defined!")

    def gui2mqtt(self, widget):
        """Function connect a Gui-widget to mqtt, it sends a mqtt set command with the value from the Gui-widget."""
        listen, name = self.objectName2mqttName(widget.objectName())
        name = widget.objectName() if name is None else name
        print(f"{self.instName}.gui2mqtt {name}")
        typ = type(widget)
        found = False
        if typ == QtWidgets.QComboBox:
            value = self.unitOfMeasurement(widget.currentText())
            found = True
        elif typ == QtWidgets.QPushButton:
            value = 1 if widget.isChecked() else 0
            found = True
        elif typ in [QtWidgets.QDoubleSpinBox, QtWidgets.QSpinBox]:
            value = widget.value()
            found = True
        if found:
            self.publish(name, value)
        else:
            print(f"Warning: {self.instName}.gui2mqtt {name}  widget={type(widget)} not yet implemented -> improve it !!!!!!"
            )

    def svg2mqtt(self, name, value):
        """Publish the name and value over mqtt.

        overwrite this function if you need a more complexer form.
        """
        self.publish(name, value)

    def isVisible(self):
        return self.gui.isVisible()

    def hide(self):
        print(self.gui.isVisible())
        self.gui.hide()

    def show(self):
        print(self.gui.isVisible())
        self.gui.show()

    def close(self, event=None):
        self.publish("mqtt_status", "disconnect")
        if hasattr(self.grandparent, "appclosed"):
            self.grandparent.appclosed(self.instName)
        self.gui.close()


if __name__ == "__main__":
    pass
    import sys

    # from mqtt_client import mqtt_init

    # broker = 127.0.0.1'
    # message_client = 'ate/DT1604092/matrix'
    # mqttclient = mqtt_init()                                              # prepare mqtt
    # mqttclient.init(None, message_client=message_client.split('/')[0])    # mqtt client connect to broker
    # mqttclient.init()

    app = QtWidgets.QApplication(sys.argv)
    window = Gui(app, "My Instrument")
    app.exec_()
