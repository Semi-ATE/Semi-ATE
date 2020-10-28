# how to do the link ?!?

standard_test_names = ['', # first item must be an empty string
                       'Contact', # aka Open/Short Test

                       'IDD',  # IDD is the measure of total current that flow`s into the power supply pin (device in idle mode - for example after POR) (page 88)
                       # maybe IDDs & IDDd ?!?!
                       'IDDq', #

                       'VOH',  # The worst case (min) voltage at the output that drives a logical 1 (page 81)
                       'VOL',  # The worst case (max) voltage at the output that drives a logical 0 (page 81)
                       'IOH',  # The maximum current the output can source when driving a logical 1 (page 81)
                       'IOL',  # The maximum current the output can sink when driving a logical 0 (page 81)
                       'VIH',  # The worst case (min) voltage at the input that is recognized as logical 1 (page 82)
                       'VIL',  # The worst case (max) voltage at the input that is recognized as logical 0 (page 82)
                       'IIH',  # The worst case (max) current the input pin can sink to maintain logic 1 voltage at output of the device it is connected to (page 82)
                       'IIL',  # The worst case (max) current the input pin can source to maintain logic 0 voltage at output of the device it is connected to (page 82)
                       'IOZ',  # output high impedance leakage current (page 89)
                       'IOZL', # the measure of output impedance leakage current from the output pin to VDD when the output pin is in tri state(high impedance state) (page 89)
                       'IOZH', # the measure of output impedance leakage current from the output pin to GND when the output pin is in tri state (page 89)
                       'IOS',  # Output Short Circuit Current
                       'IOLMAX',
                       'IOHMAX',

                       'TDR', # Time Domain Reflectometry ?!?

                       'Tr',  # RiseTime
                       'Tf',  # Fall Time
                       # maybe replace by Srr & Srf (slew rate rise & slew rate fall) ???

                       ]
