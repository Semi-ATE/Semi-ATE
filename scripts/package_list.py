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
        'namespace': 'ate_sammy'
    },
    {
        'name': 'semi-ate-plugins',
        'dir': Path(git_root_folder, 'src/ATE_semiateplugins'),
        'namespace': 'ate_semiateplugins'
    },
    {
        'name': 'semi-ate-spyder',
        'dir': Path(git_root_folder, 'src/ATE_spyder'),
        'namespace': 'ate_spyder'
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
        'name': 'semi-ate-testers',
        'dir': Path(git_root_folder, 'src/Plugins/semi_ate_testers'),
        'namespace': 'semi_ate_testers'
    },
]

integration_test_packages = [
    {
        'name': 'dummy-handler-app',
        'dir': Path(git_root_folder, 'src/integration_tests/handler_app'),
        'namespace': 'dummy_handler_app'
    },
    {
        'name': 'integration-test-common',
        'dir': Path(git_root_folder, 'src/integration_tests/Plugins/Common'),
        'namespace': 'Common'
    },
    {
        'name': 'dummy-plugin',
        'dir': Path(git_root_folder, 'src/integration_tests/Plugins/dummy_tester'),
        'namespace': 'dummy_tester'
    },
]