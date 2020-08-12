from setuptools import setup
setup( 
    name="TDK.Micronas",
    install_requires="",
    entry_points={"ate.org": ["plug = TDKMicronas:Plugin"]},
    py_modules=["TDKMicronas"],
)