# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 09:17:01 2020

@author: ZLin525F

INFO:
    icons von https://github.com/spyder-ide/qtawesome

"""
import os
import time
import importlib
import qtawesome as qta
import qdarkstyle
from PyQt5 import uic
from qtpy.QtCore import Signal
from PyQt5 import QtWidgets, QtCore

from qtpy.QtWidgets import QHBoxLayout
from spyder.api.translations import get_translation
from spyder.api.widgets.main_widget import PluginMainWidget
from pydantic import BaseModel

# Localization
_ = get_translation("spyder")


__author__ = "Zlin526F"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"
__version__ = "0.0.1"


class LabGuiDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(__file__.replace(".py", ".ui"), self)


class LabGuiConfig(BaseModel):
    broker: str
    topic: str


class LabGui(PluginMainWidget):
    """
    Gui for instruments.


    - mqtt command will be handle in mqtt_receive()

    for extend the Menubar:
        - send mqtt with {'semictrl': {'type': 'cmd', 'cmd': 'menu', 'payload': {'Instruments': '', 'scope': 'gui.instruments.softscope.softscope'}}}
        - app must have the class GUI(parent=None, name=None)
        - if you use more than one instName for the same GUI:
            use subtopic[] for the other instName in the Gui
    """

    default_tester_icon = qta.icon("mdi6.remote", color="green", scale_factor=1.0)
    actuator_types = {'Temperature': None,
                      'Magnetic Field': None,
                      'Light': None,
                      'Acceleration': None,
                      'Position': None,
                      'Pressure': None}
    _states = {  # from extern mean: no handling from Lab Gui, normally you get this message if your are running the MiniSCTGui
        "notconnect": ["no connection to broker ", "color: rgb(0, 0, 0);background-color: #ff0000"],
        "busy": ["get busy from extern", None],
        "next": ["get next from extern", None],
        "ready": ["get ready from extern", None],
        "initialized": ["get initialized from extern", None],
        "connecting": ["get connecting from extern", None],
        "loading": ["get loading from extern", None],
        "unloading": ["get unloading from extern", None],
        "softerror": ["get softerror from extern", None],
        "crash": ["crashed ", "color: rgb(255, 0, 0)"],
        "init": [
            "testflow not started / no connection",
            "color: rgb(255, 165, 0)",
        ],
        "unknown": ["unknown", None],
        "idle": ["ready -> wait for next", "color: rgb(255, 255, 0)"],
        "testing": ["testing", "color: rgb(255, 165, 0)"],
        "error": ["error", "color: rgb(0, 0, 0);background-color: #ff0000"],
        "reset": ["reset Lab Gui", None],
        "terminated": ["finish, disconnect", "color: rgb(255, 165, 0)"]
    }

    errormessages = {"unknown", "unknown"}

    command = {  # see https://github.com/Semi-ATE/Semi-ATE/blob/master/docs/project/interfacedefinitions/testapp_interface.md
        "load": {
            "type": "cmd",
            "command": "load",
            "lot_number": "123456.001",
            "sites": ["0"],
        },
        "next": {
            "type": "cmd",
            "command": "next",
            "sites": ["0"],
            "job_data": {
                "stop_on_fail": {"active": False, "value": -1},
                "sites_info": [{"siteid": "0", "partid": "1", "binning": -1}],
            },
        },
        "reset": {"type": "cmd", "command": "reset", "sites": ["0"]},
        "SetParameter": {
            "type": "cmd",
            "command": "setparameter",
            "parameters": [],
            "sites": ["0"],
        },
        "terminate": {"type": "cmd", "command": "terminate", "sites": ["0"]},
        "exec": {
            "type": "cmd",
            "command": "getexecutionstrategy",
            "sites": ["0"],
            "layout": [[0, 0]],
        },
    }
    # peripherie. e.q. Magnetfield:  {"type": "io-control-request", "periphery_type": "MagField", "ioctl_name": "set_field", "parameters": {"millitesla": 10}}
    # see: Tester\TES\apps\testApp\sequencers\SequencerHarness.py
    #    _execute_command   (init, next, terminate, reset, setloglevel, getexecutionstrategy, sethbin)

    change_status_display = Signal(str, str)

    def __init__(self, name, plugin, parent=None):
        super().__init__(name, plugin, parent)
        """Initialise the class semi_control."""
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
        self.plugin = plugin
        self.gui = LabGuiDialog()
        self.adjustUI()
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.closeEvent = self.close
        self.reset()
        self.project_info = None
        self.topinstname = ""
        self._state = "init"
        self.state = "init"
        self.gui_icons = {}
        self.flagAppclosed = False

    def setup_widget(self, project_info):
        self.project_info = project_info
        self.update_actions()

    def setup(self):
        layout = QHBoxLayout()
        layout.addWidget(self.gui)
        self.setLayout(layout)

    def update_actions(self):
        from ate_projectdatabase.Hardware import Hardware

        if self.project_info is not None:
            self.lab_control = self.project_info.lab_control
            self.lab_control.receive_msg_for_instrument.connect(self.receive_msg_for_instrument)
            self.mqtt = self.lab_control.mqtt
            self.logger = self.lab_control.logger
            hw = self.project_info.active_hardware
            base = self.project_info.active_base
            hardware_def = Hardware.get(self.project_info.file_operator, hw).definition
            tester_name = hardware_def['tester']
            actuators = hardware_def['Actuator'][base]
            self.create_button('tester', tester_name)
            print(actuators)
            for actuator in actuators:   # todo: actuartors see https://github.com/Semi-ATE/Semi-ATE/blob/master/docs/project/DevelopmentProcess/development_setup.md
                self.create_button(actuator, tester_name)    # and https://github.com/Semi-ATE/TCC_actuators

    def create_button(self, instanceName, name):
        from ate_semiateplugins.pluginmanager import get_plugin_manager

        if instanceName == 'tester':
            lib_types = get_plugin_manager().hook.get_tester_type(tester_name=name)
            if len(lib_types) >= 1:
                lib_types = lib_types[0]
            else:
                return
        else:
            lib_types = self.actuator_types[instanceName]
            if lib_types is None:
                return
        if instanceName not in self.gui_icons:                      # create new icon button
            button = QtWidgets.QToolButton(self.gui.frame)
            button.setGeometry(QtCore.QRect(10, 10, 42, 42))
            button.setIconSize(QtCore.QSize(40, 40))
            button.name = instanceName
            button.lib = None
            button.instance = None
            self.gui_icons[instanceName] = button
        else:                                                        # use existing icon button
            button = self.gui_icons[instanceName]
            if self.gui_icons[instanceName].lib is not None:
                importlib.reload(button.lib)

        button.setText(name)
        if hasattr(lib_types, 'gui'):
            button.lib = importlib.import_module(lib_types.gui)
            button.setEnabled(True)
        if button.lib is not None and hasattr(button.lib, 'icon'):
            button.setIcon(button.lib.icon)
        elif button.lib is None:
            button.setEnabled(False)

        button.setToolTip(name)
        button.clicked.connect(lambda checked, name=instanceName: self.icon_button_clicked(instanceName))
        button.subtopic = []
        button.show()

    def get_title(self):
        return _("Lab Gui")

    def update_labgui(self, test_program_name):
        self.update_actions()
        self.state = 'testing'

    def show(self):
        super().show()
        index = 0
        for app in self.gui.newMenu:
            if hasattr(app, "libname") and app.libname != "":
                self.extendedbarClicked(index)
            index += 1
        self.flagAppclosed = True

    def adjustUI(self):
        # set Menubar
        menuBar = QtWidgets.QMenuBar(self)
        self.menuBar = menuBar
        menuBar.titles = []

        # set connect:
        self.gui.newMenu = []

    def reset(self):
        print("Reset Lab Gui")
        self.setButtonActive(False)
        self._state = "reset"
        self.state = "reset"
        self.last_mqtt_time = time.time()

    # mqtt messages:
    def mqtt_send(self, topic, cmd):
        """Send messages via mqtt."""
        if cmd in self.command:
            msg = self.command[cmd]
            topic = self.sendtopic + topic
            self.mqtt.publish(topic, msg)
            self.change_status_display.emit("send " + str(msg["command"] + ", wait for answer"), "")
            print("Lab Gui.mqtt_send {}:{}".format(topic, msg))
            self.wait4answer = True
        else:
            self.error(f"Lab Gui.mqtt_send {topic}:{cmd} not found in list")

    def receive_msg_for_instrument(self, topic, msg):
        """
        call if a message from an instrument, or from semictrl (is also a instrument) received.

        """
        print(f"gui receive: {topic}, {msg}")
        if type(msg) is dict and "type" in msg and msg["type"] == "cmd" and msg["cmd"] == "menu":  # get command to extend Menu
            pindex = -1
            for addmenu in msg["payload"]:
                # the syntax is {'payload': {'Instruments': '', 'scope': 'gui.instruments.softscope.softscope'}}
                pindex += 1
                found = False
                if addmenu == 'tester':
                    continue
                if pindex == 0 and addmenu not in self.menuBar.titles:  # add new Menu Title
                    self.gui.newMenu.append(QtWidgets.QMenu(addmenu, self.gui))
                    self.gui.newMenu[-1].instance = None
                    self.menuBar.addMenu(self.gui.newMenu[-1])
                    self.menuBar.titles.append(addmenu)
                    mindex = pindex
                    found = True
                elif pindex == 0:  # Menu Title already exist
                    # print(f"     Menu Title {addmenu} already exist, do nothing")
                    continue
                else:  # create/update submenue
                    print(f"     add/update menu: {addmenu}")
                    mindex = 0
                    for menu in self.gui.newMenu:  # menu exist?
                        if hasattr(menu, "name") and menu.name == addmenu:
                            found = True
                            break
                        mindex += 1
                    if found:
                        lib = msg["payload"][addmenu].split(".")[-1]
                        try:
                            importlib.reload(self.gui.newMenu[mindex].lib)
                        except Exception as ex:
                            self.logger.error(f"    Coudn't reload lib {lib} from {msg['payload'][addmenu]}  {ex}")
                        continue
                    else:  # create menu: {addmenu} with action to lib {msg['payload'][addmenu]}
                        self.gui.newMenu.append(QtWidgets.QAction("   " + addmenu, self.gui))
                        try:
                            if msg["payload"][addmenu] != "":
                                print(f"     importlib {msg['payload'][addmenu]}")
                                self.gui.newMenu[-1].lib = importlib.import_module(msg["payload"][addmenu])
                        except Exception as ex:
                            # self.gui.newMenu[-1].lib = None
                            print(f"    Coudn't set lib, try to load {msg['payload']}[{addmenu}]  {ex}")
                            self.gui.newMenu.pop(-1)
                            continue
                        self.gui.newMenu[-1].setCheckable(True)
                        self.gui.newMenu[-1].setText("     " + addmenu)
                        self.gui.newMenu[0].addAction(self.gui.newMenu[-1])
                        self.gui.newMenu[-1].triggered.connect(lambda checked, index=len(self.gui.newMenu) - 1: self.extendedbarClicked(index))
                        print(f"         create menu: {addmenu} index = {len(self.gui.newMenu)-1}, with action to lib {msg['payload'][addmenu]}")
                if not hasattr(self.gui.newMenu[mindex], "instance"):  # GUI has not created
                    self.gui.newMenu[mindex].instance = None
                self.gui.newMenu[mindex].libname = msg["payload"][addmenu]
                self.gui.newMenu[mindex].name = addmenu
                self.gui.newMenu[mindex].subtopic = []
                print("     add/update menu : done")
                self.menuBar.adjustSize()
        elif type(msg) is dict and len(msg.keys()) == 1:  # received a message for a application in the extended Menu
            print(f"   message for the extended GUI received: '{topic}= {msg}'")
            print(f"       {self.gui.newMenu}")
            for app in self.gui.newMenu:
                self.transfer2gui(app, topic, msg)
            instanceName = list(msg.keys())[0]
            if instanceName in self.gui_icons:
                self.transfer2gui(self.gui_icons[instanceName], topic, msg)
                
                # if not hasattr(app, "instance") or app.instance is None:
                #     continue
                # print(f"   {app.instance.topinstname}.{app.name}: subtopic: {app.instance.subtopic}")
                # name = None
                # app.topinstname = self.topinstname
                # if len(app.subtopic) > 0:
                #     for subtopic in app.subtopic:
                #         if subtopic in msg.keys():
                #             name = subtopic
                # elif hasattr(app.instance, "subtopic"):  # you can also add subtopic to a each GUI, e.q. scope also listen to 'regs'
                #     for subtopic in app.instance.subtopic:
                #         if subtopic in msg.keys():
                #             name = subtopic
                # if app.name in msg.keys() and app.instance is not None:
                #     name = app.name
                # if name is not None:
                #     msg = msg[name]
                #     cmd = msg["cmd"]
                #     value = msg["payload"]
                #     print(f"    message for {app.name}: {cmd} = {msg} -->   ")
                #     try:
                #         if msg["type"] in ["set"] and hasattr(app.instance, cmd):  # set attribute
                #             # print(f"   begin set attribute {cmd}={value}")
                #             app.instance.__setattr__(cmd, value)
                #             # print("   --> set attribute done")
                #         elif msg["type"] in ["get"] and hasattr(app.instance, cmd):  # get attribute/function call
                #             if value == []:  # it is a function call?
                #                 app.instance.__getattribute__(cmd)()
                #             else:
                #                 app.instance.__setattr__(cmd, value)  # get from extern is a set for displaying....
                #         elif msg["type"] in ["set", "get"] and hasattr(app.instance, "mqttreceive"):  # get more information as only the payload
                #             app.instance.mqttreceive(name, msg)
                #         elif not hasattr(app.instance, cmd):
                #             self.logger.warning(f"{name} hat no attribute: '{cmd} = {msg}'")
                #         else:
                #             self.logger.error(f"{name} I don't now what to do with this message: '{cmd} = {msg}'")
                #     except Exception as ex:
                #         msg = f"{name} something goes wrong: '{topic} = {msg}'  {ex}"
                #         self.logger.error(msg)
                #         print(msg)

    def transfer2gui(self, app, topic, msg):
        if not hasattr(app, "instance") or app.instance is None:
            return
        print(f"   {app.instance.topinstname}.{app.name}: subtopic: {app.instance.subtopic}")
        name = None
        app.topinstname = self.topinstname
        if len(app.subtopic) > 0:
            for subtopic in app.subtopic:
                if subtopic in msg.keys():
                    name = subtopic
        elif hasattr(app.instance, "subtopic"):  # you can also add subtopic to a each GUI, e.q. scope also listen to 'regs'
            for subtopic in app.instance.subtopic:
                if subtopic in msg.keys():
                    name = subtopic
        if app.name in msg.keys() and app.instance is not None:
            name = app.name
        if name is not None:
            msg = msg[name]
            cmd = msg["cmd"]
            value = msg["payload"]
            print(f"    message for {app.name}: {cmd} = {msg} -->   ")
            try:
                if msg["type"] in ["set"] and hasattr(app.instance, cmd):  # set attribute
                    # print(f"   begin set attribute {cmd}={value}")
                    app.instance.__setattr__(cmd, value)
                    # print("   --> set attribute done")
                elif msg["type"] in ["get"] and hasattr(app.instance, cmd):  # get attribute/function call
                    if value == []:  # it is a function call?
                        app.instance.__getattribute__(cmd)()
                    else:
                        app.instance.__setattr__(cmd, value)  # get from extern is a set for displaying....
                elif msg["type"] in ["set", "get"] and hasattr(app.instance, "mqttreceive"):  # get more information as only the payload
                    app.instance.mqttreceive(name, msg)
                elif not hasattr(app.instance, cmd):
                    self.logger.warning(f"{name} hat no attribute: '{cmd} = {msg}'")
                else:
                    self.logger.error(f"{name} I don't now what to do with this message: '{cmd} = {msg}'")
            except Exception as ex:
                msg = f"{name} something goes wrong: '{topic} = {msg}'  {ex}"
                self.logger.error(msg)
                print(msg)

    def setButtonActive(self, value):
        """Activate all disabled buttons."""
        pass

    def icon_button_clicked(self, name):
        print(name)
        button = self.gui_icons[name]
        if button.instance is None:
            button.instance = button.lib.Gui(self, name, self.project_info.parent)  # start Gui
            button.instance.subtopic = button.subtopic
            button.instance.topinstname = name
        else:
            pass
            #button.instance.show()

    # display:
    def extendedbarClicked(self, index):
        if index == 0:
            return
        # print(f"extendedbarClicked {index}")
        # print(f"     name = {self.gui.newMenu[index].name}")
        # print(f"     libname = {self.gui.newMenu[index].libname}")
        # print(f"     lib = {self.gui.newMenu[index].lib}")
        # print(f"     subtopic = {self.gui.newMenu[index].subtopic}")
       #  print(f"     topinstname = {self.topinstname}")
        if self.gui.newMenu[index].isChecked():
            name = self.gui.newMenu[index].name
            if not hasattr(self.gui.newMenu[index], "lib") or self.gui.newMenu[index].lib is None:
                print(f" Gui for {name} not exist, please update the LAB-ML adjutancy lib")
                self.gui.newMenu[index].instance = None
                self.gui.newMenu[index].setChecked(False)
                return
            importlib.reload(importlib.import_module("labml_adjutancy.gui.instruments.base_instrument"))
            importlib.reload(self.gui.newMenu[index].lib)
            self.gui.newMenu[index].instance = self.gui.newMenu[index].lib.Gui(self, name, self.project_info.parent)  # start Gui
            self.gui.newMenu[index].instance.subtopic = self.gui.newMenu[index].subtopic
            self.gui.newMenu[index].instance.topinstname = self.topinstname
        elif self.gui.newMenu[index].instance is not None:
            self.gui.newMenu[index].instance.close()
            self.gui.newMenu[index].instance = None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, value):
        msg = ""
        if type(value) == tuple:
            msg = value[1]
            value = value[0]
        if value in ["idle", "testing"] and self.command["SetParameter"]["parameters"] != []:  # display the parametername if sequencer enabled
            parameters = self.command["SetParameter"]["parameters"]
            apara = []
            for parametername in parameters:
                pname = parametername["parametername"]
                pname = pname[pname.find(".") + 1:]
                pvalue = parametername["value"]
                if (pname, pvalue) not in apara:
                    apara.append((pname, pvalue))
            dmsg = ""
            for val in apara:
                dmsg = dmsg + f"{val[0]}={val[1]}, "
            msg = dmsg[:-2] + msg
        print(f"semi_control.state = {value}, oldstate ={self._state}")
        oldstate = self._state
        self._state = value if value in self._states else "unknown"
        self.change_status_display.emit(value, msg)
        if value == "terminated":
            self.setButtonActive(False)
        if value.find("error") > -1:  # wo wird das gesetzt?? TODO: change!!
            self.setButtonActive(True)
        elif value == "config" or (value == "idle" and oldstate not in ("config", "testing")):  # start identify
            print("semi_control.state: config apply")
        elif value == "idle" and oldstate in ("reset", "config", "testing") and self.gui.CBstopauto.isChecked():  # testprogramm runs through
            print("semi_control.state: idle, Auto is enabled -> send terminate")
            self.mqtt_send("cmd", "terminate")

    def set_Geometry(self, name, gui, geometry):
        found = False
        for i in range(0, QtWidgets.QDesktopWidget().screenCount()):
            screen = QtWidgets.QDesktopWidget().screenGeometry(i)
            if screen.x() < geometry[0] and screen.y() < geometry[1]:
                found = True
        if found:
            gui.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
            print(f"{name}.set_Geometry({geometry[0]}, {geometry[1]}, {geometry[2]}, {geometry[3]})")
        else:
            print(f"coudn't set last geometry for {name}, it is out of the actual screen")

    @QtCore.pyqtSlot(str, str)
    def _change_status_display(self, msg, extendmsg=""):
        print(f"       state = {msg}")
        style = self._states[msg][1] if msg in self._states else "color: rgb(255, 255, 255);background-color: transparent;"
        msg = self._states[msg][0] if msg in self._states else msg
        self.gui.Lstatus.setText(f"{extendmsg} {msg}")
        self.gui.Lstatus.setStyleSheet(style)

    def appclosed(self, name):
        """Call from an instrumet if the instrument closed itself."""
        if self.flagAppclosed:  # TODO change to a Signal
            print(f"   Control.appclosed({name})")
            for app in self.gui.newMenu:
                if app.name == name:
                    app.setChecked(False)
                    settings = [app.libname, app.isChecked()]
                    if app.instance is not None and hasattr(app.instance, "geometry"):
                        settings.append(
                            [
                                app.instance.geometry().x(),
                                app.instance.geometry().y(),
                                app.instance.width(),
                                app.instance.height(),
                            ]
                        )
                    settings.append(app.subtopic)

    def close(self, event=None):
        self.flagAppclosed = False
        super().close()

    def __del__(self):
        print("Semicontrol.__del__")
        self.close()
        super().__del__

    def debug_stop(self):
        ''' do update the state of lab control when the test application is stoped '''
        pass


if __name__ == "__main__":
    from ate_spyder.widgets.navigation import ProjectNavigation
    from ate_spyder.widgets.actions_on.utils.FileSystemOperator import FileSystemOperator
    from PyQt5.QtWidgets import QApplication
    from qtpy.QtWidgets import QMainWindow
    import qdarkstyle
    import sys

    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    app.references = set()
    main = QMainWindow()
    homedir = os.path.expanduser("~")
    project_directory = homedir + r'\ATE\packages\envs\semi-ate-awinia1\HATB'       # path to your semi-ate project
    project_info = ProjectNavigation(project_directory, homedir, main)
    project_info.active_hardware = 'HW0'
    project_info.active_base = 'PR'
    project_info.active_target = 'Device1'
    
    labgui = LabGui('Lab Gui', main)
    labgui.setup_widget(project_info)
