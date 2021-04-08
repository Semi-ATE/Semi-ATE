import json
from pathlib import Path
import pytest

from ATE.projectdatabase.Types import Types
from ATE.sammy.migration.utils import VERSION_FILE_NAME, VERSION


ALL_PROJECTS_REL_PATH = '../projects/'
NEW_PROJECT_REL_PATH = '../spyder/widgets/CI/qt/smoketest/smoke_test'
DEFINTIONS = 'definitions'


@pytest.fixture(scope="module")
def base_path():
    return Path(__file__).resolve().parent


@pytest.fixture(scope="module")
def new_proj_dir(base_path):
    return base_path.joinpath(NEW_PROJECT_REL_PATH)


@pytest.fixture(scope="module")
def old_proj_dir(base_path):
    """return the path to the last versionised Project version in "../projects"
    """

    project_dirs = base_path.joinpath(ALL_PROJECTS_REL_PATH).glob('*')
    versions_projects = {}
    for cur_proj_path in project_dirs:
        version_file = cur_proj_path.joinpath(DEFINTIONS, VERSION, VERSION_FILE_NAME)
        if version_file.exists():
            with open(version_file, 'r') as file:
                version_num = json.load(file)['version']
                versions_projects[version_num] = cur_proj_path
    return versions_projects[max(versions_projects.keys())]


def get_section_file_path(project_path: Path, section: str) -> str:
    section_file = project_path.joinpath(DEFINTIONS, section).glob("*.json")
    return section_file.__next__()


def load_db_section(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


@pytest.fixture
def data(new_proj_dir, old_proj_dir, request):
    """With request.param we get the Parameter which was parametrized at the test.
    """
    return (
        load_db_section(get_section_file_path(new_proj_dir, request.param))[0],
        load_db_section(get_section_file_path(old_proj_dir, request.param))[0]
    )


@pytest.mark.parametrize("data", [Types.Sequence()], indirect=True)
def test_check_sequence(data):
    cur_data, old_data = data

    assert set(cur_data.keys()) == set(old_data.keys())

    defs_cur_data, defs_old_data = cur_data['definition'], old_data['definition']
    assert set(defs_cur_data.keys()) == set(defs_old_data.keys())

    for (_, v_cur), (_, v_old) in zip(defs_cur_data['input_parameters'].items(), defs_old_data['input_parameters'].items()):
        assert set(v_cur.keys()) == set(v_old.keys())

    for (_, v_cur), (_, v_old) in zip(defs_cur_data['output_parameters'].items(), defs_old_data['output_parameters'].items()):
        assert set(v_cur.keys()) == set(v_old.keys())
        assert set(v_cur['Binning'].keys()) == set(v_old['Binning'].keys())


@pytest.mark.parametrize("data", [Types.Hardware()], indirect=True)
def test_check_hardware(data):
    cur_data, old_data = data

    assert set(cur_data.keys()) == set(old_data.keys())

    defs_cur_data, defs_old_data = cur_data['definition'], old_data['definition']
    assert set(defs_cur_data.keys()) == set(defs_old_data.keys())

    pcb_cur_data, pcb_old_data = cur_data['definition']['PCB'], old_data['definition']['PCB']
    assert set(pcb_cur_data.keys()) == set(pcb_old_data.keys())

    actuator_cur_data, actuator_old_data = cur_data['definition']['Actuator'], old_data['definition']['Actuator']
    assert set(actuator_cur_data.keys()) == set(actuator_old_data.keys())

    parallelism_cur_data, parallelism_old_data = cur_data['definition']['Parallelism'], old_data['definition']['Parallelism']
    assert set(parallelism_cur_data.keys()) == set(parallelism_old_data.keys())


@pytest.mark.parametrize("data", [Types.Settings(), Types.Die(), Types.Program(), Types.Group()], indirect=True)
def test_check_basic_struct(data):
    cur_data, old_data = data
    assert set(cur_data.keys()) == set(old_data.keys())
