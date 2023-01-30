# -*- coding: utf-8 -*-
"""
Created on Tue Feb 18 09:52:09 2020

@author: C. Jung

Bugs:
    wenn device ohne close in spyder beendet wird, so ist
    thread mqtt_deviceattributes._mqtt_message weiterhin aktiv

todo:

"""

import time
import platform
import json
from abc import abstractmethod
import paho.mqtt.client as mqttc
import socket
from .singleton import Singleton
from PyQt5 import QtCore
from labml_adjutancy.misc import common

__author__ = "Zlin526F"
__copyright__ = "Copyright 2020, Lab"
__credits__ = ["Zlin526F"]
__email__ = "Zlin526F@github"
__version__ = "0.0.1"


TOPIC_PREFIX = "ate"
TOPIC_CONTROL = "semictrl"
TOPIC_INSTRUMENT = "instruments"
TOPIC_INSTNAME = "tcc"


class mylogger(object):
    def __init__(self, output=None, enable=False, parent=None):
        self.output = output
        self.enable = enable
        self.parent = parent

    def debug(self, msg):
        if not self.enable:
            return
        self.display("DEBUG", msg)

    def info(self, msg):
        if not self.enable:
            return
        self.display("INFO", msg)

    def measure(self, msg):
        if not self.enable:
            return
        self.display("MEASURE", msg)

    def warning(self, msg):
        self.display("WARNING", msg)

    def error(self, msg):
        self.display("ERROR", msg)

    def display(self, typ, msg):
        msg = f"{self.parent} {typ} | {msg}"
        if self.output is None:
            print(msg)
        else:
            self.output.append(msg)

    def log_message(self, level, msg):
        self.display(level, msg)


