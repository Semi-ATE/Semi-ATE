from ATE.sammy.migration.migration_tool import MigrationTool
from ATE.sammy.verbs.verbbase import VerbBase


class Migrate(VerbBase):
    def run(self, cwd: str, arglist: list):
        print("Run migration...")

        MigrationTool.run(cwd, arglist)
