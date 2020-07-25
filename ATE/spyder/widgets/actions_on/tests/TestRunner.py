# -*- coding: utf-8 -*-
"""
Created on Mon May  4 18:13:59 2020

@author: hoeren
"""
import qdarkstyle
import qtawesome as qta
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import uic

class TestRunner(QtWidgets.QDialog):

    def __init__(self, test):
        super().__init__()

        my_ui = __file__.replace('.py', '.ui')
        if not os.path.exists(my_ui):
            raise Exception(f"can not find {my_ui}")
        uic.loadUi(my_ui, self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        print(test)
        self.testPath, self.testFile = os.path.split(test)
        self.TestName.setText('.'.join(self.testFile.split('.')[:-1]))
