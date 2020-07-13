# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 16:09:05 2019

@author: hoeren
"""
import os
import re

from PyQt5 import QtCore, QtGui
from ATE.org.actions_on.utils.BaseDialog import BaseDialog


class NewProductWizard(BaseDialog):
    def __init__(self, project_info, read_only=False):
        super().__init__(__file__)
        self.read_only = read_only
        self.project_info = project_info
        self._setup()
        self._connect_event_handler()

    def _setup(self):
        self.setWindowTitle(' '.join(re.findall('.[^A-Z]*', os.path.basename(__file__).replace('.py', ''))))

        self.existing_hardwares = self.project_info.get_active_hardware_names()
        if len(self.existing_hardwares) == 0:
            self.existing_hardwares = ['']

        from ATE.org.validation import valid_product_name_regex
        rxProductName = QtCore.QRegExp(valid_product_name_regex)
        ProductName_validator = QtGui.QRegExpValidator(rxProductName, self)
        self.ProductName.setText("")
        self.ProductName.setValidator(ProductName_validator)
        self.ProductName.textChanged.connect(self._verify)

        self.WithHardware.clear()
        for index, hardware in enumerate(self.existing_hardwares):
            self.WithHardware.addItem(hardware)
            if hardware == self.project_info.active_hardware:
                self.WithHardware.setCurrentIndex(index)

        self._update_device_list()

        self.Feedback.setText("No product name")
        self.Feedback.setStyleSheet('color: orange')

        self.referenceGradeLabel.setDisabled(True)
        self.referenceGradeLabel.setHidden(True)
        self.referenceGradeLabel.setVisible(False)

        referenced_products, first_free_grade, reference_products = self._generate_grade_reference()

        self.referenceGrade.addItems(reference_products)

        self.referenceGrade.setCurrentText('')
        self.referenceGrade.setDisabled(True)
        self.referenceGrade.setHidden(True)
        self.referenceGrade.setVisible(False)

        self.gradeLabel.setDisabled(True)
        self.gradeLabel.setHidden(True)
        self.gradeLabel.setVisible(False)

        self.grade.clear()
        self.grade.addItems(sorted(list(referenced_products)))
        for index in range(self.grade.count()):
            item_text = self.grade.itemText(index)
            if referenced_products[item_text] != '':
                self.grade.model().item(index).setEnabled(False)
                self.grade.model().item(index).setToolTip(referenced_products[item_text])
        self.grade.setCurrentText(first_free_grade)
        self.grade.setDisabled(True)
        self.grade.setHidden(True)
        self.grade.setVisible(False)

    # Type & customer
        self.Type.setCurrentText('ASSP')

        self.customerLabel.setDisabled(False)
        self.customerLabel.setHidden(True)

        self.customer.setText('')
        self.customer.setHidden(True)

    # feedback
        self.Feedback.setStyleSheet('color: orange')

    # buttons
        self.OKButton.setEnabled(False)

        self._verify()

    def _generate_grade_reference(self):
        all_products = self.project_info.get_products_info()
        reference_products = ['']
        referenced_products = {i: '' for i in ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']}
        free_grades = []

        for product in all_products:
            if product.hardware == self.WithHardware.currentText() and product.device == self.FromDevice.currentText():
                if product.grade == 'A':
                    reference_products.append(product.name)
                else:
                    referenced_products[all_products[product.name]].grade = product.grade_reference

        for product in referenced_products:
            if referenced_products[product] == '':
                free_grades.append(product)

        if len(free_grades) == 0:  # nothing free anymore
            first_free_grade = ''
        else:
            first_free_grade = sorted(free_grades)[0]

        return referenced_products, first_free_grade, reference_products

    def _update_device_list(self):
        self.existing_devices = self.project_info.get_active_device_names_for_hardware(self.project_info.active_hardware)
        self.existing_products = self.project_info.get_products()
        self.FromDevice.clear()
        self.FromDevice.addItems(self.existing_devices)
        self.FromDevice.setCurrentText('' if not len(self.existing_devices) else self.existing_devices[0])
        # TODO: why can't we set the first available device as default ? as below
        # self.FromDevice.setCurrentIndex(0)  # this is the empty string in the beginning of the list!

    def _connect_event_handler(self):
        self.FromDevice.currentIndexChanged.connect(self._verify)
        self.WithHardware.currentTextChanged.connect(self.hardware_changed)
        self.isAGrade.toggled.connect(self._a_grade_changed)
        self.referenceGrade.currentTextChanged.connect(self.referenceGradeChanged)
        self.Type.currentTextChanged.connect(self.typeChanged)
        self.CancelButton.clicked.connect(self.CancelButtonPressed)
        self.OKButton.clicked.connect(self.OKButtonPressed)

    def typeChanged(self, SelectedType):
        '''
        if the Type is 'ASIC' enable CustomerLabel and Customer
        '''
        if SelectedType == 'ASIC':
            self.customerLabel.setVisible(True)

            self.customer.blockSignals(True)
            self.customer.setText("")
            self.customer.setVisible(True)
            self.customer.blockSignals(False)
        else:
            self.customerLabel.setVisible(False)
            self.customerLabel.setEnabled(True)

            self.customer.blockSignals(True)
            self.customer.setText("")
            self.customer.setVisible(False)
            self.customer.blockSignals(False)

    def referenceGradeChanged(self):
        self._verify()

    def _a_grade_changed(self, is_A_grade):
        if is_A_grade:
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

            referenced_products, first_free_grade, reference_products = self._generate_grade_reference()

            self.referenceGrade.blockSignals(True)
            self.referenceGrade.clear()
            self.referenceGrade.addItems(reference_products)
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
            self.grade.addItems(sorted(list(referenced_products)))
            for index in range(self.grade.count()):
                item_text = self.grade.itemText(index)
                if referenced_products[item_text] != '':
                    self.grade.model().item(index).setEnabled(False)
                    self.grade.model().item(index).setToolTip(referenced_products[item_text])

            self.grade.setCurrentText(first_free_grade)
            self.grade.setDisabled(False)
            self.grade.setHidden(False)
            self.grade.setVisible(True)
            self.grade.blockSignals(False)

        self._verify()

    def hardware_changed(self, hardware):
        '''
        if the selected hardware changes, make sure the active_hardware
        at the parent level is also changed and that the new device list
        (for the new hardware) is loaded.
        '''
        self.project_info.hardware_activated.emit(hardware)

        self._update_device_list()

    def _verify(self):
        if self.existing_hardwares[0] == '':
            self.Feedback.setText("No hardware is available")
            return

        if len(self.existing_devices) == 0:
            self.Feedback.setText("No device is available")
            return

        self.Feedback.setText('')

        if not self.read_only and self.ProductName.text() in self.existing_products:
            self.Feedback.setText("Product already exists !")
            self.OKButton.setEnabled(False)
        else:
            if self.FromDevice.currentText() == "":
                self.Feedback.setText("No device selected")
                self.OKButton.setEnabled(False)
            else:  # device selected (hardware is always selected)
                self.Feedback.setText("")
                self.OKButton.setEnabled(True)

        # Grade & reference grade
        if self.Feedback.text() == '':
            if not self.isAGrade.isChecked():
                if self.referenceGrade.currentText() == '':
                    self.Feedback.setText("A non-A-Grade product needs a reference grade, select one.")
                    self.OKButton.setEnabled(False)

        if not self.ProductName.text():
            self.Feedback.setText("No product name")
            self.OKButton.setEnabled(False)

    def CancelButtonPressed(self):
        self.accept()

    def _get_actual_defintion(self):
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

        return {'name': self.ProductName.text(),
                'device': self.FromDevice.currentText(),
                'hardware': self.WithHardware.currentText(),
                'quality': self.productQuality.currentText(),
                'grade': grade,
                'grade_reference': grade_reference,
                'type': self.Type.currentText(),
                'customer': customer}

    def OKButtonPressed(self):
        configuration = self._get_actual_defintion()

        self.project_info.add_product(configuration['name'], configuration['device'],
                                      configuration['hardware'], configuration['quality'],
                                      configuration['grade'], configuration['grade_reference'],
                                      configuration['type'], configuration['customer'])
        self.accept()


def new_product_dialog(project_info):
    newProductWizard = NewProductWizard(project_info)
    newProductWizard.exec_()
    del(newProductWizard)
