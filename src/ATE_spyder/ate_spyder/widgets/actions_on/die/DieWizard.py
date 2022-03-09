# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 14:32:40 2019

@author: hoeren
"""
import os
import re

from PyQt5 import QtCore
from PyQt5 import QtGui

from ate_spyder.widgets.actions_on.utils.BaseDialog import BaseDialog
from ate_spyder.widgets.navigation import ProjectNavigation
from ate_spyder.widgets.validation import valid_die_name_regex


class DieWizard(BaseDialog):
    def __init__(self, project_info: ProjectNavigation, read_only: bool = False):
        super().__init__(__file__, project_info.parent)
        self.project_info = project_info
        self.read_only = read_only
        self._setup_ui()
        self._connect_event_handler()

    def _setup_ui(self):
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        self.existing_hardwares = self.project_info.get_active_hardware_names()
        self.withHardware.clear()
        self.withHardware.addItems(self.existing_hardwares)
        current_hardware = '' if len(self.existing_hardwares) == 0 else self.existing_hardwares[0]
        self.withHardware.setCurrentText(current_hardware)

        rxDieName = QtCore.QRegExp(valid_die_name_regex)
        DieName_validator = QtGui.QRegExpValidator(rxDieName, self)
        self.dieName.setText("")
        self.dieName.setValidator(DieName_validator)
        self.dieName.textChanged.connect(self._verify)

        self.existing_dies = self.project_info.get_active_die_names()

        self.existing_masksets = self.project_info.get_available_maskset_names()
        self.fromMaskset.addItems(self.existing_masksets)
        current_maskset = '' if len(self.existing_masksets) == 0 else self.existing_masksets[0]
        self.fromMaskset.setCurrentText(current_maskset)

        quality_grade = self.project_info.get_default_quality_grade()
        self.qualityGrade.setCurrentText(quality_grade)

        self.Type.setCurrentText('ASSP')
        self.isAGrade.setChecked(True)
        self.isAGrade.setEnabled(False)
        self.referenceGradeLabel.setHidden(True)
        self.referenceGrade.setHidden(True)
        self.gradeLabel.setHidden(True)
        self.grade.setHidden(True)
        self.customerLabel.setHidden(True)
        self.customer.setHidden(True)

        self.feedback.setStyleSheet('color: orange')

        self._verify()

    def _connect_event_handler(self):
        self.fromMaskset.currentTextChanged.connect(self.maskset_changed)
        self.withHardware.currentTextChanged.connect(self.hardware_changed)
        self.isAGrade.toggled.connect(self.a_grade_changed)
        self.referenceGrade.currentTextChanged.connect(self.reference_grade_changed)
        self.Type.currentTextChanged.connect(self.type_changed)
        self.grade.currentTextChanged.connect(self.grade_changed)
        self.customer.textChanged.connect(self.customer_changed)
        self.CancelButton.clicked.connect(self.cancel_button_pressed)
        self.OKButton.clicked.connect(self.ok_button_pressed)

    @QtCore.pyqtSlot(str)
    def hardware_changed(self, hardware):
        self.project_info.parent.hardware_activated.emit(hardware)

    @QtCore.pyqtSlot(str)
    def nameChanged(self, _):
        self._verify()

    @QtCore.pyqtSlot(str)
    def maskset_changed(self, selected_maskset):
        ASIC_masksets = self.project_info.get_ASIC_masksets()
        if selected_maskset in [maskset.name for maskset in ASIC_masksets]:
            customer = self.project_info.get_maskset_customer(selected_maskset)
            self._update_maskset_dependant_components(False, 'ASIC', customer)
        else:
            self._update_maskset_dependant_components(True, 'ASSP')

        self.a_grade_changed(self.isAGrade.isChecked())

    def _update_maskset_dependant_components(self, is_hidden, type, customer=''):
        self.grade.setCurrentText('A')
        self.Type.setCurrentText(type)
        self.customerLabel.setHidden(is_hidden)
        self.customer.setText(customer)
        self.customer.setHidden(is_hidden)

    @QtCore.pyqtSlot(bool)
    def a_grade_changed(self, isAGrade):
        if isAGrade:
            self.referenceGradeLabel.setHidden(True)
            self.referenceGrade.setHidden(True)
            self.gradeLabel.setHidden(True)
            self.grade.setHidden(True)
        else:
            self.referenceGradeLabel.setHidden(False)

            reference_dies, referenced_dies, first_free_grade = self._get_reference_dies()
            self._update_grade_section(reference_dies, referenced_dies, first_free_grade)

        self._verify()

    def _update_grade_section(self, reference_dies, referenced_dies, first_free_grade):
        self.referenceGrade.clear()
        self.referenceGrade.addItems(reference_dies)
        self.referenceGrade.setCurrentText('')
        self.referenceGrade.setHidden(False)
        self.gradeLabel.setHidden(False)

        self.grade.clear()
        self.grade.addItems(sorted(list(referenced_dies)))
        for index in range(self.grade.count()):
            item_text = self.grade.itemText(index)
            if referenced_dies[item_text] != '':
                self.grade.model().item(index).setEnabled(False)
                self.grade.model().item(index).setToolTip(referenced_dies[item_text])

        self.grade.setCurrentText(first_free_grade)
        self.grade.setHidden(False)

    def _get_reference_dies(self):
        all_dies = self.project_info.get_dies()
        reference_dies = []
        referenced_dies = {i: '' for i in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']}
        free_grades = []

        for die in all_dies:
            if die.hardware == self.withHardware.currentText() and die.maskset == self.fromMaskset.currentText():
                if die.name == self.dieName.text():
                    continue

                if die.grade == 'A':
                    reference_dies.append(die.name)
                else:
                    referenced_dies[die.grade] = die.grade_reference

        for die in referenced_dies:
            if referenced_dies[die] == '':
                free_grades.append(die)

        if len(free_grades) == 0:
            raise Exception("no secondary grades available !!!")
        else:
            first_free_grade = sorted(free_grades)[0]

        return reference_dies, referenced_dies, first_free_grade

    @QtCore.pyqtSlot(str)
    def reference_grade_changed(self, _):
        self._verify()

    def grade_changed(self, SelectedGrade):
        if SelectedGrade == 'A':
            self.referenceGradeLabel.setHidden(True)
            self.referenceGrade.setHidden(True)
        else:
            self.referenceGradeLabel.setHidden(False)
            self.referenceGrade.setHidden(False)

    @QtCore.pyqtSlot(str)
    def type_changed(self, SelectedType):
        '''
        if the Type is 'ASIC' enable CustomerLabel and Customer
        '''
        if SelectedType == 'ASIC':
            self.customerLabel.setHidden(False)
            self.customer.setVisible(True)
        else:
            self.customerLabel.setHidden(True)
            self.customer.setVisible(False)

        self._verify()

    @QtCore.pyqtSlot(str)
    def customer_changed(self, _):
        self._verify()

    def _verify(self):
        if len(self.existing_hardwares) == 0:
            self.feedback.setText("No hardware is available")
            return

        if len(self.existing_masksets) == 0:
            self.feedback.setText("No maskset is available")
            return

        self.feedback.setText("")

        if self.dieName.text() == '':
            self.feedback.setText("Supply a Die Name")
        elif not self.read_only and self.dieName.text() in self.existing_dies:
            self.feedback.setText("Die name already exists !")

        if self.feedback.text() == '':
            if self.fromMaskset.currentText() == "":
                self.feedback.setText("No maskset selected")

        if self.feedback.text() == '':
            if not self.isAGrade.isChecked():
                if self.referenceGrade.currentText() == '':
                    self.feedback.setText("A non-A-Grade product needs a reference grade, select one.")

        if self.feedback.text() == '':
            if self.Type.currentText() == "ASIC" and not self.customer.text():
                self.feedback.setText("need a customer name for the ASIC")

        if self.fromMaskset.currentText():
            self.isAGrade.setEnabled(True)

        if self.feedback.text() == '':
            self.OKButton.setEnabled(True)
        else:
            self.OKButton.setEnabled(False)

    def _get_current_configuration(self):
        if self.isAGrade.isChecked():
            grade = 'A'
            grade_reference = ''
        else:
            grade = self.grade.currentText()
            grade_reference = self.referenceGrade.currentText()
        if self.Type.currentText() == 'ASIC':
            customer = self.customer.text()
        else:
            customer = ''

        return {'name': self.dieName.text(),
                'hardware': self.withHardware.currentText(),
                'maskset': self.fromMaskset.currentText(),
                'quality': self.qualityGrade.currentText(),
                'grade': grade,
                'grade_reference': grade_reference,
                'type': self.Type.currentText(),
                'customer': customer}

    @QtCore.pyqtSlot()
    def ok_button_pressed(self):
        configuration = self._get_current_configuration()
        self.project_info.add_die(configuration['name'], configuration['hardware'], configuration['maskset'],
                                  configuration['quality'], configuration['grade'], configuration['grade_reference'],
                                  configuration['type'], configuration['customer'])
        self.accept()

    @QtCore.pyqtSlot()
    def cancel_button_pressed(self):
        self.reject()


def new_die_dialog(project_info):
    newDieWizard = DieWizard(project_info)
    newDieWizard.exec_()
    del(newDieWizard)
