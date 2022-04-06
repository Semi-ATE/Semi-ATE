#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 15 17:00:03 2020

@author: nerohmot
"""

import math

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import uic

# https://www.youtube.com/watch?v=naHtXpCiPuM

class WaferMapEditor(QtWidgets.QDialog):
    
    def __init__(self, parent):
        self.parent = parent
        super().__init__(self.parent)
        uic.loadUi(__file__.replace('.py', '.ui'), self)

        self.get_data_from_parent()
        
        self.scene = QtWidgets.QGraphicsScene()
        self.graphicsView.setScene(self.scene)
        
        self.pen = QtGui.QPen(QtCore.Qt.green)
        # self.siliconBrush
        # self.inkBrush

        self.create_wafer_map()        
        
        self.OKButton.pressed.connect(self.OK_button_pressed)
        self.CancelButton.pressed.connect(self.Cancel_button_pressed)

    def create_wafer_map(self):
        for row in range(10):
            for column in range(10):
                r = QtCore.QRectF(QtCore.QPoint(row,column), QtCore.QSizeF(20,20))
                self.scene.addRect(r, self.pen)

    def get_data_from_parent(self):
        self.DieSizeX = int(self.parent.dieSizeX.text())
        self.DieSizeY = int(self.parent.dieSizeY.text())
        self.DieRefX = float(self.parent.dieRefX.text())
        self.DieRefY = float(self.parent.dieRefY.text())
        self.XOffset = int(self.parent.xOffset.text())
        self.YOffset = int(self.parent.yOffset.text())
        self.ScribeX = float(self.parent.scribeX.text())
        self.ScribeY = float(self.parent.scribeY.text())
        self.WaferDiameter = int(self.parent.waferDiameter.currentText()) * 1000  # in μm
        self.WaferRadius = self.WaferDiameter / 2  # in μm
        if self.parent.notchRadioButton.isChecked():
            self.flat = self.WaferDiameter / 2
        else:
            self.flat = float(self.parent.flat.text())

        self.XStep = self.DieSizeX + self.ScribeX
        self.YStep = self.DieSizeY + self.ScribeY

        self.PXDies = math.ceil((self.WaferRadius - (self.DieSizeX - self.DieRefX)) / self.XStep)
        self.NXDies = math.ceil((self.WaferRadius - self.DieRefX) / self.XStep)
        self.PYDies = math.ceil((self.WaferRadius - (self.DieSizeY - self.DieRefY)) / self.YStep)
        self.NYDies = math.ceil((self.WaferRadius - self.DieRefY) / self.YStep)

        self.XDies = self.PXDies + self.NXDies
        self.YDies = self.PYDies + self.NYDies
   
        print(f"X = {self.XDies} = {self.NXDies} + {self.PXDies}")
        print(f"Y = {self.YDies} = {self.NYDies} + {self.PXDies}")
    
    
    def set_data_to_parent(self):
        pass
    
    def OK_button_pressed(self):
        self.set_data_to_parent()
        self.accept()
        
    def Cancel_button_pressed(self):
        self.reject()
    
    