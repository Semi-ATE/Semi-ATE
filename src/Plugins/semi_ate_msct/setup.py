from setuptools import find_packages, setup
from pathlib import Path
from semi_ate_msct import __version__

version = __version__
requirements_path = Path(Path(__file__).parents[0], 'requirements/run.txt')
       
with requirements_path.open('r') as f:
    install_requires = list(f)

readme_path = Path(Path(__file__).parent, './semi_ate_msct/README.md')
with readme_path.open('r') as f:
    long_description = f.read()

setup(
    name="semi-ate-msct",
    version=version,
    description='semi_ate_msct is a plugin for semi-ate-spyder.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="The Semi-ATE Project Contributors",
    author_email="ate.organization@gmail.com",
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    entry_points={"ate.org": ["msctplug = semi_ate_msct:Plugin"]},
    py_modules=["semi_ate_msct"],
)