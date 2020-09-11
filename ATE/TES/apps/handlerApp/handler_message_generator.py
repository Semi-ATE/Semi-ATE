import json
import sys

from typing import List, Optional
from ATE.TES.apps.common.logger import Logger

LOAD_PARAMTERS = ["lotNumber", "HandlerName", "HandlerType"]
START_TEST_PARAMTERS = ["Onwafer_sites", "Coordinates", "ChuckTemperature"]
NEW_WAFER_PARAMTERS = ["WaferId", "WaferWidth", "WaferHight"]


class MessageGenerator:
    def __init__(self):
        self.log = Logger.get_logger()

    def generate_status_msg(self, state: str) -> str:
        return self.__dump_message({"type": "status",
                                    "state": state})

    def generate_command_msg(self, cmd_type: str, payload: dict) -> Optional[str]:
        payload_switch = {"load_test": self.__generate_load_test_command(payload),
                          "start_dut_test": self.__generate_start_dut_test_command(payload),
                          "new_wafer": self.__generate_new_wafer_command(payload),
                          "unload_test": self.__generate_unload_test_command()}

        if cmd_type not in payload_switch:
            self.log.warning(f"failed to interpret command in {sys._getframe().f_code.co_filename}")
            return None

        job_data = payload_switch.get(cmd_type)
        if job_data is None:
            self.log.warning(f"failed to generate payload for '{cmd_type}' command")
            return None

        return self.__dump_message({"type": "cmd",
                                    "command": cmd_type,
                                    "job_data": job_data})

    def __generate_load_test_command(self, config: dict) -> Optional[str]:
        return self.__get_config_parameter(config, LOAD_PARAMTERS)

    def __generate_start_dut_test_command(self, config: dict) -> Optional[str]:
        return self.__get_config_parameter(config, START_TEST_PARAMTERS)

    def __generate_new_wafer_command(self, config: dict) -> Optional[str]:
        return self.__get_config_parameter(config, NEW_WAFER_PARAMTERS)

    def __generate_unload_test_command(self) -> Optional[str]:
        return ""

    def __dump_message(self, config: dict) -> str:
        return json.dumps(config)

    def __get_config_parameter(self, config: dict, parameters: List[str]) -> Optional[str]:
        for param in parameters:
            if config.get(param) is None:
                self.log.error(f"failed to get '{param}' parameter")
                return None

        return self.__dump_message(config)
