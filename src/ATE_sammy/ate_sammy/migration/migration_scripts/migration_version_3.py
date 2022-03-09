from ate_sammy.migration.migration_scripts.migrate_base import MigratorBase
import os


PROGRAM_SECTION = 'program'
SEQUENCE_SECTION = 'sequence'
TEST_SECTION = 'test'
TESTTARGET_SECTION = 'testtarget'
MAX_TEST_RANGE = 100
DEFAULT_GROUPS = ['checker', 'maintenance', 'production', 'engineering', 'validation', 'quality', 'qualification']
SUBFLOWS_QUALIFICATION = ['ZHM', 'ABSMAX', 'EC', 'HTOL', 'HTSL', 'DR', 'AC', 'HAST', 'ELFR', 'LU', 'TC', 'THB', 'ESD', 'RSJ']


class MigrationVersion3(MigratorBase):
    def migrate_impl(self, defs_path: str) -> int:
        super().__init__()
        self.test_collection = {}
        self.group_collection = {}
        sequence_path = os.path.join(defs_path, SEQUENCE_SECTION)
        self.migrate_section(sequence_path, lambda path: self._migrate_sequence_structure(path))

        program_path = os.path.join(defs_path, PROGRAM_SECTION)
        self.migrate_section(program_path, lambda path: self._migrate_program_structure(path))

        testtarget_path = os.path.join(defs_path, TESTTARGET_SECTION)
        self.migrate_section(testtarget_path, lambda path: self._migrate_testtarget_structure(path))
        self._generate_group_db(defs_path)
        return 0

    def _migrate_program_structure(self, file_name: str):
        configuration = self.read_configuration(file_name)
        for config in configuration:
            prog_name = config['prog_name']
            owner_name = config['owner_name']
            config['usertext'] = config['prog_name'].split('_')[-1]

            config['prog_name'] = self._generate_program_name(prog_name)
            config['owner_name'] = self._generate_owner_name(owner_name)
            self._rename_files(prog_name, config['prog_name'], config['hardware'], config['base'], file_name)

            for group in DEFAULT_GROUPS:
                if group not in config['prog_name']:
                    continue

                self.group_collection.setdefault(group, []).append(config['prog_name'])

        self.write_configuration(file_name, configuration)

    def _migrate_sequence_structure(self, file_name: str):
        configuration = self.read_configuration(file_name)
        for config in configuration:
            prog_name = config['prog_name']
            owner_name = config['owner_name']

            config['prog_name'] = self._generate_program_name(prog_name)
            config['owner_name'] = self._generate_owner_name(owner_name)
            prog_name = config['prog_name']
            for group in DEFAULT_GROUPS:
                if group not in config['prog_name']:
                    continue

                self.test_collection.setdefault(group, []).append(config['test'])

        self.write_configuration(file_name, configuration)
        os.rename(file_name, os.path.join(os.path.dirname(file_name), f'sequence{prog_name}.json'))

    @staticmethod
    def _rename_files(old_name: str, prog_name: str, hardware: str, base: str, path: str):
        binning_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(path))), 'src', hardware, base)
        os.rename(os.path.join(binning_file_path, f'{old_name}_binning.json'), os.path.join(binning_file_path, f'{prog_name}_binning.json'))

    def _migrate_testtarget_structure(self, file_name: str):
        configuration = self.read_configuration(file_name)
        for config in configuration:
            testtarget_name = config['name']
            prog_name = config['prog_name']
            if not self._generate_program_name(prog_name) or not self._generate_testtarget_name(testtarget_name):
                continue

            config['prog_name'] = self._generate_program_name(prog_name)
            config['name'] = self._generate_testtarget_name(testtarget_name)

        self.write_configuration(file_name, configuration)

    def _generate_testtarget_name(self, target_name):
        group_prefix = target_name.split('_')[-2]
        group = self._get_group_from_prefix(group_prefix)
        if not group:
            return self._generate_quali_flow_name(target_name)

        return target_name.replace(f'_{group[0].upper()}_', f'_{group}_')

    def _generate_program_name(self, prog_name: str):
        group_prefix = prog_name.split('_')[-2]
        group = self._get_group_from_prefix(group_prefix)

        if not group:
            return self._generate_quali_flow_name(prog_name)

        return prog_name.replace(f'_{group[0].upper()}_', f'_{group}_')

    def _generate_owner_name(self, owner_name: str):
        group_prefix = owner_name.split('_')[-1]
        group = self._get_group_from_prefix(group_prefix)
        if not group:
            return self._generate_quali_flow_name(owner_name)

        import re
        prefix = f'_{group[0].upper() }'
        occurs = [m.start() for m in re.finditer(prefix, owner_name)]

        def new_owner_name(string, sub, wanted, n):
            where = [m.start() for m in re.finditer(sub, string)][n - 1]
            before = string[:where]
            after = string[where:]
            after = after.replace(sub, wanted, 1)
            newString = before + after
            return newString

        return new_owner_name(owner_name, prefix, f'_{group}', len(occurs))

    @staticmethod
    def _generate_quali_flow_name(name: str):
        for sub_qual in SUBFLOWS_QUALIFICATION:
            if sub_qual in name:
                index = name.index(sub_qual)
                return name[:index] + 'qualification_' + name[index:]

        return None

    def _get_group_from_prefix(self, prefix: str):
        for group in DEFAULT_GROUPS:
            if group[0].upper() != prefix:
                continue

            return group

        return None

    @staticmethod
    def version_num() -> int:
        return 3

    def _generate_group_db(self, defs_path: str):
        group_path = os.path.join(defs_path, 'group')
        if not os.path.exists(group_path):
            os.mkdir(group_path)
        all = []
        for group in DEFAULT_GROUPS:
            programs = []
            tests = []
            if self.group_collection.get(group):
                programs = self.group_collection[group]

            if self.test_collection.get(group):
                tests = list(set(self.test_collection[group]))

            group_strcut = {'name': group, 'is_selected': True, 'is_standard': True, 'programs': programs, 'tests': tests}
            all.append(group_strcut)

        import json
        with open(os.path.join(group_path, 'group.json'), 'w') as f:
            json.dump(all, f, indent=2)
