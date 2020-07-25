#!/usr/bin/env conda run -n ATE python
# -*- coding: utf-8 -*-
from ATE.spyder.widgets.abc import testABC
import .common

#
    mqtt = mqtt()
	K2000 = pm.hook.create_proxy("k2000", mqtt)

#

class fubar(testABC):
	'''
	Created on Tuesday, May 5 2020 @ 12:02:50 (Q2 20192)
	By @author: hoeren (hoeren@micronas.com)

	'''

	hardware = 'HW0'
	base = 'FT'
	Type = 'custom'

    input_parameters = {'T' : {'Min' : -40, 'Max' : 170, 'Default' : 25,  'Unit' : '°C'},
                        'i' : {'Min' : 0.1, 'Max' : 2.5, 'Default' : 1.0, 'Unit' : 'mA'}}

    output_parameters = {'parameter1_name' : {'LSL' : None, 'USL' : 5,    'Nom' : 2.5, 'Unit' : 'Ω'},
                         'parameter2_name' : {'LSL' : 0,    'USL' : None, 'Nom' : 2.5, 'Unit' : 'mV'},
                         'R_vdd_contact'   : {'LSL' : None, 'USL' : 5,    'Nom' : 2,   'Unit' : 'Ω'}}

	def do(ip, op):
		SCT.measure(ch5)
        K2000.measure()




    def do_TARGET(ip, op):
		SCT.measure(ch5)
        K2000.measure(5)



if __name__ == '__main__':
	import os
	tester = os.environ.get('TESTER')
	tester_mode = os.environ.get('TESTERMODE')
	if tester_mode == 'DIRECT':
		pass #TODO: implement
	else: # 'INTERACTIVE'
		from ATE.org import TestRunner
		testRunner = TestRunner(__file__)
