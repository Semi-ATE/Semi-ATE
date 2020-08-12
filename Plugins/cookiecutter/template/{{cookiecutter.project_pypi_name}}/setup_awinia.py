from setuptools import setup
setup( 
    name="TDK.Micronas",
    install_requires="ATE.org",
    entry_points={"ate.org": ["plug = TDKMicronas:Plugin"]},
    py_modules=["TDKMicronas"],
)