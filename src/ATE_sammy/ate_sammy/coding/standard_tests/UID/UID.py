# -*- coding: utf-8 -*-
"""
Created on Mon Apr  6 16:44:18 2020

@author: hoeren
"""
import os

from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import uic

from ate_spyder.widgets.coding.test_generator import tdpprint
from ate_spyder.widgets.coding.test_generator import tippprint
from ate_spyder.widgets.coding.test_generator import toppprint

def generator(parent, definition):
    if definition != {}:
        from ate_spyder.widgets.coding import test_generator

        project_path = parent.active_project_path
        hardware = parent.active_hardware
        base = parent.active_base

        my_name = '.'.join(os.path.basename(__file__).split('.')[:-1])

        return test_generator(project_path, my_name, hardware, base, definition, Type='standard')

class Wizard(QtWidgets.QDialog):

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        my_ui = __file__.replace('.py', '.ui')
        if not os.path.exists(my_ui):
            raise Exception("can not find %s" % my_ui)
        uic.loadUi(my_ui, self)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self._setupUI()


    def _setupUI(self):
        self.setWindowTitle('UID')
        self.base = self.parent.active_base
        self.hardware = self.parent.active_hardware

        if self.base == 'FT':
            my_target = 'device'
        else:
            my_target = 'die'

        self.definition = {
            'doc_string' : [
                f'The UID (Unique IDentification) test will read out the UID from the {my_target}',
                f'using {self.hardware} and add it to the STDF in the right place.'
                'Note: this is *NOT* a standard logging as in STDF there is a special',
                '      field foreseen for this! (PRR:PART_ID)'
                '      file://~/doc/standards/STDF-V4-spec.pdf#40' ],
            'input_parameters' : {},
            'output_parameters' : {},
            'data' : {}
        }

        self.OKButton.clicked.connect(self.OKButtonPressed)



        self.show()

    def verify(self):
        self.feedback.setText("")

    def OKButtonPressed(self):
        print(f"hardware = '{self.hardware}', base='{self.base}'")


        self.accept()
        return self.definition

    def CancelButtonPressed(self):
        self.accept()
        return {}


def dialog(parent):
    wizard = Wizard(parent)
    definition = wizard.exec_()
    del(wizard)
    generator(parent, definition)
