from ate_sammy.migration.migration_scripts.migrate_base import MigratorBase
from ate_sammy.migration.utils import generate_path
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
            config['is_valid'] = False
            prog_dir_path = os.path.join(os.path.dirname(self.defs_path), 'src', config['hardware'], config['base'])
            prog_path = generate_path(prog_dir_path, f'{config["prog_name"]}.py')
            self.append_exception_code(prog_path)

        self.write_configuration(file_name, configuration)

    def _migrate_sequence_structure(self, file_name: str):
        configuration = self.read_configuration(file_name)
        test_num = MAX_TEST_RANGE
        configuration = self.read_configuration(file_name)
        for index, test_config in enumerate(configuration):
            test_num = MAX_TEST_RANGE * (index + 1)
            test_config['definition']['test_num'] = test_num
            for _, outputs in test_config['definition']['output_parameters'].items():
                test_num += 1
                outputs['test_num'] = test_num

        self.write_configuration(file_name, configuration)

    def version_num(self) -> int:
        return 1

    @staticmethod
    def append_exception_code(prog_path: str):
        msg = "raise Exception('test program is invalid')\n"
        with open(prog_path, 'r+') as f:
            content = f.read()
            f.seek(0, 0)
            f.write(msg + content)
