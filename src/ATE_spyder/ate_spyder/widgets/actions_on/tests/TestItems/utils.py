from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.actions_on.utils.MenuDialog import ImportDialog, Action, StandardDialog
import json
import re
from pathlib import Path
from pydantic import BaseModel


class FileStruct(BaseModel):
    version: int
    database: dict
    groups: list
    file: list


def export_content(path: Path, database: dict, file_path: Path, project_info: ProjectNavigation, test_name: str):
    data = {}
    data.update({'version': project_info.get_version()})
    data.update({'database': database})
    data.update({'groups': project_info.get_test_groups(test_name)})

    with open(path, 'w') as export:
        with open(file_path, 'r') as f:
            data.update({'file': f.readlines()})

        json.dump(data, export, indent=4)


def import_content(path: Path, project_info: ProjectNavigation, parent: object, current_version: int):
    file_struct = FileStruct(**get_file_content(path))

    if file_struct.version != current_version:
        exception = StandardDialog(parent, f"incompatible versions: current version '{current_version}' vs imported version '{file_struct.version}'")
        exception.exec_()
        return

    if not does_test_exist(file_struct.database, project_info):
        add_new_test(file_struct, project_info)
        update_test_file_impl(''.join(file_struct.file), project_info, file_struct.database)
        return

    wizard = ImportDialog(parent)
    if not wizard.exec_():
        # cancel will return with a none value
        return

    if wizard.action['type'] == Action.Rename:
        old_name = file_struct.database['name']
        file_struct.database['name'] = wizard.action['data']['name']

        add_new_test(file_struct, project_info)

        content = generate_file_content(file_struct, old_name)
        update_test_file_impl(content, project_info, file_struct.database)

    if wizard.action['type'] == Action.Overwrite:
        project_info.replace_test(file_struct.database)
        update_test_file_impl(''.join(file_struct.file), project_info, file_struct.database)


def get_file_content(path: Path):
    with open(path, 'r') as f:
        return json.load(f)


def generate_file_content(file_struct: FileStruct, old_name: str):
    to_find = f'{old_name}_BC'
    to_change = [(index, element) for index, element in enumerate(file_struct.file) if re.search(to_find, element) or re.search('class', element)]

    updated_changes = []
    for elem in to_change:
        index = elem[0]
        line = elem[1]

        if ('class' in line) and (to_find in line):
            line = f'class {file_struct.database["name"]}({file_struct.database["name"]}_BC):'
            updated_changes.append((index, line))
            continue

        line = line.replace(f'{old_name}_BC', f'{file_struct.database["name"]}_BC')
        line = line.replace(old_name, file_struct.database["name"])
        updated_changes.append((index, line))

    for (index, element) in updated_changes:
        file_struct.file[index] = element

    return ''.join(file_struct.file)


def does_test_exist(test_db: dict, project_info: ProjectNavigation):
    return project_info.does_test_exist(test_db['name'], test_db['hardware'], test_db['base'])


def add_new_test(file_struct: FileStruct, project_info: ProjectNavigation):
    file_struct.database.update({'groups': file_struct.groups})
    project_info.add_custom_test(file_struct.database)


def update_test_file_impl(file_content: str, project_info: ProjectNavigation, database: dict):
    file_name = f"{project_info.get_test_path(database['name'], database['hardware'], database['base'])}.py"
    with open(file_name, 'w') as test_file:
        test_file.write(file_content)
