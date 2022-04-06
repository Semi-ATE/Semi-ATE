import os

from ate_sammy.migration.migration_scripts.migrate_base import MigratorBase


class MigrationVersion6(MigratorBase):
    def migrate_impl(self, defs_path: str) -> int:
        super().__init__()
        prog_path = os.path.join(defs_path, 'program')
        self.sequence_base_path = os.path.join(defs_path, 'sequence')
        self.migrate_section(prog_path, lambda path: self._migrate_program(path))

        return 0

    def version_num(self) -> int:
        return 6

    def _migrate_program(self, file_name):
        prog_list = self.read_configuration(file_name)
        for prog in prog_list:
            seq_path = os.path.join(self.sequence_base_path, f"sequence{prog['prog_name']}.json")
            seq_data = self.read_configuration(seq_path)

            for _, test_config in enumerate(seq_data):
                for _, input in test_config['definition']['input_parameters'].items():
                    input['Shmoo'] = False

            self.write_configuration(seq_path, seq_data)
