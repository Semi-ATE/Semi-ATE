from setuptools import find_packages, setup
from pathlib import Path
from TDKMicronas import __version__

version = __version__
requirements_path = Path(Path(__file__).parents[0], 'requirements/run.txt')
def add_version(name: str) -> str:
    return f'{name.rstrip()}=={version}' if 'ate' in name else name.rstrip()
       
with requirements_path.open('r') as f:
    install_requires = list(map(add_version, f))

setup( 
    name="TDK.Micronas",
    version=version,
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    entry_points={"ate.org": ["plug = TDKMicronas:Plugin"]},
    py_modules=["TDKMicronas"],
)
