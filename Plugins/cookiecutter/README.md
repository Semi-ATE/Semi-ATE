# ATE.org plugin cookiecutter

- The '[interface](https://github.com/ate-org/ATE.org/tree/master/src/Plugins/cookiecutter/interface)' directory holds the code + the ui
- The '[template](https://github.com/ate-org/ATE.org/tree/master/src/Plugins/cookiecutter/template)' directory holds the (jinja2) structure of the resulting project.

# Background

A plugin for ATE.org can hold a varity of things:

- **importers** (zero or more, dependent on ATE.org)
  - Maskset (implemented inside or outside of this package)
  - Package (implemented inside or outside of this package)
- **exporters** (zero or more, dependent on ATE.org)
  - ERP (implemented inside or outside of this package)
- **tools** (zero or more, independant of ATE.org)
  ➜ implements (auditing and other tools on the project)
- **instruments** (zero or more)
  ➜ implements measurement equipment (but **not** a tester), categorized in manufacturer/instrument/implementer, so that the same instrument can have multiple implementations living next to eachother.
- **tester** (zero or one)
  ➜ implements a tester categorized in manufacturer/platform/implementer, so that again multiple tester implementations could live next to eachother.
- **equipment** (zero or more)
  ➜ implements equipment(s). An Equipment is:
  - a `prober` (with zero or more acctuators directly attached to it)
  - an `in-line handler` (with zero or more actuators directly attached to it)
  - a `batch handler` (with zero or more actuators directly attached to it)
  - an `actuator` (with exactly **one** actuator attached to it)

# toolchain

We will **NOT** go over PyPi !

The repo will be github (but can also be a github enterprise).
The repo can (but doesn't have to have) an github organization.
The repo will build for a conda-package and insert to an (anaconda) channel.

# use in the test program (automatically configured by the wizards)

pm = pluginmanager()

K2000 = pm.hooks.get_instrument("TDKMicronas.Tektronix.Keithley_2000.Jonathan_Branford")

➔ TDKMicronas : the name of plugin module
➔ Tektronix.Keithley_2000.Jonathan_Branford : 'Jonathan Bardford's implementation of the 'Keithley 2000' instrument from 'Tektronix'

note : spaces are replaced by underscores.


# jinja2 entries used:
-