import json
import os
from ate_sammy.migration.migration_scripts.migrate_base import MigratorBase


class MigrationVersion4(MigratorBase):
    def migrate_impl(self, defs_path: str) -> int:
        super().__init__()
        self._generate_settings_db(defs_path)
        return 0

    def version_num(self) -> int:
        return 4

    def _generate_settings_db(self, defs_path: str):
        settings_path = os.path.join(defs_path, 'settings')
        if not os.path.exists(settings_path):
            os.mkdir(settings_path)

        new_settings = [{
            "quality_grade": ""
        }]

        with open(os.path.join(settings_path, 'settings.json'), 'w') as f:
            json.dump(new_settings, f, indent=2)
