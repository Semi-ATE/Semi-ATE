from ATE.common.logger import (LogLevel, Logger)
import json
import sys

from typing import List, Optional

LOAD_PARAMETERS = ["lotnumber", "sublotnumber", "devicetype", "measurementtemperature"]
NEXT_PARAMETERS = ["siteid", "deviceid", "binning", "logflag", "additionalinfo"]

NEW_WAFER_PARAMTERS = ["WaferId", "WaferWidth", "WaferHight"]


class MessageGenerator:
    def __init__(self, log: Logger):
        self._log = log

    def generate_status_msg(self, state: str, message: str) -> str:
        payload = {"state": state, "message": message}
        return self.__generate_msg("status", payload)

    def generate_error_msg(self, cmd_type: str, message: str) -> str:
        payload = {"command": cmd_type, "message": message}
        return self.__dump_message(self.__generate_msg(cmd_type, payload))

    def generate_command_msg(self, cmd_type: str, job_data: dict) -> Optional[str]:
        try:
            command = {"load": lambda: self.__generate_load_test_command(job_data),
                       "next": lambda: self.__generate_next_command(job_data),
                       "endlot": lambda: self.__generate_endlot_command(),
                       "get_state": lambda: self.__generate_get_state_command(),
                       "identify": lambda: self.__generate_identify_command(),
                       }[cmd_type]()
        except KeyError:
            self._log.log_message(LogLevel.Warning(), f"failed to interpret command '{cmd_type}' in {sys._getframe().f_code.co_filename}")
            return None

        return self.__dump_message(self.__generate_msg(cmd_type, command))

    @staticmethod
    def __generate_msg(type, payload):
        return {"type": type, "payload": payload}

    def __generate_load_test_command(self, config: dict) -> Optional[str]:
        return self.__get_config_parameters(config, LOAD_PARAMETERS)

    def __generate_next_command(self, config: dict) -> Optional[str]:
        return self.__get_config_parameters(config, NEXT_PARAMETERS)

    def __generate_endlot_command(self) -> Optional[str]:
        return ""

    def __generate_get_state_command(self) -> Optional[str]:
        return ""

    def __generate_identify_command(self) -> Optional[str]:
        return ""

    @staticmethod
    def __dump_message(config: dict) -> str:
        return json.dumps(config)

    def __get_config_parameters(self, config: dict, parameters: List[str]) -> Optional[str]:
        for param in parameters:
            if config.get(param) is None:
                self.log.log_message(LogLevel.Error(), f"failed to get '{param}' parameter")
                return None

        return config
