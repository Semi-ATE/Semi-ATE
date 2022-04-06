import json
import os

from ate_sammy.migration.migration_scripts.migrate_base import MigratorBase
from ate_sammy.migration.migration_scripts.migration_version_1 import MigrationVersion1
from ate_sammy.migration.migration_scripts.migration_version_2 import MigrationVersion2
from ate_sammy.migration.migration_scripts.migration_version_3 import MigrationVersion3
from ate_sammy.migration.migration_scripts.migration_version_4 import MigrationVersion4
from ate_sammy.migration.migration_scripts.migration_version_5 import MigrationVersion5
from ate_sammy.migration.migration_scripts.migration_version_6 import MigrationVersion6

from ate_sammy.migration.utils import (generate_path, write_version_to_file, VERSION, VERSION_FILE_NAME)

DEFINITIONS = 'definitions'
MIGRATORS = [MigrationVersion1(), MigrationVersion2(), MigrationVersion3(), MigrationVersion4(), MigrationVersion5(), MigrationVersion6()]


class MigrationTool:
    @staticmethod
    def run(cwd: str, _arglist: list) -> int:
        defs_path = generate_path(cwd, DEFINITIONS)
        version = MigrationTool.get_project_version(defs_path)

        for ver_num in range(version, len(MIGRATORS)):
            migrator = MigrationTool.get_migrator(ver_num)
            return_code = migrator.migrate(defs_path)
            if return_code < 0:
                print(f'migration from version: {version} to {migrator.version_num()} requires user interaction')
                return return_code

            version = migrator.version_num()

        return 0

    @staticmethod
    def get_project_version(defs_path: str) -> str:
        version_dir = generate_path(defs_path, VERSION)
        MigrationTool.generate_version_num_if_needed(version_dir)

        with open(generate_path(version_dir, VERSION_FILE_NAME), 'r') as f:
            data = json.load(f)
            return data['version']

    @staticmethod
    def get_migrator(version_num: int) -> MigratorBase:
        return {
            0: lambda: MigrationVersion1(),
            1: lambda: MigrationVersion2(),
            2: lambda: MigrationVersion3(),
            3: lambda: MigrationVersion4(),
            4: lambda: MigrationVersion5(),
            5: lambda: MigrationVersion6(),
        }[version_num]()

    @staticmethod
    def generate_version_num_if_needed(version_dir: str):
        if not os.path.exists(version_dir):
            os.mkdir(version_dir)

        version_file = generate_path(version_dir, VERSION_FILE_NAME)
        if not os.path.exists(version_file):
            write_version_to_file(version_file, {"version": 0})
