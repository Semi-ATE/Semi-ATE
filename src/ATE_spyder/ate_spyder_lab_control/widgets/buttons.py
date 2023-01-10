# -*- coding: utf-8 -*-
"""
Created on Thu Dec 23 09:17:01 2020

@author: ZLin526F

"""

import subprocess
import importlib
from time import sleep
import qtawesome as qta
from qtpy.QtCore import Signal
from PyQt5 import QtWidgets, QtCore
from pydantic import BaseModel
from labml_adjutancy.misc.common import kill_proc_tree
from ate_semiateplugins.pluginmanager import get_plugin_manager

__author__ = "Zlin526F"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"
__version__ = "0.0.1"


BUTTON_COLUMNS = 3  # define how many buttons are in one line


class ButtonConfig(BaseModel):
    lib: str
    gui: str


class Button(QtWidgets.QToolButton):
    """
     Buttons with Menu and Icon for Lab Gui
    """

    sytle_button = {'disabled': "color: rgb(128, 128, 128);",
                    'crash': "color: rgb(255, 64, 64);",
                    'instance_ok': "color: rgb(240, 240, 240);",
                    'available': "color: rgb(64, 164, 64);",
                    'connect': "color: rgb(64, 164, 64);",
                    'disconnect': "color: rgb(255, 64, 64);",
                    }

    def __init__(self, parent, instanceName, name, index):
        """Initialise the class Lab Button."""
        self.instanceName = instanceName
        self.name = name
        self.parent = parent
        self.mqtt = parent.mqtt
        self.logger = parent.logger
        super().__init__(parent.gui.frame)
        self.mystyle = self.sytle_button['disabled']

        self.setGeometry(QtCore.QRect(10, 10, 88, 60))
        self.setIconSize(QtCore.QSize(40, 40))
        self.guiLib = ''
        self.guiLibImport = None
        self.instance = None
        self.guiInstance = None
        self.move(index)
        if name is not None:
            displayname = f'{name}\n' if len(name) < 13 else f'{name[:12]}\n'
        else:
            displayname = instanceName
        self.setText(displayname)

        if instanceName == 'tester':
            instance = get_plugin_manager().hook.get_tester_type(tester_name=name)
            self.setToolTip(f'{self.name}')
            if len(instance) >= 1:
                instance = instance[0]
                self.mystyle = self.sytle_button['instance_ok']
            else:
                instance = None
                self.mystyle = self.sytle_button['crash']
        elif name is None:
            instance = None
            self.mystyle = self.sytle_button['instance_ok']
        else:
            instance = self.create_instance(False)

        self.menu = None if (instanceName == 'tester' or name is None) else QtWidgets.QMenu(self)
        if self.menu is not None:
            self.menu.setStyle(self.parent.style())
            self.menues = {}
            self.setPopupMode(QtWidgets.QToolButton.MenuButtonPopup)        # InstantPopup, MenuButtonPopup, DelayedPopup
            items = ["change lib", "terminate"] if self.instance is not None else ["change lib"]
            for item in items:
                menu_item = QtWidgets.QAction(self.menu)
                menu_item.setText(item)
                menu_item.triggered.connect(lambda item, function=item: self.menu_clicked(instanceName, function))
                self.addAction(menu_item)
                self.menues[item] = menu_item
        self.clicked.connect(self.button_clicked)
        self.setStyleSheet(self.mystyle)
        self.instance = instance
        self.subtopic = []
        self.show()

    def create_instance(self, setstyle=True):
        instance = None
        error = ""
        parameters = self.parent.get(self.parent.project_info.file_operator, self.parent.project_info.active_hardware).definition
        lib = parameters['Actuator'][self.parent.project_info.active_base][self.name]['lib']\
            if self.name in parameters['Actuator'][self.parent.project_info.active_base].keys() else ""
        self.guiLib = parameters['Actuator'][self.parent.project_info.active_base][self.name]['gui']\
            if self.name in parameters['Actuator'][self.parent.project_info.active_base].keys() else ""
        actuators_name = self.name.replace(' ', '_')
        actuators_lib = importlib.import_module(f'ate_test_app.actuators.{actuators_name}.{actuators_name}')
        self.instanceName = actuators_lib.periphery_type if hasattr(actuators_lib, 'periphery_type') else actuators_name
        del(actuators_lib)
        if lib != "":
            try:                                        # 1. try to import as module
                instance = importlib.import_module(lib)
                self.mystyle = self.sytle_button['instance_ok']
            except Exception as ex:         # ModuleNotFoundError
                error = ex
                self.mystyle = self.sytle_button['crash']
            if instance is None:                      # 2. call as subprocess
                instance = subprocess.Popen(lib, shell=True)
                sleep(0.2)
                if instance.poll() is None:
                    self.mystyle = self.sytle_button['instance_ok']
                else:
                    del(instance)
                    instance = None
        self.lib = lib
        if instance is not None:
            if hasattr(instance, 'icon'):
                self.setIcon(self.lib.icon)
            self.instance = instance
        elif instance is None:            # no gui for this module available
            self.setToolTip(f'{self.name} not available,\nlib = {self.lib if self.lib!= "" else "empty"}\n{error}')
        if setstyle:
            self.setStyleSheet(self.mystyle)
        return instance

    def set_gui(self, guiLib):
        self.guiLib = guiLib
        self.instance = ''
        self.name = self.instanceName
        #self.button_clicked()
        #self.guiInstance.hide()

    def msg2gui(self, topic, msg):
        if self.guiInstance is None:
            print(f"    {self.instanceName}.msg2gui: guiInstance is None ")
            return
        # print(f"   {app.instance.topinstname}  {app.name}: subtopic: {app.instance.subtopic}")
        name = None
        if len(self.subtopic) > 0:
            for subtopic in self.subtopic:
                if subtopic in msg.keys():
                    name = subtopic
        elif hasattr(self.guiInstance, "subtopic"):  # you can also add subtopic to a each GUI, e.q. scope also listen to 'regs'
            for subtopic in self.guiInstance.subtopic:
                if subtopic in msg.keys():
                    name = subtopic
        if self.name in msg.keys() and self.guiInstance is not None:
            name = self.name
        if name is not None:
            msg = msg[name]
            cmd = msg["cmd"]
            value = msg["payload"]
            print(f"    {self.instanceName}.msg2gui: {self.name}, {self.instance}, {topic}, {msg}")
            if cmd == 'mqtt_status':
                self.setStyleSheet(self.sytle_button[msg["payload"]])
                self.setToolTip(f"{self.instanceName} {msg['payload']}")
            try:
                if msg["type"] in ["set"] and hasattr(self.guiInstance, cmd):  # set attribute
                    self.guiInstance.__setattr__(cmd, value)
                elif msg["type"] in ["get"] and hasattr(self.guiInstance, cmd):  # get attribute/function call
                    if value == []:  # it is a function call?
                        self.guiInstance.__getattribute__(cmd)()
                    else:
                        self.guiInstance.__setattr__(cmd, value)  # get from extern is a set for displaying....
                elif msg["type"] in ["set", "get"] and hasattr(self.guiInstance, "mqttreceive"):  # get more information as only the payload
                    self.guiInstance.mqttreceive(name, msg)
                    msg = {}
                elif not hasattr(self.guiInstance, cmd):
                    print(f"Warning! {name} has no attribute: '{cmd} = {msg}'")
                else:
                    print(f"Error: {name} I don't now what to do with this message: '{cmd} = {msg}'")
            except Exception as ex:
                msg = f"{name} something goes wrong: '{topic} = {msg}'  {ex}"
                print(msg)
                self.logger.error(msg)

    def gui_disconnect(self):
        self.setStyleSheet(self.sytle_button["disconnect"])
        self.setToolTip(f"{self.instanceName} disconnect")
        if self.guiInstance is not None:
            print(f'{self.instanceName}.guiInstance disconnect')
            self.guiInstance.gui_disconnect()

    def display_msg(self, topic, msg):
        if 'status' in msg.keys():
            self.setStyleSheet(self.sytle_button[msg['status']])
            self.setToolTip(f"{self.instanceName} {msg['status']}")
            if msg['status'] == 'crash':
                self.menues['terminate'].setText('restart')
            elif msg['status'] == 'available':
                self.menues['terminate'].setText('terminate')
        elif 'ioctl_name' in msg.keys():
            text = self.text().split('\n')[0]
            tooltip = self.toolTip().split('\n')[0]
            value = msg['ioctl_name']
            if 'result' in msg.keys():
                value = f"{value}={msg['result']}"
            self.setText(f'{text}\n\n{value[:13]}')
            self.setToolTip(f'{tooltip}\n{value}')

    def button_clicked(self):
        if self.instance is not None:
            if self.guiLib != "" and self.guiLibImport is None:
                try:
                    self.guiLibImport = importlib.import_module(self.guiLib)
                    self.guiInstance = self.guiLibImport.Gui(self, self.name, self.parent.project_info.parent)  # start Gui
                    self.guiInstance.subtopic = self.subtopic
                    self.guiInstance.topinstname = self.name
                except Exception:
                    print(f'button {self.name} could not load gui={self.guiLib}')
                    self.state = 'nogui'
            elif self.guiInstance is not None and not self.guiInstance.isVisible():
                self.guiInstance.show()
            elif self.guiInstance is not None and self.guiInstance.isVisible():
                self.guiInstance.hide()
            elif self.guiInstance is None and self.guiLibImport is not None:
                print(f'button {self.name} reload {self.guiLibImport}')
                importlib.reload(self.guiLibImport)
                self.guiInstance = self.guiLibImport.Gui(self, self.name, self.parent.project_info.parent)

    def menu_clicked(self, name, function):
        if function == 'change lib':
            from ate_spyder.widgets.actions_on.hardwaresetup.PluginConfigurationDialog import PluginConfigurationDialog

            parameters = self.parent.get(self.parent.project_info.file_operator, self.parent.project_info.active_hardware).definition
            lib_type = guilib = ''
            if self.name in parameters['Actuator'][self.parent.project_info.active_base].keys():
                lib_type = parameters['Actuator'][self.parent.project_info.active_base][self.name]['lib']
                guilib = parameters['Actuator'][self.parent.project_info.active_base][self.name]['gui']
            default_parameter = {"lib": lib_type, "gui": guilib}
            current_config = ButtonConfig(**default_parameter)
            self.setStyle(self.parent.style())
            dialog = PluginConfigurationDialog(self, name, current_config.dict().keys(), self.parent.project_info.active_hardware,
                                               self.parent.project_info, current_config.dict(), False)
            dialog.exec_()
            newparameters = dialog.get_cfg()
            del(dialog)
            newparameters['lib'] = newparameters['lib'].strip()
            newparameters['gui'] = newparameters['gui'].strip()
            if newparameters != default_parameter:
                parameters['Actuator'][self.parent.project_info.active_base][self.name] = newparameters
                self.parent.update_definition(self.parent.project_info.file_operator, self.parent.project_info.active_hardware, parameters)
                kill_proc_tree(instance=self.instance)
                self.instance = self.create_instance()
        elif function == 'terminate':
            if self.instance is not None:
                kill_proc_tree(instance=self.instance)
                self.instance = None
            else:
                print(f'restart button {self.name}.....')
                self.instance = self.create_instance()

    def move(self, index):
        x, y = index % BUTTON_COLUMNS, index // BUTTON_COLUMNS
        super().move(x*100, y*70)
        self.show()

    def close(self):
        print(f'{self.name}.close()')
        if self.instanceName != 'tester':
            print(f'    kill {self.name} with {self.instance}')
            kill_proc_tree(instance=self.instance)
            self.instance = None
        if self.guiInstance is not None:
            self.guiInstance.close()
        super().close()
