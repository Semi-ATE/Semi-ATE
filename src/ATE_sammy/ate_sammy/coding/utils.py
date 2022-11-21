from pathlib import Path


STIL_COMPILED_FILE_EXTENSION = 'hdf5'


def collect_compiled_patterns(patterns: dict, project_path: Path):
    compiled_patterns = {}
    for _, pattern_list in patterns.items():
        for pattern_tuple in pattern_list:
            name = pattern_tuple[0]
            rel_path = Path(pattern_tuple[1]).name
            compiled_file_path = project_path.joinpath('pattern_output', f'{rel_path}.{STIL_COMPILED_FILE_EXTENSION}')

            compiled_patterns[name] = str(compiled_file_path)

    return compiled_patterns
