
from setuptools import find_packages, setup

setup(
    name="ATE",
    version="0.1.0",
    description="",
    author="",
    author_email="",
    license="GPL2",
    keywords="",
    packages=find_packages(),
    entry_points={
        "spyder.plugins": [
            "ate = ATE.spyder.plugin:ATE",
        ]
    }
)
