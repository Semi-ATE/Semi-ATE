import argparse
from pathlib import Path
import shutil
from subprocess import Popen
from enum import Enum
from typing import List, Union
from package_list import distribution_packages, integration_test_packages
import re
from os.path import basename
from os import unlink

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
    SetupDirPath = 1
    InitDirPath = 2

    def __call__(self):
        return self.value


class Profile(Enum):
    Develop = 'develop'
    Cicd = 'cicd'
    Clean = 'clean'

    def __call__(self):
        return self.value

git_root_folder = Path(Path(__file__).parents[0], '../')
integration_tests_path = Path(git_root_folder, 'src/integration_tests')


def uninstall(packages: Package):
    package_list = _compute_package_list(packages, PackageType.Name)
    for p in package_list:
        print(f'Uninstalling: "{p}"')
        process = Popen(['python', '-m', 'pip', 'uninstall', '-y', '-q', p])
        exit_code = process.wait()
        if exit_code != 0:
            exit(exit_code)

def setup(packages: Package, setup_command: SetupCommand):
    setup_path_list = _compute_package_list(packages, PackageType.SetupDirPath)
    init_path_list = _compute_package_list(packages, PackageType.InitDirPath)

    for p in zip(setup_path_list, init_path_list):
        path = Path(Path(__file__).parents[0], p[0])
        if path.exists() == True:
            if setup_command == SetupCommand.Sdist:
                print(f'Generating sdist for folder {path}')

                _add_license_file(p[0], p[1])

                # create backup
                package_readme_path = Path(p[1], 'README.md')
                backup_readme_path = Path(p[1], 'README.md.bak')

                if package_readme_path.exists():
                    shutil.move(package_readme_path, backup_readme_path)

                    # replace readme by readme from the project root directory
                    global_readme_path = Path(git_root_folder, 'README.md')
                    shutil.copy(global_readme_path, package_readme_path)

                    # Extend readme
                    with package_readme_path.open('a') as readme:
                        with backup_readme_path.open('r') as temp_readme:
                            for line in temp_readme:
                                readme.write(line)
        
                # Generate SDIST
                process = Popen(['python', 'setup.py', setup_command()], cwd=str(path))
                exit_code = process.wait()

                # Revert readme changes
                if package_readme_path.exists():
                    shutil.move(backup_readme_path, package_readme_path)

                _remove_license_file(p[0], p[1])

                if exit_code != 0:
                    exit(exit_code)
            elif setup_command == SetupCommand.Install:
                print(f'Installing folder {path}')
                process = Popen(['python', '-m', 'pip', 'install', '-q', '.'], cwd=str(path))
                exit_code = process.wait()
                if exit_code != 0:
                    exit(exit_code)
            else:
                print(f'Installing folder {path} in editable mode')
                process = Popen(['python', '-m', 'pip', 'install', '-q', '-e', '.'], cwd=str(path))
                exit_code = process.wait()
                if exit_code != 0:
                    exit(exit_code)
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
    exit_code = process.wait()
    if exit_code != 0:
        exit(exit_code)


def tag_version(packages: Package, version: str):
    package_list = _compute_package_list(packages, PackageType.InitDirPath)
    for p in package_list:
        path = Path(p, '__init__.py')
        licence_path = Path(Path(__file__).parent, '../LICENSE.txt')
        with path.open('a+') as init_file:
            init_file.write('__license__ = """\n')
            with licence_path.open('r') as license_file:
                for line in license_file:
                    init_file.write(line)
            init_file.write('"""\n')
            init_file.write(f'__version__ = \'{version}\'\n')

def _compute_package_list(package_type: Package, type: PackageType) -> Union[List[str], List[Path]]:
    if package_type == Package.Distribution:
        packages = distribution_packages
    elif package_type == Package.All:
        packages = distribution_packages
        packages.extend(integration_test_packages)
    else:
        packages = integration_test_packages
    
    if type == PackageType.Name:
        return list(map(lambda entry: entry['name'], packages))
    elif type == PackageType.SetupDirPath:
        return list(map(lambda entry: entry['dir'], packages))
    else:
        # directory path to __init__.py package file
        return list(map(lambda entry: Path(entry['dir'], entry['namespace']), packages))


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


def _collect_test_requirements(include_cicd: bool) -> List[Path]:
    distribution_packages_paths = _compute_package_list(Package.Distribution, PackageType.SetupDirPath)
    distribution_packages_paths.append(integration_tests_path)
    path_list = list(map(lambda entry: Path(entry, 'requirements/test.txt'), distribution_packages_paths))
    if include_cicd == True:
        path_list.append(Path(git_root_folder, 'requirements/cicd.txt'))
    return path_list


def _collect_packages_from_paths(paths: List[Path]) -> List[str]:
    packages = set()
    for p in paths:
        if p.exists() == True:
            with p.open('r') as f:
                for line in f:
                    line_without_comment = re.sub(r'#.*$', '', line).strip()
                    if line_without_comment != '':
                        packages.add(line.strip())
    return list(packages)

def _add_license_file(manifest_folder: Path, package_folder: Path) -> None:
    # add license file to package_folder
    global_license_path = Path(git_root_folder, 'LICENSE.txt')
    shutil.copy(global_license_path, Path(package_folder, 'LICENSE.txt'))

    # extend MANIFEST.in
    manifest_path = Path(manifest_folder, 'MANIFEST.in')
    with manifest_path.open('a') as manifest:
        manifest.write('\n')
        manifest.write(f'include {basename(package_folder)}/LICENSE.txt')
        manifest.write('\n')

def _remove_license_file(manifest_folder: Path, package_folder: Path) -> None:
    # remove file if exists
    license_file_path = Path(package_folder, 'LICENSE.txt')
    if license_file_path.exists():
        unlink(license_file_path)

    # remove from MANIFEST.in
    unwanted_line = f'include {basename(package_folder)}/LICENSE.txt'
    manifest_path = Path(manifest_folder, 'MANIFEST.in')
    with manifest_path.open('r') as manifest:
        manifest_lines = manifest.readlines()
    with manifest_path.open('w') as manifest:
        for line in manifest_lines:
            if line.strip('\n') != unwanted_line and line != '\n':
                manifest.write(line)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--setup-cmd', choices=[SetupCommand.Develop(), SetupCommand.Install(), SetupCommand.Sdist()], help='runs "python setup.py" with the provided value')
    parser.add_argument('--packages', choices=[Package.Distribution(), Package.Test(), Package.All()], help='packages that should be processed')
    parser.add_argument('--uninstall', action='store_true', help='uninstall the selected packages from environment using "pip"')
    parser.add_argument('--change-env', choices=[Profile.Develop(), Profile.Cicd(), Profile.Clean()], help='Setup/Installs all packages to the current environment to be ready for developing or running CI/CD scripts. To do so this option relies on "pip".')
    parser.add_argument('--tag-version', type=str, help='Version to write into "__init__.py" package files')

    args = parser.parse_args()
    setup_command = SetupCommand.Develop if args.setup_cmd == None else _command_from_string(args.setup_cmd)
    packages = Package.All if args.packages == None else _package_from_string(args.packages)

    if args.uninstall == True:
        uninstall(packages, PackageType.Name)
    elif args.change_env != None:
        change_environment(_profile_from_string(args.change_env))
    elif args.tag_version != None:
        tag_version(packages, args.tag_version)
    else:
        setup(packages, setup_command)


if __name__ == '__main__':
    main()
