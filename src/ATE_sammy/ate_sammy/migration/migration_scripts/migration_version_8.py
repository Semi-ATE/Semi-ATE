from pathlib import Path

from ate_sammy.migration.migration_scripts.migrate_base import MigratorBase


class MigrationVersion8(MigratorBase):
    def migrate_impl(self, defs_path: str) -> int:
        super().__init__()
        all_categories_config_path = [
            Path(defs_path).joinpath('hardware'), Path(defs_path).joinpath('masksets'), Path(defs_path).joinpath('die'),
            Path(defs_path).joinpath('package'), Path(defs_path).joinpath('device'), Path(defs_path).joinpath('product'),
            Path(defs_path).joinpath('group'), Path(defs_path).joinpath('program'), Path(defs_path).joinpath('qualification'),
            Path(defs_path).joinpath('test'), Path(defs_path).joinpath('testtarget')
        ]

        for category_config_path in all_categories_config_path:
            self.migrate_section(category_config_path, lambda path: self._migrate_program(path))
        return 0

    def version_num(self) -> int:
        return 8

    def _migrate_program(self, file_name):
        category_config_list = self.read_configuration(file_name)
        for category_config in category_config_list:
            name = None
            if category_config.get('name'):
                name = category_config['name']

            if category_config.get('prog_name'):
                name = category_config['prog_name']

            if not name:
                raise Exception('category name could not be found')

            file_path = Path(file_name)
            basename = file_path.parent.name
            path = file_path.parent.joinpath(f'{basename}{name}.json')
            data = [category_config]
            self.write_configuration(path, data)

        import os
        os.remove(file_name)
