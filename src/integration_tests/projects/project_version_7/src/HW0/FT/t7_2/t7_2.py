#!/usr/bin/env conda run -n ATE python
# -*- coding: utf-8 -*-
"""
By stefan (stefan@awinia.lan)
"""
if __name__ == '__main__':
    from t7_2_BC import t7_2_BC
else:
    from t7_2.t7_2_BC import t7_2_BC


class t7_2(t7_2_BC):

    '''
    for debug puposes, a logger is available to log infomration and porpagate them to the UI.
    logging can be used as described below:
    self.log_info(<message>)
    self.log_debug(<message>)
    self.log_warning(<message>)
    self.log_error(<message>)
    self.log_measure(<message>)

    <do_not_touch>
    


    Input Parameter | Shmoo |     Min | Default | Max    | Unit | fmt
    ----------------+-------+---------+---------+--------+------+----
    ip.Temperature  |  Yes  |     -40 |   25    | 170    | °C   | .0f
    ip.in_1         |  No   | -60.000 |  0.000  | 10.000 | A    | .3f

    Parameter         | MPR | LSL | (LTL) |  Nom  | (UTL)  | USL  | Unit | fmt
    ------------------+-----+-----+-------+-------+--------+------+------+----
    op.out_1          | Yes |  -∞ | 0.000 | 0.000 | 50.000 | +∞   | K    | .3f
    op.out_2          | No  |  -∞ | 0.000 | 0.000 | 1.000  | +∞   | A    | .3f
    </do_not_touch>

    '''

    def do(self):
        """Default implementation for test."""

        # sleep used only for test puposes (CI build), without provoking sleep the test-app's state change from ready to testing could not be detected 
        # must be removed when start implementing the test !!
        import time
        time.sleep(2)

        self.op.out_1.default()
        self.op.out_2.default()


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
        from ate_spyder.widgets.actions_on.tests.TestRunner import TestRunner
        testRunner = TestRunner(__file__, None)
        testRunner.show()
        sys.exit(app.exec_())