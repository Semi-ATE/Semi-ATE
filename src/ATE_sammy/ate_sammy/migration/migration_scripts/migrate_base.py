from ate_sammy.migration.utils import (generate_path, write_version_to_file, VERSION, VERSION_FILE_NAME)
from abc import ABC, abstractmethod
import json
import os
from typing import Callable


class MigratorBase(ABC):
    def migrate(self, defs_path: str) -> int:
        self.defs_path = defs_path
        ret_code = self.migrate_impl(defs_path)
        self.update_version_num(defs_path, self.version_num())
        return ret_code

    @abstractmethod
    def migrate_impl(self, defs_path: str) -> int:
        pass

    @abstractmethod
    def version_num(self) -> int:
        pass

    @staticmethod
    def write_configuration(file_name: str, configuration: dict):
        with open(file_name, 'w') as f:
            json.dump(configuration, f, indent=2)

    @staticmethod
    def read_configuration(file_name: str) -> dict:
        with open(file_name, 'r') as f:
            data = json.load(f)
            return data

    @staticmethod
    def migrate_section(section_path: str, migrate_callback: Callable):
        for _, _, f in os.walk(section_path):
            for fi in f:
                extension = os.path.splitext(fi)[1]
                if extension != '.json':
                    continue

                migrate_callback(os.path.join(section_path, fi))

    def update_version_num(self, defs_path: str, new_version_num: str):
        version_file = generate_path(generate_path(defs_path, VERSION), VERSION_FILE_NAME)
        write_version_to_file(version_file, {"version": new_version_num})
