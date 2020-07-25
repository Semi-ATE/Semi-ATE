# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 14:00:55 2020

@author: hoeren

Measurements is a library that handels measurement type values.

It extends the base float type with :
    - +/- Inf and array as numpy does : https://numpy.org/
    - it adds error calculation to the measurement as the uncertainties package
      does : https://pypi.org/project/uncertainties/
    - it adds unit conversion to the measurement variable
      as does :
          Numericalunits :
              https://pypi.org/project/numericalunits/
              https://github.com/sbyrnes321/numericalunits
          Pint :
              https://pypi.org/project/Pint/
              https://github.com/hgrecco/pint
              https://pint.readthedocs.io/en/0.10.1/
          units : --> last rease Feb/2017
              https://pypi.org/project/units/
          si-units:
              https://github.com/unitsofmeasurement/si-units

    - it must be possible to 'cast' a measurement variable to an STDF:PTR or STDF:MPR record.
    - it must be possible to 'inject' a mesaurement variable to a metis object :-)
    - this library is PYTHON3 *ONLY*

The idea is that all measurements from the SCT tester, come ready with
the error on the measurement (real time calculated when the measurement is
done, as at that moment we know the value, ant the type, and we know the range
so why not trow away this valuable infrmation ?!?

Once we start calculating on the measurement variable the error and unit
follow the calculation so that at the end of the calculation we have not only
the calculated value, but the propagated error and the resulting unit too !!!

The idea is that this is invisible to the user (unless he wants to look at it)
but the results end up in the data loggings :-)
"""
#TODO: complete the list of 'similar' python libraries, go trugh them to see what is usefull and what is shit.
