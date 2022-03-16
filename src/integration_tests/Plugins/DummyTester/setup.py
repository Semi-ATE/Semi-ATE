from setuptools import find_packages, setup
from DummyTester import __version__

version = __version__
setup( 
    name="Dummy.Plugin",
    install_requires=['requests'],
    version=version,
    packages=find_packages(),
    include_package_data=True,
    entry_points={"ate.org": ["dummytester = DummyTester:Plugin"]},
    py_modules=["DummyTester"],
)
