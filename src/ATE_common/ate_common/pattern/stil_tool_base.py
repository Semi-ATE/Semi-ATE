import os
import shutil
from pathlib import Path
from abc import ABC, abstractmethod


class StilToolBase(ABC):
    def __init__(self):
        self._compiled_patterns = None

    def getPath(self):
        '''get the necesary information about hardware, base, target
        #TODO!   this should  do the STIL-Widget
        '''
        import __main__

        mainFileSplit = __main__.__file__.split(os.sep)
        cwd = str(Path(__main__.__file__).parent.parent.parent.parent)
        filename = os.path.splitext(mainFileSplit[-1])[0]
        target = mainFileSplit[-1].split('_')[-3]
        base = mainFileSplit[-2]
        hardware = mainFileSplit[-3]
        projectname = mainFileSplit[-4]
        return cwd, os.path.join(hardware, base, target), filename

    def _add_protocols(self, compiled_pattern_list):
        cwd, relPath, projectFilename = self.getPath()
        outputdir = cwd + os.sep + 'pattern_output'
        for root, directories, files in os.walk(os.path.join(cwd, "protocols", relPath)):
            for filename in files:
                if filename.endswith("stil.hdf5"):
                    compiled_pattern_list.append(os.path.join(outputdir, filename))
                    shutil.copy(os.path.join(root, filename), os.path.join(outputdir, filename))
        return compiled_pattern_list

    def _load_patterns(self, compiled_patterns: dict):
        self._compiled_patterns = compiled_patterns

        compiled_pattern_list = self._add_protocols(list(set(compiled_patterns.values())))

        if not compiled_pattern_list:
            print('-------- there is no pattern/protocols to load ---------')
            return

        # patterns could be assigned for multiple tests
        # retrieve all the patterns so they appear only once in the list
        # make sure compiled patterns exists
        for compiled_pattern in compiled_pattern_list:
            if not Path(compiled_pattern).exists():
                raise Exception(f'pattern binary file: \'{compiled_pattern}\' is missing, make sure to compile all required pattern files')

        self._load_patterns_impl(compiled_pattern_list)

    @abstractmethod
    def _load_patterns_impl(self, compiled_patterns: list):
        pass

    def _get_pattern_name(self, pattern_virtual_name: str):
        if not self._compiled_patterns:
            raise Exception('no patterns are loaded')

        if not self._compiled_patterns.get(pattern_virtual_name):
            raise Exception(f'pattern: \'{pattern_virtual_name}\' is not loaded')

        return Path(self._compiled_patterns[pattern_virtual_name]).stem
