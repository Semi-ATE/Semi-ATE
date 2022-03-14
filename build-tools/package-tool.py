import argparse
from pathlib import Path
from subprocess import Popen
from enum import Enum

class SetupCommand(Enum):
    Install = 'install'
    Sdist = 'sdist'
    Develop = 'develop'

    def __call__(self):
        return self.value

class Package(Enum):
    All = 'all',
    Distribution = 'distribution'
    Test = 'test'

    def __call__(self):
        return self.value

class PackageType(Enum):
    Name = 0
    Path = 1

    def __call__(self):
        return self.value

class Profile(Enum):
    Develop = 'develop'
    Cicd = 'cicd'
    Clean = 'clean'

    def __call__(self):
        return self.value

git_root_folder = Path(Path(__file__).parents[0], '../')

distribution_packages = [
    ['ate-common', Path(git_root_folder, 'src/ATE_common')],
    ['ate-project-database', Path(git_root_folder, 'src/ATE_projectdatabase')],
    ['ate-sammy', Path(git_root_folder, 'src/ATE_sammy')],
    ['semi-ate-plugins', Path(git_root_folder, 'src/ATE_semiateplugins')],
    ['ate-spyder', Path(git_root_folder, 'src/ATE_spyder')],
    ['tdk-micronas', Path(git_root_folder, 'src/Plugins/TDKMicronas')],
    ['ate-apps-common', Path(git_root_folder, 'src/Apps/common')],
    ['ate-control-app', Path(git_root_folder, 'src/Apps/control_app')],
    ['ate-master-app', Path(git_root_folder, 'src/Apps/master_app')],
    ['ate-test-app', Path(git_root_folder, 'src/Apps/test_app')],
    ['ate-handler-app', Path(git_root_folder, 'src/Apps/handler_app')],
]

integration_test_packages = [
    ['integration-test-common', Path(git_root_folder, 'src/integration_tests/Plugins/Common')],
    ['dummy-plugin', Path(git_root_folder, 'src/integration_tests/Plugins/DummyTester')],
]

integration_tests_path = Path(git_root_folder, 'src/integration_tests')

def uninstall(packages: Package):
    package_list = _compute_package_list(packages, PackageType.Name)
    for p in package_list:
        print(f'Uninstalling: "{p}"')
        process = Popen(['python', '-m', 'pip', 'uninstall', '-y', '-q', p])
        process.wait()

def setup(packages: Package, setup_command: SetupCommand):
    package_list = _compute_package_list(packages,  PackageType.Path)
    for p in package_list:
        path = Path(Path(__file__).parents[0], p)
        if path.exists() == True:
            if setup_command == SetupCommand.Sdist:
                print(f'Generating sdist for folder {path}')
                process = Popen(['python', 'setup.py', setup_command()], cwd=str(path))
                process.wait()
            elif setup_command == SetupCommand.Install:
                print(f'Installing folder {path}')
                process = Popen(['python', '-m', 'pip', 'install', '-q', '.'], cwd=str(path))
                process.wait()
            else:
                print(f'Installing folder {path} in editable mode')
                process = Popen(['python', '-m', 'pip', 'install', '-q', '-e', '.'], cwd=str(path))
                process.wait()
        else:
            print(f'ERROR: Path "{path}" could not be found!')

def change_environment(profile: Profile):
    if profile == Profile.Clean:
        uninstall(Package.All)
    else:
        setup(Package.All, SetupCommand.Develop)

    paths = _collect_test_requirements(True if profile == Profile.Clean or profile == Profile.Cicd else False)
    packages = _collect_packages_from_paths(paths)
    package_manager_action = 'uninstall' if profile == Profile.Clean else 'install'
    print_message = 'Uninstalling:' if profile == Profile.Clean else 'Innstalling:'
    process_args = ['python', '-m', 'pip', package_manager_action, *packages, '-q']

    if profile == Profile.Clean:
        process_args.append('-y')

    print(f'{print_message} {packages}')
    process = Popen(process_args)
    process.wait()

def _compute_package_list(package_type: Package, type: PackageType) -> list[str]:
    if package_type == Package.Distribution:
        packages = distribution_packages
    elif package_type == Package.All:
        packages = distribution_packages
        packages.extend(integration_test_packages)
    else:
        packages = integration_test_packages
    return list(map(lambda entry: entry[type()],packages))

def _command_from_string(value: str) -> SetupCommand:
    if value == SetupCommand.Develop():
        return SetupCommand.Develop
    elif value == SetupCommand.Install():
        return SetupCommand.Install
    else:
        return SetupCommand.Sdist

def _package_from_string(value: str) -> Package:
    if value == Package.All():
        return Package.All
    elif value == Package.Test():
        return Package.Test
    else:
        return Package.Distribution        

def _profile_from_string(value: str) -> Profile:
    if value == Profile.Develop():
        return Profile.Develop
    elif value == Profile.Cicd():
        return Profile.Cicd
    else:
        return Profile.Clean     

def _collect_test_requirements(include_cicd: bool) -> list[Path]:
    distribution_packages_paths = _compute_package_list(Package.Distribution, PackageType.Path)
    distribution_packages_paths.append(integration_tests_path)
    if include_cicd == True:
        distribution_packages_paths.append(git_root_folder)
    return list(map(lambda entry: Path(entry, 'requirements/test.txt'), distribution_packages_paths))

def _collect_packages_from_paths(paths: list[Path])-> list[str]:
    packages = set()
    for p in paths:
        if p.exists() == True:
            with p.open('r') as f:
                for line in f:
                    packages.add(line.strip())
    return list(packages)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--setup-cmd', choices=[SetupCommand.Develop(), SetupCommand.Install(), SetupCommand.Sdist()], help='runs "python setup.py" with the provided value')
    parser.add_argument('--packages', choices=[Package.Distribution(), Package.Test(), Package.All()], help='packages that should be processed')
    parser.add_argument('--uninstall', action='store_true', help='uninstall the selected packages from environment using "pip"')
    parser.add_argument('--change-env', choices=[Profile.Develop(), Profile.Cicd(), Profile.Clean()], help='Setup/Installs all packages to the current environment to be ready for developing or running CI/CD scripts. To do so this option relies on "pip".')

    args = parser.parse_args()
    setup_command = SetupCommand.Develop if args.setup_cmd == None else _command_from_string(args.setup_cmd)
    packages = Package.All if args.packages == None else _package_from_string(args.packages)

    if args.uninstall == True:
        uninstall(packages, PackageType.Name)
    elif args.change_env == None:
        setup(packages, setup_command)
    else:
        change_environment(_profile_from_string(args.change_env))


if __name__ == '__main__':
    main()