from setuptools import find_packages, setup
from pathlib import Path
from semi_ate_testers import __version__

version = __version__
requirements_path = Path(Path(__file__).parents[0], 'requirements/run.txt')
       
with requirements_path.open('r') as f:
    install_requires = list(f)

readme_path = Path(Path(__file__).parent, './semi_ate_testers/README.md')
with readme_path.open('r') as f:
    long_description = f.read()

setup( 
    name="semi-ate-testers",
    version=version,
    description='semi-ate-testers is an example implementation of a plugin that can be consumed by the semi-ate-spyder plugin and the master application.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="The Semi-ATE Project Contributors",
    author_email="ate.organization@gmail.com",
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    entry_points={"ate.org": ["plug = semi_ate_testers:Plugin"]},
    py_modules=["semi_ate_testers"],
)
