# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 09:17:01 2020

@author: C. Jung

INFO:
    icons von https://github.com/spyder-ide/qtawesome
        conda install qtawesome

TODO:
    bekommt man über project_info auch den logger.log_file ??
"""
import os
import time
import importlib
import json
import qtawesome as qta
import qdarkstyle
import socket
from PyQt5 import uic
from qtpy.QtCore import Signal
from PyQt5 import QtWidgets, QtCore

import labml_adjutancy.misc.mqtt_client as mqtt

from labml_adjutancy.misc.mqtt_client import (
    mqtt_displayattributes,
    mqtt_init,
    mylogger,
)
from labml_adjutancy.ctrl.sequencer import Sequencer
from labml_adjutancy.ctrl.barprogress import Barprogress

from qtpy.QtWidgets import QHBoxLayout
from spyder.api.translations import get_translation
from spyder.api.widgets.main_widget import PluginMainWidget
from pydantic import BaseModel

# Localization
_ = get_translation("spyder")


__author__ = "Zlin526F"
__copyright__ = "Copyright 2022, Lab"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"
__version__ = "0.0.18"


class LabControlDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(__file__.replace(".py", ".ui"), self)


class LabConrolConfig(BaseModel):
    broker: str
    topic: str


class LabControl(PluginMainWidget):
    """
    Basic controlling from Semi-ATE.

    implemented Buttons with mqtt-message (see also main_widget.ui):
      - next
      - terminate
      - reset

    - most interactions from the user with the gui will be handle in guiclicked('')
    - mqtt command will be handle in mqtt_receive()

    for extend the Menubar:
        - send mqtt with {'semictrl': {'type': 'cmd', 'cmd': 'menu', 'payload': {'Instruments': '', 'scope': 'gui.instruments.softscope.softscope'}}}
        - app must have the class GUI(parent=None, name=None)
        - if you use more than one instName for the same GUI:
            use subtopic[] for the other instName in the Gui
    """

    configfile = "lab_control.json"
    timefile = "lab_controltimes.json"

    _states = {  # from extern mean: no handling from Lab Control, normally you get this message if your are running the MiniSCTGui
        "notconnect": ["no connection to broker ", "color: rgb(0, 0, 0);background-color: #ff0000"],
        "busy": ["get busy from extern", None],
        "next": ["get next from extern", None],
        "ready": ["get ready from extern", None],
        "initialized": ["get initialized from extern", None],
        "connecting": ["get connecting from extern", None],
        "loading": ["get loading from extern", None],
        "unloading": ["get unloading from extern", None],
        "softerror": ["get softerror from extern", None],
        "breakpoint": [
            "hold on default breakpoint, click continue in spyder",
            "color: rgb(255, 165, 0)",
        ],
        "crash": ["crashed ", "color: rgb(255, 0, 0)"],
        "init": [
            "testflow not started / no connection",
            "color: rgb(255, 165, 0)",
        ],
        "unknown": ["unknown", None],
        "idle": ["ready -> wait for next", "color: rgb(255, 255, 0)"],
        "testing": ["testing", "color: rgb(255, 165, 0)"],
        "error": ["error", "color: rgb(0, 0, 0);background-color: #ff0000"],
        "logload": ["logging = last logfile", None],
        "lognotexist": ["couldn't found last logfile", None],
        "reset": ["reset Lab Control", None],
        "terminated": ["finish, disconnect", "color: rgb(255, 165, 0)"],
        "finish_seq": ["Sequencer finish", "color: rgb(0, 255, 0)"],
        "nothing_seq": [
            "no Sequencer values defined, do nothing, please disable View->Shmoo Parameters or enable Sequencer Parameters",
            "color: rgb(255, 165, 0)",
        ],
        "config": [
            "Instrument configuration done, wait for next",
            "color: rgb(255, 255, 0)",
        ],
        "configerror": [
            "Instrument configuration done, found {} errors",
            "color: rgb(0, 0, 0);background-color: #ff0000",
        ],
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

    # some examples for the received mqtt command:
    # Server received message {'type': 'cmd', 'command': 'usersettings',
    #    'payload': [{'name': 'stop_on_fail', 'active': False, 'value': -1},
    #                {'name': 'single_step', 'active': False, 'value': -1},
    #                {'name': 'stop_on_test', 'active': False, 'value': -1},
    #                {'name': 'trigger_on_test', 'active': False, 'value': -1},
    #                {'name': 'trigger_on_fail', 'active': False, 'value': -1},
    #                {'name': 'trigger_site_specific', 'active': False, 'value': -1}],
    #    'connectionid': 'fac02712-51c5-11eb-a4ed-c03eba86172a'}

    # {"type": "cmd", "command": "next", "sites": ["0"], "job_data": {
    #           "stop_on_fail": {"active": false, "value": -1},
    #           "single_step": {"active": false, "value": -1},
    #           "stop_on_test": {"active": false, "value": -1},
    #           "trigger_on_test": {"active": false, "value": -1},
    #           "trigger_on_fail": {"active": false, "value": -1},
    #           "trigger_site_specific": {"active": false, "value": -1},
    #           "sites_info": [{"siteid": "0", "partid": "1", "binning": -1}]}}

    bin_table = [
        {
            "SBIN": "1",
            "GROUP": "Good1",
            "DESCRIPTION": "",
            "HBIN": "1",
            "SBINNAME": "Good_1",
        }
    ]

    change_status_display = Signal(str, str)

    def __init__(self, name, plugin, parent=None):
        super().__init__(name, plugin, parent)
        """Initialise the class semi_control."""
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
        self.plugin = plugin
        self.passmsg = "Pass"
        self.SemiCtrlinstName = "semictrl"
        self.logging_cmd_reload = "!RELOAD!"
        self.gui = LabControlDialog()
        self.logger = mylogger(self.gui.TElogging, parent="Lab Control")
        self.logger.enable = False
        self.progressbar = Barprogress(self)
        self.sequencer = Sequencer(self, self.gui.Fsequencer)
        self.adjustUI()
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.closeEvent = self.close
        self._createFilterMenu()
        self._createSeqMenu()
        self.reset()
        self.project_info = None
        self.logfilename = ""
        self.last_HW = []
        self.cycle = 0
        self.topinstname = ""
        self._state = "init"
        self.state = "init"
        self.test_program_name = ""
        self.configdata = None
        self.saveconfigdata = None

    def setup_widget(self, project_info):
        self.project_info = project_info
        current_config = project_info.load_plugin_cfg(project_info.active_hardware, self.plugin.NAME)
        default_parameter = {"broker": '127.0.0.1', "topic": 'developmode'}
        self.current_config = LabConrolConfig(**default_parameter if current_config == {} else current_config)
        print(f'{self.plugin.NAME}.current config = {self.current_config}')

        self.sendtopic = f"ate/{self.current_config.topic}/TestApp/"
        self.logger.info(f"mqtt sendtopic = {self.sendtopic}")
        mqttclient = mqtt_init()  # prepare mqtt for controlling
        if not mqttclient.init(self.current_config.broker):   # mqtt client connect to default broker and default topic
            self.state = "notconnect"
            return
        self.mqtt = mqtt_displayattributes(mqttclient, mqttclient.topic, self.mqtt_receive)
        self.mqttclient = mqttclient
        self.mqtt.mqtt_add()
        self.computername = socket.gethostname() if self.mqttclient.broker == "127.0.0.1" else self.mqttclient.broker
        self.openconfig()
        self.menuBar.adjustSize()

    def setup(self):
        layout = QHBoxLayout()
        layout.addWidget(self.gui)
        self.setLayout(layout)

    def update_actions(self):
        pass

    def get_title(self):
        return _("Lab Control")

    def update_control(self, test_program_name):
        print(f"Lab Control.update_control({test_program_name})")

        self.test_program_name = test_program_name
        if self.project_info == "":
            self.logger.error("__call__ : no project_info found")
            return
        self.warning_cnt = 0
        self.error_cnt = 0
        path = os.path.join(
            self.project_info.project_directory,
            os.path.split(self.project_info.project_directory)[-1],
            self.project_info.active_hardware,
            self.project_info.active_base,
        )
        if self.test_program_name != "":
            self.sequencer.load(self.project_info.project_directory, self.test_program_name)
        self.progressbar.load_testbenches_time(os.path.join(path, self.timefile))
        bin_table = self.load_json(os.path.join(path, self.test_program_name + "_binning.json"))
        if bin_table is not None:
            self.bin_table = bin_table["bin-table"]
        self.logging()

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
        menuBar.titles = ["Tools", "Logging", "View"]

        nextaction = QtWidgets.QAction(self.gui)
        nextaction.setIcon(qta.icon("fa5s.step-forward", color="green", scale_factor=1.0))
        nextaction.setToolTip("Next")
        nextaction.triggered.connect(lambda: self.guiclicked("next"))
        menuBar.addAction(nextaction)
        self.nextaction = nextaction

        terminateaction = QtWidgets.QAction(self.gui)
        terminateaction.setIcon(qta.icon("fa5s.stop", color="green", scale_factor=1.0))
        terminateaction.setToolTip("Stop")
        terminateaction.triggered.connect(lambda: self.mqtt_send("cmd", "terminate"))
        menuBar.addAction(terminateaction)
        self.terminateaction = terminateaction

        resetaction = QtWidgets.QAction(self.gui)
        resetaction.setIcon(qta.icon("fa5s.reply", color="green", scale_factor=1.0))
        resetaction.setToolTip("Reset")
        resetaction.triggered.connect(lambda: self.mqtt_send("cmd", "reset"))
        menuBar.addAction(resetaction)
        self.resetaction = resetaction

        actionTools = QtWidgets.QAction(self.gui)
        actionTools.setIcon(qta.icon("ei.wrench", color="white", scale_factor=1.0))
        resetaction.setToolTip("Preferences")
        actionTools.triggered.connect(lambda: self.guiclicked("preferences"))
        menuBar.addAction(actionTools)

        menuTools = menuBar.addMenu(menuBar.titles[0])
        menuLog = menuBar.addMenu(menuBar.titles[1])
        menuView = menuBar.addMenu(menuBar.titles[2])

        resetTools = QtWidgets.QAction(self.gui)
        resetTools.setIcon(qta.icon("ei.refresh", color="white", scale_factor=1.0))
        resetTools.setText("reset Lab Control")
        resetTools.triggered.connect(self.reset)
        menuTools.addAction(resetTools)

        actionProgress = QtWidgets.QAction(self.gui)
        actionProgress.setText("    Progress")
        actionProgress.setCheckable(True)
        actionProgress.setEnabled(True)
        menuView.addAction(actionProgress)
        actionProgress.triggered.connect(lambda: self.guiclicked("progress"))
        self.actionProgress = actionProgress

        actionSequencer_Parameters = QtWidgets.QAction(self.gui)
        actionSequencer_Parameters.setText("    Shmoo Parameters")
        actionSequencer_Parameters.setCheckable(True)
        actionSequencer_Parameters.setEnabled(True)
        menuView.addAction(actionSequencer_Parameters)
        actionSequencer_Parameters.triggered.connect(lambda: self.guiclicked("sequencer"))
        self.actionSequencer_Parameters = actionSequencer_Parameters

        actionClrProTime = QtWidgets.QAction(self.gui)
        actionClrProTime.setText("Clear progress timing")
        menuLog.addAction(actionClrProTime)
        actionClrProTime.triggered.connect(self.progressbar.clrProTime)
        menuLog.addSeparator()

        actionclearLog = QtWidgets.QAction(self.gui)
        actionclearLog.setText("Clear log")
        actionclearLog.setIcon(
            qta.icon(
                "ei.trash",
                color="white",
                scale_factor=1.0,
                color_active="orange",
            )
        )
        menuLog.addAction(actionclearLog)
        actionclearLog.triggered.connect(lambda: self.guiclicked("clear"))

        actionload_File = QtWidgets.QAction(self.gui)
        actionload_File.setText("Open logfile")
        actionload_File.setIcon(
            qta.icon(
                "ei.file",
                color="white",
                scale_factor=1.0,
                color_active="orange",
            )
        )
        menuLog.addAction(actionload_File)
        actionload_File.triggered.connect(lambda: self.guiclicked("openlog"))
        menuLog.addSeparator()

        actiondebug = QtWidgets.QAction(self.gui)
        actiondebug.setText("debug Lab Control")
        actiondebug.setCheckable(True)
        actiondebug.setEnabled(True)
        menuLog.addAction(actiondebug)
        actiondebug.triggered.connect(lambda: self.guiclicked("debug"))
        self.actiondebug = actiondebug

        # set connect:
        self.gui.RBdebug.clicked.connect(lambda: self.logging(self.logging_cmd_reload))
        self.gui.RBmeasure.clicked.connect(lambda: self.logging(self.logging_cmd_reload))
        self.gui.RBinfo.clicked.connect(lambda: self.logging(self.logging_cmd_reload))
        self.gui.RBwarning.clicked.connect(lambda: self.logging(self.logging_cmd_reload))
        self.gui.RBerror.clicked.connect(lambda: self.logging(self.logging_cmd_reload))
        self.gui.CBholdonbreak.clicked.connect(lambda: self.saveconfig("holdonbreak"))  # CB = QCheckBox
        self.gui.CBstartauto.clicked.connect(self.saveconfig)
        self.gui.CBstopauto.clicked.connect(self.saveconfig)
        self.gui.CBstoponfail.clicked.connect(
            lambda: self.changeconfig(
                self.gui.CBstoponfail.isChecked(),
                "command.next.job_data.stop_on_fail.active",
            )
        )
        self.menuBar = menuBar
        self.gui.newMenu = []
        self.change_status_display.connect(self._change_status_display)
        self.gui.Gsequencer.hide()
        self.gui.Gprogress.hide()

    def _createFilterMenu(self):
        self.gui.GBfilter.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.gui.rb_onlyerrorAction = QtWidgets.QAction(self.gui)
        self.gui.rb_allAction = QtWidgets.QAction(self.gui)
        self.gui.rb_lastAction = QtWidgets.QAction(self.gui)
        self.gui.rb_onlyerrorAction.setText("only &Error")
        self.gui.rb_allAction.setText("&All")
        self.gui.rb_lastAction.setText("&Last")
        self.gui.GBfilter.addAction(self.gui.rb_onlyerrorAction)
        self.gui.GBfilter.addAction(self.gui.rb_allAction)
        self.gui.GBfilter.addAction(self.gui.rb_lastAction)
        self.gui.rb_onlyerrorAction.triggered.connect(lambda: self.filterMenuClicked("onlyerror"))
        self.gui.rb_allAction.triggered.connect(lambda: self.filterMenuClicked("all"))
        self.gui.rb_lastAction.triggered.connect(lambda: self.filterMenuClicked("last"))

    def _createSeqMenu(self):
        self.gui.Gsequencer.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        resetSeqAction = QtWidgets.QAction(self.gui)
        resetSeqAction.setText("Set All to start values")
        self.gui.Gsequencer.addAction(resetSeqAction)
        resetSeqAction.triggered.connect(self.sequencer.setfirstvalue)

    def reset(self):
        self.logger.debug("Reset Lab Control")
        self.setButtonActive(False)
        self.progressbar.finish(False)
        self.cycle = 0
        self._state = "reset"
        self.state = "reset"
        self.lasttime = "unknown"
        self.error_cnt = 0
        self.warning_cnt = 0
        self.last_mqtt_time = time.time()
        self.wait4answer = False

    # mqtt messages:
    def mqtt_send(self, topic, cmd):
        """Send messages via mqtt."""
        if cmd in self.command:
            msg = self.command[cmd]
            topic = self.sendtopic + topic
            self.mqtt.publish(topic, msg)
            self.change_status_display.emit("send " + str(msg["command"] + ", wait for answer"), "")
            self.logger.debug("Lab Control.mqtt_send {}:{}".format(topic, msg))
            self.wait4answer = True
        else:
            self.error(f"Lab Control.mqtt_send {topic}:{cmd} not found in list")

    def mqtt_receive(self, topic, msg):
        """
        Received mqtt-messages as json.

        this is a QtCore.pyqtSignal
        """
        try:
            msg = json.loads(msg)
        except Exception as ex:
            self.logger.error(f"mqtt_receive '{topic}: {msg}' with error {ex}")
            return
        topicsplit = topic.split("/")
        notfound = False
        if len(topicsplit) > 2 and topicsplit[1] == self.computername:  # received a message from an instrument ?
            if topicsplit[2] == mqtt.TOPIC_INSTRUMENT:
                self.mqttReiveMyname(topic, msg)
            elif topicsplit[2] != mqtt.TOPIC_CONTROL:
                notfound = True
        elif type(msg) is dict and "type" in msg:  # received a message from controlling
            self.mqttReceiveSemictrl(topic, msg)
        else:
            notfound = True
        if notfound:
            self.logger.warning(f"mqtt_receive '{topic}: {msg}' don_t know what to do with this message")

    def mqttReiveMyname(self, topic, msg):
        """
        call if a message from an instrument, or from semictrl (is also a instrument) received.

        """
        self.logger.debug(f"mqttReiveMyname {topic}, {msg}")
        if type(msg) is dict and self.SemiCtrlinstName in msg:  # receive a message for semictrl
            msg = msg[self.SemiCtrlinstName]
            if msg["type"] == "cmd" and msg["cmd"] == "breakpoint":
                if msg["payload"] is None:
                    self.mqtt.publish_set(
                        self.SemiCtrlinstName,
                        "_breakpoint",
                        self.gui.CBholdonbreak.isChecked(),
                    )
                elif msg["payload"] == "hold":
                    self.change_status_display.emit("breakpoint", "")
                elif msg["payload"] == "testing":
                    self.change_status_display.emit("testing", "")
            elif msg["type"] == "cmd" and msg["cmd"] == "topinstname":
                self.topinstname = msg["payload"]
            if msg["type"] == "cmd" and msg["cmd"] == "menu":  # get command to extend Menu
                pindex = -1
                for addmenu in msg["payload"]:
                    # the syntax is {'payload': {'Instruments': '', 'scope': 'gui.instruments.softscope.softscope'}}
                    pindex += 1
                    found = False
                    if pindex == 0 and addmenu not in self.gui.menuBar.titles:  # add new Menu Title
                        self.gui.newMenu.append(QtWidgets.QMenu(addmenu, self.gui))
                        self.gui.newMenu[-1].instance = None
                        self.gui.menuBar.addMenu(self.gui.newMenu[-1])
                        self.gui.menuBar.titles.append(addmenu)
                        mindex = pindex
                        found = True
                    elif pindex == 0:  # Menu Title already exist
                        self.logger.debug(f"     Menu Title {addmenu} already exist, do nothing")
                        continue
                    else:  # create/update submenue
                        self.logger.debug(f"     add/update menu: {addmenu}")
                        mindex = 0
                        for menu in self.gui.newMenu:  # menu exist?
                            if hasattr(menu, "name") and menu.name == addmenu:
                                found = True
                                break
                            mindex += 1
                        self.logger.debug(f"     found: {found}")
                        if found:
                            self.logger.debug(f"     update menu: {addmenu}")
                            lib = msg["payload"][addmenu].split(".")[-1]
                            self.logger.debug(f"     reload lib {lib} from {msg['payload'][addmenu]}")
                            self.logger.debug(f"     reload lib {str(self.gui.newMenu[mindex].lib)}")
                            try:
                                importlib.reload(self.gui.newMenu[mindex].lib)
                            except Exception as ex:
                                self.logger.error(f"    Coudn't reload lib {lib} from {msg['payload'][addmenu]}  {ex}")
                            continue
                        else:  # create menu: {addmenu} with action to lib {msg['payload'][addmenu]}
                            self.gui.newMenu.append(QtWidgets.QAction("   " + addmenu, self.gui))
                            try:
                                if msg["payload"][addmenu] != "":
                                    self.logger.debug(f"     importlib {msg['payload'][addmenu]}")
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
                    self.logger.debug("     add/update menu : done")
                    self.menuBar.adjustSize()
        elif type(msg) is dict and len(msg.keys()) == 1:  # received a message for a application in the extended Menu
            self.logger.debug(f"   message for the extended GUI received: '{topic}= {msg}'")
            for app in self.gui.newMenu:
                if not hasattr(app, "instance") or app.instance is None:
                    continue
                self.logger.debug(f"   {app.instance.topinstname}.{app.name}: subtopic: {app.instance.subtopic}")
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
                    self.logger.debug(f"    message for {app.name}: {cmd} = {msg} -->   ")
                    try:
                        if msg["type"] in ["set"] and hasattr(app.instance, cmd):  # set attribute
                            self.logger.debug(f"   begin set attribute {cmd}={value}")
                            app.instance.__setattr__(cmd, value)
                            self.logger.debug("   --> set attribute done")
                        elif msg["type"] in ["get"] and hasattr(app.instance, cmd):  # get attribute/function call
                            if value == []:  # it is a function call?
                                self.logger.debug(f"   begin call function {cmd}")
                                app.instance.__getattribute__(cmd)()
                                self.logger.debug("   --> call function done")
                            else:
                                self.logger.debug(f"   begin get/set attribute {cmd}={value}")
                                app.instance.__setattr__(cmd, value)  # get from extern is a set for displaying....
                                # app.instance.__getattribute__(cmd)
                                self.logger.debug("   --> begin get/set attribute done")
                            self.logger.debug("   function call done")
                        elif msg["type"] in ["set", "get"] and hasattr(app.instance, "mqttreceive"):  # implemented not as attribute/functioncall to get more information as only the payload
                            self.logger.debug(f"   call mqttreceive with {msg}")
                            app.instance.mqttreceive(name, msg)
                            self.logger.debug("   call mqttreceive done")
                        elif not hasattr(app.instance, cmd):
                            self.logger.warning(f"{name} hat no attribute: '{cmd} = {msg}'")
                        else:
                            self.logger.error(f"{name} I don't now what to do with this message: '{cmd} = {msg}'")
                    except Exception as ex:
                        self.logger.error(f"{name} something goes wrong: '{topic} = {msg}'  {ex}")
        else:
            pass
            self.logger.info(f"Info: semi_control.mqttReiveMyname '{topic}: {msg}' -> not implemented do nothing....")

    def mqttReceiveSemictrl(self, topic, msg):
        """
        Call if a message from ATE controlling received.

        for the received mqtt syntax: look at the comment at the beginning of the file
        """
        msgtype = msg["type"]
        self.last_mqtt_time = time.time()
        if msgtype == "cmd":  # command received
            if not self.wait4answer:
                pass
            else:
                if self.wait4answer and msg["command"] == "next" and self.state != "config":
                    self.logging(None)
                    self.display_result()
                self.logger.debug(f"actual state:{self.state} \n")
                self.wait4answer = False
        elif msgtype == "status" and "payload" in msg:  # status received
            mqttstate = msg["payload"]
            if "state" in msg:
                mqttstate = msg["state"]
            else:
                mqttstate = mqttstate["state"]
            if mqttstate.find("testing") > -1:  # test is running, so switch off the Button, function cancel is not yet implemented :-(
                self.cycle += 1
                self.setButtonActive(False)
            elif mqttstate.find("idle") > -1:  # testflow is starting or run through
                self.setButtonActive(True)
                if self.state in ["unknown", "init"]:
                    self.logging(None)
                    self.display_result()
                    self.gui.Llogfilename.setText("")
            self.logger.debug(f"semi_control.mqtt_receive: {mqttstate}")
            if mqttstate != "finish_seq":
                self.state = mqttstate
        elif msgtype == "log":
            msg = str(msg["payload"])
            msg = self.logfilter(msg, True)  # check the message if they should display on the gui
            if msg is not None:
                self.logging(msg)
        elif msgtype == "testresult":
            self.display_result(self.get_testresult(msg))
            # only for analyse, could be remove:
            with open("testresult.log", "w") as outfile:
                for index in msg["payload"]:
                    outfile.writelines(str(index))
                    outfile.write("\n")
        elif msgtype.find("io-control-") == 0:  # and "periphery_type" in msg:      # handle message from actuartors
            if topic.split("/")[2] == "TestApp" and msgtype == "io-control-request":
                newtopic = f"ate/{self.current_config.topic}/{msg['periphery_type']}/{topic.split('/')[3]}/{topic.split('/')[-1]}"
                self.mqtt.publish(newtopic, msg)
            elif topic.split("/")[2] != "Master" and msgtype == "io-control-response":
                newtopic = f"ate/{self.current_config.topic}/Master/{topic.split('/')[2]}/{topic.split('/')[-1]}"
                self.mqtt.publish(newtopic, msg)
        else:
            self.logger.warning(f"I don't know what should I do with this message: {msgtype}")

    def setButtonActive(self, value):
        """Activate all disabled buttons."""
        self.nextaction.setEnabled(value)
        self.terminateaction.setEnabled(value)
        self.resetaction.setEnabled(value)

    # logging and display:
    def extendedbarClicked(self, index):
        if index == 0:
            return
        self.logger.info(f"extendedbarClicked {index}")
        self.logger.info(f"     name = {self.gui.newMenu[index].name}")
        self.logger.info(f"     libname = {self.gui.newMenu[index].libname}")
        self.logger.info(f"     lib = {self.gui.newMenu[index].lib}")
        self.logger.info(f"     subtopic = {self.gui.newMenu[index].subtopic}")
        self.logger.info(f"     topinstname = {self.topinstname}")
        if self.gui.newMenu[index].isChecked():
            name = self.gui.newMenu[index].name
            if not hasattr(self.gui.newMenu[index], "lib") or self.gui.newMenu[index].lib is None:
                self.logger.error(f" Gui for {name} not exist, please update the LAB-ML adjutancy lib")
                self.gui.newMenu[index].instance = None
                self.gui.newMenu[index].setChecked(False)
                return
            importlib.reload(importlib.import_module("labml_adjutancy.gui.instruments.base_instrument"))
            importlib.reload(self.gui.newMenu[index].lib)
            self.gui.newMenu[index].instance = self.gui.newMenu[index].lib.Gui(self, name, self.project_info.parent)  # start Gui
            self.gui.newMenu[index].instance.subtopic = self.gui.newMenu[index].subtopic
            self.gui.newMenu[index].instance.topinstname = self.topinstname
            self.logger.debug(f" create {self.gui.newMenu[index].instance} done")
            self.logger.info(f"     geometry = {self.gui.newMenu[index].instance.gui.geometry()}")
            if "menu" in self.saveconfigdata and name in self.saveconfigdata["menu"] and len(self.saveconfigdata["menu"][name]) > 3 and self.gui.newMenu[index].instance is not None:
                self.set_Geometry(
                    name,
                    self.gui.newMenu[index].instance.gui,
                    self.saveconfigdata["menu"][name][2],
                )
            self.saveconfig()
        elif self.gui.newMenu[index].instance is not None:
            self.gui.newMenu[index].instance.close()
            self.gui.newMenu[index].instance = None
            self.saveconfig()

    def guiclicked(self, cmd):
        """Handle mouseclicks on a button."""
        if cmd == "clear":
            self.gui.TElogging.clear()
        elif cmd == "debug":
            self.logger.enable = self.actiondebug.isChecked()
        elif cmd == "openlog":
            path = os.path.join(self.project_info.project_directory, "log")
            self.logger.warning("Open explorer with: " + path)
            logfilename = QtWidgets.QFileDialog.getOpenFileName(self.gui, "Open Log", path, "log Files (*.log)")
            if logfilename[0] != "":
                self.logfilename = logfilename[0]
                self.readlog(self.logfilename)
                self.display_result()
        elif cmd == "preferences":
            from ate_spyder.widgets.actions_on.hardwaresetup.PluginConfigurationDialog import PluginConfigurationDialog

            dialog = PluginConfigurationDialog(self, self.plugin.NAME, self.current_config.dict().keys(), self.project_info.active_hardware, self.project_info, self.current_config.dict(), False)
            dialog.exec_()
            print(dialog.get_cfg())
            if dialog.get_cfg() is not None:
                self.project_info.store_plugin_cfg(self.project_info.active_hardware, self.plugin.NAME, dialog.get_cfg())
                del(dialog)
                self.mqtt.mqtt_disconnect()
                self.mqttclient.mqtt_disconnect()
                self.mqttclient.close()
                self.reset()
                self.setup_widget(self.project_info)
        elif cmd == "reset":
            self.logger.debug("Reset Lab Control")
            self.setButtonActive(True)
            self.state = "reset"
            self.progressbar.finish(False)
        elif cmd == "sequencer":
            self.logger.debug("change View Sequencer")
            if self.actionSequencer_Parameters.isChecked():
                self.gui.Gsequencer.show()
            else:
                self.gui.Gsequencer.hide()
        elif cmd == "updatesequencer":
            self.sequencer.load(self.project_info.project_directory, self.test_program_name)
        elif cmd == "progress":
            self.logger.debug("change View Progress")
            if self.actionProgress.isChecked():
                self.gui.Gprogress.show()
            else:
                self.gui.Gprogress.hide()
        elif cmd == "next" and self.state in [
            "idle",
            "finish_seq",
            "nothing_seq",
            "reset",
            "lognotexist",
        ]:
            last = True
            if self.actionSequencer_Parameters.isChecked():  # if sequencer window visible?
                (
                    self.command["SetParameter"]["parameters"],
                    last,
                ) = self.sequencer.getnext()  # than make the sequences
                if not last and self.command["SetParameter"]["parameters"] != []:
                    self.mqtt_send("cmd", "SetParameter")
                if last and self.command["SetParameter"]["parameters"] != []:
                    self.state = "finish_seq"
            else:
                self.command["SetParameter"]["parameters"] = []
            self.logger.debug(f"guiclicked('next') with {self.command['SetParameter']['parameters']}, last={last}")
            if not self.actionSequencer_Parameters.isChecked() or (not last and self.actionSequencer_Parameters.isChecked()) and self.command["SetParameter"]["parameters"] != []:
                self.mqtt_send("cmd", "next")
            elif last and self.actionSequencer_Parameters.isChecked() and self.command["SetParameter"]["parameters"] == []:
                self.state = "nothing_seq"
        else:
            self.state = (
                "error",
                f"Something is wrong with the cmd = {cmd} and state = {self.state}",
            )

    def filterMenuClicked(self, cmd):
        def lastRB(self):
            self.lastRB = {
                "debug": self.gui.RBdebug.isChecked(),
                "info": self.gui.RBinfo.isChecked(),
                "measure": self.gui.RBmeasure.isChecked(),
                "warning": self.gui.RBwarning.isChecked(),
                "error": self.gui.RBerror.isChecked(),
            }

        if cmd == "all":
            lastRB(self)
            self.gui.RBdebug.setChecked(False)
            self.gui.RBinfo.setChecked(True)
            self.gui.RBmeasure.setChecked(True)
            self.gui.RBwarning.setChecked(True)
            self.gui.RBerror.setChecked(True)
        elif cmd == "last" and hasattr(self, "lastRB"):
            self.gui.RBdebug.setChecked(self.lastRB["debug"])
            self.gui.RBinfo.setChecked(self.lastRB["info"])
            self.gui.RBmeasure.setChecked(self.lastRB["measure"])
            self.gui.RBwarning.setChecked(self.lastRB["warning"])
            self.gui.RBerror.setChecked(self.lastRB["error"])
        elif cmd == "onlyerror":
            lastRB(self)
            self.gui.RBdebug.setChecked(False)
            self.gui.RBinfo.setChecked(False)
            self.gui.RBmeasure.setChecked(False)
            self.gui.RBwarning.setChecked(False)
            self.gui.RBerror.setChecked(True)
        else:
            lastRB(self)
        self.logging(self.logging_cmd_reload)

    def logging(self, msg=None):
        """Log the message.

        msg could be also a cmd : '!RELOAD!' or '!LOAD!'
        if msg = None than clear the logging display
        """
        path = os.path.join(self.project_info.project_directory, "log", self.logfilename)
        if msg is None or msg == "":
            self.logger.debug("semi_control.logging: clear")
            self.gui.TElogging.clear()
        elif msg == "clr":
            self.logger.debug("semi_control.logging: clr")
            self.gui.TElogging.clear()
        elif msg in (self.logging_cmd_reload, "!LOAD!"):
            if self.project_info.active_hardware != "" and self.project_info.active_base != "":
                self.logger.debug(f"semi_control.logging: {msg}")
                if msg == "!LOAD!":
                    "logload"
                    self.display_result()
                else:
                    self.gui.TElogging.clear()
                self.readlog(path)
            if msg == self.logging_cmd_reload:
                self.logger.debug("    semi_control.logging: RELOAD")
                self.saveconfig()
        else:
            if msg.find("\r") == len(msg) - 1:
                msg = msg[:-1]
            # if html is not None:
            #    self.gui.TElogging.insertHtml(f'<{html}>')
            # self.gui.TElogging.insertHtml(msg + '<br>')
            # if html is not None:
            #    self.gui.TElogging.insertHtml(f'</{html}>')
            self.gui.TElogging.append(msg)
            # self.gui.TElogging.moveCursor(QtGui.QTextCursor.End)

    def getlatestlogfilename(self):
        import glob

        files = glob.glob(os.path.join(self.project_info.project_directory, "log", "*.log"))
        return max(files, key=os.path.getctime) if files != [] else ""

    def readlog(self, logfilename):
        """Read the log file with logfilename."""
        self.logger.debug("Open file " + logfilename)
        # self.gui.TElogging.clear()
        try:
            with open(logfilename, "r") as logfile:
                for line in logfile:
                    msg = self.logfilter(line)
                    if msg is not None:
                        self.gui.TElogging.append(msg)
        except Exception:
            self.state = "lognotexist"
            self.logfilename = ""
            self.gui.Llogfilename.setText(self.logfilename)
            return

    def logfilter(self, msg, progress=False):
        """
        Message filter, depends from Radiobuttons.

        search for Enter, Leave
        start Progressbar
        """
        search = "Enter"  # new testbench started
        if msg.split("|")[-1].find(search) == 0 and progress:
            testbenchname = msg[msg.find(search) + len(search) + 1 :]
            self.progressbar.start(testbenchname)
            return msg
        if msg.split("|")[-1].find("Leave") == 0 and progress:
            self.progressbar.stop()
            return msg
        result = None
        if msg.find("|ERROR") > 0:
            self.error_cnt += 1
            if self.state == "config":
                self.state = "configerror"
        elif msg.find("|WARNING") > 0:
            self.warning_cnt += 1
        if msg.find("|DEBUG   |") > 0 and self.gui.RBdebug.isChecked():
            result = msg
        elif msg.find("|INFO    |") > 0 and self.gui.RBinfo.isChecked():
            result = msg
        elif msg.find("|MEASURE |") > 0 and self.gui.RBmeasure.isChecked():
            result = msg
        elif msg.find("|WARNING |") > 0 and self.gui.RBwarning.isChecked():
            result = msg
        elif msg.find("|ERROR   |") > 0 and self.gui.RBerror.isChecked():
            result = msg
        if result is not None:
            if result[-1] == "\n":
                result = result[:-1]
            lasttime = result.split("|")
            if len(lasttime) > 2:
                self.lasttime = lasttime[1]
        return result

    @property
    def cycle(self):
        return self._cycle

    @cycle.setter
    def cycle(self, value):
        self._cycle = value
        if value > 0:
            self.gui.Lcycle.setText(f"cycle {value}")
        else:
            self.gui.Lcycle.setText("")

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
                pname = pname[pname.find(".") + 1 :]
                pvalue = parametername["value"]
                if (pname, pvalue) not in apara:
                    apara.append((pname, pvalue))
            dmsg = ""
            for val in apara:
                dmsg = dmsg + f"{val[0]}={val[1]}, "
            msg = dmsg[:-2] + msg
        self.logger.debug(f"semi_control.state = {value}, oldstate ={self._state}")
        oldstate = self._state
        self._state = value if value in self._states else "unknown"
        self.change_status_display.emit(value, msg)
        if value == "idle":
            logfilename = self.getlatestlogfilename()
            if logfilename != self.logfilename:
                self.logging("clr")
            self.logfilename = logfilename
            self.gui.Llogfilename.setText(self.logfilename)
        if value == "terminated":
            self.setButtonActive(False)
        if value.find("error") > -1:  # wo wird das gesetzt?? TODO: change!!
            self.progressbar.finish(False)
            self.setButtonActive(True)
        elif value == "config" or (value == "idle" and oldstate not in ("config", "testing")):  # start identify
            self.logger.debug("semi_control.state: config apply")
            self.cycle = 0
            self.display_result()
            if self.gui.CBstartauto.isChecked():
                self.logger.debug(f"semi_control.state: {value}, config apply, Auto is enabled -> send next")
                self.guiclicked("next")
        elif value == "idle" and oldstate in ("reset", "config", "testing") and self.actionSequencer_Parameters.isChecked() and self.gui.CBautoseq.isChecked():  # testprogramm runs through
            self.logger.debug("semi_control.state: idle, Auto sequence is enabled -> guiclicked(next)")
            self.guiclicked("next")
        elif value == "idle" and oldstate in ("reset", "config", "testing") and self.gui.CBstopauto.isChecked():  # testprogramm runs through
            self.logger.debug("semi_control.state: idle, Auto is enabled -> send terminate")
            self.mqtt_send("cmd", "terminate")

    # result:
    def get_testresult(self, msg):
        """Get the test results from the message."""
        hbin = -1
        result = ""
        if "payload" in msg:
            for mytype in msg["payload"]:
                if mytype["type"] == "PRR":
                    hbin = mytype["HARD_BIN"]
                    sbin = mytype["SOFT_BIN"]
            if hbin != -1:
                self.logger.debug(f"HBIN = {hbin}, SBIN = {sbin}")
        if hbin == 1:
            result = self.passmsg
        elif hbin != -1:
            result = f"unknown Fail ({hbin}/{sbin})"
            for bins in self.bin_table:
                if int(bins["HBIN"]) == hbin and int(bins["SBIN"]) == sbin:
                    result = f'{bins["GROUP"]} ({bins["SBINNAME"]})'
        return result

    def display_result(self, msg=None):
        """
        Display the msg in the Lresult field

        msg == None -> clear result display
        msg == 'pass' -> msg in green
            else -> msg in red
        """
        self.logger.debug(f"semi_control.display_result: {msg}")
        self.gui.Ldate.setText("Testresult from {}".format(self.lasttime))
        result = None
        if msg is None:
            self.gui.Ldate.setText("")
            self.gui.Lresult.setText("")
        elif msg != "":
            self.gui.Lresult.setText(msg)
        if msg == self.passmsg:
            result = True
            self.gui.Lresult.setStyleSheet("color: rgb(0, 0, 0);background-color: #00ff00")
        elif msg is not None and msg != "":
            self.gui.Lresult.setStyleSheet("color: rgb(0, 0, 0);background-color: #ff0000")
            result = not self.gui.CBstoponfail.isChecked()
        self.progressbar.finish(result)

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
            self.logger.warning(f"coudn't set last geometry for {name}, it is out of the actual screen")
            print(f"coudn't set last geometry for {name}, it is out of the actual screen")

    @QtCore.pyqtSlot(str, str)
    def _change_status_display(self, msg, extendmsg=""):
        self.logger.debug(f"       state = {msg}")
        style = self._states[msg][1] if msg in self._states else "color: rgb(255, 255, 255);background-color: transparent;"
        msg = self._states[msg][0] if msg in self._states else msg
        self.gui.Lstatus.setText(f"{extendmsg} {msg}")
        self.gui.Lstatus.setStyleSheet(style)

    def blockSignals(self, value):
        self.gui.CBstoponfail.blockSignals(value)
        self.gui.CBstartauto.blockSignals(value)
        self.gui.CBstopauto.blockSignals(value)
        self.gui.CBholdonbreak.blockSignals(value)
        self.gui.RBdebug.blockSignals(value)
        self.gui.RBmeasure.blockSignals(value)
        self.gui.RBinfo.blockSignals(value)
        self.gui.RBwarning.blockSignals(value)
        self.gui.RBerror.blockSignals(value)
        self.gui.rb_onlyerrorAction.blockSignals(value)
        self.gui.rb_allAction.blockSignals(value)
        self.gui.rb_lastAction.blockSignals(value)

    # configuration :
    def openconfig(self):
        """Open the configuration file c:users/$USER"""
        settings_dir = os.path.join(self.project_info.project_directory, "definitions", "lab_control")
        self.blockSignals(True)
        try:
            print(f"Control: open last settings: {os.path.join(settings_dir, self.configfile)}")
            with open(os.path.join(settings_dir, self.configfile), "r") as infile:
                data = json.load(infile)
            if __version__ != data["version"]:
                self.logger.warning(f'   {self.configfile}: wrong version = {data["version"]}, should be {__version__}')
            self.gui.RBdebug.setChecked(data["logging"]["debug"])
            self.gui.RBinfo.setChecked(data["logging"]["info"])
            self.gui.RBmeasure.setChecked(data["logging"]["measure"])
            self.gui.RBwarning.setChecked(data["logging"]["warning"])
            self.gui.RBerror.setChecked(data["logging"]["error"])
            self.gui.CBholdonbreak.setChecked(data["workaround"]["break"])
            self.gui.CBstartauto.setChecked(data["config"]["startauto"])
            self.gui.CBstopauto.setChecked(data["config"]["stopauto"])
            self.gui.CBstoponfail.setChecked(data["config"]["stoponfail"])
            self.actiondebug.setChecked(data["config"]["debug"])
            self.actionSequencer_Parameters.setChecked(data["view"]["sequencer"])
            self.actionProgress.setChecked(data["view"]["progress"])
            self.logfilename = data["result"]["logfilename"]
            self.sequencer.parameters = data["config"]["sequencer"]
            self.set_Geometry("semi-ctrl", self.gui, data["config"]["geometry"])
            self.logger.debug("   now create menu from the settings")
            if "menu" in data:
                menu = {}
                menu["type"] = "cmd"
                menu["cmd"] = "menu"
                menu["payload"] = data["menu"].copy()
                self.logger.debug(f"   read menue = {menu}")
                # syntax e.q. = {'payload': {'Instruments': '', 'scope': 'gui.instruments.softscope.softscope'}}
                for name in menu["payload"].keys():
                    if len(menu["payload"][name]) > 0:
                        menu["payload"][name] = menu["payload"][name][0]
                self.logger.debug(f"       {menu}")
                self.mqttReiveMyname("", {self.SemiCtrlinstName: menu})
                index = 0
                for app in self.gui.newMenu:
                    if app.libname != "":
                        app.setChecked(data["menu"][app.name][1])
                        if len(data["menu"][app.name]) > 3 and app.instance is not None:
                            app.subtopic = data["menu"][app.name][3]
                            app.instance.subtopic = app.subtopic
                    index += 1
            self.saveconfigdata = data
        except Exception as ex:
            print(f"{self.configfile}: {ex} not found or not ok -> use rest of default config")
            self.saveconfig()
            self.progressbar.load_testbenches_time("")
        self.gui.Llogfilename.setText(self.logfilename)
        self.guiclicked("debug")
        self.guiclicked("sequencer")
        self.guiclicked("progress")
        self.blockSignals(False)

    def saveconfig(self, button=None):
        """Save the configuration to configfile."""
        if self.project_info.project_directory == "":
            return
        data = {
            "version": __version__,
            "logging": {
                "debug": self.gui.RBdebug.isChecked(),
                "info": self.gui.RBinfo.isChecked(),
                "measure": self.gui.RBmeasure.isChecked(),
                "warning": self.gui.RBwarning.isChecked(),
                "error": self.gui.RBerror.isChecked(),
            },
            "config": {
                "startauto": self.gui.CBstartauto.isChecked(),
                "stopauto": self.gui.CBstopauto.isChecked(),
                "stoponfail": self.gui.CBstoponfail.isChecked(),
                "progname": self.test_program_name,
                "debug": self.actiondebug.isChecked(),
                "geometry": (
                    self.gui.geometry().x(),
                    self.gui.geometry().y(),
                    self.gui.width(),
                    self.gui.height(),
                ),
                "sequencer": self.sequencer.parameters,
            },
            "result": {
                "logfilename": self.logfilename,
            },
            "workaround": {
                "break": self.gui.CBholdonbreak.isChecked(),
            },
            "view": {
                "sequencer": self.actionSequencer_Parameters.isChecked(),
                "progress": self.actionProgress.isChecked(),
            },
            "menu": {},
        }
        mymenu = {}
        index = 0
        for app in self.gui.newMenu:
            # syntax = {'payload': {'Instruments': '', 'scope': 'gui.instruments.softscope.softscope'}}
            if index == 0:
                mymenu[app.name] = ""
            elif hasattr(app, "libname"):
                mymenu[app.name] = [app.libname, app.isChecked()]
                if app.instance is not None and hasattr(app.instance, "geometry"):
                    mymenu[app.name].append(
                        [
                            app.instance.geometry().x(),
                            app.instance.geometry().y(),
                            app.instance.width(),
                            app.instance.height(),
                        ]
                    )
                mymenu[app.name].append(app.subtopic)
            index += 1
        data["menu"] = mymenu
        settings_dir = os.path.join(self.project_info.project_directory, "definitions", "lab_control")
        if not os.path.exists(settings_dir):
            os.mkdir(settings_dir)
        self.logger.debug(f"write {os.path.join(settings_dir, self.configfile)}")
        with open(os.path.join(settings_dir, self.configfile), "w") as outfile:
            json.dump(data, outfile, indent=2)
        if button == "holdonbreak":
            if not self.gui.CBholdonbreak.isChecked():
                filetestbenchtime = os.path.join(
                    self.project_info.project_directory,
                    os.path.split(self.project_info.project_directory)[-1],
                    self.project_info.active_hardware,
                    self.project_info.active_base,
                    self.timefile,
                )
                self.progressbar.load_testbenches_time(filetestbenchtime)
            self.mqtt.publish_set(
                self.SemiCtrlinstName,
                "_breakpoint",
                self.gui.CBholdonbreak.isChecked(),
            )
        self.saveconfigdata = data

    def changeconfig(self, guiobject_value, cmd):
        """Assign the 'self.gui.object.connect()' to the dictionary 'self.command'."""
        cmd = cmd.split(".")
        mykey = getattr(self, cmd[0])
        iterations = len(cmd) - 1
        for index in range(1, iterations):
            mykey = mykey[cmd[index]]
        mykey[cmd[iterations]] = guiobject_value
        self.logger.debug(f"   changeconfig {cmd}")
        self.saveconfig()

    def load_json(self, filename):
        self.logger.debug(f"Open {filename} as json")
        if os.path.exists(filename):
            with open(filename, "r") as file:
                result = json.load(file)
        else:
            result = None
            self.logger.error(f"coudn't find {filename}")
        return result

    def appclosed(self, name):
        """Call from an instrumet if the instrument closed itself."""
        self.saveconfig()
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
                    self.saveconfigdata["menu"][app.name] = settings
                    self.saveconfig()

    def close(self, event=None):
        self.saveconfig()
        self.flagAppclosed = False
        super().close()

    def __del__(self):
        print("Semicontrol.__del__")
        self.close()
        super().__del__

    def debug_stop(self):
        ''' do update the state of lab control when the test application is stoped '''
