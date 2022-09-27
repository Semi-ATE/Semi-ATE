import os

from ate_sammy.migration.migration_scripts.migrate_base import MigratorBase


class MigrationVersion10(MigratorBase):
    def migrate_impl(self, defs_path: str) -> int:
        super().__init__()
        test_path = os.path.join(defs_path, 'test')
        program_path = os.path.join(defs_path, 'program')
        self.migrate_section(test_path, lambda path: self._migrate_test(path))
        self.migrate_section(program_path, lambda path: self._migrate_program(path))
        return 0

    def version_num(self) -> int:
        return 10

    def _migrate_test(self, test_folder: str):
        tests = self.read_configuration(test_folder)
        for test_data in tests:
            test_data['definition']['patterns'] = []

        self.write_configuration(test_folder, tests)

    def _migrate_program(self, program_folder: str):
        programs = self.read_configuration(program_folder)
        for program in programs:
            program['patterns'] = {}

        self.write_configuration(program_folder, programs)
