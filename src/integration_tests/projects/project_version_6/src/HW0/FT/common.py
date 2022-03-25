# -*- coding: utf-8 -*-
"""
HW0/FT/common.py


Don't edit this file. It is bound to be regenerated if the project
configuration changes. Any manual edits will be lost in that case.
"""
import json
import os
import sys
import pathlib
import traceback
from ate_test_app.sequencers.Sequencer import Sequencer
from ate_test_app.sequencers.SequencerBase import SequencerBase
from ate_test_app.sequencers.SequencerBase import SequencerBase
from ate_test_app.auto_script.AutoScriptBase import AutoScriptBase
from ate_test_app.sequencers import Harness
from ate_test_app.stages_sequence_generator.stages_sequence_generator import StagesSequenceGenerator
from ate_test_app.sequencers.mqtt.MqttConnection import MqttConnection
from ate_semiateplugins.pluginmanager import get_plugin_manager
from ate_common.logger import Logger, LogLevel


class Context:
    def __init__(
        self,
        source: str,
        params: dict,
        sequencer: SequencerBase,
        auto_script: AutoScriptBase,
        execution_strategy: StagesSequenceGenerator,
        mqtt: MqttConnection,
        harness_strategy: Harness):
        self.harness = Sequencer(sequencer, params, execution_strategy, mqtt, harness_strategy)
        self.logger = Logger(source, self.harness)

        # Logging is available @ Info Level during startup of the
        # sequencer. After the C'tor has finished, we automatically
        # revert to "Warrning"
        self.logger.set_logger_level(LogLevel.Info)
        try:
            self.auto_script = auto_script
            self.auto_script.set_logger(self.logger)
            self.auto_script.set_context(self)
            self.harness.set_after_terminate_callback(lambda: self.auto_script.after_terminate_teardown())
            self.harness.set_logger(self.logger)
            sequencer.set_logger(self.logger)
            sequencer.set_auto_script(self.auto_script)

            # Tester
            testers = get_plugin_manager().hook.get_tester(tester_name="DummySingleTester")
            assert len(testers) < 2, "The testertype DummyTester.MiniSCT maps to multiple testers. Check installed plugins."
            assert len(testers) == 1, "The testertype DummyTester.MiniSCT is not available or installed on this machine."
            self.tester_instance = testers[0]
            sequencer.set_tester_instance(self.tester_instance)

            from ate_test_app.actuators.Temperature.Temperature import TemperatureProxy
            self.Temperature_instance = TemperatureProxy()
            self.Temperature_instance.set_mqtt_client(self.harness)
            from ate_test_app.actuators.Magnetic_Field.Magnetic_Field import Magnetic_FieldProxy
            self.Magnetic_Field_instance = Magnetic_FieldProxy()
            self.Magnetic_Field_instance.set_mqtt_client(self.harness)
            from ate_test_app.actuators.Light.Light import LightProxy
            self.Light_instance = LightProxy()
            self.Light_instance.set_mqtt_client(self.harness)
            from ate_test_app.actuators.Acceleration.Acceleration import AccelerationProxy
            self.Acceleration_instance = AccelerationProxy()
            self.Acceleration_instance.set_mqtt_client(self.harness)
            from ate_test_app.actuators.Position.Position import PositionProxy
            self.Position_instance = PositionProxy()
            self.Position_instance.set_mqtt_client(self.harness)
            from ate_test_app.actuators.Pressure.Pressure import PressureProxy
            self.Pressure_instance = PressureProxy()
            self.Pressure_instance.set_mqtt_client(self.harness)

            self.setup_plugins(self.logger)
        except Exception as e:
            exc = traceback.format_exc()
            self.logger.log_message(LogLevel.Error, exc)
            # Exceptions in this stage are per definition fatal
            sys.exit()

        self.logger.set_logger_level(LogLevel.Warning)

    def setup_plugins(self, logger: Logger):
        instrument_dict = {}

        apply_configuration(instrument_dict)

        self.gp_dict = {}

        apply_configuration(self.gp_dict)

    def get_logger(self) -> Logger:
        return self.logger

    def after_exception_callback(self, source: str, error: Exception):
        self.auto_script.after_exception_teardown(source, error)

    def after_cycle_callback(self):
        self.auto_script.after_cycle_teardown()


def apply_configuration(feature_dict):
    for name, instance in feature_dict.items():
        config_file_path = pathlib.Path(os.path.join(pathlib.Path(__file__).parent.absolute(), "..", f"{name}.json"))
        if os.path.exists(config_file_path):
            with open(config_file_path) as reader:
                instance.apply_configuration(json.loads(reader.read()))


def make_context(
    source: str,
    params: dict,
    sequencer: SequencerBase,
    auto_script: AutoScriptBase,
    execution_strategy: StagesSequenceGenerator,
    mqtt: MqttConnection,
    harness_strategy: Harness
    ) -> Context:
    return Context(source, params, sequencer, auto_script, execution_strategy, mqtt, harness_strategy)