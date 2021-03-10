# -*- coding: utf-8 -*-
import io

from setuptools import find_packages, setup
from ATE import __version__

# =============================================================================
# Use Readme for long description
# =============================================================================
with io.open('README.md', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

setup(
    name="Semi-ATE",
    version=__version__,
    description="Framework for Semiconductor ATE testing projects",
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author="The Semi-ATE Project Contributors",
    author_email="ate.organization@gmail.com",
    license="GPL2",
    keywords="Semiconductor ATE Automatic Test Equipment",
    platforms=["Windows", "Linux", "Mac OS-X"],
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)',
        'Topic :: Scientific/Engineering :: Human Machine Interfaces',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ],
    entry_points={
        "spyder.plugins": [
            "ate = ATE.spyder.plugin:ATE",
        ]
    }
)
