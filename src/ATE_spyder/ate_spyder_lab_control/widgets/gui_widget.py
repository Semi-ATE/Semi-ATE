# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 09:17:01 2020

@author: ZLin526F

INFO:
    icons von https://github.com/spyder-ide/qtawesome

Todo:
    change path for setting (should not be in definitions)
    remove unnessary code

"""
import os
import time
import subprocess
import importlib
from time import sleep
import qtawesome as qta
import qdarkstyle
from PyQt5 import uic
from qtpy.QtCore import Signal
from PyQt5 import QtWidgets, QtCore

from qtpy.QtWidgets import QHBoxLayout
from spyder.api.translations import get_translation

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
from spyder.api.widgets.main_widget import PluginMainWidget
from ate_projectdatabase.Utils import DB_KEYS
from ate_projectdatabase.FileOperator import DBObject, FileOperator
from pydantic import BaseModel
from labml_adjutancy.misc.common import kill_proc_tree

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


class LabGuiButton(QtWidgets.QWidget):          #.QDialog
    def __init__(self, parent):
        super().__init__()
        uic.loadUi(os.path.dirname(__file__)+"\\guibutton_widget.ui", parent)

class LabGuiConfig(BaseModel):
    lib: str


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
    definition = {'Actuator': {'PR': {}, 'FT': {}}}
    sytle_button = {'disabled': "color: rgb(128, 128, 128);",
                    'crash': "color: rgb(255, 64, 64);",
                    'instance_ok': "color: rgb(64, 128, 64);",
                    'available': "color: rgb(64, 164, 64);"
                    }

    _states = {  # from extern mean: no handling from Lab Gui, normally you get this message if your are running the MiniSCTGui
        "init": [
            "testflow not started / no connection",
            "color: rgb(255, 165, 0)",
        ],
        "unknown": ["unknown", None],
        "error": ["error", "color: rgb(0, 0, 0);background-color: #ff0000"],
        "reset": ["reset Lab Gui", None],
    }

#    errormessages = {"unknown", "unknown"}

    command = {  # see https://github.com/Semi-ATE/Semi-ATE/blob/master/docs/project/interfacedefinitions/testapp_interface.md
        "SetParameter": {
            "type": "cmd",
            "command": "setparameter",
            "parameters": [],
            "sites": ["0"],
        },
    }
    # peripherie. e.q. Magnetfield:  {"type": "io-control-request", "periphery_type": "MagField", "ioctl_name": "set_field", "parameters": {"millitesla": 10}}
    # see: Tester\TES\apps\testApp\sequencers\SequencerHarness.py

    change_status_display = Signal(str, str)

    def __init__(self, name, plugin, parent=None):
        """Initialise the class Lab Gui."""
        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
        super().__init__(name, plugin, parent)
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
        self.lab_control = None
        self.flagAppclosed = False

    @staticmethod
    def get(session: FileOperator, name: str) -> DBObject:
        return session.query('lab_control')\
                       .filter(lambda Hardware: Hardware.name == name)\
                       .one()

    @staticmethod
    def add(session: FileOperator, name: str, definition: dict):
        hw = {
            DB_KEYS.HARDWARE.NAME: name,
            DB_KEYS.HARDWARE.DEFINITION.KEY(): definition,
        }
        session.query_with_subtype('lab_control', name).add(hw)
        session.commit()

    @staticmethod
    def remove(session: FileOperator, name: str):
        session.query('lab_control')\
                .filter(lambda Hardware: Hardware.name == name)\
                .delete()
        session.commit()

    def update_definition(self, session: FileOperator, name: str, definition: dict):
        hw = self.get(session, name)
        hw.definition = definition
        session.commit()

    def setup_widget(self, project_info):
        self.project_info = project_info
        self.update_actions()

    def setup(self):
        layout = QHBoxLayout()
        layout.addWidget(self.gui)
        self.setLayout(layout)

    def update_actions(self):
        from ate_projectdatabase.Hardware import Hardware

        for name in self.gui_icons.copy():
            self.remove_button(name)
        if self.project_info is None:
            return
        if self.lab_control is None and hasattr(self.project_info, 'lab_control'):
            self.lab_control = self.project_info.lab_control
            self.lab_control.receive_msg_for_instrument.connect(self.receive_msg_for_instrument)
            self.mqtt = self.lab_control.mqtt
            self.logger = self.lab_control.logger
        hw = self.project_info.active_hardware
        base = self.project_info.active_base
        if hw is None or hw == '':
            return
        hardware_def = Hardware.get(self.project_info.file_operator, hw).definition
        tester_name = hardware_def['tester']
        actuators = hardware_def['Actuator'][base]
        self.create_button('tester', tester_name)
        try:
            self.get(self.project_info.file_operator, hw).definition
        except AssertionError:
            self.add(self.project_info.file_operator, hw, self.definition)
        for actuator_name in actuators:   # todo: actuartors see https://github.com/Semi-ATE/Semi-ATE/blob/master/docs/project/DevelopmentProcess/development_setup.md
            self.create_button(None, actuator_name)    # and https://github.com/Semi-ATE/TCC_actuators

    def remove_button(self, name):
        button = self.gui_icons[name]
        if button.instance is not None and name != 'tester':
            kill_proc_tree(instance=button.instance)
        button.destroy()
        button.deleteLater()
        self.gui_icons.pop(name)

    def create_button(self, instanceName, name, xy=None):
        from ate_semiateplugins.pluginmanager import get_plugin_manager

        style = self.sytle_button['disabled']
        error = ""
        if instanceName == 'tester':
            instance = get_plugin_manager().hook.get_tester_type(tester_name=name)
            if len(instance) >= 1:
                instance = instance[0]
                style = self.sytle_button['instance_ok']
            else:
                instance = None
                style = self.sytle_button['crash']
        else:
            instance = None
            lib_types = self.get(self.project_info.file_operator, self.project_info.active_hardware).definition
            lib = lib_types['Actuator'][self.project_info.active_base][name]\
                if name in lib_types['Actuator'][self.project_info.active_base].keys() else ""
            actuators_name = name.replace(' ', '_')
            actuators_lib = importlib.import_module(f'ate_test_app.actuators.{actuators_name}.{actuators_name}')
            instanceName = actuators_lib.periphery_type if hasattr(actuators_lib, 'periphery_type') else actuators_name
            del(actuators_lib)
            # lib = 'magfield-dummy 127.0.0.1 1883 devlopmode 192.168.1.1 21324'
            if lib != "":
                try:                                        # 1. try to import as module
                    instance = importlib.import_module(lib)
                    style = self.sytle_button['instance_ok']
                except Exception as ex:         # ModuleNotFoundError
                    error = ex
                    style = self.sytle_button['crash']
                if instance is None:                      # 2. call as subprocess
                    instance = subprocess.Popen(lib, shell=True)
                    sleep(0.2)
                    if instance.poll() is None:
                        style = self.sytle_button['instance_ok']
                    else:
                        del(instance)
                        instance = None
        if instanceName not in self.gui_icons:                      # create new icon button
            if xy is None:
                x, y = len(self.gui_icons) % 2, len(self.gui_icons) // 2
            else:
                x, y = xy
            button = QtWidgets.QToolButton(self.gui.frame)
            #button = LabGuiButton(self.gui.frame)
            button.setGeometry(QtCore.QRect(10, 10, 88, 60))
            button.setIconSize(QtCore.QSize(40, 40))
            button.name = name
            button.instanceName = instanceName
            button.lib = None
            button.instance = None
            button.move(x*100, y*70)
            button.xy = x, y
            self.gui_icons[instanceName] = button
        else:                                                        # use existing icon button
            button = self.gui_icons[instanceName]
            if self.gui_icons[instanceName].lib is not None:
                importlib.reload(button.lib)

        displayname = f'{name}\n' if len(name) < 12 else f'{name[:11]}\n'   # {name[11:]}\n
        button.setText(displayname)
        menu = QtWidgets.QMenu(button) if instanceName != 'tester' else None

        if hasattr(instance, 'gui'):
            button.gui = importlib.import_module(instance.gui)
            button.setToolTip(name)
            style = self.sytle_button['available']
        else:
            button.setToolTip(f'no detailed Gui available for {name}')
        if instance is not None:
            if hasattr(instance, 'icon'):
                button.setIcon(button.lib.icon)
            button.instance = instance
        elif instance is None:            # no gui for this module available
            button.setToolTip(f'{name} not available,\nlib = {lib if lib!= "" else "empty"}\n{error}')
        button.setStyleSheet(style)
        if menu is not None:
            button.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)        # InstantPopup, MenuButtonPopup, DelayedPopup
            menu_action = QtWidgets.QAction(self.gui)
            menu_action.setText("change lib")
            menu_action.triggered.connect(lambda: self.buttonMenuClicked(instanceName, "change lib"))
            button.addAction(menu_action)
        button.clicked.connect(lambda checked, name=instanceName: self.icon_button_clicked(instanceName))
        button.subtopic = []
        button.show()

    def get_title(self):
        return _("Lab Gui")

    def update_labgui(self, test_program_name):
        self.update_actions()
        # self.state = 'testing'

    def show(self):
        super().show()
        index = 0
        for app in self.gui.newMenu:
            if hasattr(app, "libname") and app.libname != "":
                self.extendedbarClicked(index)
            index += 1
        self.flagAppclosed = True

    def adjustUI(self):
        self.gui.frame.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        # set Menubar
        menuBar = QtWidgets.QMenuBar(self)
        self.menuBar = menuBar
        menuBar.titles = []

        # set connect:
        self.gui.newMenu = []

    def reset(self):
        print("Reset Lab Gui")
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
        # print(f"Lab Gui.receive_msg_for_instrument: {topic}, {msg}")
        if type(msg) is dict and "type" in msg and msg["type"] == "cmd" and msg["cmd"] == "menu":  # get command to extend Menu
            pindex = -1
            for addmenu in msg["payload"]:
                # the syntax is {'payload': {'Instruments': '', 'scope': 'gui.instruments.softscope.softscope'}}
                pindex += 1
                found = False
                if addmenu == 'tester':
                    continue
# todo: this part should be replaced with creating a button icon
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
# end: to be replace....
        elif type(msg) is dict and len(msg.keys()) == 1:  # received a message for a application in the extended Menu
            print(f"   message for the extended GUI received: '{topic}= {msg}'")
# should be replaced:
            for app in self.gui.newMenu:
                self.transfer2gui(app, topic, msg)
# end
            instanceName = list(msg.keys())[0]
            if instanceName not in self.gui_icons:
                instanceName = topic.split("/")[2]
            if instanceName in self.gui_icons:
                self.msg2button(self.gui_icons[instanceName], topic, msg)
        elif topic.split("/")[2] in self.gui_icons:
            self.msg2button(self.gui_icons[topic.split("/")[2]], topic, msg)

    def msg2button(self, button, topic, msg):
        if 'status' in msg.keys():
            button.setStyleSheet(self.sytle_button[msg['status']])
            button.setToolTip(f"{button.instanceName} {msg['status']}")
        elif 'ioctl_name' in msg.keys():
            text = button.text().split('\n')[0]
            value = msg['ioctl_name']
            if 'result' in msg.keys():
                value = f"{value}={msg['result']}"
            button.setText(f'{text}\n\n{value[:13]}')
            print(f'msg2button {topic}, {msg}')

    def transfer2gui(self, app, topic, msg):
        if not hasattr(app, "instance") or app.instance is None:
            return
        print(f"    transfer2gui: {app.instance}, {topic}, {msg}")
        #print(f"   {app.instance.topinstname}  {app.name}: subtopic: {app.instance.subtopic}")
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
            try:
                if msg["type"] in ["set"] and hasattr(app.instance, cmd):  # set attribute
                    app.instance.__setattr__(cmd, value)
                elif msg["type"] in ["get"] and hasattr(app.instance, cmd):  # get attribute/function call
                    if value == []:  # it is a function call?
                        app.instance.__getattribute__(cmd)()
                    else:
                        app.instance.__setattr__(cmd, value)  # get from extern is a set for displaying....
                elif msg["type"] in ["set", "get"] and hasattr(app.instance, "mqttreceive"):  # get more information as only the payload
                    app.instance.mqttreceive(name, msg)
                    msg = {}
                elif not hasattr(app.instance, cmd):
                    print(f"Warning! {name} hat no attribute: '{cmd} = {msg}'")
                else:
                    print(f"Error: {name} I don't now what to do with this message: '{cmd} = {msg}'")
            except Exception as ex:
                msg = f"{name} something goes wrong: '{topic} = {msg}'  {ex}"
                self.logger.error(msg)
                print(msg)

    def icon_button_clicked(self, name):
        button = self.gui_icons[name]
        print(name)
        if button.instance is None:
            if button.lib is not None:
                importlib.reload(button.lib)
                button.instance = button.lib.Gui(self, name, self.project_info.parent)  # start Gui
                button.instance.subtopic = button.subtopic
                button.instance.topinstname = name

    def buttonMenuClicked(self, name, function):
        print(f'buttonMenuClicked  {name}, {function}')
        from ate_spyder.widgets.actions_on.hardwaresetup.PluginConfigurationDialog import PluginConfigurationDialog

        actuator_name = self.gui_icons[name].name
        lib_types = self.get(self.project_info.file_operator, self.project_info.active_hardware).definition
        lib_type = lib_types['Actuator'][self.project_info.active_base][actuator_name]\
            if actuator_name in lib_types['Actuator'][self.project_info.active_base].keys() else ""
        default_parameter = {"lib": lib_type}
        current_config = LabGuiConfig(**default_parameter)
        dialog = PluginConfigurationDialog(self, name, current_config.dict().keys(), self.project_info.active_hardware,
                                           self.project_info, current_config.dict(), False)
        dialog.exec_()
        newlib_type = dialog.get_cfg()['lib'].strip()
        del(dialog)
        if newlib_type != lib_type:
            lib_types['Actuator'][self.project_info.active_base][actuator_name] = newlib_type
            self.update_definition(self.project_info.file_operator, self.project_info.active_hardware, lib_types)
            xy = self.gui_icons[name].xy
            self.remove_button(name)
            self.create_button(None, actuator_name, xy)

    # display:
    def extendedbarClicked(self, index):
        if index == 0:
            return
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
        print(f"Lab Gui.state = {value}, oldstate ={self._state}")
        oldstate = self._state
        self._state = value if value in self._states else "unknown"
        self.change_status_display.emit(value, msg)

    # def set_Geometry(self, name, gui, geometry):
    #     found = False
    #     for i in range(0, QtWidgets.QDesktopWidget().screenCount()):
    #         screen = QtWidgets.QDesktopWidget().screenGeometry(i)
    #         if screen.x() < geometry[0] and screen.y() < geometry[1]:
    #             found = True
    #     if found:
    #         gui.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
    #         print(f"{name}.set_Geometry({geometry[0]}, {geometry[1]}, {geometry[2]}, {geometry[3]})")
    #     else:
    #         print(f"coudn't set last geometry for {name}, it is out of the actual screen")

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
            if name in self.gui.newMenu:
                app = self.gui.newMenu[name]
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
                app.instance = None
        elif name in self.gui_icons:
            self.gui_icons[name].instance = None

    def close(self, event=None):
        for name in self.gui_icons.copy():
            self.remove_button(name)
        self.flagAppclosed = False
        super().close()

    def __del__(self):
        print("Lab Gui.__del__")
        self.close()
        super().__del__

    def debug_stop(self):
        ''' do update the state of lab gui when the test application is stoped '''
        pass


if __name__ == "__main__":
    from ate_spyder.widgets.navigation import ProjectNavigation
    from PyQt5.QtWidgets import QApplication
    from qtpy.QtWidgets import QMainWindow
    import sys

    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    app.references = set()
    main = QMainWindow()
    homedir = os.path.expanduser("~")
    project_directory = homedir + r'\ATE\packages\envs\semi-ate-awinia1\HATB'       # path to your semi-ate project
    project_directory = homedir + r'\Work Folders\Projecte\Repository\hatc\0203\units\lab\source\python\HATC'
    project_info = ProjectNavigation(project_directory, homedir, main)
    project_info.active_hardware = 'HW0'
    project_info.active_base = 'FT'
    project_info.active_target = 'Device1'

    main.NAME = 'lab_gui'
    main.WIDGET_CLASS = LabGui
    main.CONF_SECTION = main.NAME

    labgui = LabGui('Lab Gui', main, main)
    labgui.setup_widget(project_info)
    main.show()
    sys.exit(app.exec_())
