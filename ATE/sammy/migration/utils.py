import os
import json
from pathlib import Path

VERSION = 'version'
VERSION_FILE_NAME = 'version.json'


def generate_path(cwd: str, dir_name: str) -> str:
    path = os.path.join(cwd, dir_name)
    return os.fspath(Path(path))


def write_version_to_file(file_path: str, version: dict):
    with open(file_path, 'w') as f:
        json.dump(version, f, indent=4)
