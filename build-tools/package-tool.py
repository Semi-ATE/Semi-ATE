from pathlib import Path
from os import getcwd
from subprocess import Popen

cwd=getcwd()
local_packages = [
    '../src/ATE_common',
    '../src/ATE_projectdatabase',
    '../src/ATE_sammy',
    '../src/ATE_semiateplugins',
    '../src/ATE_spyder',
    '../src/Plugins/TDKMicronas',
    '../src/Apps/common',
    '../src/Apps/control_app',
    '../src/Apps/master_app',
    '../src/Apps/test_app',
    '../src/Apps/handler_app',
]

for p in local_packages:
    path=Path(cwd, p)
    process=Popen(['python', 'setup.py', 'develop'], cwd=str(path))
    process.wait()

