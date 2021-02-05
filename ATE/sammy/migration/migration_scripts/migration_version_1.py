from ATE.sammy.migration.migration_scripts.migrate_base import MigratorBase
import os


PROGRAM_SECTION = 'program'
SEQUENCE_SECTION = 'sequence'
MAX_TEST_RANGE = 100


class MigrationVersion1(MigratorBase):
    def migrate_impl(self, defs_path: str) -> int:
        super().__init__()
        sequence_path = os.path.join(defs_path, SEQUENCE_SECTION)
        self.migrate_section(sequence_path, lambda path: self._migrate_sequence_structure(path))

        program_path = os.path.join(defs_path, PROGRAM_SECTION)
        self.migrate_section(program_path, lambda path: self._migrate_program_structure(path))
        return 0

    def _migrate_program_structure(self, file_name: str):
        configuration = self.read_configuration(file_name)
        for config in configuration:
            config['test_ranges'] = []
        self.write_configuration(file_name, configuration)

    def _migrate_sequence_structure(self, file_name: str):
        configuration = self.read_configuration(file_name)
        test_num = MAX_TEST_RANGE
        configuration = self.read_configuration(file_name)
        for index, test_config in enumerate(configuration):
            test_num = MAX_TEST_RANGE * (index + 1)
            for _, outputs in test_config['definition']['output_parameters'].items():
                outputs['test_num'] = test_num
                test_num += 1

        self.write_configuration(file_name, configuration)

    def version_num(self) -> int:
        return 1
