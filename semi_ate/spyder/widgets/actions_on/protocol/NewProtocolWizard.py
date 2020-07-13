# -*- coding: utf-8 -*-
"""
Created on Mon Nov 25 15:18:15 2019

@author: hoeren
"""
import os
import re

from ATE.org.actions import Create_new_maskset
from ATE.org.listings import list_masksets
from ATE.org.validation import is_valid_maskset_name
from PyQt5 import QtCore, QtGui, QtWidgets, uic


class NewProtocolWizard(QtWidgets.QDialog):

    def __init__(self, parent):
        super(NewProtocolWizard, self).__init__()

        my_ui = __file__.replace('.py', '.ui')
        if not os.path.exists(my_ui):
            raise Exception("can not find %s" % my_ui)
        uic.loadUi(my_ui, self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        self.parent = parent
        self.project_directory = os.path.join(self.parent.workspace_path, self.parent.active_project)
