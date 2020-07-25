#!/usr/bin/env python
#from ATE.spyder.widgets.Testing import testABC
from ATE.spyder.widgets.actions.new.program.test.testABC import testABC


class test2(testABC):
    '''
    Description:
        This test ...
    '''
    run_time = 13.56327 #ms (automatically set)

    start_state = 'UNDETERMINED'
    end_state = 'CONTACT_TEST'

    input_parameters = {'T' : {'Min' : -40, 'Max' : 170, 'Default' : 25,  'Unit' : '°C'}, # Obligatory !
                        'i' : {'Min' : 0.1, 'Max' : 2.5, 'Default' : 1.0, 'Unit' : 'mA'}}

    output_parameters = {'parameter1_name' : {'LSL' : None, 'USL' : 5,    'Nom' : 2.5, 'Unit' : 'Ω'}, # maybe add SBIN group ? - NO, auto assign testnumbers
                         'parameter2_name' : {'LSL' : 0,    'USL' : None, 'Nom' : 2.5, 'Unit' : 'mV'},
                         'R_vdd_contact'   : {'LSL' : None, 'USL' : 5,    'Nom' : 2,   'Unit' : 'Ω'}}

    def do(self, ip, op, gp, dm):
        print("Doing %s test ..." % self.__class__.__name__.split("_")[0])

    def target(self, ip, op, gp, dm):
        return self.do(ip, op, gp, dm)

    def flow(self, ip, op, gp, dm):
        return self.target(ip, op, gp, dm)
