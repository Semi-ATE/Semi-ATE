# -*- coding: utf-8 -*-
"""
HW0/FT/common.py


Don't edit this file. It is bound to be regenerated if the project
configuration changes. Any manual edits will be lost in that case.
"""
import json
import os
import pathlib
from ATE.Tester.TES.apps.testApp.sequencers.SequencerMqttClient import SequencerMqttClient
from ATE.Tester.TES.apps.testApp.sequencers.SequencerBase import SequencerBase
from ATE.semiateplugins.pluginmanager import get_plugin_manager
from ATE.common.logger import Logger


class Context:
    def __init__(self, source: str, params: dict, sequencer: SequencerBase):
        self.mqtt = SequencerMqttClient()
        self.mqtt.init_mqtt_client(params, sequencer)

        self.logger = Logger(source, self.mqtt)

        # Tester
        self.tester_instance = get_plugin_manager().hook.get_tester(tester_name="TDKMicronas.MiniSCT")[0]

        from ATE.Tester.TES.apps.testApp.actuators.Temperature.Temperature import TemperatureProxy
        self.Temperature_instance = TemperatureProxy()
        self.Temperature_instance.set_mqtt_client(self.mqtt)
        from ATE.Tester.TES.apps.testApp.actuators.Magnetic_Field.Magnetic_Field import Magnetic_FieldProxy
        self.Magnetic_Field_instance = Magnetic_FieldProxy()
        self.Magnetic_Field_instance.set_mqtt_client(self.mqtt)
        from ATE.Tester.TES.apps.testApp.actuators.Light.Light import LightProxy
        self.Light_instance = LightProxy()
        self.Light_instance.set_mqtt_client(self.mqtt)
        from ATE.Tester.TES.apps.testApp.actuators.Acceleration.Acceleration import AccelerationProxy
        self.Acceleration_instance = AccelerationProxy()
        self.Acceleration_instance.set_mqtt_client(self.mqtt)
        from ATE.Tester.TES.apps.testApp.actuators.Position.Position import PositionProxy
        self.Position_instance = PositionProxy()
        self.Position_instance.set_mqtt_client(self.mqtt)
        from ATE.Tester.TES.apps.testApp.actuators.Pressure.Pressure import PressureProxy
        self.Pressure_instance = PressureProxy()
        self.Pressure_instance.set_mqtt_client(self.mqtt)

        self.setup_plugins(self.logger)

    def setup_plugins(self, logger: Logger):
        instrument_dict = {}

        apply_configuration(instrument_dict)

        self.gp_dict = {}

        apply_configuration(self.gp_dict)

    def get_logger(self) -> Logger:
        return self.logger


def apply_configuration(feature_dict):
    for name, instance in feature_dict.items():
        config_file_path = pathlib.Path(os.path.join(pathlib.Path(__file__).parent.absolute(), "..", f"{name}.json"))
        if os.path.exists(config_file_path):
            with open(config_file_path) as reader:
                instance.apply_configuration(json.loads(reader.read()))


def make_context(source: str, params: dict, sequencer: SequencerBase) -> Context:
    return Context(source, params, sequencer)