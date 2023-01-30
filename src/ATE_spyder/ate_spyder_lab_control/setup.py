from setuptools import find_packages, setup
from pathlib import Path
from labml_adjutancy import __version__

version = __version__
requirements_path = Path(Path(__file__).parents[0], 'requirements/run.txt')

with requirements_path.open('r') as f:
    install_requires = list(f)

readme_path = Path(Path(__file__).parent, './labml_adjutancy/README.md')
with readme_path.open('r') as f:
    long_description = f.read()

setup(
    name="LabMl-adjutancy",
    version=version,
    description="adjutancy lib for the Lab labor Measurement library",
    author="Semi-ATE",
    author_email="info@Semi-ATE.org",
    maintainer='Semi-ATE',
    maintainer_email='info@Semi-ATE.org',
    url="https://github.com/Semi-ATE",
    long_description=long_description,
    long_description_content_type='text/markdown',
    license="GPL-2.0-only",
    keywords="Semiconductor ATE Automatic Test Equipment Lab Labor",
    platforms=["Windows", "Linux", "Mac OS-X"],
    packages=find_packages(),
    install_requires=install_requires,
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ],
    python_requires='>=3.8',
    entry_points={
        "spyder.plugins": "lab_control = plugin:LabControlPlugin",
        "ate.org": "labmlplug = generalpurposefunc:Plugin"
    }
)
