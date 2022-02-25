import pathlib
import shutil

def create_setup(url: str, version: str, name: str, description: str, entry_point: str = None):
    file = 'setup.py'
    newline = '\n'
    content = f'''from setuptools import find_packages, setup

setup(
    name='{name}',
    version='{version}',
    description='{description}',
    long_description='',
    long_description_content_type='',
    author="The Semi-ATE Project Contributors",
    author_email="ate.organization@gmail.com",
    license="GPL2",
    keywords="Semiconductor ATE Automatic Test Equipment Spyder Plugin",
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
    ],{newline + '    entry_points={' if entry_point else ''}{newline + '        ' + entry_point if entry_point else ''}{newline + '    }' if entry_point else ''}
)
'''
    file_path = pathlib.Path(url, file)
    with file_path.open('w') as f:
        f.write(content)

def create_structure(name: str, prefix_url: str, source_url: str, target_url: str):
    target_path = pathlib.Path(target_url, name, prefix_url)
    source_path = pathlib.Path(source_url)

    if target_path.exists():
        shutil.rmtree(str(target_path))

    shutil.copytree(str(source_path), str(target_path))