class mqtt_init(object, metaclass=Singleton):
    """Initialise the mqtt connection and provide functions for the communication."""

    def __init__(self, typ="control", logger=None):
        """Initialise the class mqtt_init.

        typ = 'instrument' for instruments
            = 'control' for guis or extern controlling (default)
        """

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                msg = f"MQTT Broker {self.broker}, user {self.username} connected"
                self.logger.info(msg)
            elif rc == 5:
                msg = f"MQTT Broker {self.broker}, user {self.username} authentication error"
                self.logger.error(msg)
            else:
                msg = f"MQTT Broker {self.broker},  user {self.username} connection failed ({mqttc.connack_string(rc)})"
                self.logger.error(msg)

        def on_disconnect(client, userdata, rc):
            msg = "MQTT Broker {} user {} disconnected".format(
                self.broker, self.username
            )
            if rc > 0:
                msg += ", {}".format(mqttc.connack_string(rc))
            print(msg)

        self.typ = typ
        self.broker = ""
        self.username = ""
        self.qos = 0
        self.retain = False
        if logger is not None:
            self.logger = logger
        else:
            self.logger = mylogger(parent=self.typ)  # enable=True
        self.mqttreceive = mqtt_signal()
        client = mqttc.Client(clean_session=True)
        client.enable_logger(logger=None)
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        self.client = client
        self.instruments = {}

    def init(
        self,
        broker="127.0.0.1",
        port=1883,
        message_client=None,
        username="",
        userpasswd="",
        qos=0,
        retain=False,
    ):
        """
        Normally call from plugin semi-control, you have not to call this function, if you use semi-control.

        message_client = None if client the instrument, like e.q. smu, digital-multimeter or thermostreamer.
                       = e.q. 'DT1604092' if control and you want connect from an extern computer to DT1604092 (but is not checked until now!!)
        """
        import socket

        self.qos = qos
        self.retain = retain
        self.username = username
        self.hostname = socket.gethostname()
        if broker.find(".") > 0:
            self.broker = broker
        else:
            self.broker = socket.gethostname(broker)
        if username != "":
            self.client.username_pw_set(username, password=userpasswd)
        try:
            self.client.connect(
                self.broker, port, 60
            )  # blocking until connection establish or timeout
        except Exception:
            self.logger.error(
                "ERROR: MQTT couldn't connect to broker {}".format(self.broker)
            )
            self.topic = message_client
            return False
        self.client.loop_start()
        if message_client is None:
            message_client = f"{TOPIC_PREFIX}"
        self.client.subscribe(f"{message_client}/#", qos=qos)
        self.logger.info(
            f"{self.__class__.__name__}.init: subscribe for {message_client}/#"
        )
        self.topic = message_client
        self.instruments = {}
        return True

    def mqtt_add(self, instrument, hostname=None):
        """
        Add first callback to get mqtt-commands from control, and append instrument to instruments-list.

        Returns:
            None.
        """
        if not hasattr(self, "hostname"):
            return
        if hostname is None:
            hostname = self.hostname
        if self.instruments == {}:
            if hostname == "":
                callback = f"{TOPIC_PREFIX}/#"
            else:
                callback = f"{TOPIC_PREFIX}/{hostname}/{TOPIC_CONTROL}/#"
            self.client.message_callback_add(callback, self._mqtt_message)
            self.logger.debug(
                f"{self.__class__.__name__}.mqtt_add: watching for {callback}"
            )
        self.instruments[instrument.instName] = instrument
        self.logger.debug(
            f"{self.__class__.__name__}.mqtt_add: add {instrument.instName} to instruments-list"
        )

    def mqtt_disconnect(self, instrument=None, hostname=None):
        """
        Remove instrument from the instruments-list, if instruments-list is empty than remove callback.

        Returns:
            None.
        """
        if hostname is None:
            if not hasattr(self, "hostname"):
                return
            hostname = self.hostname
        if instrument is not None and instrument.instName in self.instruments.keys():
            self.instruments.pop(instrument.instName)
        if self.instruments == {}:
            callback = f"{TOPIC_PREFIX}/{self.hostname}/{TOPIC_CONTROL}/#"
            self.client.message_callback_remove(callback)  # remove subscribe
            self.logger.debug(
                f"{self.__class__.__name__}.mqtt_disconnect: remove watching for {callback}"
            )

    def _mqtt_message(self, client, userdata, message):
        """
        Automatically call, if message received from broker.

          if message from an instrument than send it via channel to mqtt_receive in your application
          else if message from control than call functions/attribute from the instrument
        """
        # if self.mqtt_debug: print('{}.mqtt_message value/payload:  {} = {}'.format(self.__class__.__name__,message.topic,value))
        msg = message.payload.decode("utf-8", "ignore")
        try:
            payload = json.loads(str(msg))
        except Exception:
            # print("failed:",type(value))
            payload = msg
        endtopic = message.topic.split("/")[-1]
        if (
            self.typ == "control"
            and type(payload) is dict
            and endtopic != TOPIC_CONTROL
        ):  # message from an instrument received -> send it to a GUI or control
            self.mqttreceive.channel.emit(message.topic, msg)
        elif (
            self.typ == "instrument"
            and type(payload) is dict
            and endtopic == TOPIC_CONTROL
        ):  # message from control received, call function from instrument
            instname = list(payload.keys())[0]
            payload = payload[instname]
            if instname == TOPIC_INSTNAME:
                instname = payload["cmd"][0]
                payload["cmd"].pop(0)
            if instname in self.instruments:
                instrument = self.instruments[instname]
            else:
                if "cmd" in payload and payload["cmd"] != "mqtt_status":
                    self.logger.warning(
                        f"mqtt_message: {instname} not in my instrument list {self.instruments.keys()} payload = {payload} -> do nothing"
                    )
                return
            cmd = payload["cmd"]
            value = payload["payload"]
            typ = payload["type"]

            result = common.strcall(
                instrument, cmd, value=value, typ=typ, mqttcheck=True
            )
            if result == "ERROR":
                self.logger.warning(
                    f"{instname} get an 'not found' from a mqtt command = {cmd}, {value}"
                )
            return
        elif self.typ == "instrument" or (
            self.typ == "control" and endtopic != TOPIC_CONTROL
        ):
            print(
                f"unknown mqtt message {message.topic} = {message.payload}  -> do nothing"
            )

    def publish(self, attr, value, qos=None, retain=None):
        """Send message to broker."""
        if qos is None:
            qos = self.qos
        if retain is None:
            retain = self.retain
        try:
            value = json.dumps(value)
        except Exception as ex:
            self.logger.error(
                f"publish: couldn't send {attr} = {value} excepton occure {ex}"
            )
            return
        self.client.publish(
            f"{attr}", str(value), qos=qos, retain=retain
        )  # payload must be string,bytearray,int,float or None

    def clearpublish(self, attr):
        """Remove retained publish message from broker."""
        self.client.publish(
            attr, "", 0, True
        )  # send 0 message to remove retained flag

    def close(self):
        """Disconnect from broker."""
        if self.broker is not None:
            self.client.loop_stop()
            self.client.disconnect()
            self.client.on_connect = None
            self.client.on_disconnect = None

    def __del__(self):
        self.close()

    @abstractmethod
    def mqtt_receive(self, topic, msg):
        pass


