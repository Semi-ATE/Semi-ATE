from setuptools import find_packages, setup
from pathlib import Path
from TDKMicronas import __version__

version = __version__
requirements_path = Path(Path(__file__).parents[0], 'requirements/run.txt')
def add_version(name: str) -> str:
    return f'{name.rstrip()}=={version}' if 'ate' in name else name.rstrip()
       
with requirements_path.open('r') as f:
    install_requires = list(map(add_version, f))

readme_path = Path(Path(__file__).parent, 'TDKMicronas/README.md')
with readme_path.open('r') as f:
    long_description = f.read()

setup( 
    name="TDK.Micronas",
    version=version,
    description='TDKMicrionas is an example implementation of a plugin that can be consumed by the semi-ate-spyder plugin',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="The Semi-ATE Project Contributors",
    author_email="ate.organization@gmail.com",
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    entry_points={"ate.org": ["plug = TDKMicronas:Plugin"]},
    py_modules=["TDKMicronas"],
)
