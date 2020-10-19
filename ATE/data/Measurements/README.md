# The Measurements library

The measurement library is a library that combines features of other existing
libraries when it comes to measurments.

  - error : When we 'get' a measurment from an instrument, the instrument
  knows his 'range' and thus can automatically caclulate the error on the measuremnt.
  this error should of course propagate when we make calculations.
  - unit : as good as all measurements have a unit, when we make calculations
  the unit should propagate too. (eg 5mA* 1000Ω = 5V)
  - multiplier: a measurement should automatically get a multiplier, so that we
  don't have '0.00005138 A' but '51.380 μA' ... a '3.3f' format would be nice.


The ideal case would be that if we do 'print(a)', python would produce
the for example : (__str__) "51.38 μA ± 10 ηA" note that the main value is
truncated on the error msd (any more after comma position are bullshit anyway)
