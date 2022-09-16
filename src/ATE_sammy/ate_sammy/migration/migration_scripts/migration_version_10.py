import os

from ate_sammy.migration.migration_scripts.migrate_base import MigratorBase
from ate_common.parameter import InputColumnKey, OutputColumnKey


class MigrationVersion10(MigratorBase):
    def migrate_impl(self, defs_path: str) -> int:
        super().__init__()
        test_path = os.path.join(defs_path, 'test')
        self.migrate_section(test_path, lambda path: self._migrate_test(path))
        return 0

    def version_num(self) -> int:
        return 10

    def _migrate_test(self, file_name):
        tests = self.read_configuration(file_name)
        for test_data in tests:
            test_data['definition']['patterns'] = []

        self.write_configuration(file_name, tests)
