# Semi-ATE

**Semi**conductor **A**utomated **T**est **E**quipment

[![GitHub](https://img.shields.io/github/license/Semi-ATE/Semi-ATE?color=black)](https://github.com/Semi-ATE/Semi-ATE/blob/main/LICENSE)
[![Conda](https://img.shields.io/conda/pn/conda-forge/Semi-ATE?color=black)](https://anaconda.org/conda-forge/Semi-ATE)
![Supported Python versions](https://img.shields.io/badge/python-%3E%3D3.8-black)

[![CI](https://github.com/Semi-ATE/Semi-ATE/workflows/CI/badge.svg?branch=master)](https://github.com/Semi-ATE/Semi-ATE/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/Semi-ATE/Semi-ATE/branch/main/graph/badge.svg?token=BAP0H9OMED)](https://codecov.io/gh/Semi-ATE/Semi-ATE)
[![CD](https://github.com/Semi-ATE/Semi-ATE/workflows/CD/badge.svg)](https://github.com/Semi-ATE/Semi-ATE/actions?query=workflow%3ACD)

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/Semi-ATE/Semi-ATE?color=blue&label=GitHub&sort=semver)](https://github.com/Semi-ATE/Semi-ATE/releases/latest)
[![GitHub commits since latest release (by date)](https://img.shields.io/github/commits-since/Semi-ATE/Semi-ATE/latest)](https://github.com/Semi-ATE/Semi-ATE)
[![PyPI](https://img.shields.io/pypi/v/Semi-ATE?color=blue&label=PyPI)](https://pypi.org/project/Semi-ATE/)
![Conda (channel only)](https://img.shields.io/conda/vn/conda-forge/Semi-ATE?color=blue&label=conda-forge)

[![GitHub issues](https://img.shields.io/github/issues/Semi-ATE/Semi-ATE)](https://github.com/Semi-ATE/Semi-ATE/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/Semi-ATE/Semi-ATE)](https://github.com/Semi-ATE/Semi-ATE/pulls)

`Semi-ATE` is a tester- and instruments **AGNOSTIC** framework for **Semi**conductor **ATE** ASIC testing projects.

This means that the system is **not** build around a specific instrument (let's consider an ATE tester for a moment as a super instrument😋), it rather focuses on
organizing semiconductor testing in such a way that **all** use- (and special) corner cases have their well known place. This enables the users (read: DE's, TCE's, TE's & PE's) to focus on the **REAL** work, being the writing of good, fast and stable tests. Organizing tests into test-programs and test-programs in to flows is handled by wizards, so the only code that needs writing is the actual test! (motto: [Code is our enemy](http://www.skrenta.com/2007/05/code_is_our_enemy.html))

The `Semi-ATE` package is writen purely in Python (noarch) and provides besides libraries also a plugin to the [Spyder](https://www.spyder-ide.org/) IDE.

Still interested? Visit the [wiki](https://github.com/ate-org/Semi-ATE/wiki).

## Installation

### maxiconda

Semi-ATE, [Semi-ATE-STDF](https://github.com/Semi-ATE/STDF), [Semi-ATE-STIL](https://github.com/Semi-ATE/STIL), [Semi-ATE-DT](https://github.com/Semi-ATE/STDF) and [QScreenCast](https://github.com/Semi-ATE/QScreenCast) are all bundeled with [spyder >= 5](https://github.com/spyder-ide/spyder) in the `_spyder_` environment when one installs conda using the [maxiconda](https://github.com/Semi-ATE/maxiconda) installers. 

### miniconda / miniforge

### anaconda





## Setup Semi-ATE

## Setup on Windows

Assuming that the current directory is Semi-ATE root.

open a Windows command prompt(__CMD__) and run
the following command:

```Console
Powershell -ep Unrestricted -file setup.ps1
```

### Before starting the applications

Once, each step of the setup.ps1 is succeeded the following steps must be checked:

1) testprogram name must be adapted in ATE/Tester/TES/apps/le123456000.xml, therefore replace the 'PROGRAM_DIR#' in 'STATION' section with the following:

    ```Console
    <missing_part>/smoketest/smoke_test/src/HW0/PR/smoke_test_HW0_PR_Die1_Production_PR_1.py 
    ```

    you will find the smoketest directory in the root level of Semi-ATE directory

    \<missing_part> must be replaced with the missing path piece to fit the absolut path of the test program

2) lot number must be adapted in ATE/Tester/TES/apps/le123456000.xml.
Therefore, 'LOTNUMBER' field muss be fit. Assuming the xml file name is
'le123456000.xml', LOTNUMNBER field should look as follow:

    __\<LOTNUMBER>123456.000\</LOTNUMBER>__

3) After configuring xml-file there still one thing to do.
open the master configuration file (ATE/Tester/TES/apps/master_configuration_file.json)
and replace the 'filesystemdatasource.jobpattern' key-value with
the xml file name.

    Based on the example above, this should look something like this:
    __'filesystemdatasource.jobpattern': 'le123456000.xml'__

    ---
    __NOTE__
    </br>
    As soon the xml-file name is changed, make sure to update the lot number as discribed in 2) and 3)  !

    ---

4) in case you generate your own test-program you need to make sure
that the bin mapping inside the XML-file mappe those sbins the test-program uses.

5) make sure you got an mqtt-broker runs in your local machine.
mosquitto can be used for this purpos.

    For further informations please contact your IT.

## Running Spyder-IDE

before you can use spyder you should have already cloned the
repository from git (could be done using the 'setup.ps1' script)

If already done, than switch to spyder directory and run the following command:

```Console
python bootstrap.py
```