class mqtt_deviceattributes(object):
    """
    Handle mqqt messages for the instrument (=devices is 'transmitter').

    - topic for the device:
        f'{TOPIC_PREFIX}/'Hostname'/{TOPIC_INSTRUMENT}
    - payload:
        {"instrumentname": {"type": "set/get", "cmd": "function/attributename", "payload": yourvalues}}

      mqtt_all will be overwriten, to uncover attributes for sending mqqt-messages

    - if you define the function '_mqtt2json(value, attributename)' in your device, than this function will be call if a mqtt message should be send
      With this function you can translate the value, or it the result 'nomqtt' than the message will not be send.
    """

    import json

    mqtt_enable = False
    mqtt_list = []
    command = {
        "set": {"type": "cmd", "command": "menu", "payload": None},
    }

    def __init__(self):
        _setattr = object.__setattr__.__get__(
            self, self.__class__
        )  # set the values direct, without sending a mqtt-message
        _setattr("mqtt_debug", False)
        _setattr("_mqttclient", None)
        _setattr("_mqtt_status", "disconnect")
        _setattr("mqtt_enable", False)
        _setattr("hostname", socket.gethostname())
        _setattr("topic", f"{TOPIC_PREFIX}/{self.hostname}/{TOPIC_INSTRUMENT}")
        _setattr("mqtt_all", [])
        _setattr(
            "_mqttclient", None
        )  # normally, overwritten in setup_inst from instrument

    def mqtt_add(self, client, instrument, liste="#", qos=0):
        """
        Add the instrument to mqtt.

        calling from base_instrument, after the instrument (device) has been create.
        Normally you have not to use this function, only base_instrument use it.

        Returns:
            None.
        """
        self._mqttclient = client
        if liste == "#":
            self.mqtt_list = self.mqtt_all
        else:
            self.mqtt_list = liste
        if client is None:
            print("mqtt_add: client not defined")
            return
        client.mqtt_add(instrument)
        if self._mqttclient is not None:
            self.mqtt_enable = True
        self._mqtt_status = "disconnect"
        self.publish_set(
            "mqtt_status", "disconnect"
        )  # send mqtt_status default = disconnect
        if (
            hasattr(self, "gui") and self.gui is not None
        ):  # send a message direct to semictrl that the gui is available
            payload = {
                "semictrl": {
                    "type": "cmd",
                    "cmd": "menu",
                    "payload": {"Instruments": "", self.instName: self.gui},
                }
            }
            self._mqttclient.publish(self.topic, payload)

    def mqtt_disconnect(self):
        """
        Remove the instrument from mqtt.

        calling from base_instrument, if the instrument are closing.
        Normally you have not to use this function, only base_instrument use it.

        Returns:
            None.
        """
        if hasattr(self, "_mqttclient") and self._mqttclient is not None:
            self.publish_set("mqtt_status", "disconnect")
            self._mqtt_status = "disconnect"
            self._mqttclient.mqtt_disconnect(self)  # remove from list
        self.mqtt_enable = False

    def __setattr__(self, attr, value):
        """
        Publish attribute and value, if attribute was set and it is in mqtt_list.

        pulish mean: send 'hostname/instName/attibute/set value' to the broker
        This function will call from _mqtt_message, normally you have not to use this function.
        """
        object.__setattr__(self, attr, value)
        if (
            self.mqtt_enable and attr in self.mqtt_list
        ):  # attr == 'mqtt_status' or
            payload = {
                f"{self.instName}": {
                    "type": "set",
                    "cmd": attr,
                    "payload": value,
                }
            }
            self._mqttclient.publish(self.topic, payload)
            if self.mqtt_debug:
                print(
                    "{} {} publish: {} {}".format(
                        self.__class__.__name__,
                        self.instName,
                        self.topic,
                        payload,
                    )
                )

    def __getattribute__(self, attr, *values):
        """
        Publish attribute and value, if attribute was get and it is in mqtt_list.

        pulish mean: send 'hostname/instName/attibute/set value' to the broker
        This function will call from _mqtt_message, normally you have not to use this function.
        """
        value = super(__class__, self).__getattribute__(attr)
        if attr == "mqtt_enable":
            return value
        if (
            attr not in ["__class__", "mqtt_list", "INST_FUNCTION"]
            and attr in self.mqtt_list
        ):
            if f"{attr}()" in self.mqtt_list:
                # TODO: function-call have to add their own call from self._mqttclient.publish(), because unitl now
                #    I did'nt know to get the function parameters
                # payload = {f"{self.instName}": {'type': 'get', 'cmd': attr, 'payload': values}}
                print(
                    f"    ({value}   sorry, I did'nt know to get the function parameters -> improve it, until now  no mqtt publish"
                )
                return value
            elif hasattr(self, "_mqtt2json"):
                # print(f"    call _mqtt2json({value})")
                payload = self._mqtt2json(value, attr)
                if payload != "nomqtt":
                    payload = {
                        f"{self.instName}": {
                            "type": "get",
                            "cmd": attr,
                            "payload": payload,
                        }
                    }
            else:
                payload = {
                    f"{self.instName}": {
                        "type": "get",
                        "cmd": attr,
                        "payload": value,
                    }
                }
            if payload != "nomqtt" and self._mqttclient is not None:
                self._mqttclient.publish(self.topic, payload)
                if self.mqtt_debug:
                    print(
                        "{} {} publish: {} {}".format(
                            self.__class__.__name__,
                            self.instName,
                            self.topic,
                            payload,
                        )
                    )
        return value

    def publish(self, topic, value):
        """Publish topic as type='cmd' with paylad=value."""
        # function_name=inspect.stack()[1][3]
        payload = {
            f"{self.instName}": {"type": "cmd", "cmd": topic, "payload": value}
        }
        if self.mqtt_debug:
            print(
                f"{self.__class__.__name__}.publish: {self.topic} = {payload}"
            )
        if self._mqttclient is not None:
            self._mqttclient.publish(self.topic, payload)

    def publish_get(self, function_name, value):
        """Publish function_name as type='get' with paylad=value."""
        # function_name=inspect.stack()[1][3]
        if self.mqtt_enable:
            payload = {
                f"{self.instName}": {
                    "type": "set",
                    "cmd": function_name,
                    "payload": value,
                }
            }
            if self.mqtt_debug:
                print(
                    f"{self.__class__.__name__}.publish_get: {self.topic} = {payload}"
                )
            if self._mqttclient is not None:
                self._mqttclient.publish(self.topic, payload)

    def publish_set(self, function_name, value):
        """Publish function_name as type='set' with paylad=value."""
        # function_name=inspect.stack()[1][3]
        if self.mqtt_enable:
            payload = {
                f"{self.instName}": {
                    "type": "set",
                    "cmd": function_name,
                    "payload": value,
                }
            }
            if self.mqtt_debug:
                print(
                    f"{self.__class__.__name__}.publish_set: {self.topic} = {payload}"
                )
            if self._mqttclient is not None:
                self._mqttclient.publish(self.topic, payload)

    @property
    def mqtt_status(self):
        """Getter for the mqtt_status."""
        if self.mqtt_debug:
            print(f"{self.instName}.mqtt_status == {self._mqtt_status}")
        return self._mqtt_status

    @mqtt_status.setter
    def mqtt_status(self, value):
        """The mqtt_status should be set only from an extern mqtt message.

        value = disconnect/connect
        """
        if self.mqtt_debug:
            print(f"    {self.instName}.mqtt_status := {value}")
        self._mqtt_status = value
        if value == "connect":
            self.publish_set("mqtt_status", "connect")

    def close(self):
        if self.mqttc is not None:
            self.mqtt_disconnect()


