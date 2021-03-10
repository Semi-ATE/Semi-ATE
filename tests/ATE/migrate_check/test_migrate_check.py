import os
import json
import glob
import pytest

from ATE.projectdatabase.Types import Types
from ATE.sammy.migration.utils import generate_path, VERSION_FILE_NAME, VERSION


ALL_PROJECTS_REL_PATH = '../projects/'
NEW_PROJECT_REL_PATH = '../spyder/widgets/CI/qt/smoketest/smoke_test'
DEFINTIONS = 'definitions'


def generate_latest_project_path():
    path = ALL_PROJECTS_REL_PATH
    projects = {}
    for root, directories, _ in os.walk(path):
        for directory in directories:
            version_path = os.path.join(root, directory, DEFINTIONS, VERSION)
            if not os.path.exists(version_path):
                continue

            ver = generate_path(version_path, VERSION_FILE_NAME)
            if not os.path.exists(ver):
                continue

            with open(ver, 'r') as f:
                projects[directory] = json.load(f)['version']

        return generate_path(path, max(projects, key=lambda key: projects[key]))

    return '.'


def generate_section_new(section: str) -> str:
    path = os.path.join(NEW_PROJECT_REL_PATH, DEFINTIONS)
    return generate_path(path, section)


def generate_section_old(section: str) -> str:
    path = os.path.join(generate_latest_project_path(), DEFINTIONS)
    return generate_path(path, section)


class Test_MigrateCheck:
    def setup_method(self, test_method):
        self.cwd = os.getcwd()
        os.chdir(os.path.dirname(__file__))

    def teardown_method(self, test_method):
        os.chdir(os.path.dirname(self.cwd))

    def test_check_sequence(self):
        cur_program, old_program = self._get_db_struct_to_compare(generate_section_new(Types.Sequence()), generate_section_old(Types.Sequence()))
        cur_data = self._get_data(cur_program)[0]
        old_data = self._get_data(old_program)[0]

        success = set(cur_data.keys()) == set(old_data.keys())

        defs_cur_data, defs_ols_data = cur_data['definition'], old_data['definition']
        success = set(defs_cur_data.keys()) == set(defs_ols_data.keys()) if success else success

        for (_, v_cur), (_, v_old) in zip(defs_cur_data['input_parameters'].items(), defs_ols_data['input_parameters'].items()):
            success = set(v_cur.keys()) == set(v_old.keys()) if success else success

        for (_, v_cur), (_, v_old) in zip(defs_cur_data['output_parameters'].items(), defs_ols_data['output_parameters'].items()):
            success = set(v_cur.keys()) == set(v_old.keys()) if success else success
            success = set(v_cur['Binning'].keys()) == set(v_old['Binning'].keys()) if success else success

        if not success:
            print(Test_MigrateCheck.generate_error_message(Types.Sequence()))
            assert None

        return self

    @pytest.mark.parametrize("sections", [Types.Settings(), Types.Die(), Types.Program(), Types.Group()])
    def test_check_basic_struct(self, sections):
        cur_program, old_program = self._get_db_struct_to_compare(generate_section_new(sections), generate_section_old(sections))
        cur_data = self._get_data(cur_program)
        old_data = self._get_data(old_program)
        if set(cur_data[0].keys()) == set(old_data[0].keys()):
            return self

        print(Test_MigrateCheck.generate_error_message(sections))
        assert None

    @staticmethod
    def generate_error_message(section_name: str):
        return f'{section_name} structure has been changed, and is not compatible with older project\'s version any more, make sure to update the version number'

    @staticmethod
    def _generate_section_path(project_path: str, section: str) -> str:
        path = os.path.join(project_path, DEFINTIONS)
        return generate_path(path, section)

    @staticmethod
    def _get_data(file_name: str) -> dict:
        with open(file_name, 'r') as f:
            all = json.load(f)

        return all

    @staticmethod
    def _get_db_struct_to_compare(cur_sec_path: str, old_sec_path: str) -> tuple:
        cur_program = glob.glob(os.path.join(cur_sec_path, '*.json'))[0]
        old_program = glob.glob(os.path.join(old_sec_path, '*.json'))[0]
        return cur_program, old_program
