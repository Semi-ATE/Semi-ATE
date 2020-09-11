# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 17:43:07 2020

@author: hoeren
"""

import importlib
import os
import platform
import re
import sys

from PyQt5 import QtCore, QtWidgets, uic, QtGui

import qdarkstyle
import qtawesome as qta


class Dialog(QtWidgets.QMainWindow):

    def __init__(self, app=None):

        # get the appropriate .ui file and load it.
        my_ui = __file__.replace('.py', '.ui')
        print(my_ui)
        if not os.path.exists(my_ui):
            raise Exception("'%s' doesn't exist" % my_ui)
        uic.loadUi(my_ui, self)

        # Initialize the main window
        title = ' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', '')))
        print(title)
        self.setWindowTitle(title)

        # go
        self.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    dialog = Dialog(app)
    res = app.exec_()
    sys.exit(res)