class mqtt_signal(QtCore.QObject):
    """Class for communicate with mqtt messages .

    We need a channel to communicate with some gui widgets (e.q. QTextEdit).
    otherwhile we get the error: 'Cannot create children for a parent that is in a different thread'
    """

    channel = QtCore.pyqtSignal(str, str)


class mqtt_displayattributes(object):
    """
    mqtt messages for display and controlling (='receiver').

    docu muss überarbeitet werden:

    publish:
       - topic for display application:
            f'{TOPIC_PREFIX}/'Hostname'/{TOPIC_CONTROL}
       - payload:
           f'{"instrumentname": {"type": "set/get", "cmd": "function/attributename", "payload": yourvalues}}'

    """

    import json

    def __init__(self, client, message_client, mqtt_receive=None):
        self.mqtt_debug = False
        self.mqttclient = client
        self.instName = message_client
        # self._mqttreceive = client.mqtt_signal()
        if mqtt_receive is None:
            mqtt_receive = self.mqtt_receive
        self.mqttclient.mqttreceive.channel.connect(mqtt_receive)
        self.topic = f"{message_client}/{platform.node()}/{TOPIC_CONTROL}"

    def publish(self, attr, value):
        """Send message to broker."""
        self.mqttclient.publish(attr, value)

    def publish_set(self, instName, function_name, value):
        """Publish attribute with value as set."""
        # function_name=inspect.stack()[1][3]
        payload = {
            f"{instName}": {
                "type": "set",
                "cmd": function_name,
                "payload": value,
            }
        }
        if self.mqtt_debug:
            self.mqttclient.logger.debug(
                f"publish_set: {self.topic} = {payload}"
            )
        self.mqttclient.publish(self.topic, payload)

    def publish_get(self, instName, function_name):
        """Publish attribute with value as get."""
        # function_name=inspect.stack()[1][3]
        payload = {
            f"{instName}": {"type": "get", "cmd": function_name, "payload": ""}
        }
        if self.mqtt_debug:
            self.mqttclient.logger.debug(
                f"publish_get: {self.topic} = {payload}"
            )
        self.mqttclient.publish(self.topic, payload)

    def mqtt_add(self):
        """Add the modul as member for the mqtt communication."""
        self.mqttclient.mqtt_add(self, "")

    def mqtt_disconnect(self):
        """Remove the modul as member for the mqtt communication."""
        self.mqttclient.client.message_callback_remove(
            self.instName + "/#"
        )  # remove subscribe for this client

    @abstractmethod
    def mqtt_receive(self, topic, msg):
        print("ERROR: You have to overwrite mqtt_receive in your class")


if __name__ == "__main__":
    mqtt = mqtt_init()
    # mqtt.init('172.27.112.62', message_client='ate', username='')   # broker mosquitto on 'ubuntu-0001'
    mqtt.init(
        "127.0.0.1", message_client=f"ate/{socket.gethostname()}/", username=""
    )  # local mosquitto broker
    i = 0
    while True:
        time.sleep(0.5)
        mqtt.client.publish("mqtt_client/temperature", "25")
        i += 1
        if i > 10:
            break
    mqtt.close()
