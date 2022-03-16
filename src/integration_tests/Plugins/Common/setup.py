from setuptools import find_packages, setup
from pathlib import Path
from . import __version__

version = __version__
requirements_path = Path(Path(__file__).parents[0], '../../requirements/test.txt')
def add_version(name: str) -> str:
    return f'{name.rstrip()}=={version}' if 'ate' in name else name.rstrip()
       
with requirements_path.open('r') as f:
    install_requires = list(map(add_version, f))

setup(
    name='integration-test-common',
    version=version,
    description='',
    long_description='',
    long_description_content_type='',
    author="The Semi-ATE Project Contributors",
    author_email="ate.organization@gmail.com",
    license="GPL2",
    keywords="Semiconductor ATE Automatic Test Equipment Spyder Plugin",
    platforms=["Windows", "Linux", "Mac OS-X"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
)
