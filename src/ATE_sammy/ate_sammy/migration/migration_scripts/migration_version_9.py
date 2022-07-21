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
        source_path.rename(project_name)
