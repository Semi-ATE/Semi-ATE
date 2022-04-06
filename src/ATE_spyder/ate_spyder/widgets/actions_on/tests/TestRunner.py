# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from PyQt5 import uic
import re, os

from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog

class TestRunner(BaseDialog):
    def __init__(self, test, parent):
        super().__init__(__file__, parent)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        self.testPath, self.testFile = os.path.split(test)
        self.TestName.setText('.'.join(self.testFile.split('.')[:-1]))
