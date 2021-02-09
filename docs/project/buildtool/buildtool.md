# sammy, the Semi-ATE.org build- & project tool
Semi-ATE is split up into several modules, one of which is the buildtool "sammy" which is used to generate the executable part of all projects. The IDE uses sammy as backend when a project is edited to generate an uptodate state of the project. 

## Uusing sammy
sammy always works in the cwd and uses the __\<verb>__ __\<noun>__ __\<param>__ notation for its control.

## Verbs
### generate
The "generate" verb triggers sammy to regenerate an aspect of the project. Generate supports the following nouns:
* all: This parameter will perform a complete build of the project an regenerate all previsously generated code.
* hardware: This parameter will regenerate all the hardwaredefinitions
* sequence \<sequencename>: This parameter will regenerate a given sequence, i.e. the testprogram for this sequence is regenerated
* sequence: Regenerates all sequences
* test \<testname>: Regenerates a given test
* test: Regenerates all tests

### new
The "new" verb triggers sammy to create a new entity depending on the noun. Supported nouns:
* project \<projectname>: Creates a new folder named \<projectname> and creates a new empty project inside
* default-project \<projectname>: Creates a project using default settings with one dummy product/hardware/die/device etc. that is ready to use to start creating tests

### migrate
Migrate will attempt to convert the project in the current folder to the most recent project format. Migrate does not support any nouns.

### query
The query verb allows to query different aspects of the current project. Supported nouns:
* tests: Returns the number of tests in this project
* version: Returns the version of the projectformat

## Examples
Regenerate a projet: ``` sammy generate all ```

Regenerate the hardwaredefinitions of the project: ``` sammy generate hardware ```

Rengenerate a testprogramm named foo: ``` sammy generate sequence foo ```

Create a new project: ``` sammy new project myproject ```

Migrate a project: ```sammy migrate```

Query the version of a project: ```sammy query version```

