import os
from pathlib import Path

from ate_sammy.migration.migration_scripts.migrate_base import MigratorBase


class MigrationVersion11(MigratorBase):
    def migrate_impl(self, defs_path: str) -> int:
        super().__init__()
        self.root_path = Path(defs_path).parent

        program_path = os.path.join(defs_path, 'program')
        self.migrate_section(program_path, lambda path: self._migrate_program(path))

        project_path = Path(defs_path).parent.absolute()
        hardware_path = Path(defs_path).joinpath('hardware')
        self.migrate_section(str(hardware_path), lambda path: self._remove_dead_code(path, project_path))
        return 0

    def version_num(self) -> int:
        return 11

    def _remove_dead_code(self, hardware_folder: str, project_path: Path):
        hardwares = self.read_configuration(hardware_folder)
        for hardware in hardwares:
            hw_dir = project_path.joinpath(project_path.name, hardware['name'])
            if not hw_dir.joinpath('common.py').exists():
                continue

            hw_dir.joinpath('common.py').unlink()

    def _migrate_program(self, program_folder: str):
        programs = self.read_configuration(program_folder)
        for program in programs:
            with open(self.root_path.joinpath(self.root_path.name, f"{program['hardware']}", f"{program['base']}", f"{program['prog_name']}.yaml"), 'w'):
                pass
