# Semi-ATE
<ins>**Semi**</ins>conductor <ins>**A**</ins>utomated <ins>**T**</ins>est <ins>**E**</ins>quipment

`Semi-ATE` is a tester- and instruments **AGNOSTIC** framework for **<ins>Semi</ins>conductor <ins>ATE</ins> ASIC testing** projects.

This means that the system is **not** build around a specific instrument (let's consider an ATE tester for a moment as a super instrument😋), it rather focuses on
organizing semiconductor testing in such a way that **all** use- (and special) corner cases have their well known place. This enables the users (read: DE's, TCE's, TE's & PE's) to focus on the **REAL** work, being the writing of good, fast and stable tests. Organizing tests into test-programs and test-programs in to flows is handled by wizards, so the only code that needs writing is the actual test! (motto: [Code is our enemy](http://www.skrenta.com/2007/05/code_is_our_enemy.html))

The `Semi-ATE` package is writen purely in Python (noarch) and provides besides libraries also a plugin to the [Spyder](https://www.spyder-ide.org/) IDE.


Still interested? Visit the [wiki](https://github.com/ate-org/Semi-ATE/wiki). 

Yours,

Tom 


# Setup Semi-ATE

## HowTo: on Windows

### Setup

Assuming that the current directory is Semi-ATE root.

open a Windows command prompt(__CMD__) and run
the following command:
```Console
Powershell -ep Unrestricted -file setup.ps1
```

### Before starting the applications

**Make sure**!

1) testprogram name must be adapted in ATE/Tester/TES/apps/le306426000.xml, therefore replace the 'PROGRAM_DIR#' in 'STATION' section with the following:

    ```Console
    <missing_part>/tests/ATE/spyder/widgets/CI/qt/smoketest/smoke_test/src/HW0/PR/smoke_test_HW0_PR_Die1_Production_PR_1.py
    ```

    \<missing_part> must be replaced with the missing path piece to fit the absolut path of the test program


2) lot number must be adapted in ATE/Tester/TES/apps/le306426000.xml.
Therefore, 'LOTNUMBER' field muss be fit. Assuming the xml file name is
'le306426000.xml', LOTNUMNBER field should look as the following:
<LOTNUMBER>306426.000</LOTNUMBER>

3) After configuring xml-file there still one thing to do.
open the master configuration file (ATE/Tester/TES/apps/master_configuration_file.json)
and replace the 'filesystemdatasource.jobpattern' key-value with
the xml file name.

    Based on the example above, this should look something like this:
    'filesystemdatasource.jobpattern': 'le306426000.xml'


---
__NOTE__

As soon the xml-file name is changed, make sure to update the lot number as discribed in 2) and 3)  !

---
