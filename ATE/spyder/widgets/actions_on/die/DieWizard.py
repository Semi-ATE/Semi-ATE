# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 14:32:40 2019

@author: hoeren
"""
import os
import re

from PyQt5 import QtCore
from PyQt5 import QtGui

from ATE.spyder.widgets.actions_on.utils.BaseDialog import BaseDialog
from ATE.spyder.widgets.validation import valid_die_name_regex


class DieWizard(BaseDialog):
    def __init__(self, project_info, read_only=False):
        super().__init__(__file__)
        self.project_info = project_info
        self.read_only = read_only
        self._setup_ui()
        self._connect_event_handler()

    def _setup_ui(self):
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        # hardware
        self.existing_hardwares = self.project_info.get_active_hardware_names()
        self.withHardware.clear()
        self.withHardware.addItems(self.existing_hardwares)
        current_hardware = '' if len(self.existing_hardwares) == 0 else self.existing_hardwares[0]
        self.withHardware.setCurrentText(current_hardware)
        self.withHardware.setEnabled(True)

        # name
        rxDieName = QtCore.QRegExp(valid_die_name_regex)
        DieName_validator = QtGui.QRegExpValidator(rxDieName, self)
        self.dieName.setText("")
        self.dieName.setValidator(DieName_validator)
        self.dieName.textChanged.connect(self._verify)
        self.existing_dies = self.project_info.get_active_die_names()

        # maskset
        self.existing_masksets = self.project_info.get_available_maskset_names()
        self.fromMaskset.clear()
        #self.fromMaskset.addItems(sorted([''] + self.existing_masksets))
        # ToDo: Sort !
        for maskset in self.existing_masksets:
            self.fromMaskset.addItem(maskset.name)
        current_maskset = '' if len(self.existing_masksets) == 0 else self.existing_masksets[0].name
        self.fromMaskset.setCurrentText(current_maskset)

        # quality
        self.quality.setCurrentText('')

        # product quality
        self.quality.setCurrentText('')

        # grade
        self.isAGrade.setChecked(True)
        self.isAGrade.setEnabled(False)

        self.referenceGradeLabel.setDisabled(True)
        self.referenceGradeLabel.setHidden(True)
        self.referenceGradeLabel.setVisible(False)

        all_dies = self.project_info.get_dies()
        reference_dies = []
        referenced_dies = {i: '' for i in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']}
        free_grades = []

        for die in all_dies:
            if die.hardware == self.withHardware.currentText() and die.maskset == self.fromMaskset.currentText():
                if die.grade == 'A':
                    reference_dies.append(die.name)
                else:
                    referenced_dies[die.grade] = die.grade_reference

        for die in referenced_dies:
            if referenced_dies[die] == '':
                free_grades.append(die)

        if len(free_grades) == 0:  # nothing free anymore
            first_free_grade = ''
        else:
            first_free_grade = sorted(free_grades)[0]

        self.referenceGrade.addItems(reference_dies)
        self.referenceGrade.setCurrentText('')
        self.referenceGrade.setDisabled(True)
        self.referenceGrade.setHidden(True)
        self.referenceGrade.setVisible(False)

        self.gradeLabel.setDisabled(True)
        self.gradeLabel.setHidden(True)
        self.gradeLabel.setVisible(False)

        self.grade.clear()
        self.grade.addItems(sorted(list(referenced_dies)))
        for index in range(self.grade.count()):
            item_text = self.grade.itemText(index)
            if referenced_dies[item_text] != '':
                self.grade.model().item(index).setEnabled(False)
                self.grade.model().item(index).setToolTip(referenced_dies[item_text])
        self.grade.setCurrentText(first_free_grade)
        self.grade.setDisabled(True)
        self.grade.setHidden(True)
        self.grade.setVisible(False)

    # Type & customer
        self.Type.setCurrentText('ASSP')

        self.customerLabel.setDisabled(True)
        self.customerLabel.setHidden(True)
        self.customerLabel.setVisible(False)

        self.customer.setText('')
        self.customer.setDisabled(True)
        self.customer.setHidden(True)
        self.customer.setVisible(False)

    # feedback
        self.feedback.setStyleSheet('color: orange')

    # buttons
        self.OKButton.setEnabled(False)

        self._verify()

    def _connect_event_handler(self):
        self.fromMaskset.currentTextChanged.connect(self.masksetChanged)
        self.withHardware.currentTextChanged.connect(self.hardwareChanged)
        self.isAGrade.toggled.connect(self.isAGradeChanged)
        self.referenceGrade.currentTextChanged.connect(self.referenceGradeChanged)
        self.Type.currentTextChanged.connect(self.typeChanged)
        self.grade.currentTextChanged.connect(self.gradeChanged)

        self.customer.textChanged.connect(self.customerChanged)
        self.CancelButton.clicked.connect(self.CancelButtonPressed)
        self.OKButton.clicked.connect(self.OKButtonPressed)

    def hardwareChanged(self, hardware):
        self.dieName.blockSignals(True)
        self.dieName.setText("")
        self.dieName.blockSignals(False)

    def nameChanged(self, name):
        self._verify()

    def masksetChanged(self, SelectedMaskset):
        ASIC_masksets = self.project_info.get_ASIC_masksets()
        if SelectedMaskset in ASIC_masksets:
            self.gradeLabel.setDisabled(False)
            self.grade.blockSignals(True)
            self.grade.setCurrentText('A')
            self.grade.setDisabled(False)
            self.grade.blockSignals(False)
            self.typeLabel.setDisabled(True)
            self.Type.blockSignals(True)
            self.Type.setCurrentText('ASIC')
            self.Type.setDisabled(True)
            self.Type.blockSignals(False)
            self.customerLabel.setHidden(False)
            self.customerLabel.setDisabled(True)
            Customer = self.project_info.get_maskset_customer(SelectedMaskset)
            self.customer.blockSignals(True)
            self.customer.setText(Customer)
            self.customer.setHidden(False)
            self.customer.setDisabled(True)
            self.customer.blockSignals(True)
            self.isAGrade.setEnabled(True)
        else:
            self.gradeLabel.setDisabled(False)
            self.grade.blockSignals(True)
            self.grade.setCurrentText('A')
            self.grade.setDisabled(False)
            self.grade.blockSignals(False)
            self.typeLabel.setDisabled(False)
            self.Type.blockSignals(True)
            self.Type.setCurrentText('ASSP')
            self.Type.setDisabled(False)
            self.Type.blockSignals(False)
            self.customerLabel.setHidden(True)
            self.customer.blockSignals(True)
            self.customer.setText('')
            self.customer.setHidden(True)
            self.customer.blockSignals(True)
            self.isAGrade.setEnabled(True)
        self._verify()

    def isAGradeChanged(self, isAGrade):
        if isAGrade:
            self.referenceGradeLabel.setDisabled(True)
            self.referenceGradeLabel.setHidden(True)
            self.referenceGradeLabel.setVisible(False)

            self.referenceGrade.setDisabled(True)
            self.referenceGrade.setHidden(True)
            self.referenceGrade.setVisible(False)

            self.gradeLabel.setDisabled(True)
            self.gradeLabel.setHidden(True)
            self.gradeLabel.setVisible(False)

            self.grade.setDisabled(True)
            self.grade.setHidden(True)
            self.grade.setVisible(False)
        else:
            self.referenceGradeLabel.setDisabled(False)
            self.referenceGradeLabel.setHidden(False)
            self.referenceGradeLabel.setVisible(True)

            all_dies = self.project_info.get_dies()
            reference_dies = []
            referenced_dies = {i: '' for i in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']}
            free_grades = []

            for die in all_dies:
                if die.hardware == self.withHardware.currentText() and die.maskset == self.fromMaskset.currentText():
                    if die.grade == 'A':
                        reference_dies.append(die.name)
                    else:
                        referenced_dies[die.grade] = die.grade_reference

            for die in referenced_dies:
                if referenced_dies[die] == '':
                    free_grades.append(die)

            if len(free_grades) == 0:  # nothing free anymore
                raise Exception("no secondary grades available !!!")
                first_free_grade = ''
            else:
                first_free_grade = sorted(free_grades)[0]

            self.referenceGrade.blockSignals(True)
            self.referenceGrade.clear()
            self.referenceGrade.addItems(reference_dies)
            self.referenceGrade.setCurrentText('')
            self.referenceGrade.setDisabled(False)
            self.referenceGrade.setHidden(False)
            self.referenceGrade.setVisible(True)
            self.referenceGrade.blockSignals(False)

            self.gradeLabel.setDisabled(False)
            self.gradeLabel.setHidden(False)
            self.gradeLabel.setVisible(True)

            self.grade.blockSignals(True)
            self.grade.clear()
            self.grade.addItems(sorted(list(referenced_dies)))
            for index in range(self.grade.count()):
                item_text = self.grade.itemText(index)
                if referenced_dies[item_text] != '':
                    self.grade.model().item(index).setEnabled(False)
                    self.grade.model().item(index).setToolTip(referenced_dies[item_text])

            self.grade.setCurrentText(first_free_grade)
            self.grade.setDisabled(False)
            self.grade.setHidden(False)
            self.grade.setVisible(True)
            self.grade.blockSignals(False)

        self._verify()

    def referenceGradeChanged(self, SelectedReferenceGrade):
        self._verify()

    def gradeChanged(self, SelectedGrade):
        if SelectedGrade == 'A':
            self.referenceGradeLabel.setHidden(True)
            self.referenceGrade.setHidden(True)
        else:
            self.referenceGradeLabel.setHidden(False)
            self.referenceGrade.setHidden(False)

    def typeChanged(self, SelectedType):
        '''
        if the Type is 'ASIC' enable CustomerLabel and Customer
        '''
        if SelectedType == 'ASIC':
            self.customerLabel.setDisabled(False)
            self.customerLabel.setHidden(False)
            self.customerLabel.setVisible(True)

            self.customer.blockSignals(True)
            self.customer.setText("")
            self.customer.setDisabled(False)
            self.customer.setHidden(False)
            self.customer.setVisible(True)
            self.customer.blockSignals(False)
        else:
            self.customerLabel.setDisabled(True)
            self.customerLabel.setHidden(True)
            self.customerLabel.setVisible(False)

            self.customer.blockSignals(True)
            self.customer.setText("")
            self.customer.setDisabled(True)
            self.customer.setHidden(True)
            self.customer.setVisible(False)
            self.customer.blockSignals(False)

    def customerChanged(self, Customer):
        pass

    def _verify(self):
        if len(self.existing_hardwares) == 0:
            self.feedback.setText("No hardware is available")
            return

        if len(self.existing_masksets) == 0:
            self.feedback.setText("No maskset is available")
            return

        self.feedback.setText("")

    # Die Name
        if self.dieName.text() == '':
            self.feedback.setText("Supply a Die Name")
        elif not self.read_only and self.dieName.text() in self.existing_dies:
            self.feedback.setText("Die name already exists !")

    # Maskset
        if self.feedback.text() == '':
            if self.fromMaskset.currentText() == "":
                self.feedback.setText("No maskset selected")

    # Grade & reference grade
        if self.feedback.text() == '':
            if not self.isAGrade.isChecked():
                if self.referenceGrade.currentText() == '':
                    self.feedback.setText("A non-A-Grade product needs a reference grade, select one.")

    # Type & customer
        if self.feedback.text() == '':
            if self.Type.currentText() == "ASIC" and self.customer.text() == "":
                self.feedback.setText("need a customer name for the ASIC")

        if self.fromMaskset.currentText():
            self.isAGrade.setEnabled(True)

    # Buttons
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
        else:  # ASSP
            customer = ''

        return {'name': self.dieName.text(),
                'hardware': self.withHardware.currentText(),
                'maskset': self.fromMaskset.currentText(),
                'quality': self.quality.currentText(),
                'grade': grade,
                'grade_reference': grade_reference,
                'type': self.Type.currentText(),
                'customer': customer}

    def OKButtonPressed(self):
        configuration = self._get_current_configuration()
        self.project_info.add_die(configuration['name'], configuration['hardware'], configuration['maskset'],
                                  configuration['quality'], configuration['grade'], configuration['grade_reference'],
                                  configuration['type'], configuration['customer'])
        self.accept()

    def CancelButtonPressed(self):
        self.accept()


def new_die_dialog(project_info):
    newDieWizard = DieWizard(project_info)
    newDieWizard.exec_()
    del(newDieWizard)
