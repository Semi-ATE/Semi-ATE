import os
import json


def load_json_from_file(file_name: str):
    if not os.path.exists(file_name):
        raise FileNotFoundError(f'configuration file not found: {file_name}')

    with open(file_name) as f:
        return json.load(f)
