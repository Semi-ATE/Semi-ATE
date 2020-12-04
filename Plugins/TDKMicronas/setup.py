from setuptools import find_packages, setup

setup( 
    name="TDK.Micronas",
    install_requires=['requests'],
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    entry_points={"ate.org": ["plug = TDKMicronas:Plugin"]},
    py_modules=["TDKMicronas"],
)
