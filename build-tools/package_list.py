from pathlib import Path

git_root_folder = Path(Path(__file__).parent, '../')

# IMPORTANT: The order of the packages matters because of dependencies
distribution_packages = [
    {
        'name': 'semi-ate-common',
        'dir': Path(git_root_folder, 'src/ATE_common'),
        'namespace': 'ate_common'
    },
    {
        'name': 'semi-ate-project-database',
        'dir': Path(git_root_folder, 'src/ATE_projectdatabase'),
        'namespace': 'ate_projectdatabase'
    },
    {
        'name': 'semi-ate-sammy',
        'dir': Path(git_root_folder, 'src/ATE_sammy'),
        'namespace': 'ate_sammy'},
    {
        'name': 'semi-ate-spyder',
        'dir': Path(git_root_folder, 'src/ATE_spyder'),
        'namespace': 'ate_spyder'
    },
    {
        'name': 'semi-ate-plugins',
        'dir': Path(git_root_folder, 'src/ATE_semiateplugins'),
        'namespace': 'ate_semiateplugins'
    },
    {
        'name': 'semi-ate-apps-common',
        'dir': Path(git_root_folder, 'src/Apps/common'),
        'namespace': 'ate_apps_common'
    },
    {
        'name': 'semi-ate-control-app',
        'dir': Path(git_root_folder, 'src/Apps/control_app'),
        'namespace': 'ate_control_app'
    },
    {
        'name': 'semi-ate-master-app',
        'dir': Path(git_root_folder, 'src/Apps/master_app'),
        'namespace': 'ate_master_app'
    },
    {
        'name': 'semi-ate-test-app',
        'dir': Path(git_root_folder, 'src/Apps/test_app'),
        'namespace': 'ate_test_app'
    },
    {
        'name': 'semi-ate-handler-app',
        'dir': Path(git_root_folder, 'src/Apps/handler_app'),
        'namespace': 'ate_handler_app'
    },
    {
        'name': 'tdk-micronas',
        'dir': Path(git_root_folder, 'src/Plugins/TDKMicronas'),
        'namespace': 'TDKMicronas'
    },
]

integration_test_packages = [
    {
        'name': 'integration-test-common',
        'dir': Path(git_root_folder, 'src/integration_tests/Plugins/Common'),
        'namespace': ''
    },
    {
        'name': 'dummy-plugin',
        'dir': Path(git_root_folder, 'src/integration_tests/Plugins/DummyTester'),
        'namespace': 'DummyTester'
    },
]