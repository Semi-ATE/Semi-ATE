# Semi-ATE

**Semi**conductor **A**utomated **T**est **E**quipment

[![GitHub](https://img.shields.io/github/license/Semi-ATE/Semi-ATE?color=black)](https://github.com/Semi-ATE/Semi-ATE/blob/master/LICENSE.txt)
[![Conda](https://img.shields.io/conda/pn/conda-forge/starz?color=black)](https://www.lifewire.com/what-is-noarch-package-2193808)
[![Supported Python versions](https://img.shields.io/badge/python-%3E%3D3.8-black)](https://www.python.org/downloads/)

[![CI-CD](https://github.com/Semi-ATE/Semi-ATE/workflows/CI-CD/badge.svg)](https://github.com/Semi-ATE/Semi-ATE/actions/workflows/CICD.yml?query=workflow%3ACD)

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/Semi-ATE/Semi-ATE?color=blue&label=GitHub&sort=semver)](https://github.com/Semi-ATE/Semi-ATE/releases/latest)
[![GitHub commits since latest release (by date)](https://img.shields.io/github/commits-since/Semi-ATE/Semi-ATE/latest)](https://github.com/Semi-ATE/Semi-ATE)
[![PyPI](https://img.shields.io/pypi/v/Semi-ATE?color=blue&label=PyPI)](https://pypi.org/project/Semi-ATE/)
[![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/Semi-ATE?color=blue&label=conda-forge)](https://anaconda.org/conda-forge/semi-ate)
[![conda-forge feedstock](https://img.shields.io/github/issues-pr/conda-forge/Semi-ATE-feedstock?label=feedstock)](https://github.com/conda-forge/Semi-ATE-feedstock)

[![GitHub issues](https://img.shields.io/github/issues/Semi-ATE/Semi-ATE)](https://github.com/Semi-ATE/Semi-ATE/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/Semi-ATE/Semi-ATE)](https://github.com/Semi-ATE/Semi-ATE/pulls)
![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/semi-ate.svg?color=brightgreen)

`Semi-ATE` is a tester- and instruments **AGNOSTIC** framework for **Semi**conductor **ATE** ASIC testing projects.

This means that the system is **not** build around a specific instrument (let's consider an ATE tester for a moment as a super instrument), it rather focuses on
organizing semiconductor testing in such a way that **all** use- (and special) corner cases have their well known place. This enables the users (read: DE's, TCE's, TE's & PE's) to focus on the **REAL** work, being the writing of good, fast and stable tests. Organizing tests into test-programs and test-programs in to flows is handled by wizards, so the only code that needs writing is the actual test! (motto: [Code is our enemy](http://www.skrenta.com/2007/05/code_is_our_enemy.html))

The `Semi-ATE` package is written purely in Python (noarch) and provides besides libraries also a plugin to the [Spyder](https://www.spyder-ide.org/) IDE.

## Packages

The Semi-ATE project consists of several packages. When writing this document the following packages are maintained by the Semi-ATE project:

* semi-ate-common
* semi-ate-project-database
* semi-ate-sammy
* semi-ate-plugins
* semi-ate-testers
* semi-ate-spyder
* semi-ate-apps-common
* semi-ate-control-app
* semi-ate-master-app
* semi-ate-test-app

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



