# Import/Export

Import and Export of Tests is supported by the IDE.

### Export

User is able to import a test via right click on test from within Spyder IDE. Automatically, the exported file will be the name of the test and followed by a unique extension '<test_name>.ate'
__test_name__: could be changed
__.ate__: extension should not be changed, changing the extension will prevent importing the test 

### Import

Import is also supported from within Spyder IDE. 

the following cases are supported:
* import of non-existing test: a new test will be automatically generated and persisted
* import of already defined test: user will be provided in this case with a pop-up dialog in which three possible action are suggested:
    1. rename and followed with an input text, in which the user is able to put the new name of the exported test (rename existing test in this case is not possible)
    2. overwrite: the existing test will be in this case deleted and overwritten with the content of the imported test
    3. cancel: no changes will take place
* import of test with different version number: this case is not supported, no import is possible

