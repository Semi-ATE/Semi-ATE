#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 16 08:26:11 2020

@author: nerohmot
"""

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import uic

# https://www.youtube.com/watch?v=naHtXpCiPuM

class BondPadEditor(QtWidgets.QDialog):
    
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)
        uic.loadUi(__file__.replace('.py', '.ui'), self)

        self.get_data_from_parent()
        self.OKButton.pressed.connect(self.OK_button_pressed)
        self.CancelButton.pressed.connect(self.Cancel_button_pressed)

    def get_data_from_parent(self):
        pass
        
    def set_data_to_parent(self):
        pass
    
    def OK_button_pressed(self):
        self.set_data_to_parent()
        self.accept()
        
    def Cancel_button_pressed(self):
        self.reject()
