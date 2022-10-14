import os
from pathlib import Path

from ate_sammy.migration.migration_scripts.migrate_base import MigratorBase


class MigrationVersion11(MigratorBase):
    def migrate_impl(self, defs_path: str) -> int:
        super().__init__()
        self.root_path = Path(defs_path).parent

        program_path = os.path.join(defs_path, 'program')
        self.migrate_section(program_path, lambda path: self._migrate_program(path))
        return 0

    def version_num(self) -> int:
        return 11

    def _migrate_program(self, program_folder: str):
        programs = self.read_configuration(program_folder)
        for program in programs:
            with open(self.root_path.joinpath(self.root_path.name, f"{program['hardware']}", f"{program['base']}", f"{program['prog_name']}.yaml"), 'w'):
                pass
