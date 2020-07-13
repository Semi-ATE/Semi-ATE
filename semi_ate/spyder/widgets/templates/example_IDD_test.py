#!/usr/bin/env conda run -n ATE python
# -*- coding: utf-8 -*-

'''
Created on Friday, May 8 2020 @ 17:36:14 (Q2 20195)
By @author: hoeren (hoeren@micronas.com)
'''

import .common


class IDD(testABC):
    """one liner."""

    hardware = 'HW0'
    base = 'FT'
    Type = 'custom'

    input_parameters = {
        Temperature: {'Shmoo':  True, 'Min':   -40, 'Default':    25, 'Max':    170, '10ᵡ': '', 'Unit': '°C', 'fmt': '.0f'},
        VDD:         {'Shmoo':  True, 'Min': 1.800, 'Default': 5.000, 'Max': 16.000, '10ᵡ': '', 'Unit':  'V', 'fmt': '.3f'}}

    output_parameters = {
        current:    {'LSL': -inf, 'LTL': nan, 'Nom': 1.200, 'UTL': nan, 'USL':  inf, '10ᵡ': 'm', 'Unit': 'A', 'fmt': '.3f'},
        resistance: {'LSL': -inf, 'LTL': nan, 'Nom': 4.166, 'UTL': nan, 'USL':  inf, '10ᵡ': 'k', 'Unit': 'Ω', 'fmt': '.3f'}}

    def do(ip, op):
        """Default test procedure."""
        op.current = op.current.randomNormalWithFailrate(0.001)
        op.resistance = ip.VDD / op.current


if __name__ == '__main__':
    import os
    tester = os.environ.get('TESTER')
    tester_mode = os.environ.get('TESTERMODE')
    if tester_mode == 'DIRECT':
        pass  # TODO: implement
    else:  # 'INTERACTIVE'
        from ATE.org import TestRunner
        testRunner = TestRunner(__file__)
