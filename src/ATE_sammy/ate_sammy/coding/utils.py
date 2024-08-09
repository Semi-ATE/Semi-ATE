from pathlib import Path
import os


STIL_COMPILED_FILE_EXTENSION = 'hdf5'


def collect_compiled_patterns(patterns: dict, project_path: Path, protocols_path: str, patternoutput_path: str):
    compiled_patterns = {}
    for testbench, pattern_list in patterns.items():
        for pattern_tuple in pattern_list:
            name = pattern_tuple[0]
            rel_path = Path(pattern_tuple[1]).name
            compiled_file_path = project_path.joinpath(patternoutput_path, f'{rel_path}.{STIL_COMPILED_FILE_EXTENSION}')

            compiled_patterns[f'{testbench}_{name}'] = str(compiled_file_path)

    for root, directories, files in os.walk(os.path.join(project_path, protocols_path)):
        for filename in files:
            if filename.endswith("stil"):
                compiled_file_path = project_path.joinpath(patternoutput_path, f'{filename}.{STIL_COMPILED_FILE_EXTENSION}')
                compiled_patterns[filename.split('.')[0]] = str(compiled_file_path)

    return compiled_patterns
