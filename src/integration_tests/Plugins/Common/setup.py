from setuptools import find_packages, setup
from pathlib import Path
from Common import __version__

version = __version__
requirements_path = Path(Path(__file__).parents[0], '../../requirements/test.txt')
       
with requirements_path.open('r') as f:
    install_requires = list(f)

setup(
    name='integration-test-common',
    version=version,
    description='',
    long_description='',
    long_description_content_type='',
    author="The Semi-ATE Project Contributors",
    author_email="ate.organization@gmail.com",
    license="GPL-2.0-only",
    keywords="Semiconductor ATE Automatic Test Equipment Spyder Plugin",
    platforms=["Windows", "Linux", "Mac OS-X"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=install_requires,
)
