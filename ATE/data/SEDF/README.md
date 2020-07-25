# The SEDF (<ins>S</ins>tandard <ins>E</ins>prom <ins>D</ins>ata <ins>F</ins>ormat)  library

In the semiconductor test industry, virtually on every [PCB](https://en.wikipedia.org/wiki/Printed_circuit_board) one finds some kind of [EPROM](https://en.wikipedia.org/wiki/EPROM).

This is done for a varity of reasons like:
  - auto-detection of (PCB) board type
  - store/track calibration data
  - store/track maintenance data
  - ...

Now, Eprom's (regardless of the type) come with their own 'chalanges'
  - The used word-length (mostly 8 or 16 bit)
  - Eprom's have a limited number of times we can write to them reliably
  - Bit faiures might occure
  - We need to define addresses where we store what (😒 compatibility will be a nightmare)
  - The data to be storred need always to be packed/unpacked from/to the used type

Bref, if we don't have a library that abstracts these 'chalanges' we are forced to occupy ourselves with (verry error prune) bit-fucking.

`SEDF` defines records (inspired by STDF, hence the librarie's name choice) to store bits and pieces of information. The `SEDF` library enables us to interact with the EPROM without thinking about the details like word-size, hashes (to verify there are no bit-errors), 'addresses' (yes we don't need to pre-define them anymore so forward compatibility is now a fact), data-space, and so on.

It even has a special 'tally' record, for when you want to keep track of counts like the number of times a relay has switched without wearing out the LSB's in the Eeprom! 😍
