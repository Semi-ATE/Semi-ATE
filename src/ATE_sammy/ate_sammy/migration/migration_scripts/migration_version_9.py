import json
import shutil
from pathlib import Path

from ate_sammy.migration.migration_scripts.migrate_base import MigratorBase


class MigrationVersion9(MigratorBase):
    def migrate_impl(self, defs_path: str) -> int:
        super().__init__()
        self._migrate_project(Path(defs_path).parent)
        return 0

    def version_num(self) -> int:
        return 9

    def _migrate_project(self, project_path: Path):
        project_name = project_path.name
        source_path = project_path.joinpath('src')

        # update version structure
        version_path = project_path.joinpath('definitions').joinpath('version').joinpath('version.json')

        data = None
        with open(version_path, 'r') as f:
            data = json.load(f)

        if data and isinstance(data, dict):
            with open(version_path, 'w') as f:
                json.dump([data], f)

        if source_path.exists():
            source_path.rename(project_name)
            shutil.rmtree(source_path, ignore_errors=True)
