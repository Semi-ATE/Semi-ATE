# Semi-ATE

**Semi**conductor **A**utomated **T**est **E**quipment

[![GitHub](https://img.shields.io/github/license/Semi-ATE/Semi-ATE?color=black)](https://github.com/Semi-ATE/Semi-ATE/blob/master/LICENSE.txt)
[![Conda](https://img.shields.io/conda/pn/conda-forge/starz?color=black)](https://www.lifewire.com/what-is-noarch-package-2193808)
[![Supported Python versions](https://img.shields.io/badge/python-%3E%3D3.8-black)](https://www.python.org/downloads/)
[![CI-CD](https://github.com/Semi-ATE/Semi-ATE/workflows/CI-CD/badge.svg)](https://github.com/Semi-ATE/Semi-ATE/actions/workflows/CICD.yml?query=workflow%3ACD)

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/Semi-ATE/Semi-ATE?color=blue&label=GitHub&sort=semver)](https://github.com/Semi-ATE/Semi-ATE/releases/latest)
[![GitHub commits since latest release (by date)](https://img.shields.io/github/commits-since/Semi-ATE/Semi-ATE/latest)](https://github.com/Semi-ATE/Semi-ATE)
[![GitHub issues](https://img.shields.io/github/issues/Semi-ATE/Semi-ATE)](https://github.com/Semi-ATE/Semi-ATE/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/Semi-ATE/Semi-ATE)](https://github.com/Semi-ATE/Semi-ATE/pulls)

`Semi-ATE` is a tester- and instruments **AGNOSTIC** framework for **Semi**conductor **ATE** ASIC testing projects.

This means that the system is **not** build around a specific instrument (let's consider an ATE tester for a moment as a super instrument), it rather focuses on
organizing semiconductor testing in such a way that **all** use- (and special) corner cases have their well known place. This enables the users (read: DE's, TCE's, TE's & PE's) to focus on the **REAL** work, being the writing of good, fast and stable tests. Organizing tests into test-programs and test-programs in to flows is handled by wizards, so the only code that needs writing is the actual test! (motto: [Code is our enemy](http://www.skrenta.com/2007/05/code_is_our_enemy.html))

The `Semi-ATE` package is written purely in Python (noarch) and provides besides libraries also a plugin to the [Spyder](https://www.spyder-ide.org/) IDE.

## Packages

The Semi-ATE project is maintained in this single repository, however it is released as a set of packages (all with the same version number) to accomodate the different use-cases.

| Package Name              | PyPI Version | conda Version | feedstock |
|:------------------------- |:----:|:-----------:|:---------:|
| [Semi-ATE-common](https://github.com/conda-forge/staged-recipes/pull/18605) | [![PyPI](https://img.shields.io/pypi/v/Semi-ATE-Common?color=blue&label=PyPI)](https://pypi.org/project/Semi-ATE/) | [![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/Semi-ATE-Common?color=blue&label=conda-forge)](https://anaconda.org/conda-forge/semi-ate-common) | [![conda-forge feedstock](https://img.shields.io/github/issues-pr/conda-forge/Semi-ATE-Common-feedstock?label=feedstock)](https://github.com/conda-forge/Semi-ATE-Common-feedstock) | 
| [Semi-ATE-project-database](https://github.com/conda-forge/staged-recipes/pull/18801) |[![PyPI](https://img.shields.io/pypi/v/Semi-ATE-project-database?color=blue&label=PyPI)](https://pypi.org/project/Semi-ATE-project-database/) | [![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/Semi-ATE-project-database?color=blue&label=conda-forge)](https://anaconda.org/conda-forge/semi-ate-project-database) | [![conda-forge feedstock](https://img.shields.io/github/issues-pr/conda-forge/Semi-ATE-project-database-feedstock?label=feedstock)](https://github.com/conda-forge/Semi-ATE-project-database-feedstock) |
| [Semi-ATE-sammy](https://github.com/conda-forge/staged-recipes/pull/18814) | [![PyPI](https://img.shields.io/pypi/v/Semi-ATE-sammy?color=blue&label=PyPI)](https://pypi.org/project/Semi-ATE-sammy/) | [![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/Semi-ATE-sammy?color=blue&label=conda-forge)](https://anaconda.org/conda-forge/semi-ate-sammy) | [![conda-forge feedstock](https://img.shields.io/github/issues-pr/conda-forge/Semi-ATE-sammy-feedstock?label=feedstock)](https://github.com/conda-forge/Semi-ATE-sammy-feedstock) |
| [Semi-ATE-plugins](https://github.com/conda-forge/staged-recipes/pull/18815) | [![PyPI](https://img.shields.io/pypi/v/Semi-ATE-plugins?color=blue&label=PyPI)](https://pypi.org/project/Semi-ATE-plugins/) | [![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/Semi-ATE-plugins?color=blue&label=conda-forge)](https://anaconda.org/conda-forge/semi-ate-plugins) | [![conda-forge feedstock](https://img.shields.io/github/issues-pr/conda-forge/Semi-ATE-plugins-feedstock?label=feedstock)](https://github.com/conda-forge/Semi-ATE-plugins-feedstock) |
| [Semi-ATE-testers](https://github.com/conda-forge/staged-recipes/pull/18852) | [![PyPI](https://img.shields.io/pypi/v/Semi-ATE-testers?color=blue&label=PyPI)](https://pypi.org/project/Semi-ATE-testers/) | [![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/Semi-ATE-testers?color=blue&label=conda-forge)](https://anaconda.org/conda-forge/semi-ate-testers) | [![conda-forge feedstock](https://img.shields.io/github/issues-pr/conda-forge/Semi-ATE-testers-feedstock?label=feedstock)](https://github.com/conda-forge/Semi-ATE-testers-feedstock) |
| [Semi-ATE-spyder](https://github.com/conda-forge/staged-recipes/pull/18853) | [![PyPI](https://img.shields.io/pypi/v/Semi-ATE-spyder?color=blue&label=PyPI)](https://pypi.org/project/Semi-ATE-spyder/) | [![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/Semi-ATE-spyder?color=blue&label=conda-forge)](https://anaconda.org/conda-forge/semi-ate-spyder) | [![conda-forge feedstock](https://img.shields.io/github/issues-pr/conda-forge/Semi-ATE-spyder-feedstock?label=feedstock)](https://github.com/conda-forge/Semi-ATE-spyder-feedstock) |
| [Semi-ATE-apps-common](https://github.com/conda-forge/staged-recipes/pull/18854) | [![PyPI](https://img.shields.io/pypi/v/Semi-ATE-apps-common?color=blue&label=PyPI)](https://pypi.org/project/Semi-ATE-apps-common/) | [![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/Semi-ATE-apps-common?color=blue&label=conda-forge)](https://anaconda.org/conda-forge/semi-ate-apps-common) | [![conda-forge feedstock](https://img.shields.io/github/issues-pr/conda-forge/Semi-ATE-apps-common-feedstock?label=feedstock)](https://github.com/conda-forge/Semi-ATE-apps-common-feedstock) |
| [Semi-ATE-control-app](https://github.com/conda-forge/staged-recipes/pull/18855) | [![PyPI](https://img.shields.io/pypi/v/Semi-ATE-control-app?color=blue&label=PyPI)](https://pypi.org/project/Semi-ATE-control-app/) | [![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/Semi-ATE-control-app?color=blue&label=conda-forge)](https://anaconda.org/conda-forge/semi-ate-control-app) | [![conda-forge feedstock](https://img.shields.io/github/issues-pr/conda-forge/Semi-ATE-control-app-feedstock?label=feedstock)](https://github.com/conda-forge/Semi-ATE-control-app-feedstock) |
| [Semi-ATE-master-app](https://github.com/conda-forge/staged-recipes/pull/18864)       | [![PyPI](https://img.shields.io/pypi/v/Semi-ATE-master-app?color=blue&label=PyPI)](https://pypi.org/project/Semi-ATE-master-app/) | [![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/Semi-ATE-master-app?color=blue&label=conda-forge)](https://anaconda.org/conda-forge/semi-ate-master-app) | [![conda-forge feedstock](https://img.shields.io/github/issues-pr/conda-forge/semi-ate-master-app-feedstock?label=feedstock)](https://github.com/conda-forge/Semi-ATE-master-app-feedstock) |
| [Semi-ATE-test-app](https://github.com/conda-forge/staged-recipes/pull/18865)         | [![PyPI](https://img.shields.io/pypi/v/Semi-ATE-test-app?color=blue&label=PyPI)](https://pypi.org/project/Semi-ATE-test-app/) | [![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/Semi-ATE-test-app?color=blue&label=conda-forge)](https://anaconda.org/conda-forge/semi-ate-test-app) | [![conda-forge feedstock](https://img.shields.io/github/issues-pr/conda-forge/Semi-ATE-test-app-feedstock?label=feedstock)](https://github.com/conda-forge/Semi-ATE-test-app-feedstock) |
| Semi-ATE-installer | [![PyPI](https://img.shields.io/pypi/v/Semi-ATE-installer?color=blue&label=PyPI)](https://pypi.org/project/Semi-ATE-installer/) | [![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/Semi-ATE-installer?color=blue&label=conda-forge)](https://anaconda.org/conda-forge/semi-ate-installer) | [![conda-forge feedstock](https://img.shields.io/github/issues-pr/conda-forge/Semi-ATE-installer?label=feedstock)](https://github.com/conda-forge/Semi-ATE-installer-feedstock) |

3rd party packages needed:

[mosquitto](https://github.com/conda-forge/staged-recipes/pull/18387) : [![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/mosquitto?color=blue&label=conda-forge)](https://anaconda.org/conda-forge/mosquitto)    [![conda-forge feedstock](https://img.shields.io/github/issues-pr/conda-forge/mosquitto-feedstock?label=feedstock)](https://github.com/conda-forge/mosquitto-feedstock) 




## Installation

Installation of the packages can be achieved via `conda` or [pip](https://packaging.python.org/en/latest/tutorials/installing-packages/#use-pip-for-installing).

### Installation using pip

Each package can be installed using `python -m pip install <package-name>`:

```Console
python -m pip install semi-ate-common
python -m pip install semi-ate-project-database
python -m pip install semi-ate-sammy
python -m pip install semi-ate-plugins
python -m pip install semi-ate-testers
python -m pip install semi-ate-spyder
python -m pip install semi-ate-apps-common
python -m pip install semi-ate-control-app
python -m pip install semi-ate-master-app
python -m pip install semi-ate-test-app
```

Or all at once:

```Console
python -m pip install semi-ate-common semi-ate-project-database semi-ate-sammy semi-ate-plugins semi-ate-testers semi-ate-spyder semi-ate-apps-common semi-ate-control-app semi-ate-master-app semi-ate-test-app
```

### Installation via Conda

To be defined
