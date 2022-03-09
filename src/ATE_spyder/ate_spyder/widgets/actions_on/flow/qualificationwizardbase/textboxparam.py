# -*- coding: utf-8 -*-
from ate_projectdatabase.FileOperator import DBObject
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from ate_spyder.widgets.actions_on.flow.qualificationwizardbase.parameter import parameter


# The TextBoxParam represents a parameter that has a value
# and a name. It will generate a lineedit for dataentry
# end a label to show the name of the parameter. No validation
# is done on the input, except, that the parameter must not
# be empty
class TextBoxParam(parameter):

    def __init__(self, name):
        self.name = name
        self.inputBox = QtWidgets.QLineEdit()
        self.inputBox.setObjectName(f"txt{name}")

    # This method shall create the ui controls that
    # represent this parameter
    def create_ui_components(self, parent_container, on_change_handler):
        self.inputBox.textChanged.connect(on_change_handler)

        # Create Label with parameter name
        layout = QtWidgets.QHBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignLeft)

        textField = QtWidgets.QLabel()
        textField.setText(self.name)
        textField.setMaximumWidth(196)
        layout.addWidget(textField)

        # Append Input box
        self.inputBox.setMaximumWidth(256)
        self.inputBox.setAlignment(QtCore.Qt.AlignLeft)
        layout.addWidget(self.inputBox)

        self.unitTextField = QtWidgets.QLabel()
        self.unitTextField.setAlignment(QtCore.Qt.AlignRight)
        self.unitTextField.setMinimumWidth(64)
        self.unitTextField.setMaximumWidth(64)
        self.unitTextField.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        layout.addWidget(self.unitTextField)

        layout.insertStretch(1)
        parent_container.addLayout(layout)
        return layout

    def disable_ui_components(self):
        self.inputBox.setEnabled(False)

    # The validate method shall yield true, if the
    # data entered in the parameters fields is correct
    def validate(self) -> bool:
        good = self._validate_impl()
        if not good:
            self.inputBox.setStyleSheet('color: orange')
        else:
            self.inputBox.setStyleSheet('color: white')
        return good

    def _validate_impl(self) -> bool:
        return self.inputBox.text() != ""

    def store_values(self, dst: DBObject):
        dst.write_attribute(self.name, self.inputBox.text())

    def load_values(self, src: DBObject):
        if not src.has_attribute(self.name):
            self.inputBox.setText("")
        else:
            self.inputBox.setText(src.read_attribute(self.name))
