#!/usr/bin/env conda run -n ATE python
# -*- coding: utf-8 -*-
"""
By abdou (abdou@awinia.lan)
"""
if __name__ == '__main__':
    from ad_BC import ad_BC
else:
    from ad.ad_BC import ad_BC


class ad(ad_BC):

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
    ip.Temperature  |  Yes  | -40 |   25    | 170 | °C | .0f

    Parameter         | LSL | (LTL) |  Nom  | (UTL) | USL  | Unit | fmt
    ------------------+-----+-------+-------+-------+------+------+----
    op.new_parameter1 |  -∞ |  (-∞) | 0.000 | (+∞)  | +∞   | ˽ | .3f
    </do_not_touch>

    '''

    def do(self):
        """Default implementation for the 'ad' test."""

        # sleep used only for test puposes (CI build), without provoking sleep the test-app's state change from ready to testing could not be detected 
        # must be removed when start implementing the test !!
        import time
        time.sleep(2)

        self.op.new_parameter1.default()


if __name__ == '__main__':
    import os
    tester = os.environ.get('TESTER')
    tester_mode = os.environ.get('TESTERMODE')
    if tester_mode == 'DIRECT':
        pass  # TODO: implement
    else:  # 'INTERACTIVE'
        from PyQt5 import QtWidgets
        import sys
        import qdarkstyle
        app = QtWidgets.QApplication(sys.argv)
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        from ATE.spyder.widgets.actions_on.tests.TestRunner import TestRunner
        testRunner = TestRunner(__file__, None)
        testRunner.show()
        sys.exit(app.exec_())