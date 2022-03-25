from setuptools import find_packages, setup
from dummy_tester import __version__

version = __version__
setup( 
    name="Dummy.Plugin",
    install_requires=['requests'],
    version=version,
    packages=find_packages(),
    include_package_data=True,
    entry_points={"ate.org": ["dummytester = dummy_tester:Plugin"]},
    py_modules=["dummy_tester"],
)
