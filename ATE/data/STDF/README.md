# The STDF (<ins>S</ins>tandard <ins>T</ins>est <ins>D</ins>ata <ins>F</ins>ormat)  library

### This library is NOT intended to be the <ins>fastes in the world</ins>! 

Often people are searching for 'the fastest' STDF parser. If this is what you are after, [keep on looking](https://en.wikipedia.org/wiki/Standard_Test_Data_Format) and by all means, hit the wall later on, and at that point you might consider to return! 🤣

Ok, a `fast` parser is first of all writen in probably [C](https://en.wikipedia.org/wiki/C_(programming_language))/[C++](https://en.wikipedia.org/wiki/C%2B%2B), and it has to dispence of a lot of the checking/correcting in order to become realy fast, and probably throwing away information not deemed interesting enough (and later turns out to be vital). However in real life STDF files are **far from perfect**, meaning that fast parsers will **FAIL** to do their intended job! You might tweak them for one or another ATE in your environment, but it will **not** be a can-do-everything parser!

In any case, when you start parsing STDF's **at the moment** you want to interact with the data, you are, as they say, *too little too late* ... you must still be living in the last century (not to say last millennium 🤪)

A `good` parser is written in a higher level language (like [Python](https://www.python.org/)) and it does an awefull lot of checking (and if needed correcting) and doesn't throw any information away, so as to return reliably with full, meaningfull and correct data! This of course makes it slower. One can optimize that a bit by using [Cython](https://cython.org/) or maybe [numba](http://numba.pydata.org/) but that is besides the point.

The point is that STDF data should be converted to a useable format like [pandas](https://pandas.pydata.org/) ([numpy](https://numpy.org/) alone will not do as plenty of data is not numerical) **WHILE** the data is being generated, <ins>preferrably not</ins> post-factum and <ins>definitely not</ins> pre-usage!

Think of it like this: STDF is a very good format from the point of view of the ATE, because if a test program is crashing, we lost virtually no data! Also, in STDF <ins>everything</ins> conserning an ATE <ins>has his defined place</ins>! (as opposed to [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) or similar ... naaah, you can not call it a 'format' can you?) Anyway, STDF is an un-usable format from the point of view of data analysis! Therefore we need to convert the data to a format that **is** usable. (and if now you are thinking '[SQL](https://en.wikipedia.org/wiki/SQL)', then I can confirm that you are a die-hard masochist that still lives in the last millennium because you are clearly not up to speed when it comes to [data science](https://en.wikipedia.org/wiki/Data_science)! 🧐)   

Anyway, I did put `pandas` forward, because the rest of `ATE.org` is Python (>=3.6) based, but to be fair one could [also go the SAS- or the R way](https://www.analyticsvidhya.com/blog/2017/09/sas-vs-vs-python-tool-learn/) but those make less sense in the `ATE.org` concept.

In any case, `ATE.org` is **ONLY** outputting STDF data, so whatever (legacy) system(s) you have, `ATE.org` will play along nicely!

The `ATE.org` [Metis](/src/ATE/data/Metis/README.md) library builds on **STDF**/[numpy](https://numpy.org/)/[scipy](https://www.scipy.org/)/[pandas](https://pandas.pydata.org/)/[HDF5](https://www.hdfgroup.org/solutions/hdf5/)/[matplotlib](https://matplotlib.org/) to deliver data analysis tailored to the semiconductor test industry ... in open source!

Eat that Mentor! For years you took [money-for-nothing](https://www.youtube.com/watch?v=wTP2RUD_cL0), and in the end you still screwed your customers (cfr. `PAT`). [My-silver-lining](https://www.youtube.com/watch?v=DKL4X0PZz7M): now we will do some screwing! See how that feels! 😋 

### It is also <ins>NOT just a parser</ins>!

In `ATE.org` we also need to **<ins>write</ins>** STDF files!

Infact here are the specifications of the `ATE.org` **STDF** library:

 - [<ins>Endianness</ins>](https://en.wikipedia.org/wiki/Endianness): Little & Big
 - <ins>Versions & Extensions</ins>:
   - ~~V3~~: support depricated
   - V4:
     - [standard](/docs/standards/STDF/STDF-V4-spec.pdf)
     - [V4-2007](/docs/standards/STDF/STDF-V4-2007-spec.pdf)
     - Memory:2010.1
 - <ins>Modes</ins>: read & write
 - <ins>compressions</ins>: (in **all** modes!)
   - [gzip](https://www.gnu.org/software/gzip/)
   - [lzma](https://en.wikipedia.org/wiki/Lempel%E2%80%93Ziv%E2%80%93Markov_chain_algorithm) → turns out to be the best compressor for STDF files. 🤫
   - [bz2](https://www.sourceware.org/bzip2/)
 - <ins>encodings</ins>:
   - [ASCII](https://en.wikipedia.org/wiki/ASCII)
   - [UTF-8](https://en.wikipedia.org/wiki/UTF-8) (added to support things like 'ηA', 'μV', '°C', '-∞', ... but also to make STDF compatible with python itself 😎)
 - <ins>floating point extensions</ins>:
   - [Not A Number](https://en.wikipedia.org/wiki/NaN) (aka: NaN, nan)
   - [IEEE 754-1985](https://en.wikipedia.org/wiki/IEEE_754-1985) (aka: Infinity, Inf, inf)
