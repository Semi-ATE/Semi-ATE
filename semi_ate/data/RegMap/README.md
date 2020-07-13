# The RegMap library

## Preamble
When dealing with modern ASIC's we actually deal with SoC's ([System On a Chip](https://en.wikipedia.org/wiki/System_on_a_chip)). A SoC always has a so called register-map associated with it. Most of the interaction with the ASIC is thus done by reading/writing from/to these registers.

There is many attempts made to define a format for these register-maps.

We don't want to do another attempt (and probably fail somewhere), so we actually adopt the [IEEE1685](/docs/standards/IP-XACT (IEEE1685)/IP-XACT_v1.5.pdf) standard (aka: IP-XACT V1.5) or at least the register-map part innocent

The RegMap library let's us interact easily with the register map, but it contains also a GUI part (that can be run stand alone, or as part of ATE.org)

## Description
