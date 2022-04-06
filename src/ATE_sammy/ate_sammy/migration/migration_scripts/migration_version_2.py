from ate_sammy.migration.migration_scripts.migrate_base import MigratorBase
import os

SEQUENCE_SECTION = 'sequence'


class MigrationVersion2(MigratorBase):
    def migrate_impl(self, defs_path: str) -> int:
        sequence_path = os.path.join(defs_path, SEQUENCE_SECTION)
        self.migrate_section(sequence_path, lambda path: self._migrate_sequence_structure(path))
        return 0

    def _migrate_sequence_structure(self, file_name: str):
        configuration = self.read_configuration(file_name)
        for test_config in configuration:
            test_config['definition']['is_selected'] = True

        self.write_configuration(file_name, configuration)

    def version_num(self):
        return 2
