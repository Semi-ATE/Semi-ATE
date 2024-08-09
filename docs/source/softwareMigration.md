# Software Release: Semi-ATE Project
to make the user aware that his current project is not compatible with the newest
released API, we must have a mechanism to determine inconsistencies.

today, as soon as a project becomes incompatible, user is not even able
to open it.
in this case, user can do nothing but create a new project and migrate manually.

breaking changes are basically those, each time the database
structure is changed. 
to deal with these breaking changes we must provide a migration tool 
that tracks changes between two or more releases and propose some solution for any 
inconsistency. 

__proposal__: 
```
user get a new release and try to open his current project. if the released
API and project are not compatible, a user message would pop up to signalize 
that the project muss be migrated and propose an automatic migration if possible.
```

## Migration Tool
migration tool library is in this case python code that contains a defined link to
the database structure which have been modified and is not compatible anymore with last
released version.

this would help to determine if the new released API is backward
compatible and if the already available project still work.
if not then provide the user with all needed information to migrate the project easily or
even migrate automatically if possible.


the task of the migration tool is to detect incompatibilities within a 
database structure and ideally provide a quick fix or. a migrate option to the user.

__scenario 1__: migration tool is able to migrate project automatically without user interaction
```
suppose the instruments under hardware configuration must be for some reasons enumerated.
the build tool script will then be adapted to go throw all defined or. used instruments 
and assign each instrument with a different index.
```

__scenario 2__: migration tool is not able to migrate the project automatically, but still can 
adapt the project such that the required database structure will be integrated, but
still need to be configured manually by the user.
```
suppose now we want to expand the test program wizard with a new tab, this contains user information that are needed for the test program execution and are unique for each test program. in this case all affected test program are going to turn invalid and will be highlighted over the IDE.
```

__scenario 3__: migration tool is not able at all to migrate.
```
suppose we have three releases (release 1, release 2, release 3).
user did migrate his project only in release 1. now he want to migrate the project in the 
actual version of the API (release 3).
in this case the migration tool will try to do the migration incrementally, e.g from release
1 to release 2 and finally release 3.
if the migration from release 1 to release 2 contains a user specific 
configuration (as described in scenario 2), the tool would not be able to do the migration
to release 3.
therefore the use must first fetch release 2 and do the migration by himself and then 
migrate to release 3.

```

## Versioning
using versioning can help determine versions that need to be migrated from those trivial once.

each new created project must contain a version number extracted from the available
API and is stored in a json file and would be formatted as follow:
X.Y.Z (major, minor) where:
* major for incompatible changes:
    
    * API releases that change one or more of the database structures which cannot be 
    migrated automatically.
* minor for compatible changes:

    * API releases that provide new features (e.g new option in tree view)


unversioned projects should become a default version number known by the tool to still 
guarantee the migration to other releases.

the version number can then easily be read by the IDE to determine any inconsistency.


## Migration Strategy
developer must be aware of breaking changes that will invalidate projects created in 
previously released API. 

the migration tool should know if the next released version contains any breaking changes and
specifically where. So, the developer of the tool must provide it with all 
information needed to inform the user and if possible suggest a migration process.
the tool must provide, which database structure are affected and give some suggestion to
solve those conflicts or. incompatibilities.


## Migration Tests
there are for sure some cases where the developer is not aware that the changes 
are breaking changes. therefore, we must be able to determine automatically if it would
be a major or minor changes release.

to guarantee, that any backward incompatible release contains the correct migration tool,
we would artifact projects after each API
release. So, every new release became automatically a project of a previous released 
API, to determine if a migration to the actual release is possible.

this process must be integrated to run automatically on the build system.


## Disadvantages and Advantages
### Advantages: 
* user is not forced each time to create a new project and do the migration manually,
this would save a lot of development time
* best case, user is not involved and the tool handles the migration automatically
* user interaction is supported by the IDE e.g the migration tool provide all significant
information to the IDE, who on his turn provides the user with information to deal with those
migration issues

### Disadvantages: 
* migration from two not consecutive releases can be laborious
* user must be aware that he must (should) update  his software each time a new API is 
released.

