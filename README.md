# Semi-ATE

**Semi**conductor **A**utomated **T**est **E**quipment

[![GitHub](https://img.shields.io/github/license/Semi-ATE/Semi-ATE?color=black)](https://github.com/Semi-ATE/Semi-ATE/blob/main/LICENSE)
[![Conda](https://img.shields.io/conda/pn/conda-forge/starz?color=black)](https://www.lifewire.com/what-is-noarch-package-2193808)
[![Supported Python versions](https://img.shields.io/badge/python-%3E%3D3.7-black)](https://www.python.org/downloads/)

[![CI](https://github.com/Semi-ATE/Semi-ATE/workflows/CI/badge.svg?branch=master)](https://github.com/Semi-ATE/Semi-ATE/actions?query=workflow%3ACI)
[![CD](https://github.com/Semi-ATE/Semi-ATE/workflows/CD/badge.svg)](https://github.com/Semi-ATE/Semi-ATE/actions?query=workflow%3ACD)

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/Semi-ATE/Semi-ATE?color=blue&label=GitHub&sort=semver)](https://github.com/Semi-ATE/Semi-ATE/releases/latest)
[![GitHub commits since latest release (by date)](https://img.shields.io/github/commits-since/Semi-ATE/Semi-ATE/latest)](https://github.com/Semi-ATE/Semi-ATE)
[![PyPI](https://img.shields.io/pypi/v/Semi-ATE?color=blue&label=PyPI)](https://pypi.org/project/Semi-ATE/)
[![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/Semi-ATE?color=blue&label=conda-forge)](https://anaconda.org/conda-forge/semi-ate)
[![conda-forge feedstock](https://img.shields.io/github/issues-pr/conda-forge/Semi-ATE-feedstock?label=feedstock)](https://github.com/conda-forge/Semi-ATE-feedstock)

[![GitHub issues](https://img.shields.io/github/issues/Semi-ATE/Semi-ATE)](https://github.com/Semi-ATE/Semi-ATE/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/Semi-ATE/Semi-ATE)](https://github.com/Semi-ATE/Semi-ATE/pulls)
![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/semi-ate.svg?color=brightgreen)

`Semi-ATE` is a tester- and instruments **AGNOSTIC** framework for **Semi**conductor **ATE** ASIC testing projects.

This means that the system is **not** build around a specific instrument (let's consider an ATE tester for a moment as a super instrument😋), it rather focuses on
organizing semiconductor testing in such a way that **all** use- (and special) corner cases have their well known place. This enables the users (read: DE's, TCE's, TE's & PE's) to focus on the **REAL** work, being the writing of good, fast and stable tests. Organizing tests into test-programs and test-programs in to flows is handled by wizards, so the only code that needs writing is the actual test! (motto: [Code is our enemy](http://www.skrenta.com/2007/05/code_is_our_enemy.html))

The `Semi-ATE` package is writen purely in Python (noarch) and provides besides libraries also a plugin to the [Spyder](https://www.spyder-ide.org/) IDE.

Still interested? Visit the [wiki](https://github.com/ate-org/Semi-ATE/wiki).

## Installation



## Setup Semi-ATE

## Setup on Windows

Assuming that the current directory is Semi-ATE root.

open a Windows command prompt(__CMD__) and run
the following command:

```Console
Powershell -ep Unrestricted -file setup.ps1
```

### Before starting the applications

Once, each step of the setup.ps1 is succeeded, we are good to go.

make sure conda environment is activated

Spyder-IDE:
1) start spyder from the terminal to create your own project:
$ spyder

* create a new Semi-ATE project and then your own tests and testprograms


Applications:
to test the generated testprogram in a virtual environment, follow the steps below:

1) make sure you got an mqtt-broker runs locally in your machine.
mosquitto can be used for this purpose.

    For further information please contact your IT.

2) Make sure to change the current directory as described below:
  - from the root directory, change directory to: ATE/Tester/TES/apps

xml file (le123456000.xml) should be adapted to support the new configured sbins, the testprogram path could be  
copied from Spyder-IDE directly. (the information should be adapted inside the 'Station' section)

3) now, you can start the master and control application.
    * start master and control applications in different terminal (environment must be activated in both terminals)
        $ python launch_master.py (terminal 1)
        $ python launch_control.py (terminal 2)

    hint: master and control apps could be configured via it's configuration files 'master_config_file.json' and 'control_config_file.json'

5) after all steps 1) to 4) are done
start a browser your choice and past the following url: http://localhost:8081/

you will be able to see the MiniSCT UI
