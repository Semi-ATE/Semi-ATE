#!/usr/bin/env conda run -n ATE python
# -*- coding: utf-8 -*-
"""
By abdou (abdou@awinia.lan)
"""

import os, sys
from pathlib import Path
test_path = os.path.abspath(Path(__file__).joinpath('..'))
sys.path.append(test_path)

from fae_BC import fae_BC


class fae(fae_BC):

    '''
    for debug puposes, a logger is available to log infomration and porpagate them to the UI.
    logging can be used as described below:
    self.log_info(<message>)
    self.log_debug(<message>)
    self.log_warning(<message>)
    self.log_error(<message>)
    self.log_measure(<message>)

    <do_not_touch>
    
    Input Parameter | Shmoo | Min | Default | Max | Unit | fmt
    ----------------+-------+-----+---------+-----+------+----
    ip.Temperature  |  Yes  | -40 |   25    | 170 | °C   | .0f

    Parameter         | MPR | LSL | (LTL) |  Nom  | (UTL) | USL  | Unit | fmt
    ------------------+-----+-----+-------+-------+-------+------+------+----
    op.new_parameter1 | No  |  -∞ |  (-∞) | 0.000 | (+∞)  | +∞   | ˽    | .3f
    </do_not_touch>

    '''
    def do(self):
        """Default implementation for test."""

        # sleep used only for test puposes (CI build), without provoking sleep the test-app's state change from ready to testing could not be detected 
        # must be removed when start implementing the test !!
        import time
        time.sleep(2)

        self.op.new_parameter1.default()
